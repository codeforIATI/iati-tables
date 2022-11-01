import xmlschema
import json
import os
import sqlalchemy as sa
import tempfile
import functools
import datetime
import shutil
import base64
import subprocess
import zipfile
from textwrap import dedent
from io import StringIO
import re

import requests
import iatikit
import pathlib
from collections import defaultdict
from lxml import etree
from google.cloud import bigquery
from google.cloud.bigquery.dataset import AccessEntry
from google.oauth2 import service_account
from fastavro import parse_schema, writer

import concurrent.futures
import csv
import gzip

from iatidata import sort_iati

this_dir = pathlib.Path(__file__).parent.resolve()

output_dir = os.environ.get("IATI_TABLES_OUTPUT", '.')

schema = os.environ.get("IATI_TABLES_SCHEMA")

output_path = pathlib.Path(output_dir)


def get_engine(db_uri=None, pool_size=1):
    if not db_uri:
        db_uri = os.environ["DATABASE_URL"]

    connect_args = {}

    if schema:
        connect_args = {"options": f"-csearch_path={schema}"}

    return sa.create_engine(db_uri, pool_size=pool_size, connect_args=connect_args)


def _create_table(table, con, sql, **params):
    con.execute(
        sa.text(
            f"""DROP TABLE IF EXISTS "{table}";
                CREATE TABLE "{table}"
                AS
                {sql};"""
        ),
        **params,
    )


def create_table(table, sql, **params):
    engine = get_engine()
    with engine.connect() as con:
        _create_table(table.lower(), con, sql, **params)


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
    if not (pathlib.Path() / "__iatikitcache__").is_dir() or refresh:
        print("getting standard")
        iatikit.download.standard()


def get_registry(refresh=False):

    if not (pathlib.Path() / "__iatikitcache__").is_dir() or refresh:
        print("getting regisitry data")
        iatikit.download.data()

    return iatikit.data()


def flatten_schema_docs(cur, path=""):

    for field, value in cur.items():
        info = value.get("info")
        docs = info.get("docs", "")
        yield f"{path}{field}", docs
        for attribute, attribute_docs in info.get("attributes", {}).items():
            yield f"{path}{field}_{attribute}", attribute_docs

        yield from flatten_schema_docs(value.get("properties", {}), f"{path}{field}_")


class IATISchemaWalker(sort_iati.IATISchemaWalker):
    def __init__(self):
        self.tree = etree.parse(
            str(
                pathlib.Path()
                / "__iatikitcache__/standard/schemas/203/iati-activities-schema.xsd"
            )
        )
        self.tree2 = etree.parse(
            str(
                pathlib.Path() / "__iatikitcache__/standard/schemas/203/iati-common.xsd"
            )
        )


def get_schema_docs():
    schema_docs = IATISchemaWalker().create_schema_docs("iati-activity")

    schema_docs_lookup = {}
    for num, (field, doc) in enumerate(flatten_schema_docs(schema_docs)):
        field = field.replace("-", "")
        # leave some space for extra fields at the start
        schema_docs_lookup[field] = [num + 10, doc]

    return schema_docs_lookup


def get_sorted_schema_dict():
    schema_dict = IATISchemaWalker().create_schema_dict("iati-activity")
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
    mapping_file = (
        pathlib.Path()
        / "__iatikitcache__/standard/codelist_mappings/203/activity-mappings.json"
    )
    mappings_list = json.loads(mapping_file.read_text())

    mappings = defaultdict(list)

    for mapping in mappings_list:
        path = tuple(mapping["path"][16:].replace("-", "").split("/"))
        mappings[mapping["codelist"]].append(path)

    mappings.pop("Version")

    mappings["Country"] = [('transaction', 'recipientcountry', '@code'),
                           ('recipientcountry', '@code')]

    codelists_dir = pathlib.Path() / "__iatikitcache__/standard/codelists"

    for codelist_file in codelists_dir.glob("*.json"):
        codelist = json.loads(codelist_file.read_text())
        attributes = codelist.get("attributes")
        data = codelist.get("data")
        if not attributes or not data:
            continue

        codelist_name = attributes["name"]
        paths = mappings[codelist_name]

        for path in paths:
            for codelist_value, info in data.items():
                value_name = info.get("name", codelist_value)
                ALL_CODELIST_LOOKUP[(path, codelist_value)] = value_name


