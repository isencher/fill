"""
Template management routes.

Handles template CRUD operations and upload.
"""

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile as FastAPIUploadFile
from fastapi.responses import JSONResponse

from src.models.template import Template
from src.services.placeholder_parser import PlaceholderParser
from src.services.template_store import get_template_store

router = APIRouter(tags=["Templates"])

# Template store
_template_store = get_template_store()


@router.post("/api/v1/templates", status_code=201)
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


@router.post("/api/v1/templates/upload", status_code=201)
async def upload_template(
    file: FastAPIUploadFile = Query(...),
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


@router.get("/api/v1/templates")
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


@router.get("/api/v1/templates/{template_id}")
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


@router.put("/api/v1/templates/{template_id}")
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


@router.delete("/api/v1/templates/{template_id}")
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
