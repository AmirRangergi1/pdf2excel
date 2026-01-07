from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import openpyxl
from openpyxl.utils import get_column_letter
import io
import tempfile
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF to Excel Converter")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_content_from_pdf(pdf_file):
    """
    Extract all content from PDF without errors.
    Always returns content in table format regardless of PDF structure.
    """
    try:
        pdf_file.seek(0)
        all_content = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                logger.info(f"Processing page {page_num + 1}/{len(pdf.pages)}")
                
                # Try to extract tables first
                try:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            all_content.append({
                                'page': page_num + 1,
                                'data': table,
                                'type': 'table'
                            })
                        logger.info(f"✓ Page {page_num + 1}: Found {len(tables)} table(s)")
                        continue
                except Exception as e:
                    logger.debug(f"Table extraction failed on page {page_num + 1}: {str(e)}")
                
                # Fallback: Extract all text and organize by lines
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if lines:
                            # Create a table with one column per line
                            table_data = [[line] for line in lines]
                            all_content.append({
                                'page': page_num + 1,
                                'data': table_data,
                                'type': 'text'
                            })
                            logger.info(f"✓ Page {page_num + 1}: Extracted {len(lines)} lines of text")
                            continue
                except Exception as e:
                    logger.debug(f"Text extraction failed on page {page_num + 1}: {str(e)}")
                
                # Last resort: Get raw content info
                try:
                    info = [
                        [f"Page {page_num + 1}"],
                        [f"Size: {page.width} x {page.height}"],
                        ["No extractable content found"]
                    ]
                    all_content.append({
                        'page': page_num + 1,
                        'data': info,
                        'type': 'info'
                    })
                    logger.info(f"✓ Page {page_num + 1}: No content to extract")
                except Exception as e:
                    logger.debug(f"Info extraction failed: {str(e)}")
        
        return all_content
        
    except Exception as e:
        logger.error(f"Error extracting from PDF: {str(e)}", exc_info=True)
        # Return a default message that at least something can be created
        return [{'page': 1, 'data': [['Error: ' + str(e)]], 'type': 'error'}]


def create_excel_from_content(content):
    """Create Excel file from extracted content (tables, text, or any data)"""
    try:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        
        for idx, item in enumerate(content, 1):
            page_num = item['page']
            content_type = item['type']
            data = item['data']
            
            sheet_name = f"Page_{page_num}"
            if content_type != 'table':
                sheet_name += f"_{content_type[:5]}"
            
            sheet_name = sheet_name[:31]  # Excel limit
            ws = wb.create_sheet(sheet_name)
            
            # Write data to Excel
            for row_idx, row in enumerate(data, start=1):
                if isinstance(row, (list, tuple)):
                    for col_idx, cell_value in enumerate(row, start=1):
                        ws.cell(row=row_idx, column=col_idx, value=cell_value)
                else:
                    ws.cell(row=row_idx, column=1, value=row)
            
            # Auto-adjust column widths
            for col_idx in range(1, ws.max_column + 1):
                max_length = 0
                column_letter = get_column_letter(col_idx)
                for cell in ws[column_letter]:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        return excel_file
        
    except Exception as e:
        logger.error(f"Error creating Excel: {str(e)}")
        # Return a basic Excel file even if there's an error
        wb = openpyxl.Workbook()
        ws = wb.active
        ws['A1'] = 'Conversion Error'
        ws['A2'] = str(e)
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        return excel_file


@app.post("/api/convert")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    """Convert any PDF to Excel - always succeeds"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        logger.info(f"Converting: {file.filename}")
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract content (never fails)
        extracted_content = extract_content_from_pdf(pdf_file)
        
        if not extracted_content:
            extracted_content = [{'page': 1, 'data': [['No content found']], 'type': 'info'}]
        
        # Create Excel file
        excel_file = create_excel_from_content(extracted_content)
        
        logger.info(f"✓ Successfully converted {file.filename}")
        
        # Return Excel file
        return StreamingResponse(
            iter([excel_file.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=\"{file.filename.replace('.pdf', '')}.xlsx\""
            }
        )
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        # Return error as Excel file instead of HTTP error
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws['A1'] = 'Conversion Error'
            ws['A2'] = str(e)[:100]
            ws['A3'] = 'Please try another PDF file'
            excel_file = io.BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            return StreamingResponse(
                iter([excel_file.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=\"error_{file.filename.replace('.pdf', '')}.xlsx\""
                }
            )
        except:
            raise HTTPException(status_code=500, detail="PDF conversion failed")

@app.get("/api/health")
async def health():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "PDF to Excel Converter API"}

@app.get("/")
async def root():
    """Serve frontend index if available, otherwise health message"""
    try:
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
    except Exception:
        pass
    return {"message": "PDF to Excel Converter API is running"}

# Serve static frontend files
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300  # 5 minutes keep-alive timeout
    )
