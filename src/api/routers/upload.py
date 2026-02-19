"""
Upload API router.

Handles file upload and file listing operations.
"""

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File as FastAPIFile, UploadFile, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.api.dependencies import file_storage, database
from src.models.file import FileStatus
from src.repositories.file_repository import FileRepository


# Create router
router = APIRouter(prefix="/api/v1", tags=["Upload"])


@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(database),
    storage=Depends(file_storage),
) -> JSONResponse:
    """
    Upload a file to the system.

    Args:
        file: The file to upload (multipart/form-data)
        db: Database session
        storage: File storage service

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

    # Store file metadata in database first (to get the ID)
    file_repo = FileRepository(db)
    db_file = file_repo.create_file(
        filename=file.filename or "unnamed",
        content_type=content_type,
        size=file_size,
        file_path="",  # Will update after we know the ID
        status=FileStatus.PENDING,
    )

    # Use database-generated ID for file path
    temp_dir = Path(tempfile.gettempdir()) / "fill" / "uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / str(db_file.id)

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Update file path in database
    db_file.file_path = str(file_path)

    # Store content temporarily for parsing (keyed by database ID)
    storage.store(db_file.id, file_content)

    return JSONResponse(
        status_code=201,
        content={
            "message": "File uploaded successfully",
            "file_id": str(db_file.id),
            "filename": db_file.filename,
            "size": db_file.size,
            "status": db_file.status,
        }
    )


@router.get("/files")
async def list_files(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
    offset: int = Query(0, ge=0, description="Number of files to skip"),
    db: Session = Depends(database),
) -> JSONResponse:
    """
    List all uploaded files with pagination support.

    Args:
        limit: Maximum number of files to return (1-1000)
        offset: Number of files to skip for pagination
        db: Database session

    Returns:
        JSONResponse with list of files and pagination metadata

    Raises:
        HTTPException: 400 if pagination parameters are invalid
    """
    # Get files from database
    file_repo = FileRepository(db)
    total_count = file_repo.count_files()
    db_files = file_repo.list_files(limit=limit, offset=offset)

    # Build response with file metadata
    files_response = [
        {
            "file_id": str(f.id),
            "filename": f.filename,
            "content_type": f.content_type,
            "size": f.size,
            "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
            "status": f.status,
        }
        for f in db_files
    ]

    return JSONResponse(
        status_code=200,
        content={
            "files": files_response,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count,
        }
    )
