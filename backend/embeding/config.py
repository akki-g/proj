import os
from dataclasses import dataclass
from typing import Optional
# config for embed specifically 
@dataclass
class Config:
    # Database
    db_dsn: str = os.getenv("DB_DSN", "postgresql://nba:nba@db:5432/nba")
    
    # Ollama
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    embed_model: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
    embed_dim: int = 768  # nomic-embed-text dimension
    
    # Processing
    batch_size: int = 128  # Records per batch
    max_workers: int = 10  # Parallel embedding workers
    
    # Retry logic
    max_retries: int = 3
    retry_delay: float = 1.0
    
    @property
    def embedding_endpoint(self) -> str:
        return f"{self.ollama_host}/api/embeddings"