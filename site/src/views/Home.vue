<template>
  <v-container>
    <v-row :dense=true>
      <v-col cols=12>
        <v-card elevation="0" color="white">
          <v-card-title class="capitalize-source text-h4">
            <v-row>
              <v-col xl=2 lg=3>
                IATI Tables
              </v-col>
              <v-col xl=9 lg=9 cols=12>
                <v-chip
                  class="ml-3"
                  color="grey darken-3"
                  text-color="white"
                  href="https://colab.research.google.com/drive/15Ahauin2YgloaFEwiGjqbnv7L91xNUua"
                >
                Colab Notebook
                </v-chip>
                <v-chip
                  class="ml-3"
                  color="deep-purple darken-4"
                  text-color="white"
                  href="https://iati.fra1.digitaloceanspaces.com/iati.sqlite.zip">
                SQLite Zip
                </v-chip>
                <v-chip
                  class="ml-3"
                  color="red darken-3"
                  text-color="white"
                  href="https://iati.fra1.digitaloceanspaces.com/iati_csv.zip"
                >
                CSV Zip
                </v-chip>
                <v-chip
                  class="ml-3"
                  color="blue darken-3"
                  text-color="white"
                  href="https://iati.fra1.digitaloceanspaces.com/iati.custom.pg_dump"
                >
                PG Dump (custom)
                </v-chip>
                <v-chip
                  class="ml-3"
                  color="blue darken-2"
                  text-color="white"
                  href="https://iati.fra1.digitaloceanspaces.com/iati.dump.gz"
                >
                PG Dump (gzip)
                </v-chip>
                <v-chip
                  class="ml-3"
                  color="green darken-4"
                  text-color="white"
                  href="https://datasette.codeforiati.org"
                >
                Datasette
                </v-chip>
              </v-col>
            </v-row>
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>
    <v-row :dense=true>
      <v-col xl=4 cols=12>
        <v-card elevation="0" color="white">
          <v-card-title >
            About
          </v-card-title >
          <v-card-text >
            <p>IATI data has been transfromed into tables in order to make it easier to work with relational tools.  Below is the list of tables that have been created. Click on them to see the fields and types within.</p>
            <p><b>Last Update:</b> {{stats.updated.substring(0, 16)}}</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col xl=4 cols=12>
        <v-card elevation="0" color="white">
          <v-card-title >
            Output Formats
          </v-card-title >
          <v-card-text >
            <p>Click on the output formats above to get the data!</p>
            <p>The Colab Notebook is an online jupyter notebook and gives you a quick way to do custom analysis on the whole of IATI data.</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row :dense=true>
      <v-col cols=12>
        <div>
          <v-card elevation="0" color="white">
            <v-card-title>
              The Tables
            </v-card-title>
            <v-card-text>
              <p> Each download contains the following tables: </p>
              <v-simple-table :dense=true>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-left">
                        Table Name
                      </th>
                      <th class="text-left">
                        Row Count
                      </th>
                      <th class="text-left">
                        One-to-Many Tables
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="table in toplevel"
                      :key="table.table_name"
                    >
                      <td><TableModal :table="table" :fields="stats.fields[table.table_name]"  />  </td>
                      <td>{{ table.rows.toLocaleString() }}</td>
                      <td>
                        <v-row :dense=true>
                          <v-col xl=4 lg=6 sm=12 xs=12 v-for="child_table in getChildren(table.table_name)" :key="child_table.table_name" >
                            <TableModal :table="child_table" :fields="stats.fields[child_table.table_name]"  />
                            ({{child_table.rows.toLocaleString()}})
                          </v-col>
                        </v-row>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

// import VueScrollTo from 'vue-scrollto'
import TableModal from '@/components/TableModal'

export default {
  name: 'Home',
  components: { TableModal },
  data: () => ({
    stats: { tables: [] }
  }),
  created: function () {
    this.fetchStats()
  },
  computed: {
    toplevel: function () {
      return this.stats.tables.filter(table => (!table.table_name.includes('_')) && table.rows > 10000)
    }
  },
  methods: {
    fetchStats: async function () {
      const response = await fetch('https://iati.fra1.digitaloceanspaces.com/stats.json')
      const stats = await response.json()
      this.stats = stats
      // this.$nextTick(() => VueScrollTo.scrollTo(window.location.hash))
    },
    scrollDone: function (el) {
      window.location.hash = '#' + el.id
    },
    getChildren: function (tableName) {
      return this.stats.tables.filter((table) => {
        if (tableName === table.table_name) {
          return
        }
        return table.table_name.startsWith(tableName + '_')
      })
    }
  }
}

</script>