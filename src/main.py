"""
Fill Application - 2D Table Data Auto-Filling Web Application

Main FastAPI application entry point.
"""

import json
import os
import tempfile
from pathlib import Path
from uuid import UUID

from typing import Optional

from fastapi import Body, Depends, FastAPI, File, Form, HTTPException, Query, UploadFile as FastAPIUploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from src.models.file import FileStatus, UploadFile
from src.models.template import Template
from src.repositories.database import init_db, get_db
from src.repositories.file_repository import FileRepository
from src.repositories.template_repository import TemplateRepository
from src.repositories.mapping_repository import MappingRepository
from src.services.template_store import get_template_store
from src.services.file_storage import get_file_storage

# Initialize database on module load
init_db()

# Create FastAPI application instance
app = FastAPI(
    title="Fill API",
    description="2D Table Data Auto-Filling Web Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for development and production
# Use ALLOWED_ORIGINS env var for production (comma-separated list)
# Default: http://localhost:8000,http://localhost:3000 for development
_allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in _allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", tags=["Health"])
async def root() -> FileResponse:
    """
    Root endpoint - serves the onboarding page for first-time users,
    otherwise redirects to the upload page.

    Returns:
        FileResponse with the HTML onboarding or upload page
    """
    # Check if onboarding.html exists, serve it
    # The onboarding page itself will handle redirecting returning users
    onboarding_path = static_dir / "onboarding.html"
    if onboarding_path.exists():
        return FileResponse(onboarding_path)

    # Fallback to index.html if onboarding doesn't exist
    index_path = static_dir / "index.html"
    return FileResponse(index_path)


@app.get("/mapping", tags=["Frontend"])
async def mapping_page() -> FileResponse:
    """
    Mapping page - serves column-to-placeholder mapping interface.

    Returns:
        FileResponse with HTML mapping page
    """
    mapping_path = static_dir / "mapping.html"
    return FileResponse(mapping_path)


# File content storage service
# Uses FileStorage service for centralized, thread-safe in-memory storage
_file_storage = get_file_storage()

# Import database session dependency
from src.repositories.database import get_db


@app.post("/api/v1/upload", tags=["Upload"], status_code=201)
async def upload_file(
    file: FastAPIUploadFile = File(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Upload a file to the system.

    Args:
        file: The file to upload (multipart/form-data)
        db: Database session

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
        status="uploaded",
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
    _file_storage.store(db_file.id, file_content)

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


@app.get("/api/v1/files", tags=["Upload"])
async def list_files(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
    offset: int = Query(0, ge=0, description="Number of files to skip"),
    db: Session = Depends(get_db),
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


# Template Upload Endpoint
from src.services.placeholder_parser import PlaceholderParser

@app.post("/api/v1/templates/upload", tags=["Templates"], status_code=201)
async def upload_template(
    file: FastAPIUploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
) -> JSONResponse:
    """
    Upload a template file and automatically extract placeholders.
    
    Args:
        file: Template file (.docx or .txt)
        name: Template name
        description: Optional template description
        
    Returns:
        JSONResponse with created template and extracted placeholders
        
    Raises:
        HTTPException: 400 if file type is invalid
    """
    # Validate file extension - now supports xlsx templates too
    if not (file.filename or "").lower().endswith((".docx", ".txt", ".xlsx")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx, .txt and .xlsx files are supported."
        )
    
    # Read file content
    file_content = await file.read()
    
    # Save template file
    temp_dir = Path(tempfile.gettempdir()) / "fill" / "templates"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    safe_filename = Path(file.filename).name
    template_path = temp_dir / safe_filename
    
    with open(template_path, "wb") as f:
        f.write(file_content)
    
    # Extract placeholders
    try:
        parser = PlaceholderParser()
        
        if file.filename.lower().endswith(".docx"):
            placeholders = parser.extract_from_docx(template_path)
        elif file.filename.lower().endswith(".xlsx"):
            # Excel template - placeholders are in first sheet as markers
            # e.g., cell contains "{{订单号}}"
            import openpyxl
            wb = openpyxl.load_workbook(str(template_path))
            ws = wb.active
            
            placeholders = []
            # Scan all cells for {{placeholder}} pattern
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        cell_placeholders = parser.extract_from_text(cell.value)
                        placeholders.extend(cell_placeholders)
            
            unique_placeholders = list(dict.fromkeys(placeholders))  # Preserve order, remove duplicates
        else:
            # Text file
            content = file_content.decode("utf-8", errors="ignore")
            placeholders = parser.extract_from_text(content)
            unique_placeholders = parser.extract_unique_from_text(
                " ".join([f"{{{{{p}}}}}" for p in placeholders])
            )
    except Exception:
        # If extraction fails, use empty list
        unique_placeholders = []
    
    # Create template
    template = Template(
        name=name,
        file_path=str(template_path),
        description=description,
        placeholders=unique_placeholders,
    )
    
    # Save to store
    saved = _template_store.save_template(template)
    
    return JSONResponse(
        status_code=201,
        content={
            "message": "Template uploaded successfully",
            "template": {
                "id": saved.id,
                "name": saved.name,
                "description": saved.description,
                "placeholders": saved.placeholders,
                "file_path": saved.file_path,
                "created_at": saved.created_at.isoformat(),
            },
            "extracted_placeholders": unique_placeholders,
        }
    )


# Smart Mapping Suggestion Endpoint
from src.services.fuzzy_matcher import FuzzyMatcher

@app.post("/api/v1/mappings/suggest", tags=["Mappings"])
async def suggest_mapping(
    file_id: str = Query(..., description="ID of uploaded data file"),
    template_id: str = Query(..., description="ID of template"),
) -> JSONResponse:
    """
    Suggest column-to-placeholder mappings based on fuzzy matching.
    
    Args:
        file_id: ID of uploaded data file
        template_id: ID of template
        
    Returns:
        JSONResponse with suggested mappings and confidence scores
        
    Raises:
        HTTPException: 404 if file or template not found
    """
    # Validate file exists
    try:
        file_uuid = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
    
    if file_uuid not in _uploaded_files:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
    
    # Validate template exists
    template = _template_store.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")

    # Parse file to get column names
    file_repo = FileRepository(db)
    db_file = file_repo.get_file_by_id(file_uuid)
    if db_file is None:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    file_content = _file_storage.get(file_uuid)

    if not file_content:
        raise HTTPException(status_code=404, detail=f"File content not found: {file_id}")
    
    try:
        from src.services.parser_factory import get_parser

        # Save to temp file for parsing
        temp_dir = Path(tempfile.gettempdir()) / "fill" / "parse"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"{file_id}_{db_file.filename}"

        with open(temp_path, "wb") as f:
            f.write(file_content)

        # Parse file
        parser_class = get_parser(db_file.filename)
        parser = parser_class()

        extension = db_file.filename.lower().split(".")[-1]
        if extension == "csv":
            rows = parser.parse_csv(temp_path)
        else:
            rows = parser.parse_excel(temp_path)
        
        # Get column names from first row
        columns = list(rows[0].keys()) if rows else []
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
    
    # Use FuzzyMatcher for suggestions
    matcher = FuzzyMatcher()
    template_placeholders = template.placeholders or []
    
    suggestions = matcher.suggest_mappings(template_placeholders, columns)
    overall_confidence = matcher.calculate_overall_confidence(suggestions)
    
    # Check for unmapped items
    mapped_columns = [s["suggested_column"] for s in suggestions if s["suggested_column"]]
    unmapped_columns = [c for c in columns if c not in mapped_columns]
    
    return JSONResponse(
        status_code=200,
        content={
            "suggested_mappings": suggestions,
            "confidence": round(overall_confidence, 2),
            "can_auto_fill": overall_confidence >= 0.8,
            "unmapped_columns": unmapped_columns,
            "unmapped_placeholders": [s["placeholder"] for s in suggestions if not s["suggested_column"]],
        }
    )


# Serve templates.html
@app.get("/templates.html", tags=["Frontend"])
async def templates_page() -> FileResponse:
    """
    Template selection page - serves template selection interface.
    
    Returns:
        FileResponse with HTML template selection page
    """
    templates_path = static_dir / "templates.html"
    return FileResponse(templates_path)


# Serve mapping.html
@app.get("/mapping.html", tags=["Frontend"])
async def mapping_html_page() -> FileResponse:
    """
    Mapping page - serves column-to-placeholder mapping interface.
    
    Returns:
        FileResponse with HTML mapping page
    """
    mapping_path = static_dir / "mapping.html"
    return FileResponse(mapping_path)


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


# Output Download Endpoints
from fastapi.responses import StreamingResponse
from src.services.output_storage import get_output_storage
import zipfile
import io

_output_storage = get_output_storage()


@app.get("/api/v1/outputs/{job_id}", tags=["Outputs"])
async def download_job_outputs(job_id: str) -> StreamingResponse:
    """
    Download all outputs for a job as a ZIP file.

    Args:
        job_id: Job identifier

    Returns:
        StreamingResponse with ZIP file containing all outputs

    Raises:
        HTTPException: 404 if job not found
    """
    # Check if job exists
    if not _output_storage.job_exists(job_id):
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    # Get all outputs for the job
    outputs = _output_storage.get_job_outputs(job_id)

    if not outputs:
        raise HTTPException(
            status_code=404,
            detail=f"No outputs found for job: {job_id}"
        )

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in outputs.items():
            zip_file.writestr(filename, content)

    zip_buffer.seek(0)

    # Return ZIP file as streaming response
    return StreamingResponse(
        io.BytesIO(zip_buffer.getvalue()),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={job_id}_outputs.zip"
        }
    )


@app.get("/api/v1/outputs/{job_id}/{filename}", tags=["Outputs"])
async def download_single_output(job_id: str, filename: str) -> StreamingResponse:
    """
    Download a single output file.

    Args:
        job_id: Job identifier
        filename: Name of the file to download

    Returns:
        StreamingResponse with file content

    Raises:
        HTTPException: 404 if job or file not found
    """
    # Check if job exists
    if not _output_storage.job_exists(job_id):
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    # Get specific file
    content = _output_storage.get_output(job_id, filename)

    if content is None:
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}"
        )

    # Detect media type from filename
    if filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".txt"):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"

    # Return file as streaming response
    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# Mapping API Endpoints
