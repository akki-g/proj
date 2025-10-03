from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import logging
from backend.embeding.config import Config

class DatabaseManager:
    def __init__(self, config: Config):
        self.config = config
        self.engine = None
        self.logger = logging.getLogger(__name__)

    def get_engine(self) -> Engine:
        if not self.engine:
            self.engine = create_engine(
                self.config.db_dsn,
                pool_pre_ping=True, # to verify conn
                pool_size=5,
                max_overflow=10
            )
        
        return self.engine
    
    @contextmanager
    def get_connection(self):
        #contect manager for db conn

        engine = self.get_engine()
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
        
    def initialize_vector_tables(self):
        """Create pgvector extension and tables"""
        ddl = """
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Unified vector table for all NBA entities
        CREATE TABLE IF NOT EXISTS nba_embeddings (
            id TEXT PRIMARY KEY,
            
            -- Entity identification
            entity_type TEXT NOT NULL,  -- 'game', 'team', 'player', 'boxscore'
            entity_id TEXT NOT NULL,     -- Original ID from source table
            
            -- Foreign keys (nullable based on entity type)
            game_id BIGINT REFERENCES games(game_id) ON DELETE CASCADE,
            team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
            player_id BIGINT REFERENCES players(player_id) ON DELETE CASCADE,
            
            -- Content
            chunk_type TEXT NOT NULL,    -- 'summary', 'stats', 'profile', etc.
            content_json JSONB NOT NULL, -- Structured data
            content_text TEXT NOT NULL,  -- Human-readable text
            
            -- Vector
            embedding vector(%(dim)s),
            
            -- Metadata
            season INTEGER,
            game_date DATE,
            
            -- Tracking
            content_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Indexes for efficient retrieval
        CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
            ON nba_embeddings USING hnsw (embedding vector_l2_ops);
        CREATE INDEX IF NOT EXISTS idx_embeddings_entity 
            ON nba_embeddings(entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_embeddings_game 
            ON nba_embeddings(game_id) WHERE game_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_embeddings_team 
            ON nba_embeddings(team_id) WHERE team_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_embeddings_player 
            ON nba_embeddings(player_id) WHERE player_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_embeddings_season 
            ON nba_embeddings(season) WHERE season IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_embeddings_date 
            ON nba_embeddings(game_date) WHERE game_date IS NOT NULL;
        """ % {"dim": self.config.embed_dim}
        
        with self.get_connection() as conn:
            conn.execute(text(ddl))
            conn.commit()