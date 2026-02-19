#!/usr/bin/env python3
"""
Test script to verify the upload and parse fixes.
"""

import io
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_upload_and_parse():
    """Test file upload and parse workflow."""
    print("=" * 60)
    print("Testing Upload and Parse")
    print("=" * 60)
    
    # Test 1: Upload CSV file
    print("\n1. Uploading CSV file...")
    csv_content = b"Name,Email,Phone\nJohn,john@test.com,555-1234\nJane,jane@test.com,555-5678"
    
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test_data.csv", io.BytesIO(csv_content), "text/csv")}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 201:
        print(f"   ERROR: {response.text}")
        return False
    
    data = response.json()
    file_id = data["file_id"]
    print(f"   File ID: {file_id}")
    
    # Test 2: List files
    print("\n2. Listing files...")
    response = client.get("/api/v1/files")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return False
    
    files_data = response.json()
    print(f"   Total files: {files_data['total']}")
    file_ids = [f["file_id"] for f in files_data['files']]
    
    if file_id in file_ids:
        print("   [OK] File found in list")
    else:
        print("   [FAIL] File NOT found in list")
        print(f"   Available IDs: {file_ids}")
        return False
    
    # Test 3: Parse file
    print("\n3. Parsing file...")
    response = client.get(f"/api/v1/parse/{file_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return False
    
    parse_data = response.json()
    print(f"   Filename: {parse_data['filename']}")
    print(f"   Total rows: {parse_data['total_rows']}")
    print(f"   Preview rows: {len(parse_data['rows'])}")
    
    if parse_data['total_rows'] == 2:
        print("   [OK] Parse successful")
    else:
        print("   [FAIL] Parse returned wrong row count")
        return False
    
    return True

def test_template_upload():
    """Test template upload."""
    print("\n" + "=" * 60)
    print("Testing Template Upload")
    print("=" * 60)
    
    # Test upload text template
    print("\n1. Uploading text template...")
    template_content = b"Hello {{name}}, your order {{order_id}} is ready."
    
    response = client.post(
        "/api/v1/templates/upload",
        files={"file": ("template.txt", io.BytesIO(template_content), "text/plain")},
        data={"name": "Test Template", "description": "Test template"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 201:
        print(f"   ERROR: {response.text}")
        return False
    
    data = response.json()
    template_id = data['template']['id']
    placeholders = data['template']['placeholders']
    
    print(f"   Template ID: {template_id}")
    print(f"   Placeholders: {placeholders}")
    
    if 'name' in placeholders and 'order_id' in placeholders:
        print("   [OK] Placeholders extracted correctly")
    else:
        print("   [FAIL] Placeholders not extracted correctly")
        return False
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Fill Application - Fix Verification")
    print("=" * 60 + "\n")
    
    success = True
    
    try:
        if not test_upload_and_parse():
            success = False
    except Exception as e:
        print(f"\n✗ Upload/Parse test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    try:
        if not test_template_upload():
            success = False
    except Exception as e:
        print(f"\n✗ Template upload test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAIL] Some tests failed")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)
