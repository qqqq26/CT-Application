<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const patientId = route.params.id

const patientData = ref(null)
const error = ref(null)

// Modal State
const selectedScan = ref(null)
const showAnnotation = ref(true)

onMounted(async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/patients/${patientId}`)
    if (!response.ok) throw new Error('Patient not found')
    patientData.value = await response.json()
  } catch (err) {
    error.value = err.message
  }
})

const goToAnalysis = () => router.push(`/analyze/${patientId}`)

const openModal = (scan) => {
  selectedScan.value = scan
  showAnnotation.value = true 
}

const closeModal = () => {
  selectedScan.value = null
}
</script>

<template>
  <div class="p-8 max-w-4xl mx-auto">
    <button @click="router.push('/')" class="text-blue-600 hover:underline mb-4">&larr; Back to Search</button>

    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded">{{ error }}</div>

    <div v-else-if="patientData" class="bg-white p-6 rounded-lg shadow-md">
      <div class="flex justify-between items-start border-b pb-4 mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-800">Patient ID: {{ patientData.patient_id }}</h1>
          <p class="text-gray-600 mt-1 text-lg">
            Age: <span class="font-semibold">{{ patientData.age }}</span> | 
            Sex: <span class="font-semibold">{{ patientData.sex }}</span> |
            Total Studies: <span class="font-semibold">{{ patientData.studies.length }}</span>
          </p>
        </div>
        <button @click="goToAnalysis" class="bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition">
          + Run AI Analysis
        </button>
      </div>

      <h3 class="text-xl font-bold text-gray-800 mb-4">Clinical History</h3>
      
      <div class="space-y-6">
        <div v-for="study in patientData.studies" :key="study.study_index" class="bg-gray-50 border rounded-lg p-4">
          <h4 class="font-bold text-lg text-blue-900 border-b pb-2 mb-3">Study #{{ study.study_index }}</h4>
          
          <ul class="space-y-3">
            <li v-for="(scan, index) in study.scans" :key="index" 
                @click="openModal(scan)"
                class="bg-white border rounded p-3 flex gap-4 items-center shadow-sm cursor-pointer hover:bg-blue-50 transition">
              <img :src="`http://localhost:8000/api/view-scan/${scan.file_name}`" alt="CT Scan Thumbnail" class="w-20 h-20 object-cover border rounded bg-black" />
              <div class="flex-1">
                <span class="font-semibold block text-gray-800">{{ scan.file_name }}</span>
                <div class="mt-2 flex gap-2">
                  <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded font-medium">Slice: {{ scan.slice_index }}</span>
                  <span v-if="scan.ground_truth_box && scan.ground_truth_box.length" class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded font-medium">Annotated</span>
                </div>
              </div>
              <span class="text-gray-400 font-bold">&rarr;</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center text-gray-500 mt-10 text-xl animate-pulse">Loading patient data...</div>

    <div v-if="selectedScan" class="fixed inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center z-50 p-4">
      
      <div class="w-full max-w-3xl flex justify-between items-center mb-4">
        <h2 class="text-white text-xl font-bold">{{ selectedScan.file_name }} (Slice {{ selectedScan.slice_index }})</h2>
        <div class="flex gap-4">
          <button @click="showAnnotation = !showAnnotation" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">
            {{ showAnnotation ? 'Hide Box (Show Raw)' : 'Show Box (Annotated)' }}
          </button>
          <button @click="closeModal" class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition">Close</button>
        </div>
      </div>

      <div class="relative bg-black border border-gray-700 rounded shadow-2xl max-h-[80vh] aspect-square flex items-center justify-center overflow-hidden">
        
        <!-- <img :src="selectedScan.image_url" class="max-w-full max-h-full object-contain" alt="Full CT Scan" /> -->
        <!-- <img :src="scan.image_url" class="object-contain" /> -->

        <!-- <img :src="selectedScan.processed_image_url || selectedScan.image_url" class="max-w-full max-h-full object-contain" alt="Full CT Scan" /> -->
        <!-- <img :src="showAnnotation ? `http://localhost:8000/api/view-scan/${selectedScan.file_name}` : `http://localhost:8000/static/ct_scans/${selectedScan.file_name}`" class="max-w-full max-h-full object-contain" alt="Full CT Scan" /> -->
        <img :src="showAnnotation  ? `http://localhost:8000/api/view-scan/${selectedScan.file_name || selectedScan.image_url.split('/').pop()}`  : `http://localhost:8000/api/view-scan/${selectedScan.file_name || selectedScan.image_url.split('/').pop()}?raw=true`" 
  class="max-w-full max-h-full object-contain bg-black" alt="Full CT Scan View" />
        <svg v-if="showAnnotation && selectedScan.ground_truth_box && selectedScan.ground_truth_box.length === 4" 
             viewBox="0 0 512 512" 
             class="absolute inset-0 w-full h-full pointer-events-none">
          <rect 
            :x="selectedScan.ground_truth_box[0]" 
            :y="selectedScan.ground_truth_box[1]" 
            :width="selectedScan.ground_truth_box[2] - selectedScan.ground_truth_box[0]" 
            :height="selectedScan.ground_truth_box[3] - selectedScan.ground_truth_box[1]" 
            fill="none" 
            stroke="#ef4444" 
            stroke-width="3" 
          />
        </svg>

      </div>
    </div>

  </div>
</template>

