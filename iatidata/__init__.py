import xmlschema
import json
import os
import sqlalchemy as sa
import tempfile
import functools
import datetime
import subprocess
from textwrap import dedent

import iatikit
import pathlib
from collections import defaultdict
from lxml import etree

import concurrent.futures
import csv
import gzip

from iatidata import sort_iati

this_dir = pathlib.Path(__file__).parent.resolve()

def get_engine(schema=None, db_uri=None, pool_size=1):
    if not db_uri:
        db_uri = os.environ["DATABASE_URL"]

    connect_args = {}
    if schema:
        connect_args = {"options": f"-csearch_path={schema}"}

    return sa.create_engine(db_uri, pool_size=pool_size, connect_args=connect_args)


def create_table(table, sql, **params):

    engine = get_engine()
    with engine.connect() as con:
        con.execute(
            sa.text(
                f"""DROP TABLE IF EXISTS {table};
                    CREATE TABLE {table}
                    AS
                    {sql};"""
            ),
            **params,
        )


def create_activites_table():
    print("creating activities table")
    engine = get_engine()
    with engine.begin() as connection:
        connection.execute(
            """DROP TABLE IF EXISTS _all_activities;
               CREATE TABLE _all_activities(id SERIAL, prefix TEXT, filename TEXT, error TEXT, version TEXT, activity JSONB);
            """
        )


def get_standard(refresh=False):
    if not (pathlib.Path() / '__iatikitcache__').is_dir() or refresh:
        print("getting standard")
        iatikit.download.standard()


def get_registry(refresh=False):

    if not (pathlib.Path() / '__iatikitcache__').is_dir() or refresh:
        print("getting regisitry data")
        iatikit.download.data()

    return iatikit.data()


def flatten_schema_docs(cur, path=''):

    for field, value in cur.items():
        info = value.get('info')
        docs = info.get('docs', '')
        yield f'{path}{field}', docs
        for attribute, attribute_docs in info.get('attributes', {}).items():
            yield f'{path}{field}_{attribute}', attribute_docs

        yield from flatten_schema_docs(value.get('properties', {}), f'{path}{field}_')


class IATISchemaWalker(sort_iati.IATISchemaWalker):

    def __init__(self):
        self.tree = etree.parse(str(pathlib.Path() / '__iatikitcache__/standard/schemas/203/iati-activities-schema.xsd'))
        self.tree2 = etree.parse(str(pathlib.Path() / '__iatikitcache__/standard/schemas/203/iati-common.xsd'))


def get_schema_docs():
    schema_docs = IATISchemaWalker().create_schema_docs('iati-activity')

    schema_docs_lookup = {}
    for num, (field, doc) in enumerate(flatten_schema_docs(schema_docs)):
        field = field.replace('-', '')
        schema_docs_lookup[field] = [num + 1, doc]

    return schema_docs_lookup


def get_sorted_schema_dict():
    schema_dict = IATISchemaWalker().create_schema_dict('iati-activity')
    return schema_dict


def sort_iati_element(element, schema_subdict):
    """
    Sort the given elements children according to the order of schema_subdict.
    """
    def sort(x):
        try:
            return list(schema_subdict.keys()).index(x.tag)
        except ValueError:
            # make sure non schema elements go to the end
            return 9999

    children = list(element)
    for child in children:
        element.remove(child)
    for child in sorted(children, key=sort):
        element.append(child)
        subdict = schema_subdict.get(child.tag)
        if subdict:
            sort_iati_element(child, subdict)


ALL_CODELIST_LOOKUP = {}

def get_codelists_lookup():
    mapping_file = pathlib.Path() / '__iatikitcache__/standard/codelist_mappings/203/activity-mappings.json'
    mappings_list = json.loads(mapping_file.read_text())

    mappings = defaultdict(list)

    for mapping in mappings_list:
        path = tuple(mapping['path'][16:].replace('-', '').split('/'))
        mappings[mapping['codelist']].append(path)

    mappings.pop('Version')

    codelists_dir = pathlib.Path() / '__iatikitcache__/standard/codelists'

    for codelist_file in codelists_dir.glob('*.json'):
        codelist = json.loads(codelist_file.read_text())
        attributes = codelist.get('attributes')
        data = codelist.get('data')
        if not attributes or not data:
            continue

        codelist_name = attributes['name']
        paths = mappings[codelist_name]

        for path in paths:
            for codelist_value, info in data.items():
                value_name = info.get('name', codelist_value)
                ALL_CODELIST_LOOKUP[(path, codelist_value)] = value_name


