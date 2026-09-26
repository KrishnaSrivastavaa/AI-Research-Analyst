from typing import List
from fastembed import TextEmbedding, SparseTextEmbedding
from qdrant_client.models import PointStruct, SparseVector
from app.core.qdrant_client import qdrant_client
from app.core.configs import settings

async def store_embeddings(chunks: List, owner_id):

    dense_model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    sparse_model = SparseTextEmbedding(
        model_name="Qdrant/bm25"
    )

    points = []

    for chunk in chunks:
        dense_vector = next(dense_model.embed([chunk.content]))
        sparse_vector = next(sparse_model.embed([chunk.content]))

        points.append(
            PointStruct(
                id=chunk.id,
                vector={
                    "dense": dense_vector,
                    "sparse": SparseVector(
                        indices=sparse_vector.indices.tolist(),
                        values=sparse_vector.values.tolist(),
                    ),
                },
                payload={
                    "chunk_id": chunk.id,
                    "owner_id" : str(owner_id),
                    "document_id": chunk.doc_id,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "text": chunk.content,
                    "metadata": chunk.chunk_metadata,
                }
            )
        )

    qdrant_client.upsert(
        collection_name=settings.collection_name,
        points=points
    )


    