def save_converted_xml_to_csv(dataset_etree, csv_file, prefix=None, filename=None):

    transform = etree.XSLT(etree.parse(str(this_dir / "iati-activities.xsl")))
    schema = xmlschema.XMLSchema(
        str(
            pathlib.Path()
            / "__iatikitcache__/standard/schemas/203/iati-activities-schema.xsd"
        )
    )

    schama_dict = get_sorted_schema_dict()

    for activity in dataset_etree.findall("iati-activity"):
        version = dataset_etree.get("version", "1.01")

        activities = etree.Element("iati-activities", version=version)
        activities.append(activity)

        if version.startswith("1"):
            activities = transform(activities).getroot()

        sort_iati_element(activities.getchildren()[0], schama_dict)

        activity, error = xmlschema.to_dict(
            activities, schema=schema, validation="lax", decimal_type=float
        )

        activity = activity.get("iati-activity", [{}])[0]

        csv_file.writerow(
            [
                prefix,
                filename,
                str(error) if error else "",
                version,
                json.dumps(activity),
            ]
        )


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
        with gzip.open(f"{tmpdirname}/out.csv.gz", "wt", newline="") as f:
            csv_file = csv.writer(f)

            for num, dataset in enumerate(datasets):
                if num % 100 == 0:
                    print(bucket_num, num, flush=True)

                if dataset.filetype != "activity":
                    continue

                if not dataset.data_path:
                    print(dataset, "not found")
                    continue

                path = pathlib.Path(dataset.data_path)
                prefix, filename = path.parts[-2:]

                try:
                    root = dataset.etree.getroot()
                except Exception as e:
                    print("Error parsing XML", e)
                    continue

                save_converted_xml_to_csv(root, csv_file, prefix, filename)

        with gzip.open(f"{tmpdirname}/out.csv.gz", "rt") as f:
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
            print("DONE {job}")
            continue


def process_registry(processes=5, sample=None, refresh=False):

    if schema:
        engine = get_engine()
        engine.execute(
            f"""
            DROP schema IF EXISTS {schema} CASCADE;
            CREATE schema {schema};
            """
        )

    save_all(sample=sample, parts=processes, refresh=refresh)
    activity_objects()
    schema_analysis()
    postgres_tables()
    sql_process()


def process_activities(activities, name):
    create_activites_table()

    get_standard()

    with tempfile.TemporaryDirectory() as tmpdirname:
        print("converting to json")
        with gzip.open(f"{tmpdirname}/out.csv.gz", "wt", newline="") as f:
            csv_file = csv.writer(f)
            save_converted_xml_to_csv(activities, csv_file, name, name)

        with gzip.open(f"{tmpdirname}/out.csv.gz", "rt") as f:
            csv_file_to_db(f)

    activity_objects()
    schema_analysis()
    postgres_tables()


def flatten_object(obj, current_path="", no_index_path=tuple()):
    for key, value in list(obj.items()):
        new_no_index_path = no_index_path + (key,)

        key = key.replace("-", "")
        key = key.replace("@{http://www.w3.org/XML/1998/namespace}", "")
        key = key.replace("@", "")
        if isinstance(value, dict):
            yield from flatten_object(value, f"{current_path}{key}_", new_no_index_path)
        else:
            if isinstance(value, str):
                codelist_value_name = ALL_CODELIST_LOOKUP.get(
                    (new_no_index_path, value)
                )
                if codelist_value_name:
                    yield f"{current_path}{key}name", codelist_value_name

            if key == "$":
                if current_path:
                    yield f"{current_path}"[:-1], value
                else:
                    yield "_", value
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
        key = original_key.replace("-", "")

        if key == "narrative":
            narratives = []
            for narrative in value:
                if not narrative:
                    continue
                if isinstance(narrative, dict):
                    lang = narrative.get(
                        "@{http://www.w3.org/XML/1998/namespace}lang", ""
                    )
                    narrative = f"{lang.upper()}: {narrative.get('$', '')}"
                narratives.append(narrative)
            obj["narrative"] = ", ".join(narratives)
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
        new_object = {key.replace("-", ""): value for key, value in obj.items()}
        yield new_object, full_path, no_index_path

