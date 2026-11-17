"""
Safety-classification validation for Medical FactGuard AI.

Run from the project root:
    python validate_safety.py

This script performs:
1. Rule-based regression tests with expected labels.
2. Exploratory checks on abstracts retrieved from PubMed.

Important:
- The hand-written examples are software tests, not clinical validation.
- PubMed results are exploratory; regex outputs require human review.
- A safety signal is not proof that a treatment is safe or harmful.
"""

from collections import Counter

from backend.evidence_pipeline import EvidencePipeline


REGRESSION_CASES = [
    {
        "name": "Concern about possible adverse events",
        "sentence": (
            "Concerns about possible adverse events may delay vaccine acceptance."
        ),
        "expected": {
            "safety_topic": True,
            "safety_result": False,
            "safety_concern": True,
        },
    },
    {
        "name": "Observed adverse events",
        "sentence": (
            "Serious adverse events were reported in 12 participants."
        ),
        "expected": {
            "safety_topic": True,
            "safety_result": True,
            "safety_concern": False,
        },
    },
    {
        "name": "Comparable adverse event rates",
        "sentence": (
            "The risk of serious adverse events was similar between groups."
        ),
        "expected": {
            "safety_topic": True,
            "safety_result": True,
            "safety_concern": False,
        },
    },
    {
        "name": "Risk cannot be excluded",
        "sentence": (
            "An increased risk of adverse pregnancy outcomes cannot be excluded."
        ),
        "expected": {
            "safety_topic": True,
            "safety_result": True,
            "safety_concern": True,
        },
    },
    {
        "name": "Generic disease mortality",
        "sentence": (
            "Respiratory infections are important causes of morbidity and mortality."
        ),
        "expected": {
            "safety_topic": False,
            "safety_result": False,
            "safety_concern": False,
        },
    },
    {
        "name": "Effectiveness result without safety topic",
        "sentence": (
            "Vaccination was associated with a reduced risk of cardiovascular events."
        ),
        "expected": {
            "safety_topic": False,
            "safety_result": False,
            "safety_concern": False,
        },
    },
    {
        "name": "Pregnancy outcome result",
        "sentence": (
            "Pregnancy outcomes were similar in the intervention and control groups."
        ),
        "expected": {
            "safety_topic": True,
            "safety_result": True,
            "safety_concern": False,
        },
    },
    {
        "name": "Safety topic only",
        "sentence": (
            "The study discusses the long-term safety of the medication."
        ),
        "expected": {
            "safety_topic": False,
            "safety_result": False,
            "safety_concern": False,
        },
    },
]


PUBMED_QUERIES = [
    "vaccine adverse events safety clinical trial",
    "medication adverse effects randomized controlled trial",
    "vaccination pregnancy outcomes miscarriage safety",
]


def run_regression_tests(pipeline):
    print("\n" + "=" * 78)
    print("1. RULE-BASED REGRESSION TESTS")
    print("=" * 78)

    passed = 0
    failed = 0

    for case in REGRESSION_CASES:
        actual = pipeline.detect_safety_signals(case["sentence"])
        expected = case["expected"]

        mismatches = {
            key: {"expected": expected[key], "actual": actual[key]}
            for key in expected
            if actual[key] != expected[key]
        }

        if mismatches:
            failed += 1
            status = "FAIL"
        else:
            passed += 1
            status = "PASS"

        print(f"\n[{status}] {case['name']}")
        print("Sentence:", case["sentence"])
        print(
            "Signals:",
            {
                key: actual[key]
                for key in (
                    "safety_topic",
                    "safety_result",
                    "safety_concern",
                )
            },
        )

        if mismatches:
            print("Mismatches:", mismatches)

    total = passed + failed
    print("\nRegression summary:")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")

    return passed, failed


def run_pubmed_exploration(pipeline):
    print("\n" + "=" * 78)
    print("2. EXPLORATORY PUBMED ABSTRACT CHECK")
    print("=" * 78)
    print(
        "This section checks retrieved abstract sentences. "
        "It does not provide human-verified accuracy."
    )

    for query in PUBMED_QUERIES:
        print("\n" + "-" * 78)
        print("Query:", query)

        try:
            articles = pipeline.pubmed_retriever.retrieve(query)
        except Exception as exc:
            print(f"Retrieval error: {type(exc).__name__}: {exc}")
            continue

        if not isinstance(articles, list) or not articles:
            print("No articles returned.")
            continue

        print("Articles retrieved:", len(articles))

        totals = Counter()
        displayed = 0

        for article in articles:
            if not isinstance(article, dict):
                continue

            abstract = article.get("abstract", "")
            if not abstract:
                continue

            sentences = pipeline.abstract_parser.parse(abstract)

            article_signals = []
            for item in sentences:
                sentence = item.get("sentence", "")
                if not sentence:
                    continue

                signals = pipeline.detect_safety_signals(
                    sentence,
                    item.get("section_type", "Other"),
                )

                for key in (
                    "safety_topic",
                    "safety_result",
                    "safety_concern",
                ):
                    totals[key] += int(signals[key])

                if (
                    signals["safety_topic"]
                    or signals["safety_result"]
                    or signals["safety_concern"]
                ):
                    article_signals.append((sentence, signals))

            if article_signals:
                displayed += 1
                print("\nPMID:", article.get("pmid", "Not provided"))
                print("Title:", article.get("title", "Not provided"))

                for sentence, signals in article_signals:
                    print("\nSentence:", sentence)
                    print("Safety Topic:", signals["safety_topic"])
                    print("Safety Result:", signals["safety_result"])
                    print("Safety Concern:", signals["safety_concern"])

        print("\nSignal totals for this query:")
        print("Safety-topic sentences:", totals["safety_topic"])
        print("Safety-result sentences:", totals["safety_result"])
        print("Safety-concern sentences:", totals["safety_concern"])
        print("Articles with at least one safety signal:", displayed)


def main():
    pipeline = EvidencePipeline()

    passed, failed = run_regression_tests(pipeline)
    run_pubmed_exploration(pipeline)

    print("\n" + "=" * 78)
    if failed == 0:
        print("Regression tests passed.")
    else:
        print(
            "Some regression tests failed. Review the mismatched patterns "
            "before using the classifier."
        )

    print(
        "\nReminder: inspect retrieved sentences manually. "
        "Regex classification is a screening aid, not a validated "
        "medical safety assessment."
    )


if __name__ == "__main__":
    main()
