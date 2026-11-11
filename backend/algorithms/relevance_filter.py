from sentence_transformers import SentenceTransformer
from evidence_analysis import EvidenceAnalyzer


class RelevanceFilter:
    def __init__(
        self,
        model_name="all-MiniLM-L6-v2",
        relevance_threshold=0.35
    ):
        self.model = SentenceTransformer(model_name)
        self.relevance_threshold = relevance_threshold
        self.evidence_analyzer = EvidenceAnalyzer()

    def calculate_relevance(self, claim, evidence):
        if not claim.strip() or not evidence.strip():
            return 0.0

        embeddings = self.model.encode(
            [claim, evidence],
            normalize_embeddings=True
        )

        return float(embeddings[0] @ embeddings[1])

    def analyze_evidence(self, claim, evidence):
        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError("Claim and evidence must be strings.")

        if not claim.strip() or not evidence.strip():
            return {
                "relevance": 0.0,
                "relevance_status": "Insufficient",
                "classification": "Insufficient",
                "confidence": 0.0,
                "reason": "Claim or evidence is empty."
            }

        relevance = self.calculate_relevance(claim, evidence)

        # 관련성이 낮은 근거는 NLI 분석을 진행하지 않음
        if relevance < self.relevance_threshold:
            return {
                "relevance": relevance,
                "relevance_status": "Low Relevance",
                "classification": "Insufficient",
                "confidence": 0.0,
                "reason": "The evidence is not sufficiently related to the claim."
            }

        # 관련성이 충분하면 NLI 분석 실행
        nli_result = self.evidence_analyzer.analyze(
            claim,
            evidence
        )

        return {
            "relevance": relevance,
            "relevance_status": "Relevant",
            "classification": nli_result["label"],
            "confidence": nli_result["confidence"],
            "scores": nli_result["scores"],
            "reason": nli_result["reason"]
        }


if __name__ == "__main__":
    filter_system = RelevanceFilter()

    claim = "Vaccines reduce the risk of infectious diseases."

    evidences = [
        "Vaccination can reduce the risk of contracting certain infectious diseases.",
        "Vaccination does not reduce the risk of infectious diseases.",
        "Vaccines are an important part of public health programs.",
        "The weather is sunny today.",
        "Some medications can cause side effects."
    ]

    print("\nRELEVANCE FILTERING RESULTS")
    print("=" * 65)

    for index, evidence in enumerate(evidences, start=1):
        result = filter_system.analyze_evidence(claim, evidence)

        print(f"\n{index}. Evidence:")
        print(evidence)
        print("Relevance:", f'{result["relevance"]:.4f}')
        print("Relevance Status:", result["relevance_status"])
        print("Classification:", result["classification"])
        print("Confidence:", f'{result["confidence"]:.4f}')
        print("Reason:", result["reason"])