DATE_MAP = {'1': 'plannedstart', '2': 'actualstart', '3': 'plannedend', '4': 'actualend'}
DATE_MAP_BY_FIELD = {value: int(key) for key, value in DATE_MAP.items()}

def create_rows(result):
    rows = []

    if result.activity is None:
        return []

    # get activity dates before traversal remove them
    activity_dates = result.activity.get('activity-date', []) or []

    for object, full_path, no_index_path in traverse_object(result.activity, 1):

        (
            object_key,
            parent_keys_list,
            parent_keys_no_index,
            object_type,
            parent_keys,
        ) = path_info(full_path, no_index_path)

        object["_link"] = f'{result.id}{"." if object_key else ""}{object_key}'
        object["_link_activity"] = str(result.id)
        if object_type != 'activity':
            object["iatiidentifier"] = result.activity.get('iati-identifier')
            reporting_org = result.activity.get('reporting-org', {}) or {}
            object["reportingorg_ref"] = reporting_org.get('@ref')

        if object_type == 'activity':
            for activity_date in activity_dates:
                if not isinstance(activity_date, dict):
                    continue
                type = activity_date.get('@type')
                date = activity_date.get('@iso-date')
                if type and date and type in DATE_MAP:
                    object[DATE_MAP[type]] = date

        for no_index, full in zip(parent_keys_no_index, parent_keys_list):
            object[f"_link_{no_index}"] = f"{result.id}.{full}"

        row = dict(
            id=result.id,
            prefix=result.prefix,
            object_key=object_key,
            parent_keys=json.dumps(parent_keys),
            object_type=object_type,
            object=json.dumps(
                dict(flatten_object(object, no_index_path=no_index_path))
            ),
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
            connection = connection.execution_options(
                stream_results=True, max_row_buffer=1000
            )
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
        with engine.begin() as connection, gzip.open(paths_csv_file, "rt") as f:
            dbapi_conn = connection.connection
            copy_sql = "COPY _activity_objects FROM STDIN WITH CSV"
            cur = dbapi_conn.cursor()
            cur.copy_expert(copy_sql, f)


DATE_RE = r"^(\d{4})-(\d{2})-(\d{2})([T ](\d{2}):(\d{2}):(\d{2}(?:\.\d*)?)((-(\d{2}):(\d{2})|Z)?))?$"


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
        connection.execute(
            """
            drop table if exists _fields;
            create table _fields (table_name TEXT, field TEXT, type TEXT, count INT, docs TEXT, field_order INT)
        """
        )

        results = connection.execute(
            "SELECT object_type, key, value_type, count FROM _object_type_fields"
        )

        for object_type, key, value_type, count in results:

            order, docs = 9999, ""

            if object_type == "activity":
                path = key
            else:
                path = object_type + "_" + key
            if key.startswith("_link"):
                order = 0
                if key == '_link':
                    docs = "Priamry Key for this table. It is unique and used for other tables rows to join to this table."
                else:
                    docs = f"Foreign key to {key[6:]} tables `_link` field"
            elif key == 'iatiidentifier':
                order, docs = 1, 'A globally unique identifier for the activity.'
            elif key == 'reportingorg_ref' and object_type != 'activity':
                order, docs = 2, 'Machine-readable identification string for the organisation issuing the report.'
            elif key in DATE_MAP_BY_FIELD:
                order, docs = DATE_MAP_BY_FIELD[key] + 2, key
            else:
                order, docs = schema_lookup.get(path, [9999, ""])
                if not docs:
                    if key.endswith("name"):
                        order, docs = schema_lookup.get(path[:-4], [9999, ""])

            connection.execute(
                "insert into _fields values (%s, %s, %s, %s,  %s, %s)",
                object_type,
                key,
                value_type,
                count,
                docs,
                order,
            )

    create_table(
        "_tables",
        'SELECT table_name, min(field_order) table_order, max("count") as rows  FROM _fields WHERE field_order > 10 GROUP BY table_name',
    )


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
            field = f'x."{name}" numeric'
        elif type == "array":
            field = f'x."{name}" JSONB'
        elif type == "boolean":
            field = f'x."{name}" boolean'
        elif type == "datetime":
            field = f'x."{name}" timestamp'
        else:
            field = f'x."{name}" TEXT'

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
                "SELECT table_name, field, type FROM _fields order by table_name, field_order, field"
            )
        )
        for row in result:
            object_details[row.table_name].append(dict(name=row.field, type=row.type))

    for object_type, object_detail in object_details.items():
        field_sql, as_sql = create_field_sql(object_detail)
        table_sql = f"""
           SELECT prefix, {field_sql}
           FROM _activity_objects, jsonb_to_record(object) AS x({as_sql})
           WHERE object_type = :object_type
        """
        create_table(object_type, table_sql, object_type=object_type)

    if drop_release_objects:
        with get_engine().begin() as connection:
            connection.execute("DROP TABLE IF EXISTS _release_objects")


