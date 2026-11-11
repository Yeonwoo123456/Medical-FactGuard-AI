
import sys
import os

# Add project root to Python path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from backend.algorithms.claim_extraction import MedicalClaimExtractor


class ClaimExtractionEvaluator:

    def __init__(self):
        self.extractor = MedicalClaimExtractor()

        # Test dataset
        # True = Medical claim
        # False = Not a medical claim
        self.test_data = [
            {
                "text": "Vaccines can cause serious side effects.",
                "label": True
            },
            {
                "text": "Antibiotics are effective against bacterial infections.",
                "label": True
            },
            {
                "text": "Some cancer treatments have significant side effects.",
                "label": True
            },
            {
                "text": "Smoking increases the risk of lung cancer.",
                "label": True
            },
            {
                "text": "Exercise is important for maintaining good health.",
                "label": False
            },
            {
                "text": "The weather is sunny today.",
                "label": False
            },
            {
                "text": "Drinking water is essential for daily life.",
                "label": False
            },
            {
                "text": "The patient visited the hospital yesterday.",
                "label": False
            },
            {
                "text": "Certain medications reduce blood pressure.",
                "label": True
            },
            {
                "text": "Computer science is an interesting subject.",
                "label": False
            },

            {
                "text": "There is no reliable evidence that vaccines cause autism.",
                "label": True
            },
            {
                "text": "Although some people believe this treatment works, clinical trials have not confirmed its effectiveness.",
                "label": True
            },
            {
                "text": "Cancer is a serious disease that affects millions of people.",
                "label": False
            },
            {
                "text": "This medication does not reduce the risk of infection.",
                "label": True
            },
            {
                "text": "Many patients receive treatment at hospitals.",
                "label": False
            }
        ]

    def evaluate(self):

        true_positive = 0
        false_positive = 0
        false_negative = 0
        true_negative = 0

        print("\nCLAIM EXTRACTION TEST RESULTS")
        print("-" * 55)

        for item in self.test_data:

            text = item["text"]
            actual = item["label"]

            predicted = bool(
                self.extractor.extract_claims(text)
            )

            if predicted and actual:
                true_positive += 1
                result = "TP"

            elif predicted and not actual:
                false_positive += 1
                result = "FP"

            elif not predicted and actual:
                false_negative += 1
                result = "FN"

            else:
                true_negative += 1
                result = "TN"

            print(f"{result}: {text}")

        # Calculate evaluation metrics
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive > 0 else 0
        )

        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative > 0 else 0
        )

        f1_score = (
            2 * precision * recall / (precision + recall)
            if precision + recall > 0 else 0
        )

        accuracy = (
            (true_positive + true_negative) / len(self.test_data)
        )

        print("\nCONFUSION MATRIX")
        print("-" * 55)
        print(f"True Positive:  {true_positive}")
        print(f"False Positive: {false_positive}")
        print(f"False Negative: {false_negative}")
        print(f"True Negative:  {true_negative}")

        print("\nPERFORMANCE METRICS")
        print("-" * 55)
        print(f"Accuracy:  {accuracy:.2%}")
        print(f"Precision: {precision:.2%}")
        print(f"Recall:    {recall:.2%}")
        print(f"F1-score:  {f1_score:.2%}")


if __name__ == "__main__":

    evaluator = ClaimExtractionEvaluator()
    evaluator.evaluate()