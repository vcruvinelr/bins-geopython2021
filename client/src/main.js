import Vue from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';

Vue.use(PrimeVue);
Vue.config.productionTip = false

import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import "primeflex/primeflex.css"

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
