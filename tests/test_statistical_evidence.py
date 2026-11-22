import pytest

from backend.algorithms.statistical_evidence import (
    StatisticalEvidenceAnalyzer
)


@pytest.fixture
def analyzer():
    return StatisticalEvidenceAnalyzer()


def test_risk_ratio(analyzer):

    result = analyzer.analyze(
        "The risk was reduced (RR 0.74 (0.52 to 1.05))."
    )

    assert result["measure"] == "RR"
    assert result["estimate"] == 0.74
    assert result["null_value"] == 1.0
    assert result["includes_null"] is True


def test_odds_ratio(analyzer):

    result = analyzer.analyze(
        "The odds ratio was 0.65 (0.50 to 0.80)."
    )

    assert result["measure"] == "OR"
    assert result["estimate"] == 0.65
    assert result["includes_null"] is False


def test_hazard_ratio(analyzer):

    result = analyzer.analyze(
        "The hazard ratio was 1.45 (1.10 to 1.90)."
    )

    assert result["measure"] == "HR"
    assert result["null_value"] == 1.0


def test_mean_difference(analyzer):

    result = analyzer.analyze(
        "Mean difference was -5.2 (95% CI, -8.1 to -2.3)."
    )

    assert result["measure"] == "MD"
    assert result["null_value"] == 0.0
    assert result["includes_null"] is False


def test_risk_difference(analyzer):

    result = analyzer.analyze(
        "Risk difference was -0.12 (-0.20 to -0.04)."
    )

    assert result["measure"] == "RD"
    assert result["null_value"] == 0.0


def test_percentage_not_misclassified(analyzer):

    result = analyzer.analyze(
        "The outcome occurred in 60.2% "
        "(95% confidence interval, 40.8 to 73.8)."
    )

    assert result["available"] is False


def test_duration_not_misclassified(analyzer):

    result = analyzer.analyze(
        "Patients received treatment for 5 days."
    )

    assert result["available"] is False


def test_invalid_confidence_interval(analyzer):

    result = analyzer.analyze(
        "The odds ratio was 0.65 (0.90 to 0.50)."
    )

    assert result["confidence_interval"] is None


def test_estimate_within_ci(analyzer):

    result = analyzer.analyze(
        "The odds ratio was 0.65 (0.50 to 0.80)."
    )

    assert result["estimate_within_ci"] is True


def test_empty_sentence(analyzer):

    result = analyzer.analyze("")

    assert result["available"] is False


# --------------------------------------------------
# New tests
# --------------------------------------------------

def test_rsv_ve_ci_not_mixed_with_rr_ci(analyzer):

    sentence = (
        "RSV-associated illness with VE of -0.37% "
        "(95% CI -1.96 to 0.37; RR 1.37, "
        "95% CI 0.63 to 2.96)."
    )

    result = analyzer.analyze(sentence)

    assert result["measure"] == "RR"
    assert result["estimate"] == 1.37

    assert result["confidence_interval"] == {
        "lower": 0.63,
        "upper": 2.96
    }

    assert result["includes_null"] is True
    assert result["estimate_within_ci"] is True


def test_multiple_risk_ratios(analyzer):

    sentence = (
        "Vaccination reduced dementia risk "
        "(RR 0.76, 95% CI 0.69-0.83) "
        "and Alzheimer's disease "
        "(RR 0.53, 95% CI 0.44-0.64)."
    )

    result = analyzer.analyze(sentence)

    assert result["measure"] == "RR"
    assert result["estimate"] == 0.76

    additional = result["additional_estimates"]

    assert len(additional) == 1
    assert additional[0]["measure"] == "RR"
    assert additional[0]["estimate"] == 0.53

    assert additional[0]["confidence_interval"] == {
        "lower": 0.44,
        "upper": 0.64
    }


def test_negative_ratio_ci_rejected(analyzer):

    result = analyzer.analyze(
        "The risk ratio was 1.2 (95% CI -0.2 to 2.0)."
    )

    assert result["confidence_interval"] is None


def test_zero_ratio_ci_rejected(analyzer):

    result = analyzer.analyze(
        "The odds ratio was 0.8 (95% CI 0 to 1.2)."
    )

    assert result["confidence_interval"] is None


def test_multiple_measures_count(analyzer):

    sentence = (
        "The result was RR 0.8 (0.7 to 0.9) "
        "and OR 0.6 (0.5 to 0.8)."
    )

    result = analyzer.analyze_all(sentence)

    assert result["available"] is True
    assert len(result["results"]) == 2

    assert result["results"][0]["measure"] == "RR"
    assert result["results"][1]["measure"] == "OR"


def test_estimate_outside_ci(analyzer):

    result = analyzer.analyze(
        "The risk ratio was 1.5 (0.7 to 1.2)."
    )

    assert result["estimate_within_ci"] is False
    assert "WARNING" in result["statistical_interpretation"]


def test_difference_measure_allows_negative_ci(analyzer):

    result = analyzer.analyze(
        "Mean difference was -5.2 "
        "(95% CI -8.1 to -2.3)."
    )

    assert result["measure"] == "MD"
    assert result["confidence_interval"]["lower"] == -8.1
    assert result["confidence_interval"]["upper"] == -2.3


def test_extract_all_measures(analyzer):

    result = analyzer.extract_measures(
        "RR 0.76 (0.69 to 0.83) and OR 0.53 (0.44 to 0.64)."
    )

    assert len(result) == 2