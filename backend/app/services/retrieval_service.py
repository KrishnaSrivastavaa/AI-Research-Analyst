from app.core.qdrant_client import qdrant_client
from app.core.configs import settings
from qdrant_client import models
from fastembed import TextEmbedding, SparseTextEmbedding


async def retrieve_documents(query: str, owner_id: str, document_ids: list[int]):

    dense_model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
    
    sparse_model = SparseTextEmbedding(
        model_name="Qdrant/bm25"
    )
    dense_query_vector = next(dense_model.embed([query]))
    sparse_embedding = next(sparse_model.embed([query]))

    sparse_query_vector = models.SparseVector(
    indices=sparse_embedding.indices.tolist(),
    values=sparse_embedding.values.tolist(),
    )

    results =  qdrant_client.query_points(
                    collection_name = settings.collection_name,
                    prefetch = [
                        models.Prefetch(
                                query = dense_query_vector,
                                using="dense",
                                limit=20,
                        ),
                        models.Prefetch(
                            query=sparse_query_vector,
                            using="sparse",
                            limit=20,
                        )
                    ],

                    query=models.FusionQuery(
                        fusion=models.Fusion.RRF
                    ),

                    query_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="owner_id",
                                match=models.MatchValue(
                                    value=str(owner_id)
                                ),
                            ),
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchAny(
                                    any=document_ids
                                ),
                            ),
                        ]
                    ),
                    limit=10,
                    with_payload=True,
                )
    retrieved_chunks = [
    {
        "chunk_id": point.payload["chunk_id"],
        "document_id": point.payload["document_id"],
        "page_start": point.payload["page_start"],
        "page_end": point.payload["page_end"],
        "text": point.payload["text"],
        "score": point.score,
    }
    for point in results.points
    ]
    return retrieved_chunks