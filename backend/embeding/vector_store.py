from typing import List, Dict, Any
import logging 
from sqlalchemy import text
from db_manager import DatabaseManager
import json

class VectorStore:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def upsert_documents(self, documents: List[Dict[str, Any]]):
        # bulk upsert docs w embeds

        if not documents:
            return
        
        # sql for upsert
        upsert_sql = """
        INSERT INTO nba_embeddings (
            id, entity_type, entity_id,
            game_id, team_id, player_id,
            chunk_type, content_json, content_text,
            embeddine, content_hash,
            season, game_date
        ) VALUES (
            :id, :entity_type, :entity_id,
            :game_id, :team_id, :player_id,
            :chunk_type, :content_json, :content_text,
            :season, :game_date
        )
        ON CONFLICT (id) DO UPDATE SET
            content_json = EXCLUDED.content_json,
            content_text = EXCLUDED.content_text,
            embedding = EXCULUDED.embedding,
            content_hash = EXCLUDED.content_hash,
            updated_at = NOW()
        WHERE nba_embedding.content_hash != EXCLUDED.content_hash
        """

        with self.db.get_connection() as conn:
            # convert emb to psql arr

            for doc in documents:
                if 'embedding' in doc:
                    embedding_array = doc['embedding']
                    doc['embedding'] = embedding_array
                    doc['content_json'] = json.dumps(doc['content_json'])

            conn.execute(text(upsert_sql), documents)
            conn.commit()

        self.logger.info(f"Upserted {len(documents)} documents")



    def get_existing_hashes(self) -> Dict[str, str]:
        # get existing doc hashes for dedup

        query = """
            SELECT id, content_hash FROM nba_embeddings
        """

        with self.db.get_connection() as conn:
            res = conn.execute(text(query))
            return {row[0]: row[1] for row in res}
        
