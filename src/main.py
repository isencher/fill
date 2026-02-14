"""
Fill Application - 2D Table Data Auto-Filling Web Application

Main FastAPI application entry point.
"""

import tempfile
from pathlib import Path
from uuid import UUID

from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile as FastAPIUploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.models.file import FileStatus, UploadFile
from src.models.template import Template
from src.services.template_store import get_template_store

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


@app.get("/api/v1/files", tags=["Upload"])
async def list_files(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
    offset: int = Query(0, ge=0, description="Number of files to skip"),
) -> JSONResponse:
    """
    List all uploaded files with pagination support.

    Args:
        limit: Maximum number of files to return (1-1000)
        offset: Number of files to skip for pagination

    Returns:
        JSONResponse with list of files and pagination metadata

    Raises:
        HTTPException: 400 if pagination parameters are invalid
    """
    # Get all files from storage
    all_files = list(_uploaded_files.values())

    # Sort by uploaded_at descending (newest first)
    all_files.sort(key=lambda f: f.uploaded_at, reverse=True)

    # Apply pagination
    total_count = len(all_files)
    paginated_files = all_files[offset : offset + limit]

    # Build response with file metadata
    files_response = [
        {
            "file_id": str(f.id),
            "filename": f.filename,
            "content_type": f.content_type,
            "size": f.size,
            "uploaded_at": f.uploaded_at.isoformat(),
            "status": f.status.value,
        }
        for f in paginated_files
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


# Template API Endpoints
_template_store = get_template_store()


@app.post("/api/v1/templates", tags=["Templates"], status_code=201)
async def create_template(
    name: str = Query(..., min_length=1, max_length=200, description="Template name"),
    file_path: str = Query(..., min_length=1, description="Template file path"),
    description: Optional[str] = Query(None, max_length=1000, description="Template description"),
    placeholders: Optional[str] = Query(None, description="Comma-separated placeholder names"),
) -> JSONResponse:
    """
    Create a new template.

    Args:
        name: Template name
        file_path: Path to template file
        description: Optional template description
        placeholders: Optional comma-separated list of placeholder names

    Returns:
        JSONResponse with created template data

    Raises:
        HTTPException: 400 if template data is invalid
    """
    try:
        # Parse placeholders if provided
        placeholder_list = []
        if placeholders:
            placeholder_list = [p.strip() for p in placeholders.split(",") if p.strip()]

        # Create template instance
        template = Template(
            name=name,
            file_path=file_path,
            description=description,
            placeholders=placeholder_list,
        )

        # Save to store
        saved = _template_store.save_template(template)

        return JSONResponse(
            status_code=201,
            content={
                "message": "Template created successfully",
                "template": {
                    "id": saved.id,
                    "name": saved.name,
                    "description": saved.description,
                    "placeholders": saved.placeholders,
                    "file_path": saved.file_path,
                    "created_at": saved.created_at.isoformat(),
                }
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.get("/api/v1/templates", tags=["Templates"])
async def list_templates(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip"),
    sort_by: str = Query("created_at", description="Field to sort by (name, created_at)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
) -> JSONResponse:
    """
    List all templates with pagination and sorting.

    Args:
        limit: Maximum number of templates to return (1-1000)
        offset: Number of templates to skip for pagination
        sort_by: Field to sort by (name, created_at)
        order: Sort order (asc, desc)

    Returns:
        JSONResponse with list of templates and pagination metadata

    Raises:
        HTTPException: 400 if pagination parameters are invalid
    """
    try:
        templates = _template_store.list_templates(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )

        # Build response
        templates_response = [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "placeholders": t.placeholders,
                "file_path": t.file_path,
                "created_at": t.created_at.isoformat(),
            }
            for t in templates
        ]

        total_count = _template_store.count_templates()

        return JSONResponse(
            status_code=200,
            content={
                "templates": templates_response,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.get("/api/v1/templates/{template_id}", tags=["Templates"])
async def get_template(template_id: str) -> JSONResponse:
    """
    Get a template by ID.

    Args:
        template_id: UUID of template to retrieve

    Returns:
        JSONResponse with template data

    Raises:
        HTTPException: 404 if template not found
    """
    template = _template_store.get_template(template_id)

    if template is None:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {template_id}"
        )

    return JSONResponse(
        status_code=200,
        content={
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "placeholders": template.placeholders,
            "file_path": template.file_path,
            "created_at": template.created_at.isoformat(),
        }
    )


@app.put("/api/v1/templates/{template_id}", tags=["Templates"])
async def update_template(
    template_id: str,
    name: Optional[str] = Query(None, min_length=1, max_length=200, description="Template name"),
    file_path: Optional[str] = Query(None, min_length=1, description="Template file path"),
    description: Optional[str] = Query(None, max_length=1000, description="Template description"),
    placeholders: Optional[str] = Query(None, description="Comma-separated placeholder names"),
) -> JSONResponse:
    """
    Update a template by ID.

    Args:
        template_id: UUID of template to update
        name: Optional new template name
        file_path: Optional new template file path
        description: Optional new template description
        placeholders: Optional new comma-separated placeholder names

    Returns:
        JSONResponse with updated template data

    Raises:
        HTTPException: 404 if template not found
        HTTPException: 400 if update data is invalid
    """
    # Build updates dictionary
    updates = {}
    if name is not None:
        updates["name"] = name
    if file_path is not None:
        updates["file_path"] = file_path
    if description is not None:
        updates["description"] = description
    if placeholders is not None:
        updates["placeholders"] = [p.strip() for p in placeholders.split(",") if p.strip()]

    # Must have at least one update
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No update fields provided"
        )

    try:
        template = _template_store.update_template(template_id, **updates)

        if template is None:
            raise HTTPException(
                status_code=404,
                detail=f"Template not found: {template_id}"
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Template updated successfully",
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "placeholders": template.placeholders,
                    "file_path": template.file_path,
                    "created_at": template.created_at.isoformat(),
                }
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.delete("/api/v1/templates/{template_id}", tags=["Templates"])
async def delete_template(template_id: str) -> JSONResponse:
    """
    Delete a template by ID.

    Args:
        template_id: UUID of template to delete

    Returns:
        JSONResponse with deletion confirmation

    Raises:
        HTTPException: 404 if template not found
    """
    deleted = _template_store.delete_template(template_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {template_id}"
        )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Template deleted successfully",
            "template_id": template_id,
        }
    )
