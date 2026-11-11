
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from backend.algorithms.similarity import SemanticSimilarity


def run_tests():

    model = SemanticSimilarity()

    claim = "Vaccines can reduce the risk of infectious diseases."

    # Test 1: Similar sentence
    similar = (
        "Vaccines reduce the risk of infectious diseases."
    )

    score1 = model.calculate_similarity(claim, similar)

    test1 = score1 > 0

    # Test 2: Unrelated sentence
    unrelated = "The weather is sunny today."

    score2 = model.calculate_similarity(claim, unrelated)

    test2 = score2 == 0

    # Test 3: Empty sentence
    score3 = model.calculate_similarity("", similar)

    test3 = score3 == 0

    # Test 4: Multiple evidence comparison
    evidences = [
        similar,
        unrelated,
        "Vaccination may lower the likelihood of contracting certain diseases."
    ]

    results = model.compare_multiple(claim, evidences)

    test4 = (
        len(results) == len(evidences)
        and results[0]["similarity"] >= results[-1]["similarity"]
    )

    tests = [
        test1,
        test2,
        test3,
        test4
    ]

    print("\nSEMANTIC SIMILARITY TEST")
    print("=" * 55)

    for index, result in enumerate(tests, start=1):

        print(
            f"Test {index}:",
            "PASS" if result else "FAIL"
        )

    print("\nTEST SUMMARY")
    print("-" * 55)
    print(f"Passed: {sum(tests)}/{len(tests)}")
    print(f"Success Rate: {sum(tests)/len(tests):.2%}")

    print("\nSIMILARITY SCORES")
    print("-" * 55)
    print(f"Direct similarity: {score1:.4f}")
    print(f"Unrelated similarity: {score2:.4f}")


if __name__ == "__main__":
    run_tests()