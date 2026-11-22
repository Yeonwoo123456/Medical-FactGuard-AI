import pytest

from backend.algorithms.sentence_classifier import SentenceClassifier


@pytest.fixture
def classifier():
    return SentenceClassifier()


@pytest.mark.parametrize(
    "sentence, expected",
    [
        (
            "The aim of this study was to evaluate vaccine effectiveness.",
            "Research Objective"
        ),
        (
            "We included 26 trials with 73,428 participants.",
            "Research Method"
        ),
        (
            "The treatment reduced symptoms.",
            "Research Result"
        ),
        (
            "The intervention was associated with a lower incidence of infection.",
            "Research Result"
        ),
        (
            "No significant difference was observed between groups.",
            "Research Result"
        ),
        (
            "Serious adverse events were similar between groups.",
            "Safety Result"
        ),
        (
            "No increase in serious adverse events was observed.",
            "Safety Result"
        ),
        (
            "Previous studies have shown an association with cancer.",
            "Background"
        ),
        (
            "In conclusion, the treatment was effective.",
            "Conclusion"
        ),
        (
            "Further studies are needed to confirm these findings.",
            "Recommendation"
        ),
    ]
)
def test_sentence_classification(classifier, sentence, expected):

    result = classifier.classify(sentence)

    assert result["type"] == expected


def test_safety_term_without_result_is_not_safety_result(classifier):

    result = classifier.classify(
        "The aim was to assess adverse events."
    )

    assert result["type"] == "Research Objective"


def test_empty_sentence(classifier):

    result = classifier.classify("")

    assert result["type"] == "Other"
    assert result["confidence"] == 0.0


def test_whitespace_sentence(classifier):

    result = classifier.classify("   ")

    assert result["type"] == "Other"


def test_non_string_input(classifier):

    result = classifier.classify(None)

    assert result["type"] == "Other"


def test_result_contains_scores(classifier):

    result = classifier.classify(
        "The treatment significantly reduced infection risk."
    )

    assert "scores" in result
    assert "Research Result" in result["scores"]


def test_confidence_range(classifier):

    result = classifier.classify(
        "The treatment reduced the risk of infection."
    )

    assert 0.0 <= result["confidence"] <= 1.0