def save_converted_xml_to_csv(dataset_etree, csv_file, prefix=None, filename=None):

    transform = etree.XSLT(etree.parse(str(this_dir / 'iati-activities.xsl')))
    schema = xmlschema.XMLSchema(str(pathlib.Path() / '__iatikitcache__/standard/schemas/203/iati-activities-schema.xsd'))

    schama_dict = get_sorted_schema_dict()

    for activity in dataset_etree.findall('iati-activity'):
        version = dataset_etree.get('version', '1.01')

        activities = etree.Element("iati-activities", version=version)
        activities.append(activity)

        if version.startswith('1'):
            activities = transform(activities).getroot()

        sort_iati_element(activities.getchildren()[0], schama_dict)

        activity, error = xmlschema.to_dict(activities, schema=schema, validation='lax', decimal_type=float)

        activity = activity.get('iati-activity', [{}])[0]

        csv_file.writerow([prefix, filename, str(error) if error else '', version, json.dumps(activity)])


def csv_file_to_db(csv_fd):
    engine = get_engine()
    with engine.begin() as connection:
        dbapi_conn = connection.connection
        copy_sql = "COPY _all_activities(prefix, filename, error, version, activity)  FROM STDIN WITH CSV"
        cur = dbapi_conn.cursor()
        cur.copy_expert(copy_sql, csv_fd)


def save_part(data):
    engine = get_engine()
    bucket_num, datasets = data

    with tempfile.TemporaryDirectory() as tmpdirname:
        print(bucket_num, tmpdirname)
        with gzip.open(f'{tmpdirname}/out.csv.gz', "wt", newline="") as f:
            csv_file = csv.writer(f)

            for num, dataset in enumerate(datasets):
                if num % 100 == 0:
                    print(bucket_num, num, flush=True)

                if dataset.filetype != 'activity':
                    continue

                if not dataset.data_path:
                    print(dataset, 'not found')
                    continue

                path = pathlib.Path(dataset.data_path)
                prefix, filename = path.parts[-2:]

                try:
                    root = dataset.etree.getroot()
                except Exception as e:
                    print('Error parsing XML', e)
                    continue

                save_converted_xml_to_csv(root, csv_file, prefix, filename)

        with gzip.open(f'{tmpdirname}/out.csv.gz', "rt") as f:
            csv_file_to_db(f)

    return bucket_num


def save_all(parts=5, sample=None, refresh=False):

    create_activites_table()

    get_standard(refresh)
    registry = get_registry(refresh)

    buckets = defaultdict(list)
    for num, dataset in enumerate(registry.datasets):
        buckets[num % parts].append(dataset)
        if sample and num > sample:
            break

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for job in executor.map(save_part, buckets.items()):
            print('DONE {job}')
            continue


def process_registry(processes=5, sample=None, refresh=False):
    save_all(sample=sample, parts=processes, refresh=refresh)
    activity_objects()
    schema_analysis()
    postgres_tables()


def process_activities(activities, name):
    create_activites_table()

    get_standard()

    with tempfile.TemporaryDirectory() as tmpdirname:
        print("converting to json")
        with gzip.open(f'{tmpdirname}/out.csv.gz', "wt", newline="") as f:
            csv_file = csv.writer(f)
            save_converted_xml_to_csv(activities, csv_file, name, name)

        with gzip.open(f'{tmpdirname}/out.csv.gz', "rt") as f:
            csv_file_to_db(f)

    activity_objects()
    schema_analysis()
    postgres_tables()


def flatten_object(obj, current_path="", no_index_path=tuple()):
    for key, value in list(obj.items()):
        new_no_index_path = no_index_path + (key,)

        key = key.replace('-', '')
        key = key.replace('@{http://www.w3.org/XML/1998/namespace}', '')
        key = key.replace('@', '')
        if isinstance(value, dict):
            yield from flatten_object(value, f"{current_path}{key}_", new_no_index_path)
        else:
            if isinstance(value, str):
                codelist_value_name = ALL_CODELIST_LOOKUP.get((new_no_index_path, value))
                if codelist_value_name:
                    yield f"{current_path}{key}name", codelist_value_name

            if key == '$':
                if current_path:
                    yield f"{current_path}"[:-1], value
                else:
                    yield '_', value
            else:
                yield f"{current_path}{key}", value


@functools.lru_cache(1000)
def path_info(full_path, no_index_path):
    all_paths = []
    for num, part in enumerate(full_path):
        if isinstance(part, int):
            all_paths.append(full_path[: num + 1])

    parent_paths = all_paths[:-1]
    path_key = all_paths[-1] if all_paths else []

    object_key = ".".join(str(key) for key in path_key)
    parent_keys_list = [
        ".".join(str(key) for key in parent_path) for parent_path in parent_paths
    ]
    parent_keys_no_index = [
        "_".join(str(key) for key in parent_path if not isinstance(key, int))
        for parent_path in parent_paths
    ]
    object_type = "_".join(str(key) for key in no_index_path) or "activity"
    parent_keys = (dict(zip(parent_keys_no_index, parent_keys_list)),)
    return object_key, parent_keys_list, parent_keys_no_index, object_type, parent_keys


