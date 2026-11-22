import re


class StatisticalEvidenceAnalyzer:

    def __init__(self):

        self.measure_aliases = {
            "STANDARDIZED MEAN DIFFERENCE": "SMD",
            "RELATIVE RISK REDUCTION": "RRR",
            "RISK RATIO": "RR",
            "RELATIVE RISK": "RR",
            "ODDS RATIO": "OR",
            "HAZARD RATIO": "HR",
            "MEAN DIFFERENCE": "MD",
            "RISK DIFFERENCE": "RD",
        }

        aliases = sorted(
            self.measure_aliases.keys(),
            key=len,
            reverse=True
        )

        measure_names = (
            r"(?:" + "|".join(
                re.escape(name) for name in aliases
            ) + r"|SMD|MD|RD|RR|OR|HR|RRR)"
        )

        self.number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"

        self.measure_pattern = re.compile(
            r"(?<![A-Za-z])"
            r"(" + measure_names + r")"
            r"(?![A-Za-z])"
            r"\s*(?:(?:was|is|of|=|:)\s*)?"
            r"(" + self.number + r")",
            re.IGNORECASE
        )

        # Explicit confidence interval
        self.explicit_ci_pattern = re.compile(
            r"\b\d{1,2}(?:\.\d+)?\s*%\s*"
            r"(?:confidence\s+interval|CI)"
            r"\s*[,=:]?\s*"
            r"[\[(]?\s*"
            r"(" + self.number + r")"
            r"\s*(?:to|through|,|[-–—])\s*"
            r"(" + self.number + r")"
            r"\s*[\])]?",
            re.IGNORECASE
        )

        # Confidence interval without explicit 95% CI label
        self.bracket_ci_pattern = re.compile(
            r"[\[(]\s*"
            r"(" + self.number + r")"
            r"\s*(?:to|through|,|[-–—])\s*"
            r"(" + self.number + r")"
            r"\s*[\])]",
            re.IGNORECASE
        )

        self.certainty_pattern = re.compile(
            r"\b(very low|high|moderate|low)"
            r"\s+certainty\b",
            re.IGNORECASE
        )

        self.measure_types = {
            "RR": "ratio",
            "OR": "ratio",
            "HR": "ratio",
            "RRR": "difference",
            "MD": "difference",
            "SMD": "difference",
            "RD": "difference",
        }

    # --------------------------------------------------
    # Extract all statistical measures
    # --------------------------------------------------

    def extract_measures(self, sentence):

        if not isinstance(sentence, str) or not sentence.strip():
            return []

        results = []

        for match in self.measure_pattern.finditer(sentence):

            raw_measure = match.group(1).upper()

            measure = self.measure_aliases.get(
                raw_measure,
                raw_measure
            )

            estimate = float(match.group(2))

            measure_type = self.measure_types.get(measure)

            null_value = (
                1.0 if measure_type == "ratio"
                else 0.0
            )

            # Ratios cannot be zero or negative.
            if measure_type == "ratio" and estimate <= 0:
                continue

            results.append({
                "measure": measure,
                "estimate": estimate,
                "null_value": null_value,
                "start": match.start(),
                "end": match.end(),
            })

        return results

    # --------------------------------------------------
    # Backward-compatible single measure extraction
    # --------------------------------------------------

    def extract_measure(self, sentence):

        measures = self.extract_measures(sentence)

        if not measures:
            return None

        first = measures[0]

        return {
            "measure": first["measure"],
            "estimate": first["estimate"],
            "null_value": first["null_value"],
        }

    # --------------------------------------------------
    # Extract all confidence intervals with positions
    # --------------------------------------------------

    def extract_all_confidence_intervals(self, sentence):

        if not isinstance(sentence, str) or not sentence.strip():
            return []

        intervals = []

        patterns = [
            (self.explicit_ci_pattern, True),
            (self.bracket_ci_pattern, False),
        ]

        for pattern, explicit in patterns:

            for match in pattern.finditer(sentence):

                lower = float(match.group(1))
                upper = float(match.group(2))

                if lower > upper:
                    continue

                intervals.append({
                    "lower": lower,
                    "upper": upper,
                    "start": match.start(),
                    "end": match.end(),
                    "explicit": explicit,
                })

        # Remove duplicate intervals detected by both patterns.
        unique = []

        for interval in intervals:

            duplicate = any(
                existing["lower"] == interval["lower"]
                and existing["upper"] == interval["upper"]
                and existing["start"] == interval["start"]
                and existing["end"] == interval["end"]
                for existing in unique
            )

            if not duplicate:
                unique.append(interval)

        unique.sort(key=lambda item: item["start"])

        return unique

    # --------------------------------------------------
    # Match a confidence interval to its measure
    # --------------------------------------------------

    def match_confidence_interval(
        self,
        sentence,
        measure,
        next_measure_start=None
    ):

        intervals = self.extract_all_confidence_intervals(
            sentence
        )

        candidates = []

        for interval in intervals:

            # CI must occur after the measure estimate.
            if interval["start"] < measure["end"]:
                continue

            # Do not allow a CI to cross into the next measure.
            if (
                next_measure_start is not None
                and interval["start"] >= next_measure_start
            ):
                continue

            # Ratio confidence intervals must be positive.
            if (
                self.measure_types[measure["measure"]] == "ratio"
                and interval["lower"] <= 0
            ):
                continue

            distance = interval["start"] - measure["end"]

            candidates.append((
                distance,
                not interval["explicit"],
                interval
            ))

        if not candidates:
            return None

        # Prefer the nearest interval.
        # Explicit CI labels win when distances are equal.
        candidates.sort(
            key=lambda item: (item[0], item[1])
        )

        selected = candidates[0][2]

        return {
            "lower": selected["lower"],
            "upper": selected["upper"],
        }

    # --------------------------------------------------
    # Backward-compatible CI extraction
    # --------------------------------------------------

    def extract_confidence_interval(self, sentence):

        intervals = self.extract_all_confidence_intervals(
            sentence
        )

        if not intervals:
            return None

        first = intervals[0]

        return {
            "lower": first["lower"],
            "upper": first["upper"],
        }

    # --------------------------------------------------
    # Extract Evidence Certainty
    # --------------------------------------------------

    def extract_certainty(self, sentence):

        if not isinstance(sentence, str):
            return None

        match = self.certainty_pattern.search(sentence)

        if not match:
            return None

        return match.group(1).lower()

    # --------------------------------------------------
    # Analyze one statistical measure
    # --------------------------------------------------

    def analyze_measure(
        self,
        sentence,
        measure,
        next_measure_start=None,
        certainty=None
    ):

        ci_data = self.match_confidence_interval(
            sentence,
            measure,
            next_measure_start
        )

        result = {
            "available": True,
            "measure": measure["measure"],
            "estimate": measure["estimate"],
            "confidence_interval": ci_data,
            "null_value": measure["null_value"],
            "includes_null": None,
            "estimate_within_ci": None,
            "statistical_interpretation": "Cannot determine",
            "certainty": certainty,
        }

        if ci_data is None:
            return result

        lower = ci_data["lower"]
        upper = ci_data["upper"]
        null_value = measure["null_value"]
        estimate = measure["estimate"]

        includes_null = (
            lower <= null_value <= upper
        )

        estimate_within_ci = (
            lower <= estimate <= upper
        )

        result["includes_null"] = includes_null
        result["estimate_within_ci"] = estimate_within_ci

        if includes_null:

            interpretation = (
                "Confidence interval includes the null value"
            )

        else:

            interpretation = (
                "Confidence interval excludes the null value"
            )

        if not estimate_within_ci:

            interpretation += (
                "; WARNING: estimate is outside confidence interval"
            )

        result["statistical_interpretation"] = interpretation

        return result

    # --------------------------------------------------
    # Analyze all measures in one sentence
    # --------------------------------------------------

    def analyze_all(self, sentence):

        if not isinstance(sentence, str) or not sentence.strip():

            return {
                "available": False,
                "results": [],
                "reason": "Empty or invalid sentence."
            }

        measures = self.extract_measures(sentence)
        certainty = self.extract_certainty(sentence)

        if not measures:

            return {
                "available": False,
                "results": [],
                "reason": "No recognized statistical measure found."
            }

        results = []

        for index, measure in enumerate(measures):

            next_measure_start = None

            if index + 1 < len(measures):
                next_measure_start = measures[index + 1]["start"]

            result = self.analyze_measure(
                sentence,
                measure,
                next_measure_start,
                certainty
            )

            results.append(result)

        return {
            "available": True,
            "results": results,
        }

    # --------------------------------------------------
    # Main Analysis - Backward Compatible
    # --------------------------------------------------

    def analyze(self, sentence):

        all_results = self.analyze_all(sentence)

        if not all_results["available"]:

            return {
                "available": False,
                "reason": all_results["reason"]
            }

        results = all_results["results"]

        # First measure remains the primary result.
        primary = results[0].copy()

        # Additional measures are preserved separately.
        primary["additional_estimates"] = results[1:]

        return primary


# --------------------------------------------------
# Manual Test
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

        "Mean difference was -5.2 "
        "(95% CI, -8.1 to -2.3).",

        "Standardized mean difference was 0.45 "
        "(95% CI, 0.20 to 0.70).",

        "Risk difference was -0.12 "
        "(95% CI, -0.20 to -0.04).",

        "The outcome occurred in 60.2% "
        "(95% confidence interval, 40.8 to 73.8).",

        "Patients received treatment for 5 days.",

        "The treatment reduced symptoms by 30%.",

        (
            "RSV-associated illness with VE of -0.37% "
            "(95% CI -1.96 to 0.37; RR 1.37, "
            "95% CI 0.63 to 2.96)."
        ),

        (
            "Vaccination reduced dementia risk "
            "(RR 0.76, 95% CI 0.69-0.83) "
            "and Alzheimer's disease "
            "(RR 0.53, 95% CI 0.44-0.64)."
        ),
    ]

    for sentence in test_sentences:

        print("\nSentence:")
        print(sentence)

        result = analyzer.analyze(sentence)

        print("\nAnalysis:")

        for key, value in result.items():
            print(f"{key}: {value}")

        print("-" * 70)