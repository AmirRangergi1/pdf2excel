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
        Size: {{ formatFileSize(selectedFile.size) }}
      </div>
      <div v-if="progress > 0 && progress < 100" class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">
          {{ progress }}% {{ progress < 50 ? 'Uploading...' : 'Processing...' }}
        </div>
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
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
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
      this.statusMessage = '⏳ Uploading file... (analyzing PDF structure)'
      this.progress = 0
      
      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        
        const response = await axios.post('/api/convert', formData, {
          responseType: 'blob',
          timeout: 300000, // 5 minutes for large files
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded / progressEvent.total) * 100)
            this.progress = percentCompleted
            // Update message based on progress
            if (percentCompleted < 50) {
              this.statusMessage = `⏳ Uploading file... ${percentCompleted}%`
            } else {
              this.statusMessage = `⏳ Analyzing PDF and detecting tables... ${percentCompleted}%`
            }
          }
        })
        
        // Get detection method from response headers
        const detectionMethod = response.headers['x-detection-method'] || 'standard'
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        this.downloadLink = url
        this.downloadFileName = `${this.selectedFile.name.replace('.pdf', '')}.xlsx`
        
        this.status = 'success'
        let successMessage = '✅ Conversion successful!'
        
        // Add information about detection method if fallback was used
        if (detectionMethod.includes('fallback') || detectionMethod.includes('text')) {
          successMessage += ` (Used ${detectionMethod.replace(/_/g, ' ')} extraction)`
        } else if (detectionMethod.includes('camelot')) {
          successMessage += ' (Alternative table detection used)'
        }
        
        successMessage += ' Ready to download.'
        this.statusMessage = successMessage
        this.progress = 100
        
      } catch (error) {
        this.status = 'error'
        
        // Enhanced error messages
        if (error.response && error.response.data && error.response.data.detail) {
          const detail = error.response.data.detail
          
          // Provide helpful guidance based on error type
          if (detail.includes('No tables found')) {
            this.statusMessage = `❌ Could not extract tables. The PDF may contain:\n• Non-standard table formats\n• Scanned images without text\n• Unstructured data\n\nTry converting a different PDF or ensure it contains table data.`
          } else if (detail.includes('must be a PDF')) {
            this.statusMessage = `❌ Error: Please upload a valid PDF file.`
          } else {
            this.statusMessage = `❌ Error: ${detail}`
          }
        } else if (error.response && error.response.status === 400) {
          this.statusMessage = `❌ Conversion failed: Invalid file or unsupported format. Please ensure the PDF contains extractable data.`
        } else if (error.code === 'ECONNABORTED') {
          this.statusMessage = `❌ Error: Request timeout. The file may be too large or the server is busy.`
        } else {
          this.statusMessage = `❌ Error: ${error.message || 'Conversion failed. Please try again.'}`
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
