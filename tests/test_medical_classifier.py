
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from backend.algorithms.medical_classifier import MedicalClassifier


class ClassificationEvaluator:

    def __init__(self):

        self.classifier = MedicalClassifier()

        self.test_data = [
            {
                "text": "Vaccines can prevent infectious diseases.",
                "label": "Vaccines & Immunization"
            },
            {
                "text": "Vaccination helps develop immunity.",
                "label": "Vaccines & Immunization"
            },
            {
                "text": "Vaccine safety is evaluated through clinical studies.",
                "label": "Vaccines & Immunization"
            },
            {
                "text": "Antibiotics treat bacterial infections.",
                "label": "Medications & Treatments"
            },
            {
                "text": "Certain medications reduce blood pressure.",
                "label": "Medications & Treatments"
            },
            {
                "text": "Some drugs have serious side effects.",
                "label": "Medications & Treatments"
            },
            {
                "text": "Chemotherapy is used to treat cancer.",
                "label": "Cancer-related Medical Information"
            },
            {
                "text": "Lymphoma is a type of cancer.",
                "label": "Cancer-related Medical Information"
            },
            {
                "text": "Cancer patients may receive immunotherapy.",
                "label": "Cancer-related Medical Information"
            },
            {
                "text": "The weather is sunny today.",
                "label": "Unclassified"
            },
            {
                "text": "Computer science is an interesting subject.",
                "label": "Unclassified"
            },
            {
                "text": "I enjoy playing basketball.",
                "label": "Unclassified"
            }
        ]

    def evaluate(self):

        labels = [
            "Vaccines & Immunization",
            "Medications & Treatments",
            "Cancer-related Medical Information",
            "Unclassified"
        ]

        correct = 0
        total = len(self.test_data)

        predictions = []

        print("\nMEDICAL CLASSIFICATION RESULTS")
        print("-" * 60)

        for item in self.test_data:

            result = self.classifier.classify(item["text"])

            predicted = result["category"]
            actual = item["label"]

            predictions.append((actual, predicted))

            if predicted == actual:
                correct += 1
                status = "CORRECT"
            else:
                status = "INCORRECT"

            print(f"\n{status}: {item['text']}")
            print(f"Expected: {actual}")
            print(f"Predicted: {predicted}")

        accuracy = correct / total

        print("\nPER-CLASS PERFORMANCE")
        print("-" * 60)

        f1_scores = []

        for label in labels:

            tp = sum(
                1 for actual, predicted in predictions
                if actual == label and predicted == label
            )

            fp = sum(
                1 for actual, predicted in predictions
                if actual != label and predicted == label
            )

            fn = sum(
                1 for actual, predicted in predictions
                if actual == label and predicted != label
            )

            precision = (
                tp / (tp + fp)
                if tp + fp > 0 else 0
            )

            recall = (
                tp / (tp + fn)
                if tp + fn > 0 else 0
            )

            f1 = (
                2 * precision * recall / (precision + recall)
                if precision + recall > 0 else 0
            )

            f1_scores.append(f1)

            print(f"\nCategory: {label}")
            print(f"Precision: {precision:.2%}")
            print(f"Recall:    {recall:.2%}")
            print(f"F1-score:  {f1:.2%}")

        macro_f1 = sum(f1_scores) / len(f1_scores)

        print("\nOVERALL PERFORMANCE")
        print("-" * 60)
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Macro F1-score: {macro_f1:.2%}")
        print(f"Correct: {correct}/{total}")


if __name__ == "__main__":

    evaluator = ClassificationEvaluator()
    evaluator.evaluate()