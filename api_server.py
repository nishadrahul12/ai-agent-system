"""
REST API Server for AI Multi-Agent System
Handles file uploads (Excel, CSV), encoding detection, and processing
Runs locally on http://localhost:8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from correlation_engine import analyze as analyze_correlations
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import numpy as np
import chardet
import os
import json
from pathlib import Path
from datetime import datetime
import io
from typing import Dict, List, Optional
import sys

# Add parent directory to path so we can import orchestrator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator
from logging_config import setup_logger

# Initialize FastAPI app
app = FastAPI(
    title="AI Multi-Agent System API",
    description="REST API for intelligent data analysis",
    version="1.0.0"
)

# Add CORS middleware (allows web frontend to communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve dashboard static files (at the END, after all routes)
# We'll add this later


# Initialize logging
log = setup_logger("api_server")

# Initialize the orchestrator system
try:
    orchestrator = Orchestrator()
    log.info("Orchestrator initialized successfully")
except Exception as e:
    log.error(f"Failed to initialize Orchestrator: {e}")
    orchestrator = None

# Store uploaded files and their metadata
uploaded_files = {}
analysis_results = {}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_encoding(file_content: bytes) -> str:
    """
    Detect file encoding automatically
    Supports: UTF-8, GBK, GB18030, Big5, UTF-16, ISO-8859-1, Windows-1252
    """
    try:
        # Chardet detects encoding
        detected = chardet.detect(file_content)
        encoding = detected['encoding']
        confidence = detected['confidence']
        
        log.info(f"Detected encoding: {encoding} (confidence: {confidence})")
        
        if encoding is None:
            log.warning("Could not detect encoding, using UTF-8 as default")
            return 'utf-8'
        
        return encoding
    except Exception as e:
        log.error(f"Encoding detection error: {e}")
        return 'utf-8'


def read_file_smart(file_content: bytes, filename: str) -> tuple:
    """
    Read file with smart encoding detection
    Returns: (dataframe, encoding_used, success_message)
    """
    try:
        # Check file type
        if filename.endswith('.csv'):
            # Try to detect encoding for CSV
            encoding = detect_encoding(file_content)
            
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                log.info(f"CSV read successfully with encoding: {encoding}")
                return df, encoding, f"CSV read successfully (Encoding: {encoding})"
            except:
                # If fails, try UTF-8
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
                log.info("CSV read with UTF-8 fallback")
                return df, 'utf-8', "CSV read (UTF-8 fallback)"
        
        elif filename.endswith(('.xlsx', '.xls')):
            # Excel files
            df = pd.read_excel(io.BytesIO(file_content))
            log.info("Excel file read successfully")
            return df, 'utf-8', "Excel file read successfully"
        
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    except Exception as e:
        log.error(f"Error reading file: {e}")
        raise


def auto_detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Auto-detect column purposes based on column names
    Returns mapping: {column_name: detected_type}
    """
    column_mapping = {}
    columns = df.columns.str.lower()
    
    for i, col in enumerate(columns):
        # Check for network-related columns
        if any(x in col for x in ['region', 'location', 'area', 'site']):
            column_mapping[df.columns[i]] = 'location'
        elif any(x in col for x in ['speed', 'mbps', 'bandwidth', 'throughput']):
            column_mapping[df.columns[i]] = 'speed'
        elif any(x in col for x in ['latency', 'delay', 'ping', 'rtt']):
            column_mapping[df.columns[i]] = 'latency'
        elif any(x in col for x in ['error', 'loss', 'failure']):
            column_mapping[df.columns[i]] = 'error_rate'
        elif any(x in col for x in ['customer', 'user', 'id', 'name']):
            column_mapping[df.columns[i]] = 'customer_id'
        elif any(x in col for x in ['message', 'feedback', 'comment', 'text']):
            column_mapping[df.columns[i]] = 'message'
        elif any(x in col for x in ['sentiment', 'mood', 'tone']):
            column_mapping[df.columns[i]] = 'sentiment'
        else:
            column_mapping[df.columns[i]] = 'unknown'
    
    log.info(f"Auto-detected columns: {column_mapping}")
    return column_mapping


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/status")
async def api_status():
    """Health check endpoint - moved to /api/status"""
    return {
        "status": "online",
        "message": "AI Multi-Agent System API is running!",
        "version": "1.0.0",
        "base_url": "http://localhost:8000"
    }



