"""Simple upload API that forwards uploaded file to existing CLI (app.py)

This endpoint writes the upload to a temporary file and runs the existing
`app.py --input <tmpfile> [--pixel <pixel>] [--dry-run]` as a subprocess.
It intentionally does not change your backend logic; it only provides a
small HTTP wrapper the frontend can call.
"""
import os
import sys
import tempfile
import shutil
import subprocess
import logging
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gtm-upload-api")

app = FastAPI(title="GTM Automate Upload API")

# Allow local frontend dev origins — tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Project root (one level above this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.post("/upload")
async def upload(
    pixel: str = Form(None),
    container_id: str = Form(None),
    template_type: str = Form(None),
    file: UploadFile = File(...),
    dry_run: bool = Form(False),
):
    """Accepts multipart upload, saves to a temp file, runs existing CLI.

    Request fields:
    - pixel: optional string (frontend sends pixel selection)
    - container_id: optional string (numeric containerId or GTM-XXXX public ID)
      - file: uploaded file (.json/.xlsx/.xml)
      - dry_run: optional flag (frontend may send)

    Response: JSON with CLI stdout/stderr and exit code.
    """
    # Create temporary file with same extension
    suffix = os.path.splitext(file.filename)[1] or ""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = tmp.name

    try:
        # Write uploaded bytes to temp file
        with tmp as f:
            shutil.copyfileobj(file.file, f)
        logger.info("Saved uploaded file to %s", tmp_path)


        # Build command to run existing CLI `app.py` (add template_type)
        cmd = [sys.executable, "app.py", "--input", tmp_path]
        if container_id:
            cmd += ["--container-id", container_id]
        if template_type:
            cmd += ["--template-type", template_type]
        if dry_run:
            cmd += ["--dry-run"]

        # Ensure CLI runs from project root where app.py lives
        cwd = str(PROJECT_ROOT)
        logger.info("Running CLI: %s (cwd=%s)", " ".join(cmd), cwd)

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=1200,  # 20 minutes max (adjust if needed)
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        stdout_lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        stderr_lines = [line.strip() for line in stderr.splitlines() if line.strip()]

        # Derive a short, user-friendly message for the UI
        status = "SUCCESS" if proc.returncode == 0 else "FAILED"
        message = "Uploaded and processed successfully."
        error_code = None
        error_detail = None

        if proc.returncode != 0:
            # Look for specific known errors and map them to friendly messages
            full_output = stdout + "\n" + stderr

            if "No GTM container ID provided" in full_output:
                error_code = "MISSING_CONTAINER_ID"
                message = "Container ID is missing. Please enter a valid container ID."
            elif "Could not find GTM container matching identifier" in full_output:
                error_code = "CONTAINER_NOT_FOUND"
                message = "Cannot find this container. Check the container ID and service account access."
            elif "Authentication failed" in full_output:
                error_code = "AUTH_FAILED"
                message = "Authentication failed. Check service account credentials and permissions."
            elif "vendorTemplate.key: Unknown entity type" in full_output:
                error_code = "UNKNOWN_TEMPLATE"
                message = "Some tags use a custom template (e.g. Bing) that is not installed in this container."
            else:
                error_code = "UNKNOWN_ERROR"
                # Take only the last non-empty line as a brief detail
                lines = [l for l in full_output.splitlines() if l.strip()]
                error_detail = lines[-1] if lines else None
                message = error_detail or "Processing failed. Please check logs."

            status = "FAILED"

        result = {
            "status": status,
            "message": message,
            "errorCode": error_code,
            # Return step-by-step output so the UI can display real progress
            "steps": stdout_lines,
            "stderr": stderr_lines,
        }

        status_code = 200 if proc.returncode == 0 else 400
        return JSONResponse(result, status_code=status_code)

    except subprocess.TimeoutExpired:
        logger.exception("Processing timed out")
        return JSONResponse({"error": "Processing timed out"}, status_code=504)
    except Exception as e:
        logger.exception("Upload processing failed")
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass