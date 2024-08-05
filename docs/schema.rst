===========
Data Schema
===========

See the available tables and columns on the `IATI Datasette instance <https://datasette.codeforiati.org/iati>`_.

Global Columns
--------------

The following columns are available in all tables:

:code:`_link`
  The primary key for each table.
:code:`_link_activity` or :code:`_link_organisation`
  The foreign key to the :code:`activity` or :code:`organisation` table respectively.
:code:`dataset`
  The name of the dataset this row came from. This can be used to find the dataset in the IATI registry, using the URL: :code:`https://www.iatiregistry.org/dataset/<DATASET_NAME>`.
:code:`prefix`
  The registry publisher ID this row came from. This can be used to find the dataset in the IATI registry, using the URL: :code:`https://www.iatiregistry.org/publisher/<PREFIX>`.
