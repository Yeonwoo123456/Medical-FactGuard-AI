import re
from typing import Dict, List, Set

from sentence_transformers import SentenceTransformer
from backend.algorithms.evidence_analysis import EvidenceAnalyzer


class RelevanceFilter:
    """
    Conservative sentence-level relevance gate.

    Semantic similarity is not sufficient by itself: a sentence must also
    share the claim's key medical subject and (when explicit) clinical endpoint.
    Relevance is textual alignment, not evidence that a claim is true.
    """

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "in", "on", "for", "with", "by", "from", "and", "or",
        "but", "that", "this", "these", "those", "it", "its", "can", "could",
        "may", "might", "should", "would", "does", "do", "did", "has", "have",
        "had", "not", "no", "than", "into", "after", "before", "among",
        "which", "who", "their", "they", "we", "our", "such", "also",
    }

    SUBJECT_GROUPS = {
        "vitamin_c": (r"\bvitamin\s*c\b", r"\bascorbic\s*acid\b"),
        "zinc": (r"\bzinc\b",),
        "vaccine": (r"\bvaccin(?:e|es|ation|ations)\b", r"\bimmuni[sz]ation\b"),
        "common_cold": (r"\bcommon cold\b", r"\bupper respiratory(?: tract)? infection\b", r"\brhinovirus\b"),
        "cancer": (r"\bcancer\b", r"\bneoplasm\b", r"\btumou?r\b", r"\bcarcinoma\b"),
        "covid": (r"\bcovid(?:-19)?\b", r"\bsars-cov-2\b"),
        "hypertension": (r"\bhypertension\b", r"\bblood pressure\b"),
        "diabetes": (r"\bdiabetes\b", r"\bglycemic\b", r"\bblood glucose\b"),
        "pregnancy": (r"\bpregnan(?:t|cy)\b", r"\bmaternal\b", r"\bfetal\b"),
    }

    ENDPOINT_GROUPS = {
        "prevention": (
            r"\bprevent(?:s|ed|ing|ion)?\b", r"\bincidence\b",
            r"\boccurrence\b", r"\bnew cases?\b", r"\brisk of (?:getting|developing|contracting)\b",
            r"\b발병률\b", r"\b예방\b",
        ),
        "duration": (
            r"\bduration\b", r"\blength of\b", r"\bhow long\b",
            r"\bshorten(?:s|ed|ing)?\b", r"\brecovery time\b", r"\b기간\b",
        ),
        "severity": (
            r"\bseverity\b", r"\bsevere\b", r"\bsymptom score\b",
            r"\bsymptom burden\b", r"\b증상\b", r"\b중증도\b",
        ),
        "mortality": (
            r"\bmortality\b", r"\bdeath\b", r"\bsurvival\b",
            r"\b사망률\b",
        ),
        "safety": (
            r"\badverse events?\b", r"\bside effects?\b", r"\btoxicity\b",
            r"\bharms?\b", r"\bsafety\b", r"\b부작용\b", r"\b안전성\b",
        ),
        "blood_pressure": (
            r"\bblood pressure\b", r"\bsystolic\b", r"\bdiastolic\b",
            r"\b혈압\b",
        ),
    }

    def __init__(
        self,
        model_name=DEFAULT_MODEL,
        relevance_threshold=0.38,
        evidence_analyzer=None,
        lexical_threshold=0.12,
    ):
        if not -1.0 <= relevance_threshold <= 1.0:
            raise ValueError("relevance_threshold must be between -1 and 1.")
        if not 0.0 <= lexical_threshold <= 1.0:
            raise ValueError("lexical_threshold must be between 0 and 1.")

        self.model = SentenceTransformer(model_name)
        self.relevance_threshold = float(relevance_threshold)
        self.lexical_threshold = float(lexical_threshold)
        self.evidence_analyzer = evidence_analyzer or EvidenceAnalyzer()

    @staticmethod
    def _normalize(text: str) -> str:
        text = (text or "").casefold()
        text = text.replace("vitamin-c", "vitamin c")
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9가-힣%./+-]", " ", text)).strip()

    def _tokens(self, text: str) -> Set[str]:
        return {
            token for token in re.findall(r"[a-z]{3,}|[가-힣]{2,}", self._normalize(text))
            if token not in self.STOPWORDS
        }

    def _matched_groups(self, text: str, groups: Dict[str, tuple]) -> List[str]:
        normalized = self._normalize(text)
        return [
            name for name, patterns in groups.items()
            if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns)
        ]

    def _alignment(self, claim: str, evidence: str) -> Dict[str, object]:
        claim_subjects = self._matched_groups(claim, self.SUBJECT_GROUPS)
        evidence_subjects = self._matched_groups(evidence, self.SUBJECT_GROUPS)
        claim_endpoints = self._matched_groups(claim, self.ENDPOINT_GROUPS)
        evidence_endpoints = self._matched_groups(evidence, self.ENDPOINT_GROUPS)

        # If the claim names a recognized intervention/disease, require at
        # least one matching subject anchor in the sentence or article title.
        subject_ok = not claim_subjects or set(claim_subjects).issubset(set(evidence_subjects))

        # Explicit endpoints must match. This prevents prevention evidence
        # from being replaced by duration/severity evidence, and vice versa.
        endpoint_ok = not claim_endpoints or set(claim_endpoints).issubset(set(evidence_endpoints))

        claim_tokens = self._tokens(claim)
        evidence_tokens = self._tokens(evidence)
        lexical_coverage = (
            len(claim_tokens & evidence_tokens) / len(claim_tokens)
            if claim_tokens else 0.0
        )

        # Recognized subject and endpoint anchors carry more weight than
        # generic shared words such as "study", "effect", or "risk".
        return {
            "subject_ok": subject_ok,
            "endpoint_ok": endpoint_ok,
            "claim_subjects": claim_subjects,
            "evidence_subjects": evidence_subjects,
            "claim_endpoints": claim_endpoints,
            "evidence_endpoints": evidence_endpoints,
            "lexical_coverage": lexical_coverage,
        }

    def calculate_relevance(self, claim, evidence):
        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError("Claim and evidence must be strings.")
        if not claim.strip() or not evidence.strip():
            return 0.0
        embeddings = self.model.encode(
            [claim, evidence],
            normalize_embeddings=True,
            convert_to_tensor=True,
        )
        return float((embeddings[0] @ embeddings[1]).item())

    def analyze_evidence(self, claim, evidence):
        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError("Claim and evidence must be strings.")
        if not claim.strip() or not evidence.strip():
            return {
                "relevance": 0.0, "relevance_status": "Insufficient",
                "classification": "Insufficient", "confidence": 0.0,
                "scores": {}, "reason": "Claim or evidence is empty.",
            }

        relevance = self.calculate_relevance(claim, evidence)
        alignment = self._alignment(claim, evidence)
        subject_ok = alignment["subject_ok"]
        endpoint_ok = alignment["endpoint_ok"]
        lexical_coverage = float(alignment["lexical_coverage"])

        # When a known subject/endpoint is explicitly named, a semantic score
        # cannot override a failed clinical-topic gate.
        if not subject_ok:
            reason = "The evidence does not mention the claim's key medical subject."
        elif not endpoint_ok:
            reason = "The evidence addresses a different clinical outcome from the claim."
        elif relevance < self.relevance_threshold:
            reason = "Semantic similarity is below the relevance threshold."
        elif lexical_coverage < self.lexical_threshold and not (
            alignment["claim_subjects"] and alignment["claim_endpoints"]
        ):
            reason = "The evidence shares too little claim-specific terminology."

        else:
            nli_result = self.evidence_analyzer.analyze(claim, evidence)
            return {
                "relevance": relevance,
                "relevance_status": "Relevant",
                "classification": nli_result["label"],
                "predicted_label": nli_result.get("predicted_label", nli_result["label"]),
                "confidence": nli_result["confidence"],
                "margin": nli_result.get("margin"),
                "scores": nli_result["scores"],
                "reason": nli_result["reason"],
                "alignment": alignment,
            }

        return {
            "relevance": relevance,
            "relevance_status": "Low Relevance",
            "classification": "Insufficient",
            "predicted_label": "Insufficient",
            "confidence": 0.0,
            "margin": None,
            "scores": {},
            "reason": reason,
            "alignment": alignment,
        }


if __name__ == "__main__":
    filter_system = RelevanceFilter()
    claim = "Vitamin C prevents the common cold."
    samples = [
        "Vitamin C supplementation did not prevent common colds.",
        "Vitamin C may reduce the duration of an ongoing cold.",
        "Zinc supplementation may reduce the duration of the common cold.",
        "Hospital admission rates changed during the study.",
    ]
    for text in samples:
        result = filter_system.analyze_evidence(claim, text)
        print(text)
        print(result["relevance_status"], result["classification"], result["reason"])