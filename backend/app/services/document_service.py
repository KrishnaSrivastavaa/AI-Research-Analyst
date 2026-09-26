from typing import List

from fastapi import Depends
import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastembed import TextEmbedding
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Chunk
from app.core.database import get_db

async def process_pdf(content: bytes, doc_id: int, db: AsyncSession):
    doc = pymupdf.open(
        stream=content,
        filetype="pdf"
    )

    

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False
    )

    chunks = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()
        text = text.replace("\x00", "")
        page_chunks = text_splitter.split_text(text)

        for chunk in page_chunks:
            

            chunk = Chunk(
                doc_id = doc_id,
                chunk_index = len(chunks) - 1,
                content = chunk,
                page_start = page_number,
                page_end = page_number,
                chunk_metadata = {
                    "chunk_type": "text"
                }
            )

            chunks.append(chunk)

    db.add_all(chunks)
    await db.flush()

    return chunks  




