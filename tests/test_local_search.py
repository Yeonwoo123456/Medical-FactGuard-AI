
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest

from backend.algorithms.local_search import LocalSearchOptimizer


@pytest.fixture
def optimizer():
    instance = LocalSearchOptimizer(
        beam_width=3,
        max_results_per_query=10,
    )

    yield instance

    instance.close()


@pytest.fixture
def claim():
    return "Vaccines cause serious side effects"


@pytest.fixture
def documents():
    return [
        "Clinical studies investigate vaccine safety and side effects.",
        "Scientific research evaluates vaccine effectiveness and safety.",
        "Some studies examine adverse reactions after vaccination.",
        "Systematic reviews analyze vaccine risks and benefits.",
    ]


def test_beam_search(optimizer, claim, documents):

    results = optimizer.beam_search(
        claim,
        documents,
    )

    assert isinstance(results, list)
    assert len(results) > 0
    assert len(results) <= optimizer.beam_width

    for query, score in results:
        assert isinstance(query, str)
        assert isinstance(score, float)


def test_hill_climbing(optimizer, claim, documents):

    initial_score = optimizer.score_query(
        claim,
        documents,
    )

    optimized_query = optimizer.hill_climbing(
        claim,
        documents,
        max_iterations=5,
    )

    optimized_score = optimizer.score_query(
        optimized_query,
        documents,
    )

    assert isinstance(optimized_query, str)
    assert optimized_query.strip() != ""
    assert optimized_score >= initial_score


def test_duplicate_removal(optimizer, claim, documents):

    candidates = optimizer.generate_candidates(claim)

    assert len(candidates) == len(set(candidates))

    result = optimizer.optimize(
        claim,
        documents,
    )

    queries = result["optimized_queries"]

    assert isinstance(queries, list)
    assert all(isinstance(query, str) for query in queries)
    assert len(queries) == len(set(queries))


def test_empty_documents(optimizer, claim):

    result = optimizer.optimize(
        claim,
        [],
    )

    assert isinstance(result, dict)

    assert result["retrieved_article_count"] == 0
    assert result["articles"] == []

    beam_results = result["beam_search_results"]

    assert len(beam_results) > 0

    assert all(
        item["score"] == 0.0
        for item in beam_results
    )

    assert result["optimized_queries"] == [claim]
