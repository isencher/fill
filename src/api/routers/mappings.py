"""
Mappings API router.

Handles mapping suggestions, mapping creation, and file parsing.
"""

import json
import tempfile
import shutil
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.api.dependencies import file_storage, template_store, database
from src.models.mapping import Mapping
from src.repositories.file_repository import FileRepository
from src.repositories.mapping_repository import MappingRepository
from src.services import get_parser
from src.services.fuzzy_matcher import FuzzyMatcher


# Create router
router = APIRouter(prefix="/api/v1", tags=["Mappings", "Parsing"])


@router.post("/mappings/suggest")
async def suggest_mapping(
    file_id: str = Query(..., description="ID of uploaded data file"),
    template_id: str = Query(..., description="ID of template"),
    db: Session = Depends(database),
    storage=Depends(file_storage),
    store=Depends(template_store),
) -> JSONResponse:
    """
    Suggest column-to-placeholder mappings based on fuzzy matching.

    Args:
        file_id: ID of uploaded data file
        template_id: ID of template
        db: Database session
        storage: File storage service
        store: Template store service

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

    # Check if file content exists in storage
    file_content = storage.get(file_uuid)
    if not file_content:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    # Validate template exists
    template = store.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")

    # Parse file to get column names
    file_repo = FileRepository(db)
    db_file = file_repo.get_file_by_id(file_uuid)
    if db_file is None:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    try:
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


@router.post("/mappings", status_code=201)
async def create_mapping(
    file_id: str = Query(..., min_length=1, description="ID of uploaded file"),
    template_id: str = Query(..., min_length=1, description="ID of template"),
    column_mappings: dict[str, str] = Body(default_factory=dict),
    db: Session = Depends(database),
    store=Depends(template_store),
) -> JSONResponse:
    """
    Create a column-to-placeholder mapping.

    Args:
        file_id: ID of uploaded data file
        template_id: ID of template to fill
        column_mappings: Dictionary mapping column names to placeholder names
        db: Database session
        store: Template store service

    Returns:
        JSONResponse with created mapping data

    Raises:
        HTTPException: 400 if mapping data is invalid
        HTTPException: 404 if file or template not found
    """
    # Validate file exists in database
    try:
        file_uuid = UUID(file_id)
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
    template = store.get_template(template_id)
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
            template_id=UUID(template_id),
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


@router.get("/parse/{file_id}")
async def parse_file(
    file_id: str,
    db: Session = Depends(database),
    storage=Depends(file_storage),
) -> JSONResponse:
    """
    Parse uploaded file and return data preview (first 5 rows).

    Args:
        file_id: ID of uploaded file to parse
        db: Database session
        storage: File storage service

    Returns:
        JSONResponse with parsed data (rows and columns)

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 400 if file cannot be parsed
    """
    # Convert string ID to UUID for lookup
    try:
        file_uuid = UUID(file_id)
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
        file_content = storage.get(file_uuid)
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
            shutil.copy(file_path, temp_file_path)
        else:
            file_content = storage.get(file_uuid)
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