def traverse_object(obj, emit_object, full_path=tuple(), no_index_path=tuple()):
    for original_key, value in list(obj.items()):
        key = original_key.replace('-', '')

        if key == 'narrative':
            narratives = []
            for narrative in value:
                if not narrative:
                    continue
                if isinstance(narrative, dict):
                    lang = narrative.get('@{http://www.w3.org/XML/1998/namespace}lang', '')
                    narrative = f"{lang.upper()}: {narrative.get('$', '')}"
                narratives.append(narrative)
            obj['narrative'] = ", ".join(narratives)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            for num, item in enumerate(value):
                if not isinstance(item, dict):
                    item = {"__error": "A non object is in array of objects"}
                yield from traverse_object(
                    item, True, full_path + (key, num), no_index_path + (key,)
                )
            obj.pop(original_key)
        elif isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                obj[key] = json.dumps(value)
        elif isinstance(value, dict):
             yield from traverse_object(
                 value, False, full_path + (key,), no_index_path + (key,)
             )

    if obj and emit_object:
        new_object = {key.replace('-', ''): value for key, value in obj.items()}
        yield new_object, full_path, no_index_path


def create_rows(result):
    rows = []

    if result.activity is None:
        return []

    for object, full_path, no_index_path in traverse_object(result.activity, 1):

        (
            object_key,
            parent_keys_list,
            parent_keys_no_index,
            object_type,
            parent_keys,
        ) = path_info(full_path, no_index_path)

        object[
            "_link"
        ] = f'{result.id}{"." if object_key else ""}{object_key}'
        object["_link_activity"] = str(result.id)
        for no_index, full in zip(parent_keys_no_index, parent_keys_list):
            object[
                f"_link_{no_index}"
            ] = f"{result.id}.{full}"

        row = dict(
            id=result.id,
            prefix=result.prefix,
            object_key=object_key,
            parent_keys=json.dumps(parent_keys),
            object_type=object_type,
            object=json.dumps(dict(flatten_object(object, no_index_path=no_index_path))),
        )
        rows.append(row)

    return [list(row.values()) for row in rows]


