import re


class MedicalClassifier:

    def __init__(self):

        self.categories = {
            "Vaccines & Immunization": [
                "vaccine", "vaccines", "vaccination",
                "immunization", "immunity",
                "booster", "antibody", "antibodies",
                "measles", "polio", "influenza",
                "flu shot", "vaccine efficacy",
                "vaccine safety"
            ],

            "Medications & Treatments": [
                "medicine", "medication", "medications",
                "drug", "drugs", "antibiotic",
                "antibiotics", "treatment", "therapy",
                "therapies", "prescription", "dosage",
                "painkiller", "side effect", "side effects",
                "clinical trial", "pharmaceutical"
            ],

            "Cancer-related Medical Information": [
                "cancer", "tumor", "tumour",
                "oncology", "chemotherapy",
                "radiotherapy", "radiation therapy",
                "malignant", "malignancy",
                "carcinoma", "leukemia",
                "lymphoma", "metastasis",
                "immunotherapy", "cancer treatment"
            ]
        }

    def find_matches(self, text, keywords):

        text = text.lower()
        matches = []

        for keyword in keywords:

            pattern = (
                r'(?<!\w)' +
                re.escape(keyword) +
                r'(?!\w)'
            )

            if re.search(pattern, text):
                matches.append(keyword)

        return matches

    def classify(self, text):

        scores = {}

        for category, keywords in self.categories.items():

            matches = self.find_matches(text, keywords)
            scores[category] = len(matches)

        max_score = max(scores.values())

        if max_score == 0:
            return {
                "category": "Unclassified",
                "confidence": 0.0,
                "scores": scores
            }

        best_categories = [
            category
            for category, score in scores.items()
            if score == max_score
        ]

        if len(best_categories) > 1:
            return {
                "category": "Ambiguous",
                "confidence": 0.0,
                "scores": scores
            }

        best_category = best_categories[0]

        confidence = max_score / sum(scores.values())

        return {
            "category": best_category,
            "confidence": confidence,
            "scores": scores
        }


if __name__ == "__main__":

    classifier = MedicalClassifier()

    test_claims = [
        "Vaccines can prevent infectious diseases.",
        "Antibiotics are effective against bacterial infections.",
        "Chemotherapy is used to treat certain types of cancer.",
        "Cancer patients may receive immunotherapy.",
        "Regular exercise improves general health."
    ]

    for claim in test_claims:

        result = classifier.classify(claim)

        print("\nClaim:", claim)
        print("Category:", result["category"])
        print("Confidence:", f"{result['confidence']:.2%}")
        print("Scores:", result["scores"])
