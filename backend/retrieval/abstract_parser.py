import re


class AbstractParser:
    """Parse PubMed abstracts and discard obvious non-sentence artifacts."""

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
            "RECOMMENDATIONS": "Recommendation",
        }

        section_names = sorted(self.section_mapping, key=len, reverse=True)
        heading_pattern = "|".join(re.escape(name) for name in section_names)
        self.section_pattern = re.compile(
            r"(?<![A-Za-z])(" + heading_pattern + r")"
            r"(?::\s*|(?=(?-i:[A-Z])))",
            re.IGNORECASE,
        )

        self.abbreviations = [
            "e.g.", "i.e.", "Dr.", "Mr.", "Mrs.", "Prof.", "vs.",
            "etc.", "et al.", "Fig.", "No.", "approx.", "Inc.", "Ltd.",
        ]

        self.numeric_identifier_list_pattern = re.compile(
            r"^\s*(?:\d{1,3}(?:,\d{3})+|\d{6,})"
            r"(?:\s*[;,]\s*(?:\d{1,3}(?:,\d{3})+|\d{6,})){2,}"
            r"\s*[.;]?\s*$"
        )

    def normalize_text(self, text):
        if not isinstance(text, str):
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def is_noise_sentence(self, sentence):
        """Return True only for clear non-prose identifier/list artifacts."""
        if not isinstance(sentence, str):
            return True
        text = sentence.strip()
        if not text:
            return True
        if self.numeric_identifier_list_pattern.fullmatch(text):
            return True
        letters = re.findall(r"[A-Za-z]", text)
        digits = re.findall(r"\d", text)
        if len(digits) >= 18 and len(letters) <= 2:
            return True
        return False

    def extract_sections(self, abstract):
        text = self.normalize_text(abstract)
        if not text:
            return []

        matches = list(self.section_pattern.finditer(text))
        if not matches:
            return [{
                "section": "Unstructured",
                "section_type": "Other",
                "text": text,
            }]

        sections = []
        prefix = text[:matches[0].start()].strip()
        if prefix:
            sections.append({
                "section": "Unlabeled",
                "section_type": "Other",
                "text": prefix,
            })

        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section_name = match.group(1).upper()
            section_text = text[start:end].strip()
            if section_text:
                sections.append({
                    "section": section_name,
                    "section_type": self.section_mapping[section_name],
                    "text": section_text,
                })
        return sections

    def protect_special_periods(self, text):
        protected = text
        tokens = {}
        for index, abbreviation in enumerate(self.abbreviations):
            token = f"ABBREVIATIONTOKEN{index}END"
            protected = re.sub(
                re.escape(abbreviation),
                token,
                protected,
                flags=re.IGNORECASE,
            )
            tokens[token] = abbreviation
        protected = re.sub(r"(?<=\d)\.(?=\d)", "DECIMALPOINTTOKEN", protected)
        return protected, tokens

    def split_sentences(self, text):
        text = self.normalize_text(text)
        if not text:
            return []

        protected, tokens = self.protect_special_periods(text)
        parts = re.split(
            r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])",
            protected,
        )

        sentences = []
        for part in parts:
            sentence = part.strip()
            if not sentence:
                continue
            for token, original in tokens.items():
                sentence = sentence.replace(token, original)
            sentence = sentence.replace("DECIMALPOINTTOKEN", ".")
            if sentence and not self.is_noise_sentence(sentence):
                sentences.append(sentence)
        return sentences

    def parse(self, abstract):
        parsed_sentences = []
        for section in self.extract_sections(abstract):
            for sentence in self.split_sentences(section["text"]):
                parsed_sentences.append({
                    "section": section["section"],
                    "section_type": section["section_type"],
                    "sentence": sentence,
                })
        return parsed_sentences


if __name__ == "__main__":
    parser = AbstractParser()
    sample = (
        "METHODS: We included 26 trials with 73,428 participants. "
        "RESULTS: Vitamin C did not prevent common colds in the general population. "
        "CONCLUSIONS: The evidence does not support routine supplementation. "
        "3,963,325; 3,963,328; 3,969,019; 3,969,020."
    )
    for item in parser.parse(sample):
        print(item)