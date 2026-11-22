import pytest

from backend.evidence_pipeline import EvidencePipeline


# ==================================================
# Mock Modules
# ==================================================

class FakeAbstractParser:
    def parse(self, abstract):
        return [
            {
                "section": "RESULTS",
                "section_type": "Research Result",
                "sentence": "The treatment reduced symptoms.",
            },
            {
                "section": "SAFETY",
                "section_type": "Safety Result",
                "sentence": "Adverse events were similar between groups.",
            },
            {
                "section": "CONCLUSION",
                "section_type": "Conclusion",
                "sentence": "In conclusion, the treatment was effective.",
            },
        ]


class FakeSentenceClassifier:
    def classify(self, sentence):
        if "reduced symptoms" in sentence:
            sentence_type = "Research Result"

        elif "Adverse events" in sentence:
            sentence_type = "Safety Result"

        elif "In conclusion" in sentence:
            sentence_type = "Conclusion"

        else:
            sentence_type = "Other"

        return {
            "type": sentence_type,
            "confidence": 0.9,
            "matched_patterns": [],
            "scores": {},
        }


class FakeRelevanceFilter:
    def analyze_evidence(self, claim, evidence):
        return {
            "classification": "Supporting",
            "relevance": 0.8,
            "confidence": 0.9,
            "margin": 0.7,
            "scores": {},
            "reason": "Mock result",
        }


class FakeStatisticalAnalyzer:
    def analyze(self, sentence):
        if "reduced symptoms" in sentence:
            return {
                "available": True,
                "measure": "RR",
                "estimate": 0.75,
                "confidence_interval": [0.60, 0.90],
                "null_value": 1.0,
                "includes_null": False,
                "certainty": "moderate",
            }

        return {
            "available": False,
            "measure": None,
            "estimate": None,
            "confidence_interval": None,
            "null_value": None,
            "includes_null": None,
            "certainty": None,
        }


# ==================================================
# Pipeline Test Setup
# ==================================================

