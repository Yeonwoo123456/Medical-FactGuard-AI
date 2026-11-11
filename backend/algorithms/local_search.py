
import re
import math
from collections import Counter


class LocalSearchOptimizer:

    def __init__(self, beam_width=3, max_iterations=5):

        self.beam_width = beam_width
        self.max_iterations = max_iterations

        self.search_directions = [
            "supporting evidence",
            "contradicting evidence",
            "clinical studies",
            "systematic review",
            "scientific research",
            "risk and safety"
        ]

        self.stopwords = {
            "the", "a", "an", "is", "are", "was", "were",
            "be", "been", "being", "can", "could", "may",
            "might", "will", "would", "should", "of", "to",
            "in", "on", "at", "for", "and", "or", "but",
            "that", "this", "these", "those", "with", "from",
            "by", "as", "it", "its", "some", "people"
        }

    # Convert text into meaningful tokens
    def tokenize(self, text):

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

        return [
            word for word in words
            if word not in self.stopwords
        ]

    # Generate alternative search queries
    def generate_candidates(self, claim):

        candidates = [claim]

        for direction in self.search_directions:

            candidates.append(
                f"{claim} {direction}"
            )

        return candidates

    # Calculate cosine similarity between query and document
    def calculate_similarity(self, query, document):

        query_tokens = Counter(self.tokenize(query))
        document_tokens = Counter(self.tokenize(document))

        if not query_tokens or not document_tokens:
            return 0.0

        common_words = (
            query_tokens.keys() & document_tokens.keys()
        )

        dot_product = sum(
            query_tokens[word] * document_tokens[word]
            for word in common_words
        )

        query_norm = math.sqrt(
            sum(value ** 2 for value in query_tokens.values())
        )

        document_norm = math.sqrt(
            sum(value ** 2 for value in document_tokens.values())
        )

        if query_norm == 0 or document_norm == 0:
            return 0.0

        return dot_product / (query_norm * document_norm)

    # Evaluate query relevance against available documents
    def score_query(self, query, documents):

        if not documents:
            return 0.0

        similarities = [
            self.calculate_similarity(query, document)
            for document in documents
        ]

        similarities.sort(reverse=True)

        # Average the three most relevant documents
        top_results = similarities[:3]

        return sum(top_results) / len(top_results)

    # Beam Search
    def beam_search(self, claim, documents):

        candidates = self.generate_candidates(claim)

        scored_candidates = []

        for query in candidates:

            score = self.score_query(query, documents)

            scored_candidates.append({
                "query": query,
                "score": score
            })

        scored_candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored_candidates[:self.beam_width]

    # Generate neighboring queries
    def generate_neighbors(self, query):

        neighbors = []

        for direction in self.search_directions:

            if direction not in query.lower():

                neighbors.append(
                    f"{query} {direction}"
                )

        return neighbors

    # Hill Climbing
    def hill_climbing(self, initial_query, documents):

        current_query = initial_query
        current_score = self.score_query(
            current_query, documents
        )

        for _ in range(self.max_iterations):

            neighbors = self.generate_neighbors(
                current_query
            )

            if not neighbors:
                break

            best_neighbor = current_query
            best_score = current_score

            for neighbor in neighbors:

                score = self.score_query(
                    neighbor, documents
                )

                if score > best_score:
                    best_score = score
                    best_neighbor = neighbor

            # Stop when no better neighbor exists
            if best_score <= current_score:
                break

            current_query = best_neighbor
            current_score = best_score

        return {
            "query": current_query,
            "score": current_score
        }

    # Combine Beam Search and Hill Climbing
    def optimize(self, claim, documents):

        beam_results = self.beam_search(
            claim, documents
        )

        optimized_results = []

        for candidate in beam_results:

            result = self.hill_climbing(
                candidate["query"],
                documents
            )

            optimized_results.append(result)

        # Remove duplicate queries
        unique_results = {}

        for result in optimized_results:

            query = result["query"]

            if (
                query not in unique_results
                or result["score"] > unique_results[query]["score"]
            ):
                unique_results[query] = result

        final_results = list(unique_results.values())

        final_results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return {
            "original_claim": claim,
            "beam_search_results": beam_results,
            "optimized_queries": final_results
        }


if __name__ == "__main__":

    optimizer = LocalSearchOptimizer(
        beam_width=3,
        max_iterations=5
    )

    claim = (
        "Vaccines cause serious side effects "
        "and infectious diseases"
    )

    # Demonstration evidence documents.
    # These are synthetic examples, not real medical research.
    sample_documents = [

        "Clinical studies investigate vaccine safety "
        "and possible side effects.",

        "Scientific research evaluates whether vaccines "
        "cause adverse reactions.",

        "Systematic reviews examine vaccine effectiveness "
        "and safety.",

        "Research evaluates claims about vaccine risks "
        "and infectious diseases.",

        "Some studies report adverse events after vaccination."
    ]

    results = optimizer.optimize(
        claim,
        sample_documents
    )

    print("\nLOCAL SEARCH OPTIMIZATION")
    print("=" * 60)

    print("\nOriginal Claim:")
    print(results["original_claim"])

    print("\nBEAM SEARCH RESULTS")
    print("-" * 60)

    for index, item in enumerate(
        results["beam_search_results"], start=1
    ):

        print(f"\n{index}. Query: {item['query']}")
        print(f"   Score: {item['score']:.4f}")

    print("\nHILL CLIMBING RESULTS")
    print("-" * 60)

    for index, item in enumerate(
        results["optimized_queries"], start=1
    ):

        print(f"\n{index}. Query: {item['query']}")
        print(f"   Score: {item['score']:.4f}")