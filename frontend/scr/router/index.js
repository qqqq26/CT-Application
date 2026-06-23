// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import PatientProfile from '../views/PatientProfile.vue'
import Analysis from '../views/Analysis.vue'
import AddPatient from '../views/AddPatient.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: Login },
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/patient/:id', name: 'patient', component: PatientProfile },
    { path: '/analyze/:id', name: 'analyze', component: Analysis },
    { path: '/add-patient', name: 'add-patient', component: AddPatient },
  ]
})

// Basic navigation guard: redirect to login if not authenticated
router.beforeEach((to, from) => {
  const isAuthenticated = localStorage.getItem('user_token')
  if (to.name !== 'login' && !isAuthenticated) {
    return { name: 'login' }
  }
})

export default router