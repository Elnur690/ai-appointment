import asyncio
import logging
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generates text embeddings using Google Gemini's text-embedding-004 model."""
    
    MODEL = "text-embedding-004"
    DIMENSIONS = 768
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    async def generate_embedding(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT",
        max_retries: int = 3,
    ) -> list[float]:
        """Generate embedding for a single text.
        
        Args:
            text: The text to embed
            task_type: "RETRIEVAL_DOCUMENT" for storage, "RETRIEVAL_QUERY" for search queries
            max_retries: Number of retries on rate limit errors
        """
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.embed_content(
                    model=self.MODEL,
                    contents=text,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.DIMENSIONS,
                        task_type=task_type,
                    )
                )
                return response.embeddings[0].values
            except APIError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    wait = (2 ** attempt) + 1
                    logger.warning(f"Embedding rate limited, retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    logger.error(f"Embedding API error: {e}")
                    raise
    
    async def generate_batch_embeddings(
        self,
        texts: list[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts in a single API call."""
        try:
            response = await self.client.aio.models.embed_content(
                model=self.MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.DIMENSIONS,
                    task_type=task_type,
                )
            )
            return [emb.values for emb in response.embeddings]
        except APIError as e:
            logger.error(f"Batch embedding API error: {e}")
            raise
    
    def prepare_correction_text(self, question: str, correct_answer: str, ai_mistake: str | None = None) -> str:
        """Prepare text for embedding a correction entry.
        Combines the question context with the correct answer for semantic matching."""
        parts = [f"Customer question/situation: {question}", f"Correct response: {correct_answer}"]
        if ai_mistake:
            parts.append(f"Previous incorrect response: {ai_mistake}")
        return "\n".join(parts)
    
    def prepare_faq_text(self, question: str, answer: str) -> str:
        """Prepare text for embedding a FAQ entry."""
        return f"Question: {question}\nAnswer: {answer}"
    
    def prepare_query_text(self, customer_message: str) -> str:
        """Prepare customer message text for similarity search."""
        return f"Customer message: {customer_message}"
