import pytest
import torch

from backend.algorithms.relevance_filter import RelevanceFilter


class FakeEmbeddingModel:

    def encode(self, sentences, **kwargs):

        return torch.tensor([
            [1.0, 0.0],
            [1.0, 0.0]
        ])


class FakeEvidenceAnalyzer:

    def __init__(self, result=None):
        self.called = False

        self.result = result or {
            "label": "Supporting",
            "confidence": 0.90,
            "scores": {
                "Supporting": 0.90,
                "Contradicting": 0.05,
                "Neutral": 0.05
            },
            "reason": "Evidence supports the claim."
        }

    def analyze(self, claim, evidence):
        self.called = True
        return self.result


@pytest.fixture
def relevance_filter():

    instance = RelevanceFilter.__new__(RelevanceFilter)

    instance.model = FakeEmbeddingModel()
    instance.relevance_threshold = 0.35
    instance.evidence_analyzer = FakeEvidenceAnalyzer()

    return instance


def test_relevant_evidence(relevance_filter):

    result = relevance_filter.analyze_evidence(
        "Vaccines reduce infection risk.",
        "Vaccination reduces infection risk."
    )

    assert result["relevance_status"] == "Relevant"
    assert result["classification"] == "Supporting"
    assert relevance_filter.evidence_analyzer.called


def test_low_relevance_skips_nli(relevance_filter):

    relevance_filter.model.encode = lambda *args, **kwargs: (
        torch.tensor([
            [1.0, 0.0],
            [0.0, 1.0]
        ])
    )

    result = relevance_filter.analyze_evidence(
        "Vaccines reduce infection risk.",
        "The weather is sunny."
    )

    assert result["relevance_status"] == "Low Relevance"
    assert result["classification"] == "Insufficient"
    assert not relevance_filter.evidence_analyzer.called


def test_empty_claim(relevance_filter):

    result = relevance_filter.analyze_evidence(
        "",
        "Vaccination reduces infection risk."
    )

    assert result["classification"] == "Insufficient"


def test_empty_evidence(relevance_filter):

    result = relevance_filter.analyze_evidence(
        "Vaccines reduce infection risk.",
        ""
    )

    assert result["classification"] == "Insufficient"


def test_invalid_input(relevance_filter):

    with pytest.raises(TypeError):
        relevance_filter.analyze_evidence(
            None,
            "Evidence"
        )


def test_invalid_threshold():

    with pytest.raises(ValueError):
        RelevanceFilter.__init__(
            RelevanceFilter.__new__(RelevanceFilter),
            relevance_threshold=2.0
        )


def test_calculate_relevance(relevance_filter):

    score = relevance_filter.calculate_relevance(
        "Claim",
        "Evidence"
    )

    assert score == pytest.approx(1.0)