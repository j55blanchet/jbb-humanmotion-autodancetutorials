import { createApp } from 'vue';

import App from './App.vue';

import './registerServiceWorker';

require('@/assets/main.scss');

const app = createApp(App);
app.mount('#app');
