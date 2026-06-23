// import './assets/main.css'

// import { createApp } from 'vue'
// import App from './App.vue'

// createApp(App).mount('#app')
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 
import './style.css'          

const app = createApp(App)

app.use(router) 
app.mount('#app')