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
    sparse_query_vector = next(sparse_model.embed([query]))

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
    