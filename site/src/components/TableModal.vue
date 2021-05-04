<template>
  <v-dialog
    v-model="open"
    scrollable
    @input="v => change(v)"
  >
    <template v-slot:activator="{ on, attrs }">
      <a
        v-bind="attrs"
        v-on="on"
      >
        {{ table.table_name }}
      </a>
    </template>
      <v-card>
        <v-card-title class="ml-4">
          {{table.table_name}}
          <v-btn
            icon
            @click="change(false)"
            class="ml-auto"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-simple-table :dense=true>
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">
                    Field
                  </th>
                  <th class="text-left">
                    Type
                  </th>
                  <th class="text-left">
                    Field Usage Count
                  </th>
                  <th class="text-left">
                    Docs
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="field in fields"
                  :key="field.field"
                >
                  <td>{{ field.field }}</td>
                  <td>{{ field.type }}</td>
                  <td>{{ field.count.toLocaleString() }}</td>
                  <td>{{ field.docs}}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>
  </v-dialog>
</template>

<script>

export default {
  name: 'TableModal',
  props: ['table', 'fields'],
  data: () => ({
    open: false
  }),
  methods: {
    change: function (v) {
      if (v) {
        window.location.hash = '#' + this.table.table_name
      }
      if (!v) {
        this.open = false
        window.location.hash = '#'
      }
    }
  },
  created: function () {
    if (location.hash === '#' + this.table.table_name) {
      this.open = true
    }
  }
}

</script>
