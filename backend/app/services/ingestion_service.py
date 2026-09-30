from typing import List
from fastembed import TextEmbedding, SparseTextEmbedding
from qdrant_client.models import PointStruct, SparseVector, Filter, FieldCondition, MatchValue
from app.core.qdrant_client import qdrant_client
from app.core.configs import settings

async def store_embeddings(chunks: List, owner_id):

    dense_model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    sparse_model = SparseTextEmbedding(
        model_name="Qdrant/bm25"
    )

    batch_size = 100

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start:start + batch_size]

        points = []

        for chunk in batch:

            dense_vector = next(
                dense_model.embed([chunk.content])
            )

            sparse_vector = next(
                sparse_model.embed([chunk.content])
            )

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
                        "owner_id": str(owner_id),
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

        print(
            f"Uploaded Qdrant batch: "
            f"{start} - {start + len(batch) - 1}"
        )


async def delete_document_vectors(document_id: int):
    qdrant_client.delete(
        collection_name=settings.collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )