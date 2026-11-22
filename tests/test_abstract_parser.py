import pytest

from backend.retrieval.abstract_parser import AbstractParser


@pytest.fixture
def parser():
    return AbstractParser()


def test_structured_abstract(parser):

    abstract = """
    BACKGROUND: HPV infection is associated with cancer.
    OBJECTIVE: To evaluate vaccine effectiveness.
    METHODS: We analyzed 100 participants.
    RESULTS: Vaccines reduced infection.
    CONCLUSIONS: Vaccines were effective.
    """

    results = parser.parse(abstract)

    section_types = [
        item["section_type"]
        for item in results
    ]

    assert "Background" in section_types
    assert "Research Objective" in section_types
    assert "Research Method" in section_types
    assert "Research Result" in section_types
    assert "Conclusion" in section_types


def test_missing_space_after_heading(parser):

    abstract = (
        "Adverse effectsThe risk was similar "
        "between groups."
    )

    sections = parser.extract_sections(abstract)

    assert sections[0]["section_type"] == "Safety Result"


def test_unstructured_abstract(parser):

    abstract = (
        "This study evaluated vaccine effectiveness. "
        "The results showed reduced infection."
    )

    sections = parser.extract_sections(abstract)

    assert len(sections) == 1
    assert sections[0]["section"] == "Unstructured"


def test_decimal_protection(parser):

    sentences = parser.split_sentences(
        "The mean age was 3.14 years. "
        "The results were significant."
    )

    assert len(sentences) == 2
    assert "3.14" in sentences[0]


def test_abbreviation_protection(parser):

    sentences = parser.split_sentences(
        "The result was significant, e.g. "
        "in the treatment group. "
        "The control group showed no effect."
    )

    assert len(sentences) == 2
    assert "e.g." in sentences[0]


def test_empty_abstract(parser):

    assert parser.parse("") == []


def test_non_string_input(parser):

    assert parser.parse(None) == []


def test_short_sentence_preserved(parser):

    sentences = parser.split_sentences(
        "No effect. The result was significant."
    )

    assert len(sentences) == 2
    assert sentences[0] == "No effect."


def test_conclusion_heading(parser):

    sections = parser.extract_sections(
        "AUTHORS' CONCLUSIONS: The treatment was effective."
    )

    assert sections[0]["section_type"] == "Conclusion"


def test_safety_section(parser):

    sections = parser.extract_sections(
        "ADVERSE EVENTS: No serious adverse events occurred."
    )

    assert sections[0]["section_type"] == "Safety Result"