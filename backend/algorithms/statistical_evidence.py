
import re


class StatisticalEvidenceAnalyzer:

    def __init__(self):

        # Statistical measure and estimate
        self.measure_pattern = re.compile(
            r"\b("
            r"risk ratio|odds ratio|hazard ratio|"
            r"RR|OR|HR"
            r")\b"
            r"\s*(?:(?:was|is|of|=|:)\s*)?"
            r"([0-9]+(?:\.[0-9]+)?)",
            re.IGNORECASE
        )

        # Confidence interval patterns
        self.ci_patterns = [

            # [0.85 to 1.98] or (0.85 to 1.98)
            re.compile(
                r"[\[(]\s*"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s+to\s+"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s*[\])]",
                re.IGNORECASE
            ),

            # [0.85, 1.98] or (0.85, 1.98)
            re.compile(
                r"[\[(]\s*"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s*,\s*"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s*[\])]"
            ),

            # (0.85-1.98) or (0.85–1.98)
            re.compile(
                r"[\[(]\s*"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s*[-–—]\s*"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s*[\])]"
            )
        ]

        self.certainty_pattern = re.compile(
            r"\b(high|moderate|low|very low)"
            r"\s+certainty\b",
            re.IGNORECASE
        )

    # --------------------------------------------------
    # Extract Statistical Measure
    # --------------------------------------------------

    def extract_measure(self, sentence):

        match = self.measure_pattern.search(sentence)

        if not match:
            return None

        measure = match.group(1).upper()

        aliases = {
            "RISK RATIO": "RR",
            "ODDS RATIO": "OR",
            "HAZARD RATIO": "HR"
        }

        measure = aliases.get(measure, measure)

        return {
            "measure": measure,
            "estimate": float(match.group(2))
        }

    # --------------------------------------------------
    # Extract Confidence Interval
    # --------------------------------------------------

    def extract_confidence_interval(self, sentence):

        for pattern in self.ci_patterns:

            match = pattern.search(sentence)

            if match:

                lower = float(match.group(1))
                upper = float(match.group(2))

                if lower > upper:
                    return None

                return {
                    "lower": lower,
                    "upper": upper
                }

        return None

    # --------------------------------------------------
    # Extract Evidence Certainty
    # --------------------------------------------------

    def extract_certainty(self, sentence):

        match = self.certainty_pattern.search(sentence)

        if not match:
            return None

        return match.group(1).lower()

    # --------------------------------------------------
    # Analyze Statistical Result
    # --------------------------------------------------

    def analyze(self, sentence):

        measure_data = self.extract_measure(sentence)
        ci_data = self.extract_confidence_interval(sentence)
        certainty = self.extract_certainty(sentence)

        if not measure_data:

            return {
                "available": False,
                "reason": "No recognized statistical measure found."
            }

        measure = measure_data["measure"]
        estimate = measure_data["estimate"]

        result = {
            "available": True,
            "measure": measure,
            "estimate": estimate,
            "confidence_interval": ci_data,
            "null_value": 1.0,
            "includes_null": None,
            "statistical_interpretation": "Cannot determine",
            "certainty": certainty
        }

        if ci_data:

            lower = ci_data["lower"]
            upper = ci_data["upper"]

            includes_null = (
                lower <= 1.0 <= upper
            )

            result["includes_null"] = includes_null

            if includes_null:

                result["statistical_interpretation"] = (
                    "Confidence interval includes the null value"
                )

            else:

                result["statistical_interpretation"] = (
                    "Confidence interval excludes the null value"
                )

        return result


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    analyzer = StatisticalEvidenceAnalyzer()

    test_sentences = [

        "Mortality was 11/10,000 compared with 14/10,000 "
        "(RR 1.29 [0.85 to 1.98]; low certainty).",

        "The risk was reduced "
        "(RR 0.74 (0.52 to 1.05), moderate certainty).",

        "The odds ratio was 0.65 (0.50 to 0.80).",

        "The hazard ratio was 1.45 (1.10 to 1.90).",

        "The odds ratio of 0.72 [0.60, 0.91] was reported."
    ]

    for sentence in test_sentences:

        print("\nSentence:")
        print(sentence)

        result = analyzer.analyze(sentence)

        print("\nAnalysis:")

        for key, value in result.items():
            print(f"{key}: {value}")

        print("-" * 70)
