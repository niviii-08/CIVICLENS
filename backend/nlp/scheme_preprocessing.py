import json
import logging
from typing import Dict, Any, List, Optional
from backend.nlp.preprocessing import normalize_whitespace, normalize_unicode
import re

logger = logging.getLogger(__name__)

SCHEME_PREPROCESSING_CONFIG = {
    "fields_to_include": [
        "scheme_name",
        "sector_category", 
        "description",
        "objectives",
        "target_beneficiaries"
    ],
    "normalize_unicode": True,
    "lowercase": True,
    "clean_artifacts": True,
    "fallback_fields": ["scheme_name", "department_name"]
}

class SchemeTextPreprocessor:
    """
    Prepares Historical Scheme data for semantic similarity analysis.
    Constructs a unified text representation by intelligently joining selected fields,
    cleaning extraction artifacts, and normalizing text while preserving domain terminology.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or SCHEME_PREPROCESSING_CONFIG

    def _clean_artifacts(self, text: str) -> str:
        """Removes common PDF extraction artifacts without damaging real content."""
        if not text:
            return ""
        cleaned = re.sub(r'\(cid:\d+\)', '', text)
        cleaned = cleaned.replace('\x00', '')
        cleaned = re.sub(r'\.{2,}', ' ', cleaned)
        cleaned = re.sub(r'-{2,}', ' ', cleaned)
        return cleaned

    def generate_semantic_text(self, scheme_data: Dict[str, Any]) -> str:
        """
        Combines and processes scheme data into a single string optimized for embeddings.
        Avoids stopword removal to preserve sentence structure for Transformer models.
        """
        parts = []

        for field in self.config.get("fields_to_include", []):
            val = scheme_data.get(field)
            if val and isinstance(val, str) and val.strip():
                parts.append(val.strip())

        if not parts:
            for field in self.config.get("fallback_fields", []):
                val = scheme_data.get(field)
                if val and isinstance(val, str) and val.strip():
                    parts.append(val.strip())

        combined_text = " . ".join(parts)

        if not combined_text:
            return ""

        if self.config.get("clean_artifacts"):
            combined_text = self._clean_artifacts(combined_text)

        if self.config.get("normalize_unicode"):
            combined_text = normalize_unicode(combined_text)

        combined_text = normalize_whitespace(combined_text)

        if self.config.get("lowercase"):
            combined_text = combined_text.lower()

        return combined_text

    def process_record(self, scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a raw/DB scheme dictionary and returns a new dictionary 
        containing the original data PLUS the 'semantic_text' field.
        This preserves the original text separately from processed text.
        """
        processed = scheme_data.copy()

        semantic_text = self.generate_semantic_text(scheme_data)
        processed["semantic_text"] = semantic_text
        processed["nlp_config_version"] = "1.0"

        return processed

    def save_config(self, filepath: str = "config/nlp_scheme_preprocessing.json"):
        """Stores preprocessing configuration."""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=4)

