import asyncio

from qdrant_client import models

from app.core.qdrant_client import qdrant_client
from app.core.configs import settings


async def setup_qdrant():

    exists =  qdrant_client.collection_exists(
        collection_name=settings.collection_name
    )

    if exists:
        print(f"Collection '{settings.collection_name}' already exists.")
        return

    await qdrant_client.create_collection(
        collection_name=settings.collection_name,
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

    print(f"Collection '{settings.collection_name}' created successfully.")


if __name__ == "__main__":
    asyncio.run(setup_qdrant())