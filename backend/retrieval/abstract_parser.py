
import re


class AbstractParser:

    def __init__(self):

        self.section_mapping = {
            "BACKGROUND": "Background",
            "INTRODUCTION": "Background",

            "OBJECTIVE": "Research Objective",
            "OBJECTIVES": "Research Objective",
            "AIM": "Research Objective",
            "AIMS": "Research Objective",

            "METHOD": "Research Method",
            "METHODS": "Research Method",
            "METHODOLOGY": "Research Method",
            "SEARCH METHODS": "Research Method",
            "SELECTION CRITERIA": "Research Method",
            "DATA COLLECTION AND ANALYSIS": "Research Method",

            "RESULT": "Research Result",
            "RESULTS": "Research Result",
            "MAIN RESULTS": "Research Result",
            "FINDINGS": "Research Result",
            "EFFICACY ENDPOINTS": "Research Result",
            "HPV16/18 NEGATIVE": "Research Result",
            "REGARDLESS OF HPV DNA STATUS": "Research Result",

            "CONCLUSION": "Conclusion",
            "CONCLUSIONS": "Conclusion",
            "AUTHORS' CONCLUSIONS": "Conclusion",

            "ADVERSE EFFECTS": "Safety Result",
            "ADVERSE EVENTS": "Safety Result",
            "PREGNANCY OUTCOMES": "Safety Result",

            "RECOMMENDATION": "Recommendation",
            "RECOMMENDATIONS": "Recommendation"
        }

        section_names = sorted(
            self.section_mapping.keys(),
            key=len,
            reverse=True
        )

        heading_pattern = "|".join(
            re.escape(name) for name in section_names
        )

        # A heading must either:
        # 1. Be followed by a colon, or
        # 2. Be immediately followed by an uppercase letter.
        #
        # The second rule handles headings such as:
        # Adverse effectsThe risk...
        # Pregnancy outcomesAmong those...

        self.section_pattern = re.compile(
            r"(?<![A-Za-z])("
            + heading_pattern
            + r")(?::\s*|(?=(?-i:[A-Z])))",
            re.IGNORECASE
        )

        self.abbreviations = [
            "e.g.", "i.e.", "Dr.", "Mr.", "Mrs.",
            "Prof.", "vs.", "etc.", "et al."
        ]

    # --------------------------------------------------
    # Normalize Abstract
    # --------------------------------------------------

    def normalize_text(self, text):

        if not isinstance(text, str):
            return ""

        text = text.replace("\n", " ")
        text = text.replace("\r", " ")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # --------------------------------------------------
    # Extract Sections
    # --------------------------------------------------

    def extract_sections(self, abstract):

        text = self.normalize_text(abstract)

        if not text:
            return []

        matches = list(
            self.section_pattern.finditer(text)
        )

        if not matches:

            return [{
                "section": "Unstructured",
                "section_type": "Other",
                "text": text
            }]

        sections = []

        prefix = text[:matches[0].start()].strip()

        if prefix:

            sections.append({
                "section": "Unlabeled",
                "section_type": "Other",
                "text": prefix
            })

        for index, match in enumerate(matches):

            start = match.end()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(text)

            section_name = match.group(1).upper()

            section_text = text[start:end].strip()

            if not section_text:
                continue

            sections.append({
                "section": section_name,
                "section_type": self.section_mapping[section_name],
                "text": section_text
            })

        return sections

    # --------------------------------------------------
    # Protect Abbreviations and Decimal Numbers
    # --------------------------------------------------

    def protect_special_periods(self, text):

        protected = text
        tokens = {}

        for index, abbreviation in enumerate(
            self.abbreviations
        ):

            token = f"ABBREVIATIONTOKEN{index}"

            pattern = re.compile(
                re.escape(abbreviation),
                re.IGNORECASE
            )

            if pattern.search(protected):

                protected = pattern.sub(
                    token,
                    protected
                )

                tokens[token] = abbreviation

        protected = re.sub(
            r"(?<=\d)\.(?=\d)",
            "DECIMALPOINTTOKEN",
            protected
        )

        return protected, tokens

    # --------------------------------------------------
    # Split Sentences
    # --------------------------------------------------

    def split_sentences(self, text):

        text = self.normalize_text(text)

        if not text:
            return []

        protected, tokens = self.protect_special_periods(
            text
        )

        parts = re.split(
            r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])",
            protected
        )

        sentences = []

        for part in parts:

            sentence = part.strip()

            if not sentence:
                continue

            for token, original in tokens.items():

                sentence = sentence.replace(
                    token,
                    original
                )

            sentence = sentence.replace(
                "DECIMALPOINTTOKEN",
                "."
            )

            if len(sentence) > 10:
                sentences.append(sentence)

        return sentences

    # --------------------------------------------------
    # Parse Full Abstract
    # --------------------------------------------------

    def parse(self, abstract):

        sections = self.extract_sections(abstract)

        parsed_sentences = []

        for section in sections:

            sentences = self.split_sentences(
                section["text"]
            )

            for sentence in sentences:

                parsed_sentences.append({
                    "section": section["section"],
                    "section_type": section["section_type"],
                    "sentence": sentence
                })

        return parsed_sentences


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    parser = AbstractParser()

    sample_abstract = """
    BACKGROUND: Persistent HPV infection is associated
    with cervical cancer. HPV vaccines can prevent infection.

    OBJECTIVES: To evaluate vaccine protection and safety.

    METHODS: We included 26 trials with 73,428 participants.

    MAIN RESULTS: Vaccines reduced the risk of cervical precancer.
    Adverse effectsThe risk of serious adverse events was similar
    between control and HPV vaccines.

    Pregnancy outcomesAmong those who became pregnant during
    the studies, we did not find an increased risk of miscarriage.

    The effects on congenital abnormalities and stillbirths
    are uncertain.

    AUTHORS' CONCLUSIONS: HPV vaccines protect against
    cervical precancer.
    """

    results = parser.parse(sample_abstract)

    print("\nABSTRACT PARSER RESULTS")
    print("=" * 70)

    for item in results:

        print("\nSection:", item["section"])
        print("Section Type:", item["section_type"])
        print("Sentence:", item["sentence"])