def activity_objects():
    print("generating activity_objects")

    get_codelists_lookup()

    engine = get_engine()
    engine.execute(
        """
        DROP TABLE IF EXISTS _activity_objects;
        CREATE TABLE _activity_objects(id bigint, prefix TEXT,
        object_key TEXT, parent_keys JSONB, object_type TEXT, object JSONB);
        """
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        with engine.begin() as connection:
            connection = connection.execution_options(stream_results=True, max_row_buffer=1000)
            results = connection.execute(
                "SELECT id, prefix, activity FROM _all_activities"
            )
            paths_csv_file = tmpdirname + "/paths.csv"

            print("Making CSV file")
            with gzip.open(paths_csv_file, "wt", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                for num, result in enumerate(results):
                    if num % 10000 == 0:
                        print(str(datetime.datetime.utcnow()), num)
                    csv_writer.writerows(create_rows(result))

        print("Uploading Data")
        with engine.begin() as connection, gzip.open(
            paths_csv_file, "rt"
        ) as f:
            dbapi_conn = connection.connection
            copy_sql = "COPY _activity_objects FROM STDIN WITH CSV"
            cur = dbapi_conn.cursor()
            cur.copy_expert(copy_sql, f)


DATE_RE = r'^(\d{4})-(\d{2})-(\d{2})([T ](\d{2}):(\d{2}):(\d{2}(?:\.\d*)?)((-(\d{2}):(\d{2})|Z)?))?$'


def schema_analysis():
    print("doing schema analysis")
    create_table(
        "_object_type_aggregate",
        f"""SELECT
              object_type,
              each.key,
              CASE
                 WHEN jsonb_typeof(value) != 'string'
                     THEN jsonb_typeof(value)
                 WHEN (value ->> 0) ~ '{DATE_RE}'
                     THEN 'datetime'
                 ELSE 'string'
              END value_type,
              count(*)
           FROM
              _activity_objects ro, jsonb_each(object) each
           GROUP BY 1,2,3;
        """,
    )

    create_table(
        "_object_type_fields",
        """SELECT
              object_type,
              key,
              CASE WHEN
                  count(*) > 1
              THEN 'string'
              ELSE max(value_type) end value_type,
              SUM("count") AS "count"
           FROM
              _object_type_aggregate
           WHERE
              value_type != 'null'
           GROUP BY 1,2;
        """,
    )

    schema_lookup = get_schema_docs()

    engine = get_engine()
    with engine.begin() as connection:
        connection.execute('''
            drop table if exists _fields;
            create table _fields (table_name TEXT, field TEXT, type TEXT, count INT, docs TEXT, field_order INT)
        ''')

        results = connection.execute(
            "SELECT object_type, key, value_type, count FROM _object_type_fields"
        )

        for object_type, key, value_type, count in results:

            order, docs = 9999, ''

            if object_type == 'activity':
                path = key
            else:
                path = object_type + '_' + key
            if key.startswith('_link'):
                order = 0
                docs = '_link field'
            else:
                order, docs = schema_lookup.get(path, [9999, ''])
                if not docs:
                    if key.endswith('name'):
                        order, docs = schema_lookup.get(path[:-4], [9999, ''])

            connection.execute('insert into _fields values (%s, %s, %s, %s,  %s, %s)',
                                object_type, key, value_type, count, docs, order)

    create_table('_tables', 'SELECT table_name, min(field_order) table_order, max("count") as rows  FROM _fields WHERE field_order <> 0 GROUP BY table_name')
        

def create_field_sql(object_details, sqlite=False):
    fields = []
    lowered_fields = set()
    fields_with_type = []
    for num, item in enumerate(object_details):
        name = item["name"]

        if sqlite and name.lower() in lowered_fields:
            name = f'"{name}_{num}"'

        type = item["type"]
        if type == "number":
            field = f'"{name}" numeric'
        elif type == "array":
            field = f'"{name}" JSONB'
        elif type == "boolean":
            field = f'"{name}" boolean'
        elif type == "datetime":
            field = f'"{name}" timestamp'
        else:
            field = f'"{name}" TEXT'

        lowered_fields.add(name.lower())
        fields.append(f'"{name}"')
        fields_with_type.append(field)

    return ", ".join(fields), ", ".join(fields_with_type)


def postgres_tables(drop_release_objects=False):
    print("making postgres tables")
    object_details = defaultdict(list)
    with get_engine().begin() as connection:
        result = list(
            connection.execute(
                "SELECT table_name, field, type FROM _fields order by field_order"
            )
        )
        for row in result:
            object_details[row.table_name].append(dict(name=row.field,
                                                  type=row.type))


    for object_type, object_detail in object_details.items():
        field_sql, as_sql = create_field_sql(object_detail)
        table_sql = f"""
           SELECT prefix, {field_sql}
           FROM _activity_objects, jsonb_to_record(object) AS ({as_sql})
           WHERE object_type = :object_type
        """
        create_table(object_type, table_sql, object_type=object_type)

    if drop_release_objects:
        with get_engine().begin() as connection:
            connection.execute("DROP TABLE IF EXISTS _release_objects")


def export_sqlite():
    sqlite_file = pathlib.Path() / 'iati.sqlite'
    if sqlite_file.is_file():
        sqlite_file.unlink()

    object_details = defaultdict(list)
    with tempfile.TemporaryDirectory() as tmpdirname, get_engine().begin() as connection:
        result = list(
            connection.execute(
                "SELECT table_name, field, type FROM _fields order by field_order"
            )
        )
        for row in result:
            object_details[row.table_name].append(dict(name=row.field,
                                                  type=row.type))

        for object_type, object_details in object_details.items():
            print(f"importing table {object_type}")
            with open(f"{tmpdirname}/{object_type}.csv", "wb") as out:
                dbapi_conn = connection.connection
                copy_sql = f'COPY "{object_type.lower()}" TO STDOUT WITH (FORMAT CSV, FORCE_QUOTE *)'
                cur = dbapi_conn.cursor()
                cur.copy_expert(copy_sql, out)

            _, field_def = create_field_sql(object_details, sqlite=True)

            target_object_type = object_type
            if object_type == 'transaction':
                target_object_type = 'trans'

            import_sql = f"""
            .mode csv
            CREATE TABLE "{target_object_type}" (prefix, {field_def}) ;
            .import '{tmpdirname}/{object_type}.csv' "{target_object_type}" """

            print(import_sql)

            subprocess.run(
                ["sqlite3", f"{sqlite_file}"],
                input=dedent(import_sql),
                text=True,
                check=True,
            )

            os.remove(f"{tmpdirname}/{object_type}.csv")


        with open(f"{tmpdirname}/fields.csv", "w") as csv_file:

            dbapi_conn = connection.connection
            copy_sql = f'COPY "_fields" TO STDOUT WITH (FORMAT CSV, FORCE_QUOTE *)'
            cur = dbapi_conn.cursor()
            cur.copy_expert(copy_sql, csv_file)

        import_sql = f"""
            .mode csv
            CREATE TABLE _fields (table_name TEXT, field TEXT, type TEXT, count INT, docs TEXT, field_order INT);
            .import {tmpdirname}/fields.csv "_fields" """

        subprocess.run(
            ["sqlite3", f"{sqlite_file}"],
            input=dedent(import_sql),
            text=True,
            check=True,
        )


        subprocess.run(
            ["gzip", "-k", "-9", f"{sqlite_file}"],
            check=True
        )

