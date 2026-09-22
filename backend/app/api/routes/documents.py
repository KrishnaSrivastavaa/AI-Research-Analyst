from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.dependencies.auth_dependency import get_current_user
from supabase import create_client
from app.core.configs import settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.models.models import Doc

import hashlib
import fitz

supabase = create_client(settings.supabase_url, settings.supabase_key)

router = APIRouter()


@router.post("/documents")
async def get_documents(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    return {
        "message" : "Authentication successful",
        "user": current_user["user_metadata"]["name"],
        "file" : file
    }


@router.post("/upload")
async def upload_file(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    contents = await file.read()

    size_bytes = len(contents)

    content_hash = hashlib.sha256(contents).hexdigest()

    pdf = fitz.open(stream=contents, filetype="pdf")

    page_count = len(pdf)


    doc = Doc(
        owner_id = current_user["sub"],
        doc_name = file.filename,
        file_path="",
        mime_type = file.content_type,
        size_bytes=size_bytes,
        page_count = page_count,
        content_hash = content_hash,
        status="processing"
    )
    try: 
        db.add(doc)

        await db.flush()

        storage_path = f"{current_user['sub']}/{doc.id}.pdf"

        doc.file_path = storage_path

        response = (
            supabase.storage
            .from_("AI_Research_analyst_file_bucket")
            .upload(
                path=storage_path,
                file=contents,
                file_options={
                    "content-type": "application/pdf"
                }
            )
        )

        await db.commit() 
    except Exception:
        await db.rollback()
        raise