def augment_transaction():

    with get_engine().begin() as connection:
        connection.execute(
            """
            drop table if exists _exchange_rates;
            create table _exchange_rates(date text,rate float,Currency text, frequency text, source text, country_code text, country text);
        """
        )

        r = requests.get(
            "https://raw.githubusercontent.com/codeforIATI/imf-exchangerates/gh-pages/imf_exchangerates.csv",
            stream=True,
        )
        f = StringIO(r.text)
        dbapi_conn = connection.connection
        copy_sql = f"COPY _exchange_rates FROM STDIN WITH (FORMAT CSV, HEADER)"
        cur = dbapi_conn.cursor()
        cur.copy_expert(copy_sql, f)

        connection.execute(
            """
            drop table if exists _monthly_currency;
            create table _monthly_currency as select distinct on (substring(date, 1,7), currency) substring(date, 1,7) yearmonth, rate, currency from _exchange_rates;
        """
        )

        _create_table(
            "tmp_transaction_usd",
            connection,
            """
            select 
               t._link, case when coalesce(value_currency, activity.defaultcurrency) = 'USD' then value else value / rate end value_usd 
            from 
               transaction t 
            join
               activity using (_link_activity)
            left join 
               _monthly_currency mc on greatest(substring(value_valuedate::text, 1,7), to_char(current_date-60, 'yyyy-mm')) = yearmonth and lower(coalesce(value_currency, activity.defaultcurrency)) =  lower(currency)
           """,
        )

        _create_table(
            "tmp_transaction_sector",
            connection,
            """select distinct on (_link_transaction) _link_transaction, code, codename from transaction_sector where vocabulary is null or vocabulary in ('', '1');""",
        )

        _create_table(
            "tmp_transaction",
            connection,
            """SELECT 
                   t.*, value_usd, ts.code as sector_code, ts.codename as sector_codename 
               FROM  
                   transaction t 
               LEFT JOIN
                    tmp_transaction_sector ts on t._link = ts._link_transaction
               LEFT JOIN
                    tmp_transaction_usd usd on t._link = usd._link
            """,
        )

        result = connection.execute(
            """
            select 
                sum(case when value_usd is not null then 1 else 0 end) value_usd,
                sum(case when sector_code is not null then 1 else 0 end) sector_code,
                sum(case when sector_codename is not null then 1 else 0 end) sector_codename
            from 
                tmp_transaction
        """
        ).fetchone()

        connection.execute(
            """
            insert into _fields values('transaction', 'value_usd', 'number', %s, 'Value in USD', 10000); 
            insert into _fields values('transaction', 'sector_code', 'string', %s, 'Sector code for default vocabulary', 10001);  
            insert into _fields values('transaction', 'sector_codename', 'string', %s, 'Sector code name for default vocabulary', 10002);   
        """,
            *result,
        )

        connection.execute(
            """
            drop table if exists tmp_transaction_usd;
            drop table if exists tmp_transaction_sector;
            drop table if exists transaction;
            alter table tmp_transaction rename to transaction;
        """
        )


