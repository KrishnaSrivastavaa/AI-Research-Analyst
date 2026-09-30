import asyncio

from qdrant_client import models


from app.core.configs import settings
from app.core.qdrant_client import qdrant_client


async def setup_qdrant():

    collection_name = settings.collection_name

    exists = qdrant_client.collection_exists(
        collection_name=collection_name
    )

    if not exists:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams()
            },
        )

        print(f"Collection '{collection_name}' created successfully.")

    else:
        print(f"Collection '{collection_name}' already exists.")

    # Get current collection configuration
    collection_info = qdrant_client.get_collection(
        collection_name=collection_name
    )

    payload_schema = collection_info.payload_schema

    # document_id index
    if "document_id" not in payload_schema:
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.INTEGER,
        )
        print("Created payload index: document_id")
    else:
        print("Payload index already exists: document_id")

    # owner_id index
    if "owner_id" not in payload_schema:
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="owner_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print("Created payload index: owner_id")
    else:
        print("Payload index already exists: owner_id")

if __name__ == "__main__":
    asyncio.run(setup_qdrant())