=======
Process
=======

Once a day, IATI Tables pulls the latest `IATI Data Dump <https://iati-data-dump.codeforiati.org/>`_ and processes it.
The `metadata table <https://datasette.codeforiati.org/iati/metadata>`_ shows the timestamp of the data dump which was used, and at what time IATI Tables processed the data.

IATI Tables replaces all the data each time it runs, so updates and removals will be respected.

IATI Tables serves raw data. It doesn't perform any deduplication or corrections.
For example, if an activity has been published multiple times, it will appear multiple times in IATI tables.
