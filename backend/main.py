from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
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

def extract_tables_from_pdf(pdf_file):
    """
    Extract tables from PDF with multi-strategy fallback approach:
    1. pdfplumber with aggressive settings (lines+edges detection)
    2. pdfplumber with text-based detection
    3. Extract structured text from PDF (last resort)
    """
    try:
        tables = []
        detection_method = None
        
        # Strategy 1: pdfplumber with aggressive table detection (lines+edges)
        logger.info("Attempting Strategy 1: pdfplumber with aggressive settings (lines+edges)...")
        tables = _pdfplumber_extract(pdf_file, strategy="lines_edges")
        if tables:
            detection_method = "pdfplumber (lines+edges)"
            logger.info(f"✓ Strategy 1 successful: Found {len(tables)} table(s)")
            return tables, detection_method
        
        # Strategy 2: pdfplumber with text-based edge detection
        logger.info("Attempting Strategy 2: pdfplumber with text-based detection...")
        tables = _pdfplumber_extract(pdf_file, strategy="text")
        if tables:
            detection_method = "pdfplumber (text-based)"
            logger.info(f"✓ Strategy 2 successful: Found {len(tables)} table(s)")
            return tables, detection_method
        
        # Strategy 3: Extract structured text from PDF (last resort)
        logger.info("Attempting Strategy 3: Text-based table structure extraction...")
        tables = _extract_text_structure(pdf_file)
        if tables:
            detection_method = "text_structure (fallback)"
            logger.info(f"✓ Strategy 3 successful: Extracted {len(tables)} structured text block(s)")
            return tables, detection_method
        
        # No tables found with any method
        logger.warning("❌ All extraction strategies failed - no tables found")
        return [], None
        
    except Exception as e:
        logger.error(f"Error in table extraction: {str(e)}", exc_info=True)
        raise Exception(f"Error extracting tables from PDF: {str(e)}")


def _pdfplumber_extract(pdf_file, strategy="lines_edges"):
    """Extract tables using pdfplumber with specified strategy"""
    try:
        pdf_file.seek(0)  # Reset file pointer
        tables = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = None
                
                if strategy == "lines_edges":
                    # Use both lines and edges for aggressive detection
                    page_tables = page.extract_tables(
                        table_settings={
                            "vertical_strategy": "lines_edges",
                            "horizontal_strategy": "lines_edges",
                            "snap_tolerance": 3,
                            "join_tolerance": 3
                        }
                    )
                elif strategy == "text":
                    # Use text-based detection with relaxed tolerances
                    page_tables = page.extract_tables(
                        table_settings={
                            "vertical_strategy": "lines",
                            "horizontal_strategy": "text",
                            "snap_tolerance": 5,
                            "join_tolerance": 5,
                            "intersection_tolerance": 5
                        }
                    )
                
                if page_tables:
                    for table in page_tables:
                        tables.append({
                            'page': page_num + 1,
                            'data': table,
                            'method': f'pdfplumber_{strategy}'
                        })
        
        return tables
    except Exception as e:
        logger.debug(f"pdfplumber {strategy} strategy failed: {str(e)}")
        return []


def _extract_text_structure(pdf_file):
    """
    Extract structured text from PDF as last resort.
    Groups text by vertical position to create pseudo-table structure.
    This handles PDFs with text-based layouts without visible borders.
    """
    try:
        pdf_file.seek(0)  # Reset file pointer
        tables = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract all text with position information
                text_objects = page.chars
                
                if not text_objects:
                    continue
                
                # Group characters by Y-coordinate (same row)
                rows = {}
                for obj in text_objects:
                    y_pos = round(obj['top'], 1)  # Round to handle slight variations
                    if y_pos not in rows:
                        rows[y_pos] = []
                    rows[y_pos].append(obj)
                
                # Sort rows by Y position and extract text
                if rows:
                    sorted_rows = sorted(rows.items())
                    table_data = []
                    
                    for y_pos, chars_in_row in sorted_rows:
                        # Sort characters by X position (left to right)
                        sorted_chars = sorted(chars_in_row, key=lambda x: x['x0'])
                        
                        # Group characters into columns (with spacing threshold)
                        columns = []
                        current_col = []
                        last_x = None
                        
                        for char in sorted_chars:
                            x_pos = char['x0']
                            
                            # If there's a significant gap, start a new column
                            if last_x is not None and (x_pos - last_x) > 10:
                                if current_col:
                                    col_text = ''.join([c['text'] for c in current_col]).strip()
                                    columns.append(col_text)
                                    current_col = []
                            
                            current_col.append(char)
                            last_x = x_pos + char['width']
                        
                        # Add last column
                        if current_col:
                            col_text = ''.join([c['text'] for c in current_col]).strip()
                            columns.append(col_text)
                        
                        # Only add non-empty rows
                        if any(col for col in columns):
                            table_data.append(columns)
                    
                    # Only add if we have meaningful content
                    if len(table_data) > 1:  # At least 2 rows
                        tables.append({
                            'page': page_num + 1,
                            'data': table_data,
                            'method': 'text_structure'
                        })
        
        return tables
    except Exception as e:
        logger.debug(f"Text structure extraction failed: {str(e)}")
        return []


def create_excel_from_tables(tables, detection_method=None):
    """Create Excel file from extracted tables with metadata about detection method"""
    try:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # Add metadata sheet if using fallback method
        if detection_method and detection_method != "pdfplumber (lines+edges)":
            meta_ws = wb.create_sheet("_INFO", 0)
            meta_ws['A1'] = "Detection Method"
            meta_ws['B1'] = detection_method
            meta_ws['A2'] = "Status"
            meta_ws['B2'] = "Used fallback table extraction"
            meta_ws.column_dimensions['A'].width = 20
            meta_ws.column_dimensions['B'].width = 40
        
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
    """Convert PDF file to Excel with smart table detection and fallback strategies"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Processing PDF file: {file.filename}")
        
        # Read file content
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract tables from PDF using multi-strategy approach
        tables, detection_method = extract_tables_from_pdf(pdf_file)
        
        if not tables:
            logger.error(f"Failed to extract any content from {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail="No tables found in PDF. Please ensure the PDF contains table data or structured text."
            )
        
        logger.info(f"Successfully extracted {len(tables)} table(s) using: {detection_method}")
        
        # Create Excel file
        excel_file = create_excel_from_tables(tables, detection_method)
        
        # Return Excel file
        return FileResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{file.filename.replace('.pdf', '')}.xlsx",
            headers={
                "X-Detection-Method": detection_method or "unknown"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion failed for {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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
