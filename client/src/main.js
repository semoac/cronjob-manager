import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import BootstrapVue from "bootstrap-vue";
import moment from "moment";
import cronstrue from "cronstrue";

Vue.config.productionTip = false;
Vue.use(BootstrapVue);
Vue.filter("formatDate", function(value) {
  if (value) {
    return moment(String(value)).format("DD/MM/YYYY hh:mm");
  }
});
Vue.filter("formatCron", function(value) {
  if (value) {
    return cronstrue.toString(value);
  }
});

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

new Vue({
  router,
  render: h => h(App)
}).$mount("#app");
