from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str
    neo4j_database: str
    embedding_model: str
    embedding_dimension: int
    openai_api_key: str

    class Config:
        env_file = ".env"