def transaction_breakdown():
    with get_engine().begin() as connection:
        connection.execute(
            """
        drop table if exists transaction_breakdown;
        create table transaction_breakdown AS

        with sector_count AS 
            (select _link_activity, code, codename, coalesce(percentage, 100) as percentage, count(*) over activity AS cou, sum(coalesce(percentage, 100)) over activity AS total_percentage FROM sector where coalesce(vocabulary, '1') = '1' and coalesce(percentage, 100) <> 0  window activity as (partition by _link_activity)),

        country_100 AS (
            SELECT _link_activity from recipientcountry group by 1 having sum(coalesce(percentage, 100)) >= 100
        ), 

        country_region AS ( 
            select *, sum(percentage) over (partition by _link_activity) AS total_percentage from
                (select prefix, _link_activity, 'country' as locationtype, code as country_code, codename as country_codename, '' as region_code , '' as region_codename, coalesce(percentage, 100) as percentage FROM recipientcountry where coalesce(percentage, 100) <> 0
                    union all
                 select rr.prefix, _link_activity, 'region' as locationtype, ''          , '', code as regioncode, codename             , coalesce(percentage, 100) as percentage 
                 FROM recipientregion rr
                 LEFT JOIN country_100 c1 using (_link_activity)
                 WHERE coalesce(vocabulary, '1') = '1' and coalesce(percentage, 100) <> 0 and c1._link_activity is null  
                ) a
        )

        select 
            t.prefix,
            t._link_activity, 
            t._link as _link_transaction, 
            t.iatiidentifier, 
            t.reportingorg_ref, 
            t.transactiontype_code,
            t.transactiontype_codename,
            t.transactiondate_isodate,
            coalesce(t.sector_code, sc.code) sector_code, 
            coalesce(t.sector_codename, sc.codename) sector_codename,
            coalesce(t.recipientcountry_code, cr.country_code) recipientcountry_code,
            coalesce(t.recipientcountry_codename, cr.country_codename) recipientcountry_codename, 
            coalesce(t.recipientregion_code, cr.region_code) recipientregion_code,
            coalesce(t.recipientregion_codename, cr.region_codename) recipientregion_codename, 
            value * coalesce(sc.percentage/sc.total_percentage, 1) * coalesce(cr.percentage/cr.total_percentage, 1) AS value,
            t.value_currency,
            t.value_valuedate,
            value_usd * coalesce(sc.percentage/sc.total_percentage, 1) * coalesce(cr.percentage/cr.total_percentage, 1) AS value_usd, 
            coalesce(sc.percentage/sc.total_percentage, 1) * coalesce(cr.percentage/cr.total_percentage, 1) AS percentage_used 
        from 
           transaction t 
        left join 
           sector_count sc on t._link_activity = sc._link_activity and t.sector_code is null
        left join 
           country_region cr on t._link_activity = cr._link_activity and coalesce(t.recipientregion_code, t.recipientcountry_code) is null and cr.total_percentage<>0;

        insert into _tables select 'transaction_breakdown', (select max(case when table_order = 9999 then 0 else table_order end) from _tables) count, (select count(*) from transaction_breakdown);
        """
        )

        result = connection.execute(
            """
        select 
            sum(case when _link_activity is not null then 1 else 0 end) _link_activity,
            sum(case when _link_transaction is not null then 1 else 0 end) _link_transaction,
            sum(case when iatiidentifier is not null then 1 else 0 end) iatiidentifier,
            sum(case when reportingorg_ref is not null then 1 else 0 end) reportingorg_ref,
            sum(case when transactiontype_code is not null then 1 else 0 end) transactiontype_code,
            sum(case when transactiontype_codename is not null then 1 else 0 end) transactiontype_codename,
            sum(case when transactiondate_isodate is not null then 1 else 0 end) transactiondate_isodate,
            sum(case when sector_code is not null then 1 else 0 end) sector_code,
            sum(case when sector_codename is not null then 1 else 0 end) sector_codename,
            sum(case when recipientcountry_code is not null then 1 else 0 end) recipientcountry_code,
            sum(case when recipientcountry_codename is not null then 1 else 0 end) recipientcountry_codenme,
            sum(case when recipientregion_code is not null then 1 else 0 end) recipientregion_code,
            sum(case when recipientregion_codename is not null then 1 else 0 end) recipientregion_codename,
            sum(case when value is not null then 1 else 0 end) "value",
            sum(case when value_currency is not null then 1 else 0 end) value_currency,
            sum(case when value_valuedate is not null then 1 else 0 end) value_valuedate,
            sum(case when value_usd is not null then 1 else 0 end) value_usd,
            sum(case when percentage_used is not null then 1 else 0 end) percentage_used
        from 
            transaction_breakdown
        """
        )

        connection.execute(
            """
        insert into _fields values ('transaction_breakdown','_link_activity','string','%s','_link field', 1);
        insert into _fields values ('transaction_breakdown','_link_transaction','string','%s','_link field', 2);
        insert into _fields values ('transaction_breakdown','iatiidentifier','string','%s','A globally unique identifier for the activity.', 3);
        insert into _fields values ('transaction_breakdown','reportingorg_ref','string','%s','Machine-readable identification string for the organisation issuing the report.', 4); 
        insert into _fields values ('transaction_breakdown','transactiontype_code','string','%s','Transaction Type Code', 5);
        insert into _fields values ('transaction_breakdown','transactiontype_codename','string','%s','Transaction Type Codelist Name', 6); 
        insert into _fields values ('transaction_breakdown','transactiondate_isodate','string','%s','Transaction date', 7); 
        insert into _fields values ('transaction_breakdown','sector_code','string','%s','Sector code', 8);
        insert into _fields values ('transaction_breakdown','sector_codename','string','%s','Sector code codelist name', 9);
        insert into _fields values ('transaction_breakdown','recipientcountry_code','string','%s','Recipient Country Code', 10);
        insert into _fields values ('transaction_breakdown','recipientcountry_codename','string','%s','Recipient Country Code', 11);
        insert into _fields values ('transaction_breakdown','recipientregion_code','string','%s','Recipient Region Code', 12);
        insert into _fields values ('transaction_breakdown','recipientregion_codename','string','%s','Recipient Region Codelist Name', 13);
        insert into _fields values ('transaction_breakdown','value','number','%s','Value', 14);
        insert into _fields values ('transaction_breakdown','value_currency','string','%s','Transaction Currency', 15);
        insert into _fields values ('transaction_breakdown','value_valuedate','datetime','%s','Transaction Date', 16);
        insert into _fields values ('transaction_breakdown','value_usd','number','%s','Value in USD', 17);
        insert into _fields values ('transaction_breakdown','percentage_used','number','%s','Percentage of transaction this row represents', 18);
        """,
            *result,
        )


