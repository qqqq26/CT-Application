<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')

const handleLogin = () => {
  // Mock login: Accept anything, set a token, and redirect to dashboard
  localStorage.setItem('user_token', 'mock_hospital_token_123')
  router.push('/')
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-200">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
      <h2 class="text-2xl font-bold text-center text-gray-800 mb-6">Radiologist Login</h2>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Hospital ID</label>
          <input v-model="username" type="text" required class="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input v-model="password" type="password" required class="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500">
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition">Sign In</button>
      </form>
    </div>
  </div>
</template>