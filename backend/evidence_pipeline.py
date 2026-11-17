import re

from backend.algorithms.medical_classifier import MedicalClassifier
from backend.algorithms.relevance_filter import RelevanceFilter
from backend.algorithms.sentence_classifier import SentenceClassifier
from backend.algorithms.statistical_evidence import StatisticalEvidenceAnalyzer
from backend.retrieval.abstract_parser import AbstractParser
from backend.retrieval.pubmed_retriever import PubMedRetriever


class EvidencePipeline:
    """Coordinates retrieval, sentence classification, and evidence analysis."""

    PRIMARY_SENTENCE_TYPES = {
        "Research Result",
        "Safety Result",
        "Conclusion",
    }

    def __init__(self):
        self.abstract_parser = AbstractParser()
        self.medical_classifier = MedicalClassifier()
        self.relevance_filter = RelevanceFilter()
        self.sentence_classifier = SentenceClassifier()
        self.statistical_analyzer = StatisticalEvidenceAnalyzer()
        self.pubmed_retriever = PubMedRetriever()

        # Textual uncertainty is separate from statistical uncertainty.
        self.uncertainty_patterns = [
            r"\bcannot be excluded\b",
            r"\bcould not be excluded\b",
            r"\buncertain\b",
            r"\bunclear\b",
            r"\binsufficient evidence\b",
            r"\bno significant difference\b",
            r"\bnot statistically significant\b",
            r"\bmay be associated\b",
            r"\bpossible\b",
            r"\bpotential\b",
            r"\blimited evidence\b",
            r"\bnot enough data\b",
            r"\bno data are reported\b",
            r"\bdata were not available\b",
            r"\bremains uncertain\b",
            r"\bfurther research is needed\b",
            r"\bthe evidence is inconclusive\b",
            r"\bthe results are inconclusive\b",
        ]

        # These patterns identify a safety-related topic, not a proven harm.
        self.safety_topic_patterns = [
            r"\badverse events?\b",
            r"\badverse effects?\b",
            r"\bserious adverse events?\b",
            r"\bserious adverse effects?\b",
            r"\bside effects?\b",
            r"\bvaccine-related harms?\b",
            r"\bdrug-related harms?\b",
            r"\btreatment-related harms?\b",
            r"\bmedication-related harms?\b",
            r"\bmiscarriage\b",
            r"\bstillbirth\b",
            r"\bcongenital abnormalities\b",
            r"\bpregnancy outcomes?\b",
            r"\bpregnancy complications?\b",
            r"\btoxicity\b",
            r"\bfatal adverse events?\b",
            r"\bserious harms?\b",
            r"\brare harms?\b",
            r"\bvaccine-related deaths?\b",
            r"\bdeath following vaccination\b",
            r"\btreatment-related mortality\b",
            r"\bvaccine safety\b",
            r"\bdrug safety\b",
            r"\btreatment safety\b",
            r"\bmedication safety\b",
            r"\bsafety profile\b",
        ]

        # These patterns identify reported safety findings or explicit
        # safety conclusions. They do not establish that a treatment is
        # medically safe or unsafe.
        self.safety_result_patterns = [
            r"\badverse events? (?:were|was) "
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",
            r"\badverse effects? (?:were|was) "
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",
            r"\bserious adverse events? (?:were|was) "
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",
            r"\bside effects? (?:were|was) "
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",
            r"\b(?:increased|higher|reduced|lower) risk of "
            r"(?:serious )?(?:adverse events?|adverse effects?|"
            r"miscarriage|stillbirth|pregnancy outcomes?|"
            r"pregnancy complications?)\b",
            r"\brisk of (?:serious )?(?:adverse events?|adverse effects?|"
            r"miscarriage|stillbirth|pregnancy outcomes?) "
            r"(?:was|were|is|are) "
            r"(?:similar|higher|lower|increased|reduced)\b",
            r"\b(?:miscarriage|stillbirth|congenital abnormalities) "
            r"(?:were|was|occurred|reported|observed)\b",
            r"\b(?:pregnancy outcomes?|pregnancy complications?) "
            r"(?:were|was) "
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",
            r"\b(?:adverse events?|adverse effects?|serious harms?) "
            r"(?:occurred|were reported|was reported|were observed|"
            r"was observed)\b",
            r"\b(?:have|has|had) been judged not to be related\b",
            r"\b(?:was|were) judged not to be related\b",
            r"\b(?:was|were) not considered related\b",
            r"\b(?:was|were) not related to the vaccine\b",
            # An explicit statement that a risk cannot be ruled out is
            # a reported safety conclusion, but it remains uncertain.
            r"\bcannot be excluded\b",
            r"\bcould not be excluded\b",
        ]

        # These patterns identify concerns, not actual observed outcomes.
        self.safety_concern_patterns = [
            r"\bconcerns? about\b",
            r"\bconcerns? regarding\b",
            r"\bdoubts? about\b",
            r"\bpossible adverse events?\b",
            r"\bpotential adverse events?\b",
            r"\bpotential adverse effects?\b",
            r"\bpotential harms?\b",
            r"\bcannot be excluded\b",
            r"\bcould not be excluded\b",
            r"\buncertain safety\b",
            r"\bconcerns? over vaccine safety\b",
        ]

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def matches_any(patterns, text):
        text = text if isinstance(text, str) else ""
        return [
            pattern
            for pattern in patterns
            if re.search(pattern, text, re.IGNORECASE)
        ]

    # ------------------------------------------------------------------
    # Medical claim classification
    # ------------------------------------------------------------------

    def classify_claim(self, claim):
        result = self.medical_classifier.classify(claim)

        if isinstance(result, tuple):
            category = result[0] if len(result) > 0 else "Unknown"
            confidence = result[1] if len(result) > 1 else 0.0
            keywords = result[2] if len(result) > 2 else []
        elif isinstance(result, dict):
            category = result.get("category", "Unknown")
            confidence = result.get("confidence", 0.0)
            keywords = result.get("matched_keywords", [])
        else:
            category = str(result)
            confidence = 0.0
            keywords = []

        return category, self.to_float(confidence), keywords

    # ------------------------------------------------------------------
    # Evidence result normalization
    # ------------------------------------------------------------------

    def normalize_evidence_result(self, result):
        if not isinstance(result, dict):
            return {
                "classification": "Insufficient",
                "relevance": 0.0,
                "confidence": 0.0,
            }

        classification = result.get(
            "classification",
            result.get("label", "Insufficient"),
        )

        allowed_labels = {
            "Supporting",
            "Contradicting",
            "Neutral",
            "Insufficient",
        }
        if classification not in allowed_labels:
            classification = "Insufficient"

        return {
            "classification": classification,
            "relevance": self.to_float(
                result.get("relevance", result.get("similarity", 0.0))
            ),
            "confidence": self.to_float(result.get("confidence", 0.0)),
        }

    # ------------------------------------------------------------------
    # Uncertainty detection
    # ------------------------------------------------------------------

    def detect_uncertainty(self, sentence):
        matches = self.matches_any(self.uncertainty_patterns, sentence)
        return {
            "is_uncertain": bool(matches),
            "matched_patterns": matches,
        }

    # ------------------------------------------------------------------
    # Safety classification
    # ------------------------------------------------------------------

    def detect_safety_signals(self, sentence, section_type="Other"):
        """Return separate signals for topic, finding, and concern.

        section_type is retained for backward compatibility. The decision
        is based on sentence content rather than the section label alone.
        """
        topic_matches = self.matches_any(
            self.safety_topic_patterns, sentence
        )
        result_matches = self.matches_any(
            self.safety_result_patterns, sentence
        )
        concern_matches = self.matches_any(
            self.safety_concern_patterns, sentence
        )

        safety_topic = bool(topic_matches)
        safety_result = safety_topic and bool(result_matches)
        safety_concern = safety_topic and bool(concern_matches)

        return {
            "safety_topic": safety_topic,
            "safety_result": safety_result,
            "safety_concern": safety_concern,
            "topic_patterns": topic_matches,
            "result_patterns": result_matches,
            "concern_patterns": concern_matches,
        }

    def detect_safety_evidence(self, sentence, section_type="Other"):
        """Backward-compatible alias for older code."""
        return self.detect_safety_signals(
            sentence, section_type
        )["safety_topic"]

    # ------------------------------------------------------------------
    # Evidence counting and statistical summary
    # ------------------------------------------------------------------

    @staticmethod
    def count_classifications(results):
        counts = {
            "Supporting": 0,
            "Contradicting": 0,
            "Neutral": 0,
            "Insufficient": 0,
        }

        for result in results:
            label = result.get("evidence_classification", "Insufficient")
            if label in counts:
                counts[label] += 1

        return counts

    @staticmethod
    def summarize_statistics(results):
        summary = {
            "analyzed_sentences": 0,
            "confidence_intervals_found": 0,
            "intervals_including_null": 0,
            "intervals_excluding_null": 0,
            "sentences_without_detected_statistics": 0,
            "certainty_levels": {
                "high": 0,
                "moderate": 0,
                "low": 0,
                "very low": 0,
            },
        }

        for result in results:
            statistical = result.get("statistical_analysis") or {}

            if not statistical.get("available"):
                summary["sentences_without_detected_statistics"] += 1
                continue

            summary["analyzed_sentences"] += 1

            if statistical.get("confidence_interval") is not None:
                summary["confidence_intervals_found"] += 1

                includes_null = statistical.get("includes_null")
                if includes_null is True:
                    summary["intervals_including_null"] += 1
                elif includes_null is False:
                    summary["intervals_excluding_null"] += 1

            certainty = statistical.get("certainty")
            if certainty in summary["certainty_levels"]:
                summary["certainty_levels"][certainty] += 1

        return summary

    # ------------------------------------------------------------------
    # Analyze an individual article
    # ------------------------------------------------------------------

    def analyze_article(self, claim, article):
        abstract = article.get("abstract", "")
        parsed_sentences = self.abstract_parser.parse(abstract or "")
        sentence_results = []

        for item in parsed_sentences:
            sentence = item.get("sentence", "")
            if not isinstance(sentence, str) or not sentence.strip():
                continue

            section_type = item.get("section_type", "Other")

            # Classify sentence content; use the abstract section only
            # as a fallback when the classifier returns "Other".
            sentence_type_result = self.sentence_classifier.classify(sentence)
            final_type = sentence_type_result.get("type", "Other")
            type_confidence = self.to_float(
                sentence_type_result.get("confidence", 0.0)
            )

            if (
                final_type == "Other"
                and section_type not in {"Other", "Unstructured"}
            ):
                final_type = section_type

            raw_evidence = self.relevance_filter.analyze_evidence(
                claim, sentence
            )
            evidence = self.normalize_evidence_result(raw_evidence)

            uncertainty = self.detect_uncertainty(sentence)
            safety = self.detect_safety_signals(sentence, section_type)

            statistical = self.statistical_analyzer.analyze(sentence)
            if not isinstance(statistical, dict):
                statistical = {"available": False}

            sentence_results.append({
                "section": item.get("section", ""),
                "original_section_type": section_type,
                "sentence": sentence,
                "sentence_type": final_type,
                "type_confidence": type_confidence,
                "evidence_classification": evidence["classification"],
                "relevance": evidence["relevance"],
                "evidence_confidence": evidence["confidence"],
                "is_uncertain": uncertainty["is_uncertain"],
                "uncertainty_patterns": uncertainty["matched_patterns"],
                "safety_topic": safety["safety_topic"],
                "safety_result": safety["safety_result"],
                "safety_concern": safety["safety_concern"],
                # Retained for compatibility with existing UI/code.
                "is_safety_evidence": safety["safety_topic"],
                "statistical_analysis": statistical,
            })

        # Only result and conclusion sentences enter evidence summaries.
        primary_results = [
            result
            for result in sentence_results
            if result["sentence_type"] in self.PRIMARY_SENTENCE_TYPES
        ]

        # Safety analysis includes actual safety findings only.
        safety_results = [
            result
            for result in primary_results
            if result["safety_result"]
        ]

        # Effectiveness analysis excludes every safety-topic sentence,
        # not only sentences classified as actual safety findings.
        effectiveness_results = [
            result
            for result in primary_results
            if (
                not result["safety_topic"]
                and result["sentence_type"] != "Safety Result"
            )
        ]

        overall_counts = self.count_classifications(primary_results)
        effectiveness_counts = self.count_classifications(
            effectiveness_results
        )
        safety_counts = self.count_classifications(safety_results)

        safety_topic_count = sum(
            result["safety_topic"] for result in sentence_results
        )
        safety_concern_count = sum(
            result["safety_concern"] for result in sentence_results
        )

        uncertainty_count = sum(
            result["is_uncertain"] for result in primary_results
        )

        statistical_uncertainty_count = sum(
            1
            for result in primary_results
            if (
                (result.get("statistical_analysis") or {}).get("available")
                and (result.get("statistical_analysis") or {}).get(
                    "includes_null"
                ) is True
            )
        )

        statistical_summary = self.summarize_statistics(primary_results)

        supporting = overall_counts["Supporting"]
        contradicting = overall_counts["Contradicting"]

        if supporting and contradicting:
            classification = "Mixed"
        elif supporting > contradicting:
            classification = "Supporting"
        elif contradicting > supporting:
            classification = "Contradicting"
        elif primary_results:
            classification = "Neutral"
        else:
            classification = "Insufficient"

        return {
            "pmid": article.get("pmid", ""),
            "title": article.get("title", ""),
            "year": article.get("year", ""),
            "journal": article.get("journal", ""),
            "url": article.get("url", ""),
            "classification": classification,
            "overall_counts": overall_counts,
            "effectiveness_analysis": {
                "sentence_count": len(effectiveness_results),
                "counts": effectiveness_counts,
            },
            "safety_analysis": {
                "sentence_count": len(safety_results),
                "counts": safety_counts,
                "safety_topic_count": safety_topic_count,
                "safety_concern_count": safety_concern_count,
            },
            "uncertainty_count": uncertainty_count,
            "statistical_uncertainty_count": statistical_uncertainty_count,
            "statistical_summary": statistical_summary,
            "sentences": sentence_results,
        }

    # ------------------------------------------------------------------
    # Analyze a medical claim
    # ------------------------------------------------------------------

    def analyze_claim(self, claim):
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("Claim must be a non-empty string.")

        claim = claim.strip()
        category, category_confidence, keywords = self.classify_claim(claim)

        articles = self.pubmed_retriever.retrieve(claim)
        if not isinstance(articles, list):
            articles = []

        analyzed_articles = [
            self.analyze_article(claim, article)
            for article in articles
            if isinstance(article, dict)
        ]

        return {
            "status": "Analysis completed",
            "claim": claim,
            "category": category,
            "category_confidence": category_confidence,
            "matched_keywords": keywords,
            "retrieved_articles": len(articles),
            "analyzed_articles": len(analyzed_articles),
            "articles": analyzed_articles,
        }

    # ------------------------------------------------------------------
    # Print analysis report
    # ------------------------------------------------------------------

    def print_report(self, result):
        print("\nMEDICAL FACTGUARD AI")
        print("=" * 75)
        print("Status:", result["status"])
        print("Claim:", result["claim"])
        print("Category:", result["category"])
        print("Category Confidence:", result["category_confidence"])
        print("Retrieved Articles:", result["retrieved_articles"])
        print("Analyzed Articles:", result["analyzed_articles"])

        for article in result["articles"]:
            print("\n" + "=" * 75)
            print("PMID:", article["pmid"])
            print("Title:", article["title"])
            print("Year:", article["year"])
            print("Journal:", article["journal"])
            print("URL:", article["url"])
            print("\nArticle Evidence Summary:", article["classification"])

            print("\nOverall Evidence Counts:")
            for label, count in article["overall_counts"].items():
                print(f"{label}: {count}")

            effectiveness = article["effectiveness_analysis"]
            print("\nEffectiveness Analysis:")
            print("Sentence Count:", effectiveness["sentence_count"])
            for label, count in effectiveness["counts"].items():
                print(f"{label}: {count}")

            safety = article["safety_analysis"]
            print("\nSafety Analysis:")
            print("Actual Safety Result Count:", safety["sentence_count"])
            print("Safety Topic Count:", safety["safety_topic_count"])
            print("Safety Concern Count:", safety["safety_concern_count"])
            for label, count in safety["counts"].items():
                print(f"{label}: {count}")

            print("\nUncertainty Analysis:")
            print("Textual Uncertainty:", article["uncertainty_count"])
            print(
                "Intervals Including Null:",
                article["statistical_uncertainty_count"],
            )

            print("\nStatistical Summary:")
            for key, value in article["statistical_summary"].items():
                print(f"{key}: {value}")

            print("\nSentence Details:")
            for sentence in article["sentences"]:
                print("\nSentence:", sentence["sentence"])
                print("Original Section:", sentence["section"])
                print(
                    "Original Section Type:",
                    sentence["original_section_type"],
                )
                print("Sentence Type:", sentence["sentence_type"])
                print("Evidence:", sentence["evidence_classification"])
                print("Relevance:", round(sentence["relevance"], 4))
                print(
                    "Evidence Confidence:",
                    round(sentence["evidence_confidence"], 4),
                )
                print("Uncertain:", sentence["is_uncertain"])
                print("Safety Topic:", sentence["safety_topic"])
                print("Safety Result:", sentence["safety_result"])
                print("Safety Concern:", sentence["safety_concern"])

                statistical = sentence["statistical_analysis"]
                if statistical.get("available"):
                    print("\nStatistical Analysis:")
                    print("Measure:", statistical.get("measure"))
                    print("Estimate:", statistical.get("estimate"))
                    print(
                        "Confidence Interval:",
                        statistical.get("confidence_interval"),
                    )
                    print("Null Value:", statistical.get("null_value"))
                    print("Includes Null:", statistical.get("includes_null"))
                    print(
                        "Interpretation:",
                        statistical.get("statistical_interpretation"),
                    )
                    print("Study Certainty:", statistical.get("certainty"))

                print("-" * 70)


if __name__ == "__main__":
    pipeline = EvidencePipeline()
    test_claim = "Vaccines reduce the risk of infectious diseases."

    try:
        result = pipeline.analyze_claim(test_claim)
        pipeline.print_report(result)
    except Exception as error:
        print("\nANALYSIS ERROR")
        print(f"{type(error).__name__}: {error}")
