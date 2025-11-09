from __future__ import annotations

import difflib
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from .registry import SkillMeta, SkillMetadata


@dataclass(slots=True)
class SkillMatch:
    """Represents a simple substring search result."""

    skill: SkillMetadata
    score: int


class SkillSelector:
    """Substring based selector used by the CLI search command."""

    def __init__(self, skills: Iterable[SkillMetadata]):
        self._skills = list(skills)

    def search(self, query: str, *, language: str | None = None) -> list[SkillMatch]:
        normalized_query = query.lower()
        matches: list[SkillMatch] = []
        for skill in self._skills:
            if language and skill.language != language:
                continue
            haystacks = [skill.name, skill.description, skill.prelude]
            score = sum(normalized_query in (text or "").lower() for text in haystacks)
            if score:
                matches.append(SkillMatch(skill=skill, score=score))
        matches.sort(key=lambda match: (-match.score, match.skill.name))
        return matches


def _tokenise(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _common_prefix_length(a: str, b: str) -> int:
    count = 0
    for char_a, char_b in zip(a, b):
        if char_a != char_b:
            break
        count += 1
    return count


class Selector:
    """Perform lightweight semantic search across skills."""

    def __init__(self, skills: Sequence[SkillMeta]):
        self._skills = list(skills)
        self._tokens = [_tokenise(skill.searchable_text) for skill in self._skills]
        self._idf = self._build_idf(self._tokens)
        self._doc_vectors = [self._build_vector(tokens) for tokens in self._tokens]
        self._doc_norms = [self._vector_norm(vec) for vec in self._doc_vectors]
        self._full_texts = [skill.searchable_text.lower() for skill in self._skills]

    def _build_idf(self, documents: Sequence[Sequence[str]]):
        df: Counter[str] = Counter()
        for tokens in documents:
            for token in set(tokens):
                df[token] += 1
        total_docs = len(documents)
        idf = {token: math.log((1 + total_docs) / (1 + count)) + 1 for token, count in df.items()}
        self._idf_default = math.log(1 + total_docs) + 1
        return idf

    def _build_vector(self, tokens: Sequence[str]):
        counts = Counter(tokens)
        total = sum(counts.values()) or 1
        vector = {}
        for token, count in counts.items():
            tf = count / total
            idf = self._idf.get(token, self._idf_default)
            vector[token] = tf * idf
        return vector

    @staticmethod
    def _vector_norm(vector):
        return math.sqrt(sum(value * value for value in vector.values()))

    def _query_vector(self, query_tokens: Sequence[str]):
        counts = Counter(query_tokens)
        total = sum(counts.values()) or 1
        vector = {}
        for token, count in counts.items():
            tf = count / total
            idf = self._idf.get(token, self._idf_default)
            vector[token] = tf * idf
        norm = self._vector_norm(vector)
        return vector, norm

    def search(self, query: str, k: int = 5, threshold: float = 0.0) -> List[Tuple[SkillMeta, float]]:
        if not query or not query.strip():
            return []

        query_tokens = _tokenise(query)
        if not query_tokens:
            return []
        query_vector, query_norm = self._query_vector(query_tokens)

        results: List[Tuple[SkillMeta, float]] = []
        for skill, doc_vector, doc_norm, full_text, tokens in zip(
            self._skills, self._doc_vectors, self._doc_norms, self._full_texts, self._tokens
        ):
            cosine = 0.0
            if doc_norm and query_norm:
                cosine = sum(doc_vector.get(token, 0.0) * weight for token, weight in query_vector.items())
                cosine /= doc_norm * query_norm

            substring_score = 0.0
            lowered_query = query.lower()
            if lowered_query in full_text:
                substring_score = 1.0
            else:
                best_weighted = 0.0
                for token in query_tokens:
                    for candidate in tokens:
                        ratio = difflib.SequenceMatcher(None, token, candidate).ratio()
                        if ratio <= 0.0:
                            continue
                        prefix = _common_prefix_length(token, candidate)
                        base = 0.1
                        if prefix:
                            base += prefix / max(len(token), 1)
                        weighted = ratio * min(base, 1.0)
                        if weighted > best_weighted:
                            best_weighted = weighted
                substring_score = best_weighted

            score = max(cosine, substring_score)
            if score >= threshold:
                results.append((skill, score))

        results.sort(key=lambda item: (-item[1], item[0].identifier))
        return results[:k]
