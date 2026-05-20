from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def evidence_text(
    record: dict[str, Any],
    include_gold_questions: bool = False,
    text_field: str = "metadata",
) -> str:
    fields = [
        record.get("page_id", ""),
        record.get("document_id", ""),
        str(record.get("page_no", "")),
        record.get("page_summary", ""),
        " ".join(record.get("question_types", [])),
    ]
    if text_field == "vlm_summary":
        fields.extend(
            [
                record.get("visual_summary", ""),
                record.get("answer_relevant_text", ""),
                " ".join(record.get("detected_elements", [])),
            ]
        )
    if include_gold_questions:
        fields.extend(qa.get("question", "") for qa in record.get("qas", []))
    return "\n".join(str(field) for field in fields if field)


@dataclass
class SearchResult:
    page_id: str
    score: float


class BM25Index:
    def __init__(
        self,
        page_ids: list[str],
        doc_tokens: list[list[str]],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.page_ids = page_ids
        self.doc_tokens = doc_tokens
        self.k1 = k1
        self.b = b
        self.doc_len = [len(tokens) for tokens in doc_tokens]
        self.avgdl = sum(self.doc_len) / max(len(self.doc_len), 1)
        self.term_freqs = [Counter(tokens) for tokens in doc_tokens]
        df: Counter[str] = Counter()
        for tf in self.term_freqs:
            df.update(tf.keys())
        self.idf = {
            term: math.log(1 + (len(doc_tokens) - freq + 0.5) / (freq + 0.5))
            for term, freq in df.items()
        }

    @classmethod
    def from_records(
        cls,
        records: list[dict[str, Any]],
        include_gold_questions: bool = False,
        text_field: str = "metadata",
    ) -> "BM25Index":
        page_ids = [record["page_id"] for record in records]
        doc_tokens = [
            tokenize(
                evidence_text(
                    record,
                    include_gold_questions=include_gold_questions,
                    text_field=text_field,
                )
            )
            for record in records
        ]
        return cls(page_ids=page_ids, doc_tokens=doc_tokens)

    def search(self, query: str, k: int = 5) -> list[SearchResult]:
        query_terms = tokenize(query)
        scores: list[SearchResult] = []
        for idx, tf in enumerate(self.term_freqs):
            score = 0.0
            length = self.doc_len[idx] or 1
            for term in query_terms:
                if term not in tf:
                    continue
                freq = tf[term]
                denom = freq + self.k1 * (1 - self.b + self.b * length / self.avgdl)
                score += self.idf.get(term, 0.0) * (freq * (self.k1 + 1) / denom)
            if score > 0:
                scores.append(SearchResult(page_id=self.page_ids[idx], score=score))
        scores.sort(key=lambda item: item.score, reverse=True)
        return scores[:k]

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_ids": self.page_ids,
            "doc_tokens": self.doc_tokens,
            "k1": self.k1,
            "b": self.b,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BM25Index":
        return cls(
            page_ids=payload["page_ids"],
            doc_tokens=payload["doc_tokens"],
            k1=payload.get("k1", 1.5),
            b=payload.get("b", 0.75),
        )
