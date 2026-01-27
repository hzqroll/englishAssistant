"""
Text preprocessing module.

This module handles first stage of text correction pipeline:
sentence splitting, speaker detection, and Chinese character detection.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re
import nltk
from nltk.tokenize import sent_tokenize


@dataclass
class Message:
    """
    Represents a single message or sentence in text.

    Attributes:
        text: The message/sentence text
        speaker: Detected speaker (for dialogues) or None
        has_chinese: Whether message contains Chinese characters
        start_index: Start position in original text
        end_index: End position in original text
        metadata: Additional metadata
    """

    text: str
    speaker: Optional[str]
    has_chinese: bool
    start_index: int
    end_index: int
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PreprocessedText:
    """
    Result of text preprocessing.

    Attributes:
        messages: List of processed messages/sentences
        original_text: The original input text
        is_dialogue: Whether text is detected as dialogue
        speaker_count: Number of detected speakers
        chinese_ratio: Ratio of Chinese characters to total
        metadata: Additional preprocessing metadata
    """

    messages: List[Message]
    original_text: str
    is_dialogue: bool
    speaker_count: int
    chinese_ratio: float
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}


class Preprocessor:
    """
    Text preprocessor for analysis pipeline.

    Handles sentence splitting, speaker detection, and Chinese
    character detection as first stage of correction pipeline.

    Attributes:
        sentence_split_pattern: Regex pattern for splitting sentences
        chinese_char_pattern: Regex pattern for Chinese characters
        speaker_pattern: Regex pattern for detecting speakers
    """

    def __init__(self):
        """Initialize preprocessor with default patterns."""
        self.sentence_split_pattern = re.compile(r"[.!?]+\s+")
        self.chinese_char_pattern = re.compile(r"[\u4e00-\u9fff]")
        self.speaker_pattern = re.compile(r"^([A-Z][a-z]+):\s*")

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

    def preprocess(self, text: str) -> PreprocessedText:
        """
        Preprocess input text.

        Performs sentence splitting, speaker detection, and Chinese
        character detection.

        Args:
            text: Input text to preprocess

        Returns:
            PreprocessedText object with analysis results

        Example:
            ```python
            preprocessor = Preprocessor()
            result = preprocessor.preprocess("Hello world. How are you?")
            assert len(result.messages) == 2
            ```
        """
        messages = self._split_sentences(text)
        speakers = self._detect_speakers(messages)
        chinese_info = self._detect_chinese(text)

        is_dialogue = self._is_dialogue(speakers)
        speaker_count = len(set(speakers)) if speakers else 0

        processed_messages = []
        current_pos = 0
        for i, msg in enumerate(messages):
            speaker = speakers[i] if i < len(speakers) else None
            has_chinese = self._detect_chinese(msg)["has_chinese"]

            msg_start = text.find(msg, current_pos)
            msg_end = msg_start + len(msg)

            processed_messages.append(
                Message(
                    text=msg,
                    speaker=speaker,
                    has_chinese=has_chinese,
                    start_index=msg_start,
                    end_index=msg_end,
                    metadata={},
                )
            )
            current_pos = msg_end

        return PreprocessedText(
            messages=processed_messages,
            original_text=text,
            is_dialogue=is_dialogue,
            speaker_count=speaker_count,
            chinese_ratio=chinese_info["ratio"],
            metadata={
                "total_chinese_chars": len(chinese_info["chinese_chars"]),
                "detected_speakers": list(set(speakers)) if speakers else [],
            },
        )

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using NLTK.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]

    def _detect_speakers(self, sentences: List[str]) -> List[Optional[str]]:
        """
        Detect speakers in dialogue format.

        Args:
            sentences: List of sentences

        Returns:
            List of speakers (None for non-dialogue)
        """
        speakers = []
        for sentence in sentences:
            match = self.speaker_pattern.match(sentence)
            speakers.append(match.group(1) if match else None)
        return speakers

    def _detect_chinese(self, text: str) -> Dict[str, Any]:
        """
        Detect Chinese characters in text.

        Args:
            text: Input text

        Returns:
            Dictionary with detection results
        """
        chinese_chars = self.chinese_char_pattern.findall(text)
        has_chinese = len(chinese_chars) > 0
        ratio = len(chinese_chars) / len(text) if text else 0.0

        return {"has_chinese": has_chinese, "ratio": ratio, "chinese_chars": chinese_chars}

    def _is_dialogue(self, speakers: List[Optional[str]]) -> bool:
        """
        Determine if text is in dialogue format.

        Args:
            speakers: List of detected speakers

        Returns:
            True if dialogue format detected
        """
        detected_speakers = [s for s in speakers if s is not None]

        if len(detected_speakers) == 0:
            return False

        if len(detected_speakers) < 2:
            return False

        unique_speakers = set(detected_speakers)
        if len(unique_speakers) < 2:
            return False

        speaker_pattern_count = len(detected_speakers) / len(speakers)
        return speaker_pattern_count >= 0.5
