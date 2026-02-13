"""
Fill Application - 2D Table Data Auto-Filling Web Application

Main FastAPI application entry point.
"""

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, File, HTTPException, UploadFile as FastAPIUploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.models.file import FileStatus, UploadFile

# Create FastAPI application instance
app = FastAPI(
    title="Fill API",
    description="2D Table Data Auto-Filling Web Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """
    Root health check endpoint.

    Returns:
        dict with status indicator
    """
    return {"status": "ok"}


# In-memory storage for uploaded files (TODO: replace with database in Phase 9)
_uploaded_files: dict[UUID, UploadFile] = {}


@app.post("/api/v1/upload", tags=["Upload"], status_code=201)
async def upload_file(file: FastAPIUploadFile = File(...)) -> JSONResponse:
    """
    Upload a file to the system.

    Args:
        file: The file to upload (multipart/form-data)

    Returns:
        JSONResponse with upload confirmation including file_id

    Raises:
        HTTPException: 400 if file type is invalid
        HTTPException: 413 if file size exceeds limit
    """
    # Validate file extension
    if not (file.filename or "").lower().endswith((".xlsx", ".csv")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .xlsx and .csv files are supported."
        )

    # Read file content to determine size
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {max_size} bytes"
        )

    # Determine content type
    content_type = file.content_type or "application/octet-stream"

    # Create UploadFile model instance
    upload_file = UploadFile(
        filename=file.filename or "unnamed",
        content_type=content_type,
        size=file_size,
        status=FileStatus.PENDING,
    )

    # Save file to temporary storage
    # In a production environment, this would use object storage or a file system
    temp_dir = Path(tempfile.gettempdir()) / "fill" / "uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / str(upload_file.id)

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Store file metadata in memory
    _uploaded_files[upload_file.id] = upload_file

    return JSONResponse(
        status_code=201,
        content={
            "message": "File uploaded successfully",
            "file_id": str(upload_file.id),
            "filename": upload_file.filename,
            "size": upload_file.size,
            "status": upload_file.status.value,
        }
    )
