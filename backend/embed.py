import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text
from backend.config import DB_DSN, EMBED_MODEL
from backend.utils import ollama_embed

from backend.embeding.embed_pipeline import EmbeddingPipeline

# Example of a row embedding for the game_details table
# TODO: Customize this

# implemented entire pipeline under embedding/
if __name__ == "__main__":
    pipeline = EmbeddingPipeline()
    pipeline.run()