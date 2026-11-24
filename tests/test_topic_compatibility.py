from backend.evidence_pipeline import EvidencePipeline


def test_vaccine_evidence_with_vaccine_topic_is_compatible():
    result = EvidencePipeline.check_topic_compatibility(
        "Vaccines reduce the risk of infectious diseases.",
        "Vaccination was associated with a lower incidence of infection."
    )
    assert result["compatible"] is True


def test_statin_claim_rejects_unrelated_antidiarrheal_sentence():
    result = EvidencePipeline.check_topic_compatibility(
        "Statins reduce LDL cholesterol.",
        "Antidiarrheal medication should not always be taken."
    )
    assert result["compatible"] is False
    assert "statin" in result["missing_topics"]


def test_statin_claim_accepts_sentence_that_mentions_statins():
    result = EvidencePipeline.check_topic_compatibility(
        "Statins may cause gastrointestinal side effects.",
        "Statin use was associated with gastrointestinal adverse events."
    )
    assert result["compatible"] is True


def test_vaccine_claim_rejects_unrelated_cancer_only_sentence():
    result = EvidencePipeline.check_topic_compatibility(
        "Vaccines reduce infectious diseases.",
        "Cancer treatment outcomes improved after therapy."
    )
    assert result["compatible"] is False
