<template>
  <div class="container">
    <h1>Project list</h1>
    <hr />
    <br />
    <br />
    <div :hidden="loading" class="text-center">
      <b-spinner label="Spinning"></b-spinner>
      <b-spinner type="grow" label="Spinning"></b-spinner>
      <b-spinner variant="primary" label="Spinning"></b-spinner>
      <b-spinner variant="primary" type="grow" label="Spinning"></b-spinner>
      <b-spinner variant="success" label="Spinning"></b-spinner>
      <b-spinner variant="success" type="grow" label="Spinning"></b-spinner>
    </div>
    <ul class="list-group">
      <li class="list-group-item" v-for="(namespace, index) in namespaces" :key="index">
        <router-link :to="{ name: 'cronjobs', params: { namespace: namespace }}">{{ namespace }}</router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Namespaces",
  data() {
    return {
      namespaces: [],
      loading: false
    };
  },
  methods: {
    getNamespaces() {
      const path = process.env.VUE_APP_URL + "/api/v1/namespaces";
      axios.get(path).then(res => {
        this.namespaces = res.data.namespaces;
        this.loading = true;
      });
    }
  },
  created() {
    document.title = "Cronjob Manager - Project List";
    this.getNamespaces();
  }
};
</script>