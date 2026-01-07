from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import openpyxl
from openpyxl.utils import get_column_letter
import io
import tempfile
import os

app = FastAPI(title="PDF to Excel Converter")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_tables_from_pdf(pdf_file):
    """Extract tables from PDF file"""
    try:
        tables = []
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                if page_tables:
                    for table in page_tables:
                        tables.append({
                            'page': page_num + 1,
                            'data': table
                        })
        return tables
    except Exception as e:
        raise Exception(f"Error extracting tables from PDF: {str(e)}")

def create_excel_from_tables(tables):
    """Create Excel file from extracted tables"""
    try:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        for idx, table_info in enumerate(tables):
            sheet_name = f"Table_{table_info['page']}_{idx + 1}"
            # Limit sheet name to 31 characters (Excel limit)
            sheet_name = sheet_name[:31]
            ws = wb.create_sheet(sheet_name)
            
            table_data = table_info['data']
            
            # Write data to Excel
            for row_idx, row in enumerate(table_data, start=1):
                for col_idx, cell in enumerate(row, start=1):
                    ws.cell(row=row_idx, column=col_idx, value=cell)
            
            # Auto-adjust column widths
            for col_idx, col in enumerate(ws.columns, start=1):
                max_length = 0
                column_letter = get_column_letter(col_idx)
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to bytes
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        return excel_file
    except Exception as e:
        raise Exception(f"Error creating Excel file: {str(e)}")

@app.post("/api/convert")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    """Convert PDF file with tables to Excel"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read file content
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract tables from PDF
        tables = extract_tables_from_pdf(pdf_file)
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in PDF")
        
        # Create Excel file
        excel_file = create_excel_from_tables(tables)
        
        # Return Excel file
        return FileResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{file.filename.replace('.pdf', '')}.xlsx"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PDF to Excel Converter API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
