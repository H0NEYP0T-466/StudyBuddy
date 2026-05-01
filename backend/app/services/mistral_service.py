import os
import base64
import numpy as np
from typing import List
from mistralai import Mistral
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("MISTRAL")


class MistralService:
    def __init__(self):
        self.api_key = settings.mistral_api_key
        if self.api_key:
            self.client = Mistral(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("MISTRAL_API_KEY not set — Mistral services will be unavailable")

    # ------------------------------------------------------------------ #
    #  Embeddings (for RAG)
    # ------------------------------------------------------------------ #
    async def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using mistral-embed-2312.

        Args:
            texts: List of text strings to embed.

        Returns:
            numpy array of shape (len(texts), 1024).
        """
        if not self.client:
            raise RuntimeError("Mistral client not initialised (missing API key)")

        # Mistral embed API accepts up to ~16 k tokens per batch.
        # We chunk into batches of 25 to stay well within limits.
        BATCH_SIZE = 25
        all_embeddings = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]
            response = self.client.embeddings.create(
                model="mistral-embed-2312",
                inputs=batch,
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return np.array(all_embeddings, dtype="float32")

    # ------------------------------------------------------------------ #
    #  OCR (for notes / pen2pdf)
    # ------------------------------------------------------------------ #
    def ocr_extract(self, file_path: str) -> str:
        """Extract text from a file (PDF or image) using Mistral OCR.

        Args:
            file_path: Absolute or relative path to the file.

        Returns:
            Extracted markdown text.
        """
        if not self.client:
            raise RuntimeError("Mistral client not initialised (missing API key)")

        ext = os.path.splitext(file_path)[1].lower()

        # Encode file
        with open(file_path, "rb") as f:
            base64_file = base64.b64encode(f.read()).decode("utf-8")

        # Determine document / image type
        if ext == ".pdf":
            document_type = "document_url"
            mime_type = "application/pdf"
        else:
            document_type = "image_url"
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
            }
            mime_type = mime_map.get(ext, "image/jpeg")

        logger.info(f"Running Mistral OCR on {os.path.basename(file_path)} ({mime_type})")

        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": document_type,
                f"{document_type}": f"data:{mime_type};base64,{base64_file}",
            },
            table_format="html",
            include_image_base64=False,
        )

        text = "\n\n".join([page.markdown for page in ocr_response.pages])
        logger.success(f"OCR extracted {len(text)} characters from {os.path.basename(file_path)}")
        return text


# Global singleton
mistral_service = MistralService()
