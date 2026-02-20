"""
Templates API router.

Handles template CRUD operations and file upload.
"""

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File as FastAPIFile, Form, Query, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.api.dependencies import template_store, database, validate_uuid
from src.models.template import Template
from src.services.placeholder_parser import PlaceholderParser


# Create router
router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])


@router.post("", status_code=201)
async def create_template(
    name: str = Query(..., min_length=1, max_length=200, description="Template name"),
    file_path: str = Query(..., min_length=1, description="Template file path"),
    description: Optional[str] = Query(None, max_length=1000, description="Template description"),
    placeholders: Optional[str] = Query(None, description="Comma-separated placeholder names"),
    store=Depends(template_store),
) -> JSONResponse:
    """
    Create a new template.

    Args:
        name: Template name
        file_path: Path to template file
        description: Optional template description
        placeholders: Optional comma-separated list of placeholder names
        store: Template store service

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
        saved = store.save_template(template)

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


@router.post("/upload", status_code=201)
async def upload_template(
    file: UploadFile = FastAPIFile(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    store=Depends(template_store),
) -> JSONResponse:
    """
    Upload a template file and automatically extract placeholders.

    Args:
        file: Template file (.docx or .txt)
        name: Template name
        description: Optional template description
        store: Template store service

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
    saved = store.save_template(template)

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


@router.get("")
async def list_templates(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip"),
    sort_by: str = Query("created_at", description="Field to sort by (name, created_at)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    store=Depends(template_store),
) -> JSONResponse:
    """
    List all templates with pagination and sorting.

    Args:
        limit: Maximum number of templates to return (1-1000)
        offset: Number of templates to skip for pagination
        sort_by: Field to sort by (name, created_at)
        order: Sort order (asc, desc)
        store: Template store service

    Returns:
        JSONResponse with list of templates and pagination metadata

    Raises:
        HTTPException: 400 if pagination parameters are invalid
    """
    try:
        templates = store.list_templates(
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

        total_count = store.count_templates()

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


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    store=Depends(template_store),
) -> JSONResponse:
    """
    Get a template by ID.

    Args:
        template_id: UUID of template to retrieve
        store: Template store service

    Returns:
        JSONResponse with template data

    Raises:
        HTTPException: 404 if template not found
    """
    # Validate UUID format
    await validate_uuid(template_id, "template ID")

    template = store.get_template(template_id)

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


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    name: Optional[str] = Query(None, min_length=1, max_length=200, description="Template name"),
    file_path: Optional[str] = Query(None, min_length=1, description="Template file path"),
    description: Optional[str] = Query(None, max_length=1000, description="Template description"),
    placeholders: Optional[str] = Query(None, description="Comma-separated placeholder names"),
    store=Depends(template_store),
) -> JSONResponse:
    """
    Update a template by ID.

    Args:
        template_id: UUID of template to update
        name: Optional new template name
        file_path: Optional new template file path
        description: Optional new template description
        placeholders: Optional new comma-separated placeholder names
        store: Template store service

    Returns:
        JSONResponse with updated template data

    Raises:
        HTTPException: 404 if template not found
        HTTPException: 400 if update data is invalid
    """
    # Validate UUID format
    await validate_uuid(template_id, "template ID")

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
        template = store.update_template(template_id, **updates)

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


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    store=Depends(template_store),
) -> JSONResponse:
    """
    Delete a template by ID.

    Args:
        template_id: UUID of template to delete
        store: Template store service

    Returns:
        JSONResponse with deletion confirmation

    Raises:
        HTTPException: 404 if template not found
    """
    # Validate UUID format
    await validate_uuid(template_id, "template ID")

    deleted = store.delete_template(template_id)

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
