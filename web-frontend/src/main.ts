import { createApp } from 'vue';

import App from './App.vue';

import './registerServiceWorker';
import { startGestureDetection } from './services/GestureDetection';

require('bulma-slider');

require('@/assets/main.scss');

const app = createApp(App);
app.mount('#app');

startGestureDetection();
