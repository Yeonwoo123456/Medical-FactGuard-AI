
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from backend.algorithms.local_search import LocalSearchOptimizer


def run_tests():

    optimizer = LocalSearchOptimizer(
        beam_width=3,
        max_iterations=5
    )

    claim = "Vaccines cause serious side effects"

    documents = [
        "Clinical studies investigate vaccine safety and side effects.",
        "Scientific research evaluates vaccine effectiveness and safety.",
        "Some studies examine adverse reactions after vaccination.",
        "Systematic reviews analyze vaccine risks and benefits."
    ]

    print("\nLOCAL SEARCH TEST")
    print("=" * 60)

    # Test 1: Beam Search
    beam_results = optimizer.beam_search(
        claim, documents
    )

    test1 = (
        len(beam_results) > 0
        and len(beam_results) <= optimizer.beam_width
    )

    print("\nTest 1 - Beam Search")
    print("PASS" if test1 else "FAIL")

    # Test 2: Hill Climbing
    initial_score = optimizer.score_query(
        claim, documents
    )

    hill_result = optimizer.hill_climbing(
        claim, documents
    )

    test2 = hill_result["score"] >= initial_score

    print("\nTest 2 - Hill Climbing")
    print("PASS" if test2 else "FAIL")

    # Test 3: Duplicate removal
    optimized = optimizer.optimize(
        claim, documents
    )

    queries = [
        item["query"]
        for item in optimized["optimized_queries"]
    ]

    test3 = len(queries) == len(set(queries))

    print("\nTest 3 - Duplicate Removal")
    print("PASS" if test3 else "FAIL")

    # Test 4: Empty documents
    empty_result = optimizer.optimize(
        claim, []
    )

    test4 = (
        len(empty_result["beam_search_results"]) > 0
        and all(
            item["score"] == 0
            for item in empty_result["optimized_queries"]
        )
    )

    print("\nTest 4 - Empty Documents")
    print("PASS" if test4 else "FAIL")

    # Summary
    results = [test1, test2, test3, test4]

    passed = sum(results)
    total = len(results)

    print("\nTEST SUMMARY")
    print("-" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print(f"Success Rate: {passed / total:.2%}")


if __name__ == "__main__":
    run_tests()