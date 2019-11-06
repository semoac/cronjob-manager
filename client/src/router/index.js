import Vue from "vue";
import VueRouter from "vue-router";
import Namespaces from "@/views/Namespaces.vue";
import Cronjobs from "@/views/Cronjobs.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "namespaces",
    component: Namespaces,
    props: true
  },
  {
    path: "/cronjobs/:namespace",
    name: "cronjobs",
    component: Cronjobs,
    props: true
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
