"""
Outputs API router.

Handles file download operations including ZIP and single file downloads.
"""

import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.dependencies import output_storage


# Create router
router = APIRouter(prefix="/api/v1/outputs", tags=["Outputs"])


@router.get("/{job_id}")
async def download_job_outputs(
    job_id: str,
    storage=Depends(output_storage),
) -> StreamingResponse:
    """
    Download all outputs for a job as a ZIP file.

    Args:
        job_id: Job identifier
        storage: Output storage service

    Returns:
        StreamingResponse with ZIP file containing all outputs

    Raises:
        HTTPException: 404 if job not found
    """
    # Check if job exists
    if not storage.job_exists(job_id):
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    # Get all outputs for the job
    outputs = storage.get_job_outputs(job_id)

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


@router.get("/{job_id}/{filename}")
async def download_single_output(
    job_id: str,
    filename: str,
    storage=Depends(output_storage),
) -> StreamingResponse:
    """
    Download a single output file.

    Args:
        job_id: Job identifier
        filename: Name of the file to download
        storage: Output storage service

    Returns:
        StreamingResponse with file content

    Raises:
        HTTPException: 404 if job or file not found
    """
    # Check if job exists
    if not storage.job_exists(job_id):
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    # Get specific file
    content = storage.get_output(job_id, filename)

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
