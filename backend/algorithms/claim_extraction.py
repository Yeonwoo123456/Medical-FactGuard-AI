import re


class MedicalClaimExtractor:

    def __init__(self):

        # Medical-related keywords
        self.medical_keywords = [
            "vaccine", "vaccines", "vaccination", "immunization",
            "medicine", "medication", "drug", "drugs",
            "treatment", "treatments", "therapy", "therapies",
            "cancer", "tumor", "tumour", "disease", "diseases",
            "infection", "infections", "virus", "viruses",
            "bacteria", "bacterial", "symptom", "symptoms",
            "side effect", "side effects",
            "cure", "cures", "clinical trial",
            "antibiotic", "antibiotics", "health",
            "medical", "patient", "patients",
            "blood pressure", "heart disease",
            "immune system", "immunity"
        ]

        # Expressions that may indicate a claim
        self.claim_indicators = [
            "cause", "causes", "caused", "causing",
            "prevent", "prevents", "prevented",
            "cure", "cures", "cured",
            "increase", "increases", "decrease", "decreases",
            "reduce", "reduces", "improve", "improves",
            "lead to", "leads to", "result in", "results in",
            "effective", "ineffective",
            "safe", "unsafe", "harmful", "beneficial",
            "proven", "evidence", "study", "studies",
            "associated with", "linked to",
            "claim", "claims", "suggest", "suggests",
            "show", "shows", "indicate", "indicates",
            "risk", "risks", "side effect", "side effects",
            "develop", "develops", "transmit", "transmits","effectiveness", "ineffective",
            "confirm", "confirmed", "confirmation", "fail", "fails", "failed",
            "work", "works", "working","believe", "believes","not effective", 
            "no evidence", "not proven", "cannot prevent"
        ]

    # Split input text into sentences
    def split_sentences(self, text):

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    # Check whether a sentence contains medical information
    def has_medical_keyword(self, sentence):

        sentence_lower = sentence.lower()

        return any(
            re.search(
                r'\b' + re.escape(keyword) + r'\b',
                sentence_lower
            )
            for keyword in self.medical_keywords
        )

    # Check whether a sentence expresses a claim
    def has_claim_indicator(self, sentence):

        sentence_lower = sentence.lower()

        return any(
            re.search(
                r'\b' + re.escape(indicator) + r'\b',
                sentence_lower
            )
            for indicator in self.claim_indicators
        )

    # Determine whether a sentence is a medical claim candidate
    def is_medical_claim(self, sentence):

        return (
            self.has_medical_keyword(sentence)
            and self.has_claim_indicator(sentence)
        )

    # Extract medical claim candidates
    def extract_claims(self, text):

        sentences = self.split_sentences(text)

        claims = []
        seen = set()

        for sentence in sentences:

            if self.is_medical_claim(sentence):

                normalized = re.sub(
                    r'\s+', ' ', sentence.lower()
                ).strip()

                if normalized not in seen:
                    claims.append(sentence)
                    seen.add(normalized)

        return claims


if __name__ == "__main__":

    extractor = MedicalClaimExtractor()

    sample_text = """
    Some people claim that vaccines cause serious diseases.
    Exercise is important for maintaining good health.
    Antibiotics are effective against bacterial infections.
    Drinking water helps maintain normal body functions.
    Some cancer treatments have significant side effects.
    """

    results = extractor.extract_claims(sample_text)

    print("Extracted Medical Claims:")
    
    if results:
        for index, claim in enumerate(results, start=1):
            print(f"{index}. {claim}")
    else:
        print("No medical claims detected.")
