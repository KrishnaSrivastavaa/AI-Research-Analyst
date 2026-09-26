from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str 
    supabase_url: str
    supabase_key: str
    qdrant_api_key: str
    qdrant_url: str
    collection_name: str

    model_config = SettingsConfigDict(
        env_file=".env",

    )

settings = Settings()