def sql_process():
    augment_transaction()
    transaction_breakdown()


def export_stats():

    stats_file = output_path / "stats.json"

    stats = {"updated": str(datetime.datetime.utcnow())}
    with get_engine().begin() as connection:
        results = connection.execute(
            "SELECT to_json(_tables) as table FROM _tables order by table_order"
        )
        stats['tables'] = [row.table for row in results]

        fields = defaultdict(list)

        results = connection.execute(
            "SELECT table_name, to_json(_fields) as field_info FROM _fields order by table_name, field_order, field"
        )

        for result in results:
            fields[result.table_name].append(result.field_info)

        stats['fields'] = fields

        stats_file.write_text(json.dumps(stats, indent=2))

        activities = [row.iatiidentifier for row in connection.execute(
            "SELECT iatiidentifier from activity group by 1"
        )]

        with gzip.open(str(output_path / 'activities.json.gz'), "wt") as activities_file:
            json.dump(activities, activities_file)


def export_sqlite():
    sqlite_file = output_path / "iati.sqlite"
    if sqlite_file.is_file():
        sqlite_file.unlink()
    datasette_file = output_path / "iati.db"
    if datasette_file.is_file():
        datasette_file.unlink()

    object_details = defaultdict(list)
    with tempfile.TemporaryDirectory() as tmpdirname, get_engine().begin() as connection:
        result = list(
            connection.execute(
                "SELECT table_name, field, type FROM _fields order by  table_name, field_order, field"
            )
        )
        for row in result:
            object_details[row.table_name].append(dict(name=row.field, type=row.type))

        indexes = []

        for object_type, object_details in object_details.items():

            target_object_type = re.sub("[^0-9a-zA-Z]+", "_", object_type.lower())
            if object_type == "transaction":
                target_object_type = "trans"

            fks = []

            for num, item in enumerate(object_details):
                name = item["name"]
                if name.startswith('_link'):
                    indexes.append(f'CREATE INDEX "{target_object_type}_{name}" on "{target_object_type}"("{name}");')
                if name.startswith('_link_'):
                    foreign_table = name[6:]
                    if foreign_table == "transaction":
                        foreign_table = "trans"
                    if object_type == 'activity':
                        continue
                    fks.append(f',FOREIGN KEY("{name}") REFERENCES "{foreign_table}"(_link)')

            print(f"importing table {object_type}")
            with open(f"{tmpdirname}/{object_type}.csv", "wb") as out:
                dbapi_conn = connection.connection
                copy_sql = f'COPY "{object_type.lower()}" TO STDOUT WITH (FORMAT CSV, FORCE_QUOTE *)'
                cur = dbapi_conn.cursor()
                cur.copy_expert(copy_sql, out)

            _, field_def = create_field_sql(object_details, sqlite=True)

            

            import_sql = f"""
            .mode csv
            CREATE TABLE "{target_object_type}" (prefix, {field_def} {' '.join(fks)}) ;
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

        shutil.copy(sqlite_file, datasette_file)

        subprocess.run(
            ["sqlite3", f"{datasette_file}"],
            input='\n'.join(indexes),
            text=True,
            check=True,
        )

        subprocess.run(["gzip", "-f", "-9", f"{datasette_file}"], check=True)
        subprocess.run(["gzip", "-fk", "-9", f"{sqlite_file}"], check=True)
        subprocess.run(["zip", f"{output_path}/iati.sqlite.zip", f"{sqlite_file}"], check=True)



def export_csv():
    with get_engine(schema).begin() as connection, zipfile.ZipFile(f"{output_dir}/iati_csv.zip", "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        result = list(
            connection.execute(
                "SELECT table_name FROM _tables"
            )
        )
        for row in result:
            csv_output_path = output_path / f"{row.table_name}.csv"
            with open(f"{csv_output_path}", "wb") as out:
                dbapi_conn = connection.connection
                copy_sql = f'COPY "{row.table_name.lower()}" TO STDOUT WITH CSV HEADER'
                cur = dbapi_conn.cursor()
                cur.copy_expert(copy_sql, out)

            zip_file.write(
                f"{output_dir}/{row.table_name}.csv",
                arcname=f"iati/{row.table_name}.csv",
            )
            csv_output_path.unlink()


name_allowed_pattern = re.compile(r"[\W]+")


def create_avro_schema(object_type, object_details):
    fields = []
    schema = {"type": "record", "name": object_type, "fields": fields}
    for item in object_details:
        type = item["type"]
        if type == "number":
            type = "double"
        if type == "datetime":
            type = "string"

        field = {
            "name": name_allowed_pattern.sub("", item["name"]),
            "type": [type, "null"],
            "doc": item.get("description"),
        }

        if type == "array":
            field["type"] = [
                {"type": "array", "items": "string", "default": []},
                "null",
            ]

        fields.append(field)

    return schema


def generate_avro_records(result, object_details):

    cast_to_string = set(
        [field["name"] for field in object_details if field["type"] == "string"]
    )

    for row in result:
        new_object = {}
        for key, value in row.object.items():
            new_object[name_allowed_pattern.sub("", key)] = (
                str(value) if key in cast_to_string else value
            )
        yield new_object


def export_bigquery():

    json_acct_info = json.loads(
        base64.b64decode(os.environ["GOOGLE_SERVICE_ACCOUNT"])
    )

    credentials = service_account.Credentials.from_service_account_info(json_acct_info)

    client = bigquery.Client(credentials=credentials)

    with tempfile.TemporaryDirectory() as tmpdirname, get_engine().begin() as connection:
        dataset_id = "iati-tables.iati"
        client.delete_dataset(dataset_id, delete_contents=True, not_found_ok=True)
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "EU"

        dataset = client.create_dataset(dataset, timeout=30)

        access_entries = list(dataset.access_entries)
        access_entries.append(
            AccessEntry("READER", "specialGroup", "allAuthenticatedUsers")
        )
        dataset.access_entries = access_entries

        dataset = client.update_dataset(dataset, ["access_entries"])

        object_details = defaultdict(list)
        result = list(
            connection.execute(
                "SELECT table_name, field, type, docs FROM _fields order by table_name, field_order, field"
            )
        )

        for row in result:
            object_details[row.table_name].append(dict(name=row.field, type=row.type, description=row.docs))

        for object_type, object_details in object_details.items():
            print(f"loading {object_type}")
            result = connection.execute(
                sa.text(
                    f'SELECT to_jsonb("{object_type.lower()}") AS object FROM "{object_type.lower()}"'
                )
            )
            schema = create_avro_schema(object_type, object_details)

            with open(f"{tmpdirname}/{object_type}.avro", "wb") as out:
                writer(
                    out,
                    parse_schema(schema),
                    generate_avro_records(result, object_details),
                    validator=True,
                    codec="deflate",
                )

            table_id = f"{dataset_id}.{object_type}"

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.AVRO
            )

            with open(f"{tmpdirname}/{object_type}.avro", "rb") as source_file:
                client.load_table_from_file(
                    source_file, table_id, job_config=job_config, size=None, timeout=5
                )


def export_pgdump():
    subprocess.run(
        [
            "pg_dump",
            "--no-owner",
            "-f",
            f"{output_dir}/iati.custom.pg_dump",
            "-n",
            schema or 'public',
            "-F",
            "c",
            os.environ["DATABASE_URL"]
        ],
        check=True
    )
    cmd = f"""
       pg_dump --no-owner -n {schema or 'public'} {os.environ["DATABASE_URL"]} | gzip > {output_dir}/iati.dump.gz
    """
    subprocess.run(
        cmd, shell=True, check=True
    )


def export_all():
    export_stats()
    export_sqlite()
    export_csv()
    export_pgdump()
    try:
        export_bigquery()
    except Exception as e:
        print("Big query failed, proceeding anyway")


def upload_all():
    s3_dir = "s3://iati/"

    files = ["stats.json", "iati.sqlite.gz", "iati.db.gz",
             "iati.sqlite", "iati.sqlite.zip", 
             "activities.json.gz", "iati_csv.zip", 
             "iati.custom.pg_dump", "iati.dump.gz"]

    for file in files:
        subprocess.run(["s3cmd", "put", f"{output_dir}/{file}", s3_dir], check=True)
        subprocess.run(["s3cmd", "setacl", f"{s3_dir}{file}", "--acl-public"], check=True)


def run_all(sample=None, refresh=True, processes=5):
    process_registry(refresh=refresh, sample=sample, processes=processes)
    export_all()
    upload_all()
