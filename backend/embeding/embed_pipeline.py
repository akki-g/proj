import logging
from typing import List, Dict, Any
from tqdm import tqdm

from config import Config
from db_manager import DatabaseManager
from data_extractor import DataExtractor
from document_builder import DocumentBuilder
from embedding_service import EmbeddingService
from vector_store import VectorStore

class EmbeddingPipeline:
    # main pipeline orchestrator 
    def __init__(self):
        self.config = Config()
        self.db_manager = DatabaseManager(self.config)
        self.extractor = DataExtractor(self.db_manager)
        self.builder = DocumentBuilder()
        self.embedding_service = EmbeddingService(self.config)
        self.vector_store = VectorStore(self.db_manager)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger(__name__)

    def process_entity_type(self, entity_name: str, extract_func: callable, build_func: callable) -> int:
        self.logger.info(f"Processing {entity_name}...")

        raw = extract_func()
        if not raw:
            self.logger.warning(f"No {entity_name} data found")
            return 0
        
        docs = []
        for rec in raw:
            doc = build_func(rec)
            docs.append(doc)

        existing_hashes = self.vector_store.get_existing_hashes()
        new_docs = [
            doc for doc in docs
            if doc['id'] not in existing_hashes or
            existing_hashes[doc['id']] != doc['content_hash']
        ]

        if not new_docs:
            self.logger.info(f"No new/changed {entity_name} doc")
            return 0
        
        self.logger.info(f"Processing {len(new_docs)} new/changed {entity_name} docs")

        texts = [doc['content_text'] for doc in new_docs]
        all_embeds = []

        for i in tqdm(range(0, len(texts), self.config.batch_size),
                      desc=f"Embedding {entity_name}"):
            batch = texts[i:i+self.config.batch_size]
            batch_embeds = self.embedding_service.embed_batch(batch)
            all_embeds.extend(batch_embeds)

        for doc, embed in zip(new_docs, all_embeds):
            doc['embedding'] = embed

        self.vector_store.upsert_documents(new_docs)

        return len(new_docs)
    
    def run(self):
        self.logger.info("Starting NBA Embedding Pipeling")

        self.logger.info("Init vector db...")
        self.db_manager.initialize_vector_tables()

        stats = {}

        stats['teams'] = self.process_entity_type(
            'teams',
            self.extractor.extract_teams,
            self.builder.build_team_document
        )

        stats['players'] = self.process_entity_type(
            'players',
            self.extractor.extract_players,
            self.builder.build_player_document
        )

        stats['games'] = self.process_entity_type(
            'games',
            self.extractor.extract_games,
            self.builder.build_game_document
        )

        stats['boxscores'] = self.process_entity_type(
            'boxscores',
            self.extractor.extract_boxscores,
            self.builder.build_boxscore_document
        )

        self.logger.info("Pipeline completed successfully")

        for entity, count in stats.items():
            self.logger.info(f"{entity}: {count} documents processed")

        return stats
    

if __name__ == "__main__":
    pipeline = EmbeddingPipeline()

    pipeline.run()
