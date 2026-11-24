import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class EvidenceAnalyzer:

    def __init__(
        self,
        model_name="cross-encoder/nli-deberta-v3-small",
        confidence_threshold=0.55,
        margin_threshold=0.10,
        max_length=512
    ):

        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.margin_threshold = margin_threshold
        self.max_length = max_length

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )

        self.model.to(self.device)
        self.model.eval()

        self.id2label = self.model.config.id2label

    # --------------------------------------------------
    # Normalize Model Labels
    # --------------------------------------------------

    def _normalize_label(self, raw_label, index):

        # Normalize common label formatting variations.
        label = str(raw_label).strip().lower().replace("-", "_").replace(" ", "_")

        if "entail" in label or "support" in label:
            return "Supporting"

        if "contradict" in label:
            return "Contradicting"

        if "neutral" in label:
            return "Neutral"

        # Fallback is only safe for the known model's
        # documented three-class output order.
        # Numeric string labels are handled in the same way as LABEL_0 etc.

        if (
            self.model_name == "cross-encoder/nli-deberta-v3-small"
            and (
                label.startswith("label_")
                or label.isdigit()
            )
        ):

            fallback_labels = {
                0: "Contradicting",
                1: "Supporting",
                2: "Neutral"
            }

            if index in fallback_labels:
                return fallback_labels[index]

        raise ValueError(
            f"Unrecognized NLI label: {raw_label}. "
            "Check the model's id2label configuration."
        )

    # --------------------------------------------------
    # Analyze Evidence
    # --------------------------------------------------

    def analyze(self, claim, evidence):

        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError(
                "Claim and evidence must be strings."
            )

        if not claim.strip() or not evidence.strip():

            return {
                "label": "Insufficient",
                "confidence": 0.0,
                "scores": {},
                "reason": "Claim or evidence is empty."
            }

        # Evidence = Premise
        # Claim = Hypothesis
        inputs = self.tokenizer(
            evidence,
            claim,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():

            outputs = self.model(**inputs)

            probabilities = torch.softmax(
                outputs.logits,
                dim=-1
            )[0]

        if len(probabilities) != 3:
            raise ValueError(
                "Expected a three-class NLI model, "
                f"but received {len(probabilities)} classes."
            )

        scores = {}

        for index, probability in enumerate(probabilities):

            raw_label = self.id2label.get(
                index,
                f"LABEL_{index}"
            )

            label = self._normalize_label(
                raw_label,
                index
            )

            if label in scores:
                raise ValueError(
                    f"Duplicate NLI label detected: {label}"
                )

            scores[label] = float(probability.item())

        required_labels = {
            "Supporting",
            "Contradicting",
            "Neutral"
        }

        if set(scores.keys()) != required_labels:
            raise ValueError(
                f"Unexpected NLI labels: {scores.keys()}"
            )

        ranked_scores = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        predicted_label, confidence = ranked_scores[0]
        second_confidence = ranked_scores[1][1]

        margin = confidence - second_confidence

        if (
            confidence < self.confidence_threshold
            or margin < self.margin_threshold
        ):

            final_label = "Insufficient"

        else:

            final_label = predicted_label

        return {
            "label": final_label,
            "predicted_label": predicted_label,
            "confidence": confidence,
            "margin": margin,
            "scores": scores,
            "reason": self._generate_reason(final_label)
        }

    # --------------------------------------------------
    # Generate Explanation
    # --------------------------------------------------

    def _generate_reason(self, label):

        reasons = {
            "Supporting": (
                "The evidence supports the given claim."
            ),

            "Contradicting": (
                "The evidence contradicts the given claim."
            ),

            "Neutral": (
                "The evidence does not establish support "
                "or contradiction."
            ),

            "Insufficient": (
                "The model's prediction is not sufficiently "
                "confident to assign a reliable classification."
            )
        }

        return reasons.get(
            label,
            "The evidence could not be classified."
        )


if __name__ == "__main__":

    analyzer = EvidenceAnalyzer()

    claim = (
        "Vaccines reduce the risk of infectious diseases."
    )

    evidences = [
        "Vaccination can reduce the risk of contracting certain infectious diseases.",
        "Vaccination does not reduce the risk of infectious diseases.",
        "Vaccines are an important part of public health programs.",
        "The weather is sunny today."
    ]

    print("\nEVIDENCE ANALYSIS RESULTS")
    print("=" * 65)

    for index, evidence in enumerate(evidences, start=1):

        result = analyzer.analyze(claim, evidence)

        print(f"\n{index}. Evidence:")
        print(evidence)
        print("Classification:", result["label"])
        print("Predicted label:", result["predicted_label"])
        print("Confidence:", f'{result["confidence"]:.4f}')
        print("Margin:", f'{result["margin"]:.4f}')
        print("Scores:", result["scores"])
        print("Reason:", result["reason"])