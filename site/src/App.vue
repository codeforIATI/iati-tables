<template>
  <v-app>
    <v-app-bar v-if="false" app>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </v-app-bar>
    <v-main>
      <router-view/>
    </v-main>
  </v-app>
</template>

<style>
</style>
