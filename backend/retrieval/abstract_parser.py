import re


class AbstractParser:

    def __init__(self):

        # --------------------------------------------------
        # Section Mapping
        # --------------------------------------------------

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
            "STUDY DESIGN": "Research Method",
            "DATA SOURCES": "Research Method",
            "SEARCH METHODS": "Research Method",
            "SELECTION CRITERIA": "Research Method",
            "DATA COLLECTION AND ANALYSIS": "Research Method",
            "PARTICIPANTS": "Research Method",
            "INTERVENTIONS": "Research Method",

            "RESULT": "Research Result",
            "RESULTS": "Research Result",
            "MAIN RESULTS": "Research Result",
            "FINDINGS": "Research Result",
            "EFFICACY ENDPOINTS": "Research Result",

            "CONCLUSION": "Conclusion",
            "CONCLUSIONS": "Conclusion",
            "AUTHORS' CONCLUSIONS": "Conclusion",

            "ADVERSE EFFECTS": "Safety Result",
            "ADVERSE EVENTS": "Safety Result",
            "SAFETY RESULTS": "Safety Result",
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
            re.escape(name)
            for name in section_names
        )

        # Recognizes:
        # BACKGROUND: ...
        # METHODS: ...
        # Adverse effectsThe risk ...
        #
        # The second form handles missing spaces
        # between headings and their content.

        self.section_pattern = re.compile(
            r"(?<![A-Za-z])("
            + heading_pattern
            + r")"
            r"(?::\s*|(?=(?-i:[A-Z])))",
            re.IGNORECASE
        )

        # --------------------------------------------------
        # Abbreviations
        # --------------------------------------------------

        self.abbreviations = [
            "e.g.",
            "i.e.",
            "Dr.",
            "Mr.",
            "Mrs.",
            "Prof.",
            "vs.",
            "etc.",
            "et al.",
            "Fig.",
            "No.",
            "approx.",
            "Inc.",
            "Ltd."
        ]

    # --------------------------------------------------
    # Normalize Abstract
    # --------------------------------------------------

    def normalize_text(self, text):

        if not isinstance(text, str):
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

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

        # Text before the first heading

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
                "section_type": self.section_mapping[
                    section_name
                ],
                "text": section_text
            })

        return sections

    # --------------------------------------------------
    # Protect Special Periods
    # --------------------------------------------------

    def protect_special_periods(self, text):

        protected = text
        tokens = {}

        for index, abbreviation in enumerate(
            self.abbreviations
        ):

            token = f"ABBREVIATIONTOKEN{index}END"

            pattern = re.compile(
                re.escape(abbreviation),
                re.IGNORECASE
            )

            protected = pattern.sub(
                token,
                protected
            )

            tokens[token] = abbreviation

        # Protect decimal points:
        # 3.14 -> 3DECIMALPOINTTOKEN14

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

        # Split after sentence-ending punctuation.
        # Also supports missing spaces before uppercase
        # letters, e.g. "infection.The results..."

        parts = re.split(
            r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])",
            protected
        )

        sentences = []

        for part in parts:

            sentence = part.strip()

            if not sentence:
                continue

            # Restore abbreviations

            for token, original in tokens.items():

                sentence = sentence.replace(
                    token,
                    original
                )

            # Restore decimal points

            sentence = sentence.replace(
                "DECIMALPOINTTOKEN",
                "."
            )

            # Keep short but meaningful sentences.
            # Avoid arbitrary length-based deletion.

            if sentence:
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
# Manual Test
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