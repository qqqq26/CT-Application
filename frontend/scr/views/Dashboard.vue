<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const searchPatient = () => {
  if (searchQuery.value.trim() !== '') {

    router.push(`/patient/${searchQuery.value}`)
  }
}
</script>

<template>
  <div class="p-8 flex flex-col items-center pt-20">
    <div class="w-full max-w-2xl bg-white p-8 rounded-xl shadow-md">
      <h1 class="text-2xl font-bold text-gray-800 mb-6">Patient Search</h1>
      <div class="flex gap-4">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Enter Patient ID (e.g., 000231)" 
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          @keyup.enter="searchPatient"
        />
        <button @click="searchPatient" class="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700">
          Search
        </button>
      </div>
    </div>
  </div>

  <div class="mt-6 text-center border-t pt-6">
  <p class="text-gray-600 mb-2">Patient not in the system?</p>
  <button @click="router.push('/add-patient')" class="px-6 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition">
    + Add New Patient
  </button>
</div>
</template>