def make_pipeline():
    """
    Construct the pipeline without downloading AI models
    or connecting to PubMed.
    """

    pipeline = EvidencePipeline.__new__(EvidencePipeline)

    # Inject mock modules
    pipeline.abstract_parser = FakeAbstractParser()
    pipeline.sentence_classifier = FakeSentenceClassifier()
    pipeline.relevance_filter = FakeRelevanceFilter()
    pipeline.statistical_analyzer = FakeStatisticalAnalyzer()

    # Initialize uncertainty patterns
    pipeline.uncertainty_patterns = [
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

    # Initialize safety topic patterns
    pipeline.safety_topic_patterns = [
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
        r"\bvaccine safety\b",
        r"\bdrug safety\b",
        r"\btreatment safety\b",
        r"\bmedication safety\b",
        r"\bsafety profile\b",
    ]

    # Initialize safety result patterns
    pipeline.safety_result_patterns = [
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

        r"\b(?:adverse events?|adverse effects?|serious harms?) "
        r"(?:occurred|were reported|was reported|were observed|"
        r"was observed)\b",

        r"\bcannot be excluded\b",
        r"\bcould not be excluded\b",
    ]

    # Initialize safety concern patterns
    pipeline.safety_concern_patterns = [
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

    return pipeline


# ==================================================
# Article Analysis Tests
# ==================================================

def test_analyze_article_returns_expected_structure():
    pipeline = make_pipeline()

    article = {
        "pmid": "12345678",
        "title": "Example Clinical Study",
        "year": "2025",
        "journal": "Example Journal",
        "url": "https://example.com",
        "abstract": "Example abstract",
    }

    result = pipeline.analyze_article(
        "The treatment is effective.",
        article,
    )

    assert result["pmid"] == "12345678"
    assert result["title"] == "Example Clinical Study"

    assert "classification" in result
    assert "overall_counts" in result
    assert "effectiveness_analysis" in result
    assert "safety_analysis" in result
    assert "statistical_summary" in result
    assert "sentences" in result


def test_analyze_article_classifies_sentences():
    pipeline = make_pipeline()

    result = pipeline.analyze_article(
        "The treatment is effective.",
        {"abstract": "Example abstract"},
    )

    sentence_types = [
        item["sentence_type"]
        for item in result["sentences"]
    ]

    assert "Research Result" in sentence_types
    assert "Safety Result" in sentence_types
    assert "Conclusion" in sentence_types


def test_analyze_article_counts_evidence():
    pipeline = make_pipeline()

    result = pipeline.analyze_article(
        "The treatment is effective.",
        {"abstract": "Example abstract"},
    )

    counts = result["overall_counts"]

    assert counts["Supporting"] == 3
    assert counts["Contradicting"] == 0
    assert counts["Insufficient"] == 0


# ==================================================
# Safety and Effectiveness Tests
# ==================================================

def test_safety_and_effectiveness_are_separated():
    pipeline = make_pipeline()

    result = pipeline.analyze_article(
        "The treatment is effective.",
        {"abstract": "Example abstract"},
    )

    safety = result["safety_analysis"]
    effectiveness = result["effectiveness_analysis"]

    assert safety["sentence_count"] == 1
    assert safety["safety_topic_count"] == 1

    # Safety sentences should not enter effectiveness analysis.
    assert effectiveness["sentence_count"] == 2


# ==================================================
# Statistical Analysis Tests
# ==================================================

def test_statistical_summary_is_generated():
    pipeline = make_pipeline()

    result = pipeline.analyze_article(
        "The treatment is effective.",
        {"abstract": "Example abstract"},
    )

    summary = result["statistical_summary"]

    assert summary["analyzed_sentences"] == 1
    assert summary["confidence_intervals_found"] == 1
    assert summary["intervals_excluding_null"] == 1


# ==================================================
# Uncertainty Detection Tests
# ==================================================

def test_uncertainty_detection():
    pipeline = make_pipeline()

    result = pipeline.detect_uncertainty(
        "The results remain uncertain."
    )

    assert result["is_uncertain"] is True
    assert len(result["matched_patterns"]) > 0


# ==================================================
# Evidence Normalization Tests
# ==================================================

def test_normalize_evidence_result():
    pipeline = make_pipeline()

    result = pipeline.normalize_evidence_result({
        "classification": "Supporting",
        "relevance": 0.82,
        "confidence": 0.91,
    })

    assert result["classification"] == "Supporting"
    assert result["relevance"] == 0.82
    assert result["confidence"] == 0.91


def test_invalid_evidence_result_becomes_insufficient():
    pipeline = make_pipeline()

    result = pipeline.normalize_evidence_result(None)

    assert result["classification"] == "Insufficient"
    assert result["relevance"] == 0.0
    assert result["confidence"] == 0.0


# ==================================================
# Full Claim Analysis Integration Test
# ==================================================

def test_analyze_claim_connects_search_optimizer():
    pipeline = make_pipeline()

    class FakeMedicalClassifier:
        def classify(self, claim):
            return {
                "category": "Vaccines & Immunization",
                "confidence": 0.9,
                "scores": {
                    "vaccine": 3,
                },
            }

    class FakeSearchOptimizer:
        def optimize(self, claim):
            return {
                "articles": [
                    {
                        "pmid": "12345678",
                        "title": "Example Clinical Study",
                        "year": "2025",
                        "journal": "Example Journal",
                        "url": "https://example.com",
                        "abstract": "Example abstract",
                    }
                ],
                "evaluated_query_count": 5,
                "retrieved_article_count": 1,
                "optimized_queries": [
                    "vaccine effectiveness"
                ],
                "beam_search_results": [],
                "optimization_note": "Mock search",
            }

    pipeline.medical_classifier = FakeMedicalClassifier()
    pipeline.local_search_optimizer = FakeSearchOptimizer()

    result = pipeline.analyze_claim(
        "Vaccines reduce the risk of infectious diseases."
    )

    assert result["status"] == "Analysis completed"
    assert result["category"] == "Vaccines & Immunization"
    assert result["retrieved_articles"] == 1
    assert result["analyzed_articles"] == 1
    assert len(result["articles"]) == 1


# ==================================================
# Input Validation Tests
# ==================================================

def test_analyze_claim_rejects_empty_claim():
    pipeline = make_pipeline()

    with pytest.raises(ValueError):
        pipeline.analyze_claim("   ")