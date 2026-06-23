<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const patientId = route.params.id

const selectedFile = ref(null)
const rawImageUrl = ref(null)
const processedImageUrl = ref(null)
const showProcessed = ref(false) 

const isProcessing = ref(false)
const results = ref(null)


const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    rawImageUrl.value = URL.createObjectURL(file)
    processedImageUrl.value = null
    results.value = null
    showProcessed.value = false
  }
}

const runAnalysis = async () => {
  if (!selectedFile.value) return
  isProcessing.value = true
  
  const formData = new FormData()
  formData.append('main_slice', selectedFile.value)

  try {
    const response = await fetch('http://localhost:8000/api/predict', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      alert(`AI Server Error: ${errorData.detail || 'Prediction failed'}`)
      return
    }
    
    const data = await response.json()
    results.value = data
    processedImageUrl.value = data.processed_image 
    showProcessed.value = true 
    
  } catch (error) {
    alert("Error connecting to AI server.")
    console.error(error)
  } finally {
    isProcessing.value = false
  }
}

const acceptResult = async () => {
  if (!results.value) return

  const fileName = selectedFile.value.name
  const parts = fileName.replace('.png', '').split('_')
  const sliceIndex = parseInt(parts[parts.length - 1]) || 0

  const hasFindings = results.value.findings && results.value.findings.length > 0
  const payload = {
    file_name: fileName,
    slice_index: sliceIndex,
    lesion_type: hasFindings ? 5 : 0,
    ground_truth_box: hasFindings ? results.value.findings[0].bbox : []
  }

  try {
    await fetch(`http://localhost:8000/api/patients/${patientId}/add_scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    alert("Report Signed & Saved to Medical Record.")
    router.push(`/patient/${patientId}`) 
  } catch (error) {
    alert("Error saving to database.")
  }
}

const denyResult = () => {
  if(confirm("Are you sure you want to discard these AI findings?")) {
    results.value = null
    processedImageUrl.value = null
    showProcessed.value = false
  }
}

const currentImage = computed(() => {
  return showProcessed.value && processedImageUrl.value ? processedImageUrl.value : rawImageUrl.value
})
</script>

<template>
  <div class="p-8 max-w-5xl mx-auto">
    <button @click="router.push(`/patient/${patientId}`)" class="text-blue-600 hover:underline mb-4">&larr; Back to Patient</button>
    
    <div class="bg-white p-6 rounded-lg shadow-md grid grid-cols-3 gap-6">
      
      <div class="col-span-1 border-r pr-6">
        <h2 class="text-xl font-bold mb-4 text-gray-800">Upload & Analyze</h2>
        <input type="file" accept=".png" @change="handleFileUpload" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 mb-6">
        
        <button @click="runAnalysis" :disabled="!selectedFile || isProcessing" class="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-400 transition-colors mb-4 shadow-sm">
          {{ isProcessing ? 'Analyzing Model...' : 'Run AI Model' }}
        </button>

        <div v-if="results" class="p-4 bg-gray-50 border rounded-lg">
          <p class="font-semibold text-gray-700 mb-2">Display Mode:</p>
          <div class="flex items-center gap-2">
            <input type="checkbox" id="toggle" v-model="showProcessed" class="w-5 h-5 text-blue-600">
            <label for="toggle" class="text-gray-800 select-none">Show Pre-processed (HU) & Box</label>
          </div>
        </div>
      </div>

      <div class="col-span-2 flex flex-col items-center">
        
        <div v-if="rawImageUrl" class="relative bg-black rounded overflow-hidden shadow-inner flex justify-center items-center aspect-square w-full max-w-[512px]">
          
          <img :src="currentImage" class="max-w-full max-h-full object-contain" alt="CT Scan" />

          <svg v-if="showProcessed && results?.findings?.length > 0" 
                viewBox="0 0 512 512" 
                class="absolute inset-0 w-full h-full pointer-events-none">
            <rect 
              v-for="(finding, idx) in results.findings" :key="idx"
              :x="finding.bbox[0]" 
              :y="finding.bbox[1]" 
              :width="finding.bbox[2] - finding.bbox[0]" 
              :height="finding.bbox[3] - finding.bbox[1]" 
              fill="none" 
              stroke="#ef4444" 
              stroke-width="3" 
            />
          </svg>
        </div>

        <div v-else class="w-full aspect-square border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-400">
          No image uploaded
        </div>

        <div v-if="results" class="w-full mt-6 bg-blue-50 border border-blue-200 p-4 rounded-lg flex justify-between items-center">
          <div>
            <h3 class="font-bold text-blue-900 text-lg">AI Findings Review</h3>
            <p class="text-blue-800">
              Detected <span class="font-bold">{{ results.findings?.length || 0 }}</span> lesion(s). 
              <span v-if="results.findings?.length > 0">
                Highest Confidence: <span class="font-bold">{{ results.findings[0]?.probability }}%</span>
              </span>
            </p>
          </div>
          <div class="flex gap-3">
            <button @click="denyResult" class="px-4 py-2 bg-white text-red-600 border border-red-200 font-bold rounded hover:bg-red-50 transition">Deny / Override</button>
            <button @click="acceptResult" class="px-6 py-2 bg-green-600 text-white font-bold rounded shadow hover:bg-green-700 transition">Accept & Save Report</button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>