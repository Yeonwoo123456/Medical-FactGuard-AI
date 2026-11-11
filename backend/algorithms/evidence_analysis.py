import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class EvidenceAnalyzer:
    def __init__(
        self,
        model_name="cross-encoder/nli-deberta-v3-small",
        confidence_threshold=0.55,
        margin_threshold=0.10
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.margin_threshold = margin_threshold

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )
        self.model.eval()

        # 모델이 제공하는 실제 label 정보를 사용
        self.id2label = self.model.config.id2label

    def analyze(self, claim, evidence):
        if not isinstance(claim, str) or not isinstance(evidence, str):
            raise TypeError("Claim and evidence must be strings.")

        if not claim.strip() or not evidence.strip():
            return {
                "label": "Insufficient",
                "confidence": 0.0,
                "scores": {},
                "reason": "Claim or evidence is empty."
            }

        # Evidence = Premise, Claim = Hypothesis
        inputs = self.tokenizer(
            evidence,
            claim,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)[0]

        scores = {}

        # 모델의 label 이름을 읽어 결과를 정리
        for index, probability in enumerate(probabilities):
            raw_label = str(
                self.id2label.get(index, f"LABEL_{index}")
            ).lower()

            if "entail" in raw_label:
                label = "Supporting"
            elif "contradict" in raw_label:
                label = "Contradicting"
            elif "neutral" in raw_label:
                label = "Neutral"
            else:
                # 일반적인 NLI 모델의 label 순서에 대한 fallback
                fallback_labels = {
                    0: "Contradicting",
                    1: "Supporting",
                    2: "Neutral"
                }
                label = fallback_labels.get(index, raw_label)

            scores[label] = float(probability.item())

        # 세 가지 NLI 점수가 모두 존재하는지 확인
        required_labels = [
            "Supporting",
            "Contradicting",
            "Neutral"
        ]

        if not all(label in scores for label in required_labels):
            raise ValueError(
                f"Unexpected NLI model labels: {self.id2label}"
            )

        ranked_scores = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        predicted_label, confidence = ranked_scores[0]
        second_confidence = ranked_scores[1][1]

        # 모델의 판단이 불확실하면 Insufficient 처리
        if (
            confidence < self.confidence_threshold
            or confidence - second_confidence < self.margin_threshold
        ):
            final_label = "Insufficient"
        else:
            final_label = predicted_label

        return {
            "label": final_label,
            "confidence": confidence,
            "scores": scores,
            "reason": self._generate_reason(final_label)
        }

    def _generate_reason(self, label):
        reasons = {
            "Supporting": "The evidence supports the given claim.",
            "Contradicting": "The evidence contradicts the given claim.",
            "Neutral": "The evidence is related but does not establish support or contradiction.",
            "Insufficient": "The model's prediction is not sufficiently confident."
        }

        return reasons[label]


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
        print("Confidence:", f'{result["confidence"]:.4f}')
        print("Scores:", result["scores"])
        print("Reason:", result["reason"])