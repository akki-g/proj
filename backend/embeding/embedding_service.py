import requests
import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from backend.embeding.config import Config

class EmbeddingService:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # start sess w conn pooling
        self.session = requests.Session()
        retry_strat = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strat,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    
    def _embed_single(self, text: str) -> Optional[List[float]]:
        # gen embedding for single text

        try:
            res = self.session.post(
                self.config.embedding_endpoint,
                json={
                    "model": self.config.embed_model,
                    "prompt": text
                },
                timeout=30
            )
            res.raise_for_status()
            return res.json()["embedding"]
        except Exception as e:
            self.logger.error(f"Embedding Failed: {e}")
            print(f"Embedding failed: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = [None] * len(texts)

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_idx = {
                executor.submit(self._embed_single, text): idx 
                for idx, text in enumerate(texts)
            }
            
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    embedding = future.result()
                    if embedding and len(embedding) == self.config.embed_dim:
                        embeddings[idx] = embedding
                    else:
                        # retry again
                        self.logger.warning(f"Retrying embedding {idx}")
                        embeddings[idx] = self._embed_single(texts[idx])
                except Exception as e:
                    self.logger.error(f"Failed to embed text {idx}: {e}")
                    raise
        
        if any(e is None for e in embeddings):
            failed = [i for i, e in enumerate(embeddings) if e is None]
            raise ValueError(f"Failed to generate embeddings for indicies: {failed}")


        return embeddings
