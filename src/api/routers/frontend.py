"""
Frontend API router.

Handles serving of HTML pages and static frontend assets.
"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


# Create router
router = APIRouter(tags=["Frontend", "Health"])

# Get static directory path
static_dir = Path(__file__).parent.parent.parent / "static"
static_dir.mkdir(exist_ok=True)


@router.get("/")
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


@router.get("/mapping")
async def mapping_page() -> FileResponse:
    """
    Mapping page - serves column-to-placeholder mapping interface.

    Returns:
        FileResponse with HTML mapping page
    """
    mapping_path = static_dir / "mapping.html"
    return FileResponse(mapping_path)


@router.get("/templates.html")
async def templates_page() -> FileResponse:
    """
    Template selection page - serves template selection interface.

    Returns:
        FileResponse with HTML template selection page
    """
    templates_path = static_dir / "templates.html"
    return FileResponse(templates_path)


@router.get("/mapping.html")
async def mapping_html_page() -> FileResponse:
    """
    Mapping page - serves column-to-placeholder mapping interface.

    Returns:
        FileResponse with HTML mapping page
    """
    mapping_path = static_dir / "mapping.html"
    return FileResponse(mapping_path)
