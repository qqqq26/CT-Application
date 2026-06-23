<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const patientId = ref('')
const age = ref('')
const sex = ref('M')
const error = ref(null)
const isSubmitting = ref(false)

const submitPatient = async () => {
  error.value = null
  isSubmitting.value = true

  try {
    const response = await fetch('http://localhost:8000/api/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: patientId.value,
        age: parseInt(age.value),
        sex: sex.value
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || "Failed to create patient")
    }

    router.push(`/patient/${patientId.value}`)

  } catch (err) {
    error.value = err.message
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center pt-20">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-md">
      <button @click="router.push('/')" class="text-blue-600 hover:underline mb-6 block">&larr; Back to Dashboard</button>
      
      <h1 class="text-2xl font-bold text-gray-800 mb-6">Register New Patient</h1>
      
      <form @submit.prevent="submitPatient" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Patient ID</label>
          <input v-model="patientId" type="text" required placeholder="e.g., 999123" class="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500">
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Age</label>
          <input v-model="age" type="number" required min="0" max="120" class="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500">
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Sex</label>
          <select v-model="sex" class="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500">
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>

        <button type="submit" :disabled="isSubmitting" class="w-full bg-green-600 text-white py-2 rounded font-bold hover:bg-green-700 disabled:bg-gray-400 transition">
          {{ isSubmitting ? 'Saving...' : 'Create Patient Profile' }}
        </button>
      </form>
    </div>
  </div>
</template>