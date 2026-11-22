from sentence_transformers import SentenceTransformer

from backend.algorithms.evidence_analysis import EvidenceAnalyzer


class RelevanceFilter:

    def __init__(
        self,
        model_name="all-MiniLM-L6-v2",
        relevance_threshold=0.35,
        evidence_analyzer=None
    ):

        if not -1.0 <= relevance_threshold <= 1.0:
            raise ValueError(
                "relevance_threshold must be between -1 and 1."
            )

        self.model = SentenceTransformer(model_name)

        self.relevance_threshold = relevance_threshold

        self.evidence_analyzer = (
            evidence_analyzer
            if evidence_analyzer is not None
            else EvidenceAnalyzer()
        )

    # --------------------------------------------------
    # Calculate Semantic Relevance
    # --------------------------------------------------

    def calculate_relevance(self, claim, evidence):

        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError(
                "Claim and evidence must be strings."
            )

        if not claim.strip() or not evidence.strip():
            return 0.0

        embeddings = self.model.encode(
            [claim, evidence],
            normalize_embeddings=True,
            convert_to_tensor=True
        )

        similarity = embeddings[0] @ embeddings[1]

        return float(similarity.item())

    # --------------------------------------------------
    # Analyze Evidence
    # --------------------------------------------------

    def analyze_evidence(self, claim, evidence):

        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError(
                "Claim and evidence must be strings."
            )

        if not claim.strip() or not evidence.strip():

            return {
                "relevance": 0.0,
                "relevance_status": "Insufficient",
                "classification": "Insufficient",
                "confidence": 0.0,
                "scores": {},
                "reason": "Claim or evidence is empty."
            }

        relevance = self.calculate_relevance(
            claim,
            evidence
        )

        # Step 1: Relevance filtering

        if relevance < self.relevance_threshold:

            return {
                "relevance": relevance,
                "relevance_status": "Low Relevance",
                "classification": "Insufficient",
                "confidence": 0.0,
                "scores": {},
                "reason": (
                    "The evidence is not sufficiently related "
                    "to the claim. NLI analysis was skipped."
                )
            }

        # Step 2: NLI analysis

        nli_result = self.evidence_analyzer.analyze(
            claim,
            evidence
        )

        return {
            "relevance": relevance,
            "relevance_status": "Relevant",
            "classification": nli_result["label"],
            "predicted_label": nli_result.get(
                "predicted_label",
                nli_result["label"]
            ),
            "confidence": nli_result["confidence"],
            "margin": nli_result.get("margin"),
            "scores": nli_result["scores"],
            "reason": nli_result["reason"]
        }


if __name__ == "__main__":

    filter_system = RelevanceFilter()

    claim = (
        "Vaccines reduce the risk of infectious diseases."
    )

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

        result = filter_system.analyze_evidence(
            claim,
            evidence
        )

        print(f"\n{index}. Evidence:")
        print(evidence)

        print(
            "Relevance:",
            f'{result["relevance"]:.4f}'
        )

        print(
            "Relevance Status:",
            result["relevance_status"]
        )

        print(
            "Classification:",
            result["classification"]
        )

        print(
            "Confidence:",
            f'{result["confidence"]:.4f}'
        )

        print("Reason:", result["reason"])