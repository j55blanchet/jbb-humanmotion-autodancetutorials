import { createApp } from 'vue';

import App from './App.vue';

import './registerServiceWorker';
import { startGestureDetection } from './services/GestureDetection';

require('@/assets/main.scss');

const app = createApp(App);
app.mount('#app');

startGestureDetection();
