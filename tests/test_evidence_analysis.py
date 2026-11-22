import pytest
import torch

from types import SimpleNamespace

from backend.algorithms.evidence_analysis import EvidenceAnalyzer


class FakeTokenizer:

    def __call__(self, *args, **kwargs):

        return {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]])
        }


class FakeModel:

    def __init__(self, logits, id2label):

        self.logits = logits
        self.config = SimpleNamespace(
            id2label=id2label
        )

    def __call__(self, **kwargs):

        return SimpleNamespace(
            logits=self.logits
        )


@pytest.fixture
def analyzer():

    instance = EvidenceAnalyzer.__new__(
        EvidenceAnalyzer
    )

    instance.model_name = "cross-encoder/nli-deberta-v3-small"
    instance.confidence_threshold = 0.55
    instance.margin_threshold = 0.10
    instance.max_length = 512
    instance.device = torch.device("cpu")

    instance.tokenizer = FakeTokenizer()

    instance.id2label = {
        0: "CONTRADICTION",
        1: "ENTAILMENT",
        2: "NEUTRAL"
    }

    instance.model = FakeModel(
        torch.tensor([[0.0, 4.0, 0.0]]),
        instance.id2label
    )

    return instance


def test_supporting_classification(analyzer):

    result = analyzer.analyze(
        "Vaccines reduce infection risk.",
        "Vaccination reduces the risk of infection."
    )

    assert result["label"] == "Supporting"
    assert result["predicted_label"] == "Supporting"
    assert result["confidence"] > 0.55


def test_contradicting_classification(analyzer):

    analyzer.model.logits = torch.tensor(
        [[4.0, 0.0, 0.0]]
    )

    result = analyzer.analyze(
        "Vaccines reduce infection risk.",
        "Vaccination does not reduce infection risk."
    )

    assert result["label"] == "Contradicting"


def test_neutral_classification(analyzer):

    analyzer.model.logits = torch.tensor(
        [[0.0, 0.0, 4.0]]
    )

    result = analyzer.analyze(
        "Vaccines reduce infection risk.",
        "Vaccines are used in public health programs."
    )

    assert result["label"] == "Neutral"


def test_low_confidence_returns_insufficient(analyzer):

    analyzer.model.logits = torch.tensor(
        [[0.34, 0.33, 0.33]]
    )

    result = analyzer.analyze(
        "Claim",
        "Evidence"
    )

    assert result["label"] == "Insufficient"


def test_empty_input(analyzer):

    result = analyzer.analyze(
        "",
        "Evidence"
    )

    assert result["label"] == "Insufficient"


def test_invalid_input(analyzer):

    with pytest.raises(TypeError):

        analyzer.analyze(
            None,
            "Evidence"
        )


def test_generic_label_mapping_for_known_model(analyzer):

    result = analyzer._normalize_label(
        "LABEL_0",
        0
    )

    assert result == "Contradicting"


def test_unknown_model_generic_label_rejected(analyzer):

    analyzer.model_name = "unknown-nli-model"

    with pytest.raises(ValueError):

        analyzer._normalize_label(
            "LABEL_0",
            0
        )