from src.services import get_parser
from src.models.mapping import Mapping


@app.get("/api/v1/parse/{file_id}", tags=["Parsing"])
async def parse_file(file_id: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Parse uploaded file and return data preview (first 5 rows).

    Args:
        file_id: ID of uploaded file to parse
        db: Database session

    Returns:
        JSONResponse with parsed data (rows and columns)

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 400 if file cannot be parsed
    """
    from uuid import UUID as UUID_TYPE
    
    # Convert string ID to UUID for lookup
    try:
        file_uuid = UUID_TYPE(file_id)
    except ValueError:
        # Treat invalid UUID format as file not found for better UX
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_id}"
        )

    # Check if file exists in database
    file_repo = FileRepository(db)
    db_file = file_repo.get_file_by_id(file_uuid)
    
    if db_file is None:
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_id}"
        )

    # Get file content from filesystem
    file_path = Path(db_file.file_path)
    if not file_path.exists():
        # Try to get from memory cache
        file_content = _file_storage.get(file_uuid)
        if file_content:
            # Re-write to disk
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file_content)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"File content not found: {file_id}"
            )

    # Parse file based on extension
    try:
        parser_class = get_parser(db_file.filename)
        file_extension = db_file.filename.lower().split('.')[-1]

        # Create temp file for parsing
        temp_dir = Path(tempfile.gettempdir()) / "fill" / "parse"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Copy file to temp location if needed
        temp_filename = f"{file_id}_{db_file.filename}"
        temp_file_path = temp_dir / temp_filename

        if file_path.exists():
            import shutil
            shutil.copy(file_path, temp_file_path)
        else:
            file_content = _file_storage.get(file_uuid)
            if file_content:
                with open(temp_file_path, "wb") as f:
                    f.write(file_content)
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"File content not found: {file_id}"
                )

        # Parse based on file type
        if file_extension == "csv":
            rows = parser_class.parse_csv(temp_file_path)
        elif file_extension in ("xlsx", "xlsm"):
            rows = parser_class.parse_excel(temp_file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        # Return first 5 rows for preview
        preview_rows = rows[:5] if rows else []

        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id,
                "filename": db_file.filename,
                "rows": preview_rows,
                "total_rows": len(rows),
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse file: {str(e)}"
        )


@app.post("/api/v1/mappings", tags=["Mappings"], status_code=201)
async def create_mapping(
    file_id: str = Query(..., min_length=1, description="ID of uploaded file"),
    template_id: str = Query(..., min_length=1, description="ID of template"),
    column_mappings: dict[str, str] = Body(default_factory=dict),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Create a column-to-placeholder mapping.

    Args:
        file_id: ID of uploaded data file
        template_id: ID of template to fill
        column_mappings: Dictionary mapping column names to placeholder names
        db: Database session

    Returns:
        JSONResponse with created mapping data

    Raises:
        HTTPException: 400 if mapping data is invalid
        HTTPException: 404 if file or template not found
    """
    from uuid import UUID as UUID_TYPE
    
    # Validate file exists in database
    try:
        file_uuid = UUID_TYPE(file_id)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_id}"
        )

    file_repo = FileRepository(db)
    db_file = file_repo.get_file_by_id(file_uuid)
    if db_file is None:
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_id}"
        )

    # Validate template exists
    template = _template_store.get_template(template_id)
    if template is None:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {template_id}"
        )

    # Create mapping in database
    try:
        mapping_repo = MappingRepository(db)
        db_mapping = mapping_repo.create_mapping(
            file_id=file_uuid,
            template_id=UUID_TYPE(template_id),
            column_mappings=column_mappings or {}
        )

        return JSONResponse(
            status_code=201,
            content={
                "message": "Mapping created successfully",
                "id": str(db_mapping.id),
                "file_id": str(db_mapping.file_id),
                "template_id": str(db_mapping.template_id),
                "column_mappings": json.loads(db_mapping.column_mappings),
                "created_at": db_mapping.created_at.isoformat() if db_mapping.created_at else None,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
