<template>
  <div class="container">
    <h1>📄 PDF to Excel Converter</h1>
    <p class="subtitle">Convert PDF tables to Excel spreadsheets instantly</p>
    
    <div 
      class="upload-zone" 
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      :class="{ dragover: isDragging }"
    >
      <div class="upload-icon">📁</div>
      <div class="upload-text">Drag and drop your PDF here</div>
      <div class="upload-subtext">or click to browse</div>
      <input 
        ref="fileInput"
        type="file" 
        accept=".pdf" 
        @change="handleFileSelect"
      >
    </div>
    
    <div v-if="selectedFile" class="file-info show">
      <div class="file-name">📋 {{ selectedFile.name }}</div>
      <div style="font-size: 12px; color: #666;">
        Size: {{ (selectedFile.size / 1024).toFixed(2) }} KB
      </div>
      <div v-if="progress > 0 && progress < 100" class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>
    
    <div class="button-group" v-if="selectedFile">
      <button 
        class="btn-convert" 
        @click="convertPDF"
        :disabled="isLoading"
      >
        <span v-if="isLoading" class="spinner"></span>
        {{ isLoading ? 'Converting...' : 'Convert to Excel' }}
      </button>
      <button 
        class="btn-clear" 
        @click="clearFile"
        :disabled="isLoading"
      >
        Clear
      </button>
    </div>
    
    <div v-if="downloadLink" class="button-group">
      <button 
        class="btn-download" 
        @click="downloadExcel"
      >
        ⬇️ Download Excel File
      </button>
    </div>
    
    <div 
      v-if="statusMessage" 
      class="status" 
      :class="{ 
        show: true,
        loading: status === 'loading',
        success: status === 'success',
        error: status === 'error'
      }"
    >
      <span v-if="status === 'loading'" class="spinner"></span>
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      selectedFile: null,
      isDragging: false,
      isLoading: false,
      progress: 0,
      status: null,
      statusMessage: '',
      downloadLink: null,
      downloadFileName: ''
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleFileSelect(event) {
      const files = event.target.files
      if (files && files.length > 0) {
        this.selectedFile = files[0]
        this.downloadLink = null
        this.statusMessage = ''
      }
    },
    handleDrop(event) {
      this.isDragging = false
      const files = event.dataTransfer.files
      if (files && files.length > 0) {
        const file = files[0]
        if (file.type === 'application/pdf') {
          this.selectedFile = file
          this.downloadLink = null
          this.statusMessage = ''
        } else {
          this.status = 'error'
          this.statusMessage = 'Please drop a PDF file'
          setTimeout(() => {
            this.statusMessage = ''
          }, 3000)
        }
      }
    },
    async convertPDF() {
      if (!this.selectedFile) return
      
      this.isLoading = true
      this.status = 'loading'
      this.statusMessage = 'Converting PDF to Excel...'
      this.progress = 0
      
      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        
        const response = await axios.post('/api/convert', formData, {
          responseType: 'blob',
          onUploadProgress: (progressEvent) => {
            this.progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          }
        })
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        this.downloadLink = url
        this.downloadFileName = `${this.selectedFile.name.replace('.pdf', '')}.xlsx`
        
        this.status = 'success'
        this.statusMessage = '✅ Conversion successful! Ready to download.'
        this.progress = 100
        
      } catch (error) {
        this.status = 'error'
        if (error.response && error.response.data && error.response.data.detail) {
          this.statusMessage = `❌ Error: ${error.response.data.detail}`
        } else if (error.response && error.response.status === 400) {
          this.statusMessage = '❌ Error: No tables found in PDF. Please ensure the PDF contains table data.'
        } else {
          this.statusMessage = `❌ Error: ${error.message || 'Conversion failed'}`
        }
        this.progress = 0
      } finally {
        this.isLoading = false
      }
    },
    downloadExcel() {
      if (this.downloadLink) {
        const link = document.createElement('a')
        link.href = this.downloadLink
        link.download = this.downloadFileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    },
    clearFile() {
      this.selectedFile = null
      this.downloadLink = null
      this.statusMessage = ''
      this.progress = 0
      this.$refs.fileInput.value = ''
    }
  }
}
</script>