@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        orchestrator_status = orchestrator.get_orchestrator_status() if orchestrator else None
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "orchestrator": orchestrator_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    
# ============================================================================
# COLUMN TYPE MANAGEMENT
# ============================================================================

COLUMN_TYPES_FILE = Path(__file__).parent / "column_types_memory.json"

def load_column_types():
    """Load column types from memory file"""
    try:
        if COLUMN_TYPES_FILE.exists():
            with open(COLUMN_TYPES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default if doesn't exist
            default_types = {
                "common_column_types": {
                    "Standard": [
                        {"value": "location", "label": "📍 Location", "icon": "📍"},
                        {"value": "speed", "label": "⚡ Speed/Throughput", "icon": "⚡"},
                        {"value": "latency", "label": "⏱️ Latency/Delay", "icon": "⏱️"},
                        {"value": "error_rate", "label": "❌ Error Rate", "icon": "❌"},
                        {"value": "date_time", "label": "📅 Date/Time", "icon": "📅"},
                        {"value": "percentage", "label": "📊 Percentage", "icon": "📊"},
                        {"value": "count", "label": "🔢 Count", "icon": "🔢"}
                    ],
                    "Telecom": [
                        {"value": "pdcp_throughput", "label": "📡 PDCP Throughput", "icon": "📡"},
                        {"value": "sinr_level", "label": "📶 SINR Level", "icon": "📶"},
                        {"value": "cqi_index", "label": "📊 CQI Index", "icon": "📊"},
                        {"value": "rrc_connected_ue", "label": "👥 RRC Connected Users", "icon": "👥"},
                        {"value": "prb_utilization", "label": "🔌 PRB Utilization", "icon": "🔌"}
                    ],
                    "user_saved": {}
                }
            }
            save_column_types(default_types)
            return default_types
    except Exception as e:
        log.error(f"Error loading column types: {e}")
        return {}

def save_column_types(types_data):
    """Save column types to memory file"""
    try:
        with open(COLUMN_TYPES_FILE, 'w', encoding='utf-8') as f:
            json.dump(types_data, f, indent=2, ensure_ascii=False)
        log.info("Column types saved")
    except Exception as e:
        log.error(f"Error saving column types: {e}")

@app.get("/column-types")
async def get_column_types():
    """Get available column types (dropdown options)"""
    try:
        types = load_column_types()
        return {
            "status": "success",
            "column_types": types
        }
    except Exception as e:
        log.error(f"Error getting column types: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )

@app.post("/save-column-mapping")
async def save_column_mapping(file_id: str, mapping: Dict):
    """Save user's column mapping for future use"""
    try:
        types = load_column_types()
        
        # Save custom mappings user created
        for column_name, column_type in mapping.items():
            if column_type not in ["location", "speed", "latency", "error_rate", "unknown"]:
                # It's a custom type, save it
                types["common_column_types"]["user_saved"][column_name] = column_type
        
        save_column_types(types)
        
        return {
            "status": "success",
            "message": "Column mappings saved for future use"
        }
    except Exception as e:
        log.error(f"Error saving mapping: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload Excel or CSV file
    Automatically detects encoding
    Returns: file_id, columns, encoding, auto-detected column mapping
    """
    try:
        log.info(f"Uploading file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Check file size (5GB limit)
        file_size_gb = len(content) / (1024**3)
        if file_size_gb > 5:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size_gb:.2f}GB (max 5GB)"
            )
        
        # Read file with smart encoding detection
        df, encoding, read_message = read_file_smart(content, file.filename)
        
        # Auto-detect columns
        column_mapping = auto_detect_columns(df)
        
        # Generate file ID
        file_id = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store file metadata
        uploaded_files[file_id] = {
            "filename": file.filename,
            "encoding": encoding,
            "columns": list(df.columns),
            "shape": df.shape,
            "auto_column_mapping": column_mapping,
            "upload_time": datetime.now().isoformat(),
            "dataframe": df  # Keep dataframe in memory for now
        }
        
        log.info(f"File stored with ID: {file_id}")
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "encoding": encoding,
            "encoding_message": read_message,
            "file_size_mb": round(len(content) / (1024**2), 2),
            "rows": df.shape[0],
            "columns": list(df.columns),
            "auto_column_mapping": column_mapping,
            "message": "File uploaded successfully. Review auto-detected columns and confirm or adjust mapping."
        }
    
    except Exception as e:
        log.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Upload failed: {str(e)}"
        )


@app.post("/analyze")
async def analyze_data(
    file_id: str,
    task_type: str = "network_analysis",
    custom_column_mapping: Optional[Dict] = None
):
    """
    Analyze uploaded file data
    Accepts: file_id, task_type, optional custom column mapping
    """
    try:
        log.info(f"Analyzing file: {file_id} with task: {task_type}")
        
        # Validate file exists
        if file_id not in uploaded_files:
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_id}"
            )
        
        # Get file data
        file_data = uploaded_files[file_id]
        df = file_data["dataframe"]
        
        # Use custom mapping if provided, otherwise use auto-detected
        column_mapping = custom_column_mapping or file_data["auto_column_mapping"]
        
        log.info(f"Using column mapping: {column_mapping}")
        
        # Create task for orchestrator
        task_id = orchestrator.add_task(
            description=f"Analyze {file_data['filename']} - Task: {task_type}",
            priority="high",
            task_type=task_type,
            data={
                "dataframe_shape": df.shape,
                "columns": list(df.columns),
                "column_mapping": column_mapping,
                "encoding": file_data["encoding"],
                "sample_data": df.head(5).to_dict()
            }
        )
        
        log.info(f"Task created: {task_id}")
        
        # Process task
        results = orchestrator.process_tasks(max_tasks=1)
        
        # Store results
        analysis_results[task_id] = {
            "task_id": task_id,
            "file_id": file_id,
            "filename": file_data["filename"],
            "task_type": task_type,
            "column_mapping": column_mapping,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        log.info(f"Analysis complete for task: {task_id}")
        
        return {
            "status": "success",
            "task_id": task_id,
            "file_id": file_id,
            "filename": file_data["filename"],
            "analysis_complete": True,
            "results": results,
            "download_url": f"/download/{task_id}",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {str(e)}"
        )

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

@app.post("/correlation-analysis")
async def correlation_analysis(
    request_data: dict = Body(...)
):
    """
    Analyze correlations between source and target columns
    """
    try:
        # Extract parameters from request
        file_id = request_data.get('file_id')
        target_column = request_data.get('target_column')
        source_columns = request_data.get('source_columns')
        
        log.info(f"Correlation request - file_id: {file_id}, target: {target_column}, sources: {source_columns}")
        
        # Validate inputs
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id required")
        
        if file_id not in uploaded_files:
            raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
        
        if not target_column:
            raise HTTPException(status_code=400, detail="target_column required")
        
        if not source_columns or len(source_columns) < 2:
            raise HTTPException(status_code=400, detail="At least 2 source columns required")
        
        # Get dataframe
        df = uploaded_files[file_id]["dataframe"]
        
        # Validate columns exist
        if target_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{target_column}' not found")
        
        for col in source_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Source column '{col}' not found")
        
        log.info(f"Running correlation analysis...")
        
        # Run analysis
        results = analyze_correlations(df, target_column, source_columns)
        
        if results.get('status') == 'error':
            raise HTTPException(status_code=400, detail=results.get('message'))
        
        log.info(f"✅ Correlation analysis complete. Best model: {results.get('best_model')}")
        
        return {
            "status": "success",
            "analysis": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Correlation analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.get("/get-numeric-columns/{file_id}")
async def get_numeric_columns(file_id: str):
    """
    Get list of numeric columns from uploaded file
    (For correlation analysis selection)
    """
    try:
        log.info(f"Getting numeric columns for file: {file_id}")
        
        if file_id not in uploaded_files:
            log.error(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
        
        df = uploaded_files[file_id]["dataframe"]
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        log.info(f"Found {len(numeric_cols)} numeric columns: {numeric_cols}")
        
        return {
            "status": "success",
            "numeric_columns": numeric_cols,
            "total_columns": len(numeric_cols)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting numeric columns: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting numeric columns: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """Get analysis results for a task"""
    try:
        if task_id not in analysis_results:
            raise HTTPException(
                status_code=404,
                detail=f"Results not found for task: {task_id}"
            )
        
        return {
            "status": "success",
            "data": analysis_results[task_id]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error retrieving results: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )


@app.get("/download/{task_id}")
async def download_results(task_id: str, format: str = "json"):
    """Download results in JSON, Excel, or CSV format"""
    try:
        if task_id not in analysis_results:
            raise HTTPException(
                status_code=404,
                detail=f"Results not found: {task_id}"
            )
        
        result_data = analysis_results[task_id]
        
        if format == "json":
            # Return as JSON
            return JSONResponse(content=result_data)
        
        elif format == "excel":
            # Convert to Excel
            df = pd.DataFrame([result_data])
            excel_file = f"/tmp/{task_id}_results.xlsx"
            df.to_excel(excel_file, index=False)
            return FileResponse(excel_file, filename=f"{task_id}_results.xlsx")
        
        elif format == "csv":
            # Convert to CSV
            df = pd.DataFrame([result_data])
            csv_file = f"/tmp/{task_id}_results.csv"
            df.to_csv(csv_file, index=False)
            return FileResponse(csv_file, filename=f"{task_id}_results.csv")
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Download error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Download failed: {str(e)}"
        )


@app.get("/files")
async def list_files():
    """List all uploaded files"""
    try:
        files_list = []
        for file_id, file_data in uploaded_files.items():
            files_list.append({
                "file_id": file_id,
                "filename": file_data["filename"],
                "encoding": file_data["encoding"],
                "rows": file_data["shape"][0],
                "columns": len(file_data["shape"]),
                "upload_time": file_data["upload_time"]
            })
        
        return {
            "status": "success",
            "total_files": len(files_list),
            "files": files_list
        }
    
    except Exception as e:
        log.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )


@app.get("/tasks")
async def list_tasks():
    """List all analysis tasks and results"""
    try:
        tasks_list = []
        for task_id, task_data in analysis_results.items():
            tasks_list.append({
                "task_id": task_id,
                "filename": task_data["filename"],
                "task_type": task_data["task_type"],
                "timestamp": task_data["timestamp"]
            })
        
        return {
            "status": "success",
            "total_tasks": len(tasks_list),
            "tasks": tasks_list
        }
    
    except Exception as e:
        log.error(f"Error listing tasks: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )

# ============================================================================
# SERVE DASHBOARD
# ============================================================================

try:
    import os
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    
    dashboard_path = Path(__file__).parent / "dashboard"
    if dashboard_path.exists():
        # Mount dashboard at root, serving index.html as default
        app.mount("/", StaticFiles(directory=str(dashboard_path), html=True), name="dashboard")
        log.info(f"Dashboard mounted at: {dashboard_path}")
except Exception as e:
    log.warning(f"Dashboard mount warning: {e}")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    log.info("=" * 60)
    log.info("Starting AI Multi-Agent System API Server")
    log.info("=" * 60)
    log.info("Access the API at: http://localhost:8000")
    log.info("API Documentation: http://localhost:8000/docs")
    log.info("=" * 60)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
