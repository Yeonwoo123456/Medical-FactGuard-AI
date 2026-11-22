
from typing import List, Dict, Any, Optional, Tuple

from backend.retrieval.pubmed_retriever import PubMedRetriever
from backend.algorithms.search_result_evaluator import SearchResultEvaluator


class LocalSearchOptimizer:
    """
    Optimizes PubMed search queries and ranks retrieved articles.

    Search strategy:
    1. Original medical claim
    2. Systematic reviews and meta-analyses
    3. Randomized controlled trials
    4. Safety and adverse events
    5. Observational studies

    Relevance scores measure textual relevance only.
    They do not indicate whether a medical claim is true.
    """

    def __init__(
        self,
        retriever: Optional[PubMedRetriever] = None,
        evaluator: Optional[SearchResultEvaluator] = None,
        beam_width: int = 3,
        max_results_per_query: int = 10,
    ):
        self.retriever = retriever or PubMedRetriever(
            max_results=max_results_per_query
        )

        self.evaluator = evaluator or SearchResultEvaluator()

        self.beam_width = max(1, beam_width)
        self.max_results_per_query = max_results_per_query
        self._owns_retriever = retriever is None

        self.search_directions = [
            "supporting evidence",
            "contradicting evidence",
            "clinical studies",
            "systematic review",
            "scientific research",
            "risk and safety",
        ]

    # --------------------------------------------------
    # 1. Document normalization
    # --------------------------------------------------

    @staticmethod
    def normalize_documents(
        documents: Optional[List[Any]],
    ) -> List[Dict[str, Any]]:
        """
        Converts string documents and dictionary documents
        into a consistent dictionary format.
        """

        if not documents:
            return []

        normalized = []

        for document in documents:

            if isinstance(document, str):

                text = document.strip()

                if not text:
                    continue

                normalized.append({
                    "title": text,
                    "abstract": "",
                    "pmid": None,
                    "url": None,
                })

            elif isinstance(document, dict):

                normalized.append({
                    **document,
                    "title": str(document.get("title") or ""),
                    "abstract": str(document.get("abstract") or ""),
                })

        return normalized

    # --------------------------------------------------
    # 2. Query generation
    # --------------------------------------------------

    def generate_candidates(self, claim: str) -> List[str]:
        """Generates different PubMed search queries."""

        if not claim or not claim.strip():
            return []

        claim = claim.strip()

        candidates = [
            claim,
            (
                f"({claim}) AND "
                "(systematic review[Publication Type] "
                "OR meta-analysis[Publication Type])"
            ),
            (
                f"({claim}) AND "
                "(randomized controlled trial[Publication Type])"
            ),
            (
                f"({claim}) AND "
                "(adverse events OR safety OR harms)"
            ),
            (
                f"({claim}) AND "
                "(cohort OR observational OR case-control)"
            ),
        ]

        return list(dict.fromkeys(candidates))

    # --------------------------------------------------
    # 3. Query scoring
    # --------------------------------------------------

    def score_query(
        self,
        query: str,
        documents: List[Any],
    ) -> float:
        """
        Scores a query using the textual relevance
        of the supplied documents.

        Supports both strings and dictionaries.
        """

        normalized_documents = self.normalize_documents(documents)

        if not normalized_documents:
            return 0.0

        scores = []

        for document in normalized_documents:

            title = document.get("title", "")
            abstract = document.get("abstract", "")

            document_text = f"{title} {abstract}".strip()

            if not document_text:
                continue

            similarity = self.evaluator.calculate_cosine_similarity(
                query,
                document_text,
            )

            scores.append(float(similarity))

        if not scores:
            return 0.0

        scores.sort(reverse=True)

        top_scores = scores[:3]

        return sum(top_scores) / len(top_scores)

    # --------------------------------------------------
    # 4. Beam search
    # --------------------------------------------------

    def beam_search(
        self,
        claim: str,
        documents: List[Any],
    ) -> List[Tuple[str, float]]:
        """
        Ranks generated search candidates.

        This method uses supplied documents.
        It does not perform PubMed requests.
        """

        candidates = self.generate_candidates(claim)

        scored_candidates = []

        for query in candidates:

            score = self.score_query(
                query,
                documents,
            )

            scored_candidates.append(
                (query, score)
            )

        scored_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scored_candidates[:self.beam_width]

    # --------------------------------------------------
    # 5. Neighbor generation
    # --------------------------------------------------

    def generate_neighbors(self, query: str) -> List[str]:
        """Generates neighboring queries."""

        if not query or not query.strip():
            return []

        neighbors = []
        query_lower = query.lower()

        for direction in self.search_directions:

            if direction.lower() not in query_lower:

                neighbors.append(
                    f"{query} {direction}"
                )

        return neighbors

    # --------------------------------------------------
    # 6. Hill climbing
    # --------------------------------------------------

    def hill_climbing(
        self,
        initial_query: str,
        documents: List[Any],
        max_iterations: int = 5,
    ) -> str:
        """
        Improves a query using a fixed document set.

        Returns the optimized query string.
        Does not retrieve new documents during iterations.
        """

        if not initial_query or not initial_query.strip():
            return ""

        current_query = initial_query.strip()

        current_score = self.score_query(
            current_query,
            documents,
        )

        for _ in range(max(0, max_iterations)):

            neighbors = self.generate_neighbors(
                current_query
            )

            if not neighbors:
                break

            best_query = current_query
            best_score = current_score

            for neighbor in neighbors:

                neighbor_score = self.score_query(
                    neighbor,
                    documents,
                )

                if neighbor_score > best_score:

                    best_query = neighbor
                    best_score = neighbor_score

            if best_query == current_query:
                break

            current_query = best_query
            current_score = best_score

        return current_query

    # --------------------------------------------------
    # 7. Article deduplication
    # --------------------------------------------------

    @staticmethod
    def deduplicate_articles(
        articles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Removes duplicate articles using PMID."""

        unique_articles = []
        seen_pmids = set()

        for article in articles:

            if not isinstance(article, dict):
                continue

            pmid = article.get("pmid")

            if pmid:

                pmid = str(pmid)

                if pmid in seen_pmids:
                    continue

                seen_pmids.add(pmid)

            unique_articles.append(article)

        return unique_articles

    # --------------------------------------------------
    # 8. PubMed retrieval
    # --------------------------------------------------

    def retrieve_candidates(
        self,
        claim: str,
    ) -> Dict[str, Any]:
        """
        Executes generated PubMed queries and evaluates
        the retrieved articles.
        """

        queries = self.generate_candidates(claim)

        query_results = []
        all_articles = []

        for query in queries:

            try:

                articles = self.retriever.retrieve(query)

                if not isinstance(articles, list):
                    articles = []

                query_score = self.evaluator.calculate_query_score(
                    claim,
                    articles,
                )

                query_results.append({
                    "query": query,
                    "score": float(query_score),
                    "article_count": len(articles),
                    "status": "success",
                })

                all_articles.extend(articles)

            except Exception as error:

                query_results.append({
                    "query": query,
                    "score": 0.0,
                    "article_count": 0,
                    "status": "failed",
                    "error": str(error),
                })

        unique_articles = self.deduplicate_articles(
            all_articles
        )

        ranked_articles = self.evaluator.evaluate_articles(
            claim,
            unique_articles,
        )

        query_results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        selected_queries = query_results[:self.beam_width]

        return {
            "articles": ranked_articles,
            "query_results": query_results,
            "selected_queries": selected_queries,
            "retrieved_article_count": len(unique_articles),
            "evaluated_query_count": len(queries),
        }

    # --------------------------------------------------
    # 9. Main optimization pipeline
    # --------------------------------------------------

    def optimize(
        self,
        claim: str,
        documents: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point.

        If documents are supplied:
            Uses existing documents for query optimization.

        If documents are None:
            Retrieves articles from PubMed.
        """

        if not claim or not claim.strip():

            return {
                "articles": [],
                "retrieved_article_count": 0,
                "evaluated_query_count": 0,
                "optimized_queries": [],
                "beam_search_results": [],
                "article_relevance": [],
                "optimization_note": "Empty claim provided.",
            }

        claim = claim.strip()

        # Compatibility mode:
        # Use supplied documents without PubMed retrieval.
        if documents is not None:

            normalized_documents = self.normalize_documents(
                documents
            )

            beam_results = self.beam_search(
                claim,
                normalized_documents,
            )

            best_query = self.hill_climbing(
                claim,
                normalized_documents,
            )

            ranked_articles = self.evaluator.evaluate_articles(
                claim,
                normalized_documents,
            )

            return {
                "articles": ranked_articles,
                "retrieved_article_count": len(normalized_documents),
                "evaluated_query_count": len(
                    self.generate_candidates(claim)
                ),
                "optimized_queries": [best_query] if best_query else [],
                "beam_search_results": [
                    {
                        "query": query,
                        "score": score,
                    }
                    for query, score in beam_results
                ],
                "article_relevance": [
                    article.get("relevance", {})
                    for article in ranked_articles
                ],
                "optimization_note": (
                    "Used supplied documents. "
                    "No new PubMed retrieval was performed."
                ),
            }

        # Actual PubMed retrieval mode.
        search_result = self.retrieve_candidates(claim)

        articles = search_result["articles"]
        selected_queries = search_result["selected_queries"]

        return {
            "articles": articles,
            "retrieved_article_count": (
                search_result["retrieved_article_count"]
            ),
            "evaluated_query_count": (
                search_result["evaluated_query_count"]
            ),
            "optimized_queries": [
                item["query"]
                for item in selected_queries
            ],
            "beam_search_results": [
                {
                    "query": item["query"],
                    "score": item["score"],
                    "article_count": item["article_count"],
                    "status": item["status"],
                }
                for item in selected_queries
            ],
            "article_relevance": [
                article.get("relevance", {})
                for article in articles
            ],
            "optimization_note": (
                "Articles were retrieved using multiple PubMed "
                "search strategies and ranked by lexical relevance. "
                "Relevance does not establish truth or study quality."
            ),
            "query_results": search_result["query_results"],
        }

    # --------------------------------------------------
    # 10. Resource management
    # --------------------------------------------------

    def close(self):
        """Closes the PubMed session if this class owns it."""

        if self._owns_retriever:
            self.retriever.close()


if __name__ == "__main__":

    optimizer = LocalSearchOptimizer(
        beam_width=3,
        max_results_per_query=5,
    )

    try:

        test_claim = (
            "Vaccines reduce the risk of severe infectious disease."
        )

        result = optimizer.optimize(test_claim)

        print("\n========== SEARCH SUMMARY ==========")

        print(
            "Evaluated queries:",
            result["evaluated_query_count"],
        )

        print(
            "Retrieved articles:",
            result["retrieved_article_count"],
        )

        print("\n========== OPTIMIZED QUERIES ==========")

        for item in result["beam_search_results"]:

            print(f"\nQuery: {item['query']}")
            print(f"Score: {item['score']}")

            if "status" in item:
                print(f"Status: {item['status']}")

        print("\n========== TOP ARTICLES ==========")

        for article in result["articles"][:5]:

            print("\nTitle:", article.get("title"))
            print("PMID:", article.get("pmid"))

            print(
                "Relevance:",
                article.get("relevance", {}).get(
                    "relevance_score",
                    0.0,
                ),
            )

            print("URL:", article.get("url"))

    finally:
        optimizer.close()
