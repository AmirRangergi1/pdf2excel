# PDF to Excel Converter

A single-page web application that converts PDF tables to Excel spreadsheets.

## Stack

- **Frontend**: Vue.js 3 + Vite
- **Backend**: Python FastAPI
- **PDF Processing**: pdfplumber
- **Excel Generation**: openpyxl

## Project Structure

```
pdf2excel/
├── frontend/           (Vue.js application)
│   ├── src/
│   │   ├── App.vue     (Main application component)
│   │   └── main.js     (Vue initialization)
│   ├── index.html      (HTML entry point)
│   ├── vite.config.js  (Vite configuration)
│   └── package.json
├── backend/            (FastAPI application)
│   ├── main.py         (FastAPI app with PDF extraction)
│   └── requirements.txt (Python dependencies)
└── README.md
```

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the FastAPI server:
   ```bash
   python main.py
   ```
   The backend will run on `http://localhost:8000`

### Frontend Setup

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will open on `http://localhost:5173`

## Usage

1. **Upload PDF**: Drag and drop a PDF file with tables onto the upload zone, or click to browse
2. **Convert**: Click "Convert to Excel" button
3. **Download**: Once conversion is complete, click "Download Excel File" to get your spreadsheet

## Features

✅ Drag and drop file upload  
✅ Real-time progress tracking  
✅ Automatic table extraction from PDFs  
✅ Multi-table support (each table on separate sheet)  
✅ Auto-adjusted column widths  
✅ Error handling with user-friendly messages  
✅ Beautiful, responsive UI  

## API Endpoints

### POST `/api/convert`
Converts a PDF file with tables to an Excel file.

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `file` (PDF file)

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Returns: Excel file (.xlsx)

**Example:**
```javascript
const formData = new FormData()
formData.append('file', pdfFile)
const response = await fetch('/api/convert', {
  method: 'POST',
  body: formData
})
const excelBlob = await response.blob()
```

## Error Handling

The application handles various error scenarios:
- Invalid file types (only PDF accepted)
- PDFs without tables
- Corrupted PDF files
- Network errors

All errors are displayed with clear, user-friendly messages.

## Development

### Backend
- Built with FastAPI for high performance
- CORS enabled for frontend communication
- Automatic OpenAPI documentation at `/docs`

### Frontend
- Vue 3 with Composition API
- Vite for fast development and optimized builds
- Responsive design with modern CSS
- Axios for API communication

## Building for Production

### Frontend
```bash
cd frontend
npm run build
```
This creates an optimized build in the `dist/` folder.

### Backend
The FastAPI application is production-ready. Deploy using:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Requirements

- Python 3.8+
- Node.js 16+
- pip package manager
- npm or yarn

## Dependencies

**Backend:**
- fastapi
- uvicorn
- pdfplumber
- openpyxl
- python-cors
- python-multipart

**Frontend:**
- vue
- axios
- vite
- @vitejs/plugin-vue

## License

MIT