# backend/algorithms/local_search.py

import re
from typing import Any, Dict, List, Optional, Tuple

from backend.retrieval.pubmed_retriever import PubMedRetriever
from backend.algorithms.search_result_evaluator import SearchResultEvaluator


class LocalSearchOptimizer:
    """
    PubMed search optimizer with medical concept expansion
    and progressive query relaxation.

    Relevance scores represent textual relevance only.
    They do not establish whether a medical claim is true.
    """

    # Maximum number of unique articles passed to the analysis pipeline.
    MAX_TOTAL_ARTICLES = 10

    # --------------------------------------------------
    # Medical concept dictionary
    # --------------------------------------------------

    MEDICAL_CONCEPTS = {
        # Specific organism/disease concepts must appear before broad
        # concepts such as "infectious_disease" and "cancer". This keeps
        # the first PubMed query focused on the actual claim.
        "helicobacter_pylori": {
            "mesh": "Helicobacter pylori",
            "terms": [
                "helicobacter pylori",
                "h pylori",
                "h pylori infection",
                "helicobacter infection",
                "helicobacter pylori infection",
            ],
        },
        "gastric_cancer": {
            "mesh": "Stomach Neoplasms",
            "terms": [
                "gastric cancer",
                "stomach cancer",
                "gastric carcinoma",
                "stomach carcinoma",
                "gastric neoplasm",
                "stomach neoplasm",
                "stomach neoplasms",
                "gastric adenocarcinoma",
            ],
        },
        "vaccine": {
            "mesh": "Vaccines",
            "terms": [
                "vaccine",
                "vaccines",
                "vaccination",
                "vaccinations",
                "immunization",
                "immunisation",
            ],
        },
        "immunity": {
            "mesh": "Immunity",
            "terms": [
                "immunity",
                "immune response",
                "immune system",
                "immune responses",
                "immunogenicity",
                "antibody",
                "antibodies",
            ],
        },
        "infectious_disease": {
            "mesh": "Communicable Diseases",
            "terms": [
                "infectious disease",
                "infectious diseases",
                "communicable disease",
                "communicable diseases",
                "infection",
                "infections",
                "pathogen",
                "pathogens",
            ],
        },
        "safety": {
            "mesh": "Drug-Related Side Effects and Adverse Reactions",
            "terms": [
                "safety",
                "adverse event",
                "adverse events",
                "adverse effect",
                "adverse effects",
                "side effect",
                "side effects",
                "harm",
                "harms",
                "risk",
                "risks",
            ],
        },
        "effectiveness": {
            "mesh": "Treatment Outcome",
            "terms": [
                "effectiveness",
                "efficacy",
                "effective",
                "prevention",
                "prevent",
                "preventing",
                "protection",
                "protective effect",
                "reduced risk",
            ],
        },
        "cancer": {
            "mesh": "Neoplasms",
            "terms": [
                "cancer",
                "cancers",
                "tumor",
                "tumour",
                "malignancy",
                "neoplasm",
                "neoplasms",
            ],
        },
        "medication": {
            "mesh": "Drug Therapy",
            "terms": [
                "medication",
                "medications",
                "drug",
                "drugs",
                "medicine",
                "medicines",
                "pharmacotherapy",
            ],
        },
        "cardiovascular": {
            "mesh": "Cardiovascular Diseases",
            "terms": [
                "cardiovascular",
                "heart disease",
                "cardiac disease",
                "blood pressure",
                "hypertension",
                "stroke",
            ],
        },
        "pregnancy": {
            "mesh": "Pregnancy",
            "terms": [
                "pregnancy",
                "pregnant",
                "maternal",
                "fetal",
                "foetal",
                "birth outcome",
                "birth outcomes",
            ],
        },
        "respiratory": {
            "mesh": "Respiratory Tract Diseases",
            "terms": [
                "respiratory",
                "lung disease",
                "pulmonary",
                "pneumonia",
                "asthma",
                "bronchitis",
            ],
        },
    }

    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were",
        "be", "been", "being", "to", "of", "in", "on",
        "at", "for", "from", "by", "with", "without",
        "and", "or", "but", "as", "that", "this",
        "these", "those", "it", "its", "their",
        "they", "them", "we", "our", "you",
        "can", "could", "may", "might", "should",
        "would", "will", "does", "do", "did",
        "has", "have", "had", "not", "than",
        "which", "who", "what", "when", "where",
        "while", "because", "therefore", "such",
        "also", "both", "each", "other", "more",
        "most", "many", "some", "any", "all",
        "very", "often", "generally", "usually",
        "biological", "preparation", "providing",
        "causing", "itself", "specific", "trains",
        "train", "recognize", "recognise", "fight",
        "system", "systems", "active",
    }

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

        self.beam_width = max(1, int(beam_width))
        self.max_results_per_query = max(
            1,
            int(max_results_per_query),
        )

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
    # 1. Text normalization
    # --------------------------------------------------

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text without discarding Korean or English medical terms."""
        if not isinstance(text, str):
            return ""

        # Remove invisible characters while preserving Hangul, Latin text,
        # digits, whitespace, and hyphens used in medical terminology.
        text = text.replace("\u200b", " ").replace("\ufeff", " ")
        text = re.sub(r"https?://\S+", " ", text, flags=re.IGNORECASE)
        text = re.sub(
            r"\[[^\]]*(?:출처|source|citation)[^\]]*\]",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        text = text.lower()
        text = re.sub(r"[^a-z0-9\uac00-\ud7a3\s\-]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    # --------------------------------------------------
    # 2. Medical concept extraction
    # --------------------------------------------------

    def extract_medical_concepts(
        self,
        claim: str,
    ) -> List[Dict[str, Any]]:
        """
        Finds medical concepts using phrase-aware matching.
        """

        normalized = self.normalize_text(claim)

        if not normalized:
            return []

        detected = []

        for concept_name, data in self.MEDICAL_CONCEPTS.items():
            matched_terms = []

            # Prefer longer phrases before shorter terms.
            terms = sorted(
                data["terms"],
                key=len,
                reverse=True,
            )

            for term in terms:
                pattern = (
                    r"(?<![a-z0-9])"
                    + re.escape(term)
                    + r"(?![a-z0-9])"
                )

                if re.search(pattern, normalized):
                    matched_terms.append(term)

            if matched_terms:
                detected.append({
                    "concept": concept_name,
                    "mesh": data["mesh"],
                    # Preserve the actually matched wording for diagnostics.
                    "matched_terms": matched_terms,
                    # Search all known synonyms for better recall, even when
                    # the user's claim contains only one variant.
                    "search_terms": sorted(
                        data["terms"],
                        key=len,
                        reverse=True,
                    ),
                })

        return detected

    # --------------------------------------------------
    # 3. General keyword extraction
    # --------------------------------------------------

    def extract_keywords(
        self,
        claim: str,
        max_keywords: int = 8,
    ) -> List[str]:
        """
        Extracts useful non-stopword terms.

        Known medical concept terms are excluded because
        they are already represented by concept groups.
        """

        normalized = self.normalize_text(claim)

        if not normalized:
            return []

        concepts = self.extract_medical_concepts(claim)

        concept_terms = set()

        for concept in concepts:
            for term in concept["matched_terms"]:
                concept_terms.update(term.split())

        keywords = []

        for word in normalized.split():
            if word in self.STOPWORDS:
                continue

            if word in concept_terms:
                continue

            if len(word) < 4:
                continue

            if word.isdigit():
                continue

            if word not in keywords:
                keywords.append(word)

        return keywords[:max_keywords]

    # --------------------------------------------------
    # 4. PubMed term formatting
    # --------------------------------------------------

    @staticmethod
    def quote_pubmed_phrase(term: str) -> str:
        term = term.replace('"', "").strip()

        if not term:
            return ""

        # Single words do not need quotation marks.
        if " " not in term:
            return f"{term}[Title/Abstract]"

        return f'"{term}"[Title/Abstract]'

    @staticmethod
    def mesh_query(mesh_term: str) -> str:
        safe_term = mesh_term.replace('"', "").strip()

        return f'"{safe_term}"[MeSH Terms]'

    # --------------------------------------------------
    # 5. Build one concept group
    # --------------------------------------------------

    def build_concept_group(
        self,
        concept: Dict[str, Any],
        include_mesh: bool = True,
    ) -> str:
        """
        Builds an OR group for one medical concept.

        Example:
        ("Vaccines"[MeSH Terms]
         OR vaccine[Title/Abstract]
         OR vaccination[Title/Abstract])
        """

        terms = concept.get("search_terms") or concept.get("matched_terms", [])

        formatted_terms = []

        if include_mesh and concept.get("mesh"):
            formatted_terms.append(
                self.mesh_query(concept["mesh"])
            )

        for term in terms[:4]:
            formatted_terms.append(
                self.quote_pubmed_phrase(term)
            )

        # Remove duplicates while preserving order.
        formatted_terms = list(
            dict.fromkeys(
                item for item in formatted_terms if item
            )
        )

        if not formatted_terms:
            return ""

        if len(formatted_terms) == 1:
            return formatted_terms[0]

        return "(" + " OR ".join(formatted_terms) + ")"

    # --------------------------------------------------
    # 6. Build medical query
    # --------------------------------------------------

    def build_medical_query(
        self,
        claim: str,
    ) -> str:
        """
        Builds the main high-recall medical search query.

        Different concepts are connected with AND.
        Synonyms within one concept are connected with OR.
        """

        concepts = self.extract_medical_concepts(claim)

        if not concepts:
            keywords = self.extract_keywords(
                claim,
                max_keywords=5,
            )

            if not keywords:
                return ""

            return " AND ".join(
                self.quote_pubmed_phrase(word)
                for word in keywords[:3]
            )

        groups = []

        for concept in concepts:
            group = self.build_concept_group(
                concept,
                include_mesh=True,
            )

            if group:
                groups.append(group)

        # Avoid adding weak, unrelated words from long claims.
        if groups:
            return " AND ".join(groups)

        return ""

    # --------------------------------------------------
    # 7. Progressive query levels
    # --------------------------------------------------

    def generate_query_levels(
        self,
        claim: str,
    ) -> List[Dict[str, Any]]:
        """
        Build progressively broader PubMed queries.

        The first query uses the primary concept and, when available,
        one closely related concept. Long natural-language claims are
        therefore not sent to PubMed as one giant AND expression.
        """
        concepts = self.extract_medical_concepts(claim)
        levels: List[Dict[str, Any]] = []

        if concepts:
            groups = [
                self.build_concept_group(concept)
                for concept in concepts
            ]
            groups = [group for group in groups if group]

            # Start with the first two concepts for a balance of recall
            # and specificity.
            if len(groups) >= 2:
                levels.append({
                    "name": "moderate",
                    "query": " AND ".join(groups[:2]),
                })

            # Retain the strict query as a later refinement.
            if len(groups) >= 3:
                levels.append({
                    "name": "specific",
                    "query": " AND ".join(groups),
                })

            # Primary medical concept alone is the broad fallback.
            levels.append({
                "name": "broad",
                "query": groups[0],
            })

            # Use an OR expansion only as a last-resort recall strategy.
            if len(groups) > 1:
                levels.append({
                    "name": "expanded",
                    "query": "(" + " OR ".join(groups) + ")",
                })
        else:
            keywords = self.extract_keywords(claim, max_keywords=5)
            if keywords:
                # AND is too restrictive for arbitrary long sentences.
                # Use OR for fallback terms and let ranking assess relevance.
                levels.append({
                    "name": "keyword",
                    "query": "(" + " OR ".join(
                        self.quote_pubmed_phrase(word)
                        for word in keywords[:5]
                    ) + ")",
                })

        unique_levels = []
        seen = set()
        for level in levels:
            query = level.get("query", "").strip()
            if query and query not in seen:
                seen.add(query)
                unique_levels.append({
                    "name": level["name"],
                    "query": query,
                })
        return unique_levels

    # --------------------------------------------------
    # 8. Query generation
    # --------------------------------------------------

    def generate_candidates(
        self,
        claim: str,
    ) -> List[str]:
        """
        Generate a small set of high-recall initial queries.

        Search-type filters are optional variants, not mandatory filters
        on every query, so a claim is not lost merely because PubMed has
        few records of one publication type.
        """
        levels = self.generate_query_levels(claim)
        if not levels:
            return []

        candidates = [level["query"] for level in levels[:3]]
        primary_query = levels[0]["query"]

        candidates.extend([
            (
                f"({primary_query}) AND "
                "(systematic review[Publication Type] "
                "OR meta-analysis[Publication Type])"
            ),
            (
                f"({primary_query}) AND "
                "(randomized controlled trial[Publication Type])"
            ),
        ])

        return list(dict.fromkeys(
            query.strip() for query in candidates if query.strip()
        ))

    # --------------------------------------------------
    # 9. Fallback query generation
    # --------------------------------------------------

    def generate_fallback_queries(
        self,
        claim: str,
    ) -> List[str]:
        """
        Returns progressively broader query strings.

        These are attempted only if the initial searches
        return no articles.
        """

        levels = self.generate_query_levels(claim)

        fallback_queries = [
            level["query"]
            for level in levels[1:]
        ]

        # Add a keyword fallback for claims with useful
        # non-concept terms.
        keywords = self.extract_keywords(
            claim,
            max_keywords=4,
        )

        if keywords:
            fallback_queries.append(
                " OR ".join(
                    self.quote_pubmed_phrase(word)
                    for word in keywords[:3]
                )
            )

        return list(dict.fromkeys(
            query for query in fallback_queries if query
        ))

    # --------------------------------------------------
    # 10. Document normalization
    # --------------------------------------------------

    @staticmethod
    def normalize_documents(
        documents: Optional[List[Any]],
    ) -> List[Dict[str, Any]]:
        """
        Supports both dictionaries and plain-text documents.
        """

        if not isinstance(documents, list):
            return []

        normalized = []

        for document in documents:
            if isinstance(document, dict):
                # Copy so downstream normalization never mutates caller data.
                normalized.append(dict(document))

            elif isinstance(document, str):
                normalized.append({
                    "pmid": None,
                    "title": document[:300],
                    "abstract": document,
                    "year": None,
                    "journal": None,
                    "url": None,
                })

        return normalized

    # --------------------------------------------------
    # 11. Query scoring
    # --------------------------------------------------

    def score_query(
        self,
        query: str,
        documents: List[Any],
    ) -> float:
        normalized_documents = self.normalize_documents(
            documents
        )

        if not normalized_documents:
            return 0.0

        scores = []

        for document in normalized_documents:
            title = document.get("title", "") or ""
            abstract = document.get("abstract", "") or ""

            if not isinstance(title, str):
                title = str(title)
            if not isinstance(abstract, str):
                abstract = str(abstract)

            document_text = f"{title} {abstract}".strip()

            if not document_text:
                continue

            try:
                similarity = (
                    self.evaluator.calculate_cosine_similarity(
                        query,
                        document_text,
                    )
                )

                scores.append(float(similarity))

            except Exception:
                continue

        if not scores:
            return 0.0

        scores.sort(reverse=True)

        top_scores = scores[:3]

        return sum(top_scores) / len(top_scores)

    # --------------------------------------------------
    # 12. Beam search
    # --------------------------------------------------

    def beam_search(
        self,
        claim: str,
        documents: List[Any],
    ) -> List[Tuple[str, float]]:
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
    # 13. Neighbor generation
    # --------------------------------------------------

    def generate_neighbors(
        self,
        query: str,
    ) -> List[str]:
        if not query or not query.strip():
            return []

        neighbors = []

        query_lower = query.lower()

        for direction in self.search_directions:
            if direction.lower() not in query_lower:
                neighbors.append(
                    f"({query}) AND ({direction})"
                )

        return neighbors

    # --------------------------------------------------
    # 14. Hill climbing
    # --------------------------------------------------

    def hill_climbing(
        self,
        initial_query: str,
        documents: List[Any],
        max_iterations: int = 5,
    ) -> str:
        current_query = initial_query

        current_score = self.score_query(
            current_query,
            documents,
        )

        for _ in range(max_iterations):
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
    # 15. Article deduplication
    # --------------------------------------------------

    @staticmethod
    def deduplicate_articles(
        articles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
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
    # 16. Article ranking
    # --------------------------------------------------

    def rank_articles(
        self,
        claim: str,
        articles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not articles:
            return []

        try:
            ranked = self.evaluator.evaluate_articles(
                claim,
                articles,
            )

            if isinstance(ranked, list):
                # evaluate_articles returns articles ordered by relevance.
                return ranked[:self.MAX_TOTAL_ARTICLES]

        except Exception:
            pass

        # Keep the pipeline bounded even if ranking fails.
        return articles[:self.MAX_TOTAL_ARTICLES]

    # --------------------------------------------------
    # 17. Execute one PubMed query
    # --------------------------------------------------

    def execute_query(
        self,
        claim: str,
        query: str,
        strategy: str = "standard",
    ) -> Dict[str, Any]:
        try:
            articles = self.retriever.retrieve(query)

            if not isinstance(articles, list):
                articles = []

            articles = [
                article
                for article in articles
                if isinstance(article, dict)
            ]

            try:
                score = self.evaluator.calculate_query_score(
                    claim,
                    articles,
                )

                score = float(score)

            except Exception:
                score = 0.0

            return {
                "query": query,
                "strategy": strategy,
                "score": score,
                "article_count": len(articles),
                "status": "success",
                "articles": articles,
            }

        except Exception as error:
            return {
                "query": query,
                "strategy": strategy,
                "score": 0.0,
                "article_count": 0,
                "status": "failed",
                "error": str(error),
                "articles": [],
            }

    # --------------------------------------------------
    # 18. PubMed retrieval
    # --------------------------------------------------

    def retrieve_candidates(
        self,
        claim: str,
    ) -> Dict[str, Any]:
        """
        Retrieve, deduplicate, and rank PubMed articles.

        Fallback searches continue until a minimum unique pool is found
        or all progressively broader queries have been attempted.
        Query failures are kept separate from successful empty searches.
        """
        initial_queries = self.generate_candidates(claim)
        query_results: List[Dict[str, Any]] = []
        all_articles: List[Dict[str, Any]] = []
        already_searched = set()

        for query in initial_queries:
            result = self.execute_query(
                claim, query, strategy="initial"
            )
            query_results.append(result)
            all_articles.extend(result.get("articles", []))
            already_searched.add(query)

        unique_articles = self.deduplicate_articles(all_articles)
        fallback_used = False

        # Aim for at least five unique candidates where possible.
        # This is a retrieval target, not a claim that all are relevant.
        target_count = min(5, self.max_results_per_query)

        if len(unique_articles) < target_count:
            fallback_used = True
            for query in self.generate_fallback_queries(claim):
                if query in already_searched:
                    continue

                result = self.execute_query(
                    claim, query, strategy="fallback"
                )
                query_results.append(result)
                all_articles.extend(result.get("articles", []))
                already_searched.add(query)

                unique_articles = self.deduplicate_articles(
                    all_articles
                )
                if len(unique_articles) >= target_count:
                    break

        ranked_articles = self.rank_articles(claim, unique_articles)

        query_results.sort(
            key=lambda item: float(item.get("score", 0.0)),
            reverse=True,
        )
        selected_queries = query_results[:self.beam_width]

        failed_query_count = sum(
            item.get("status") == "failed" for item in query_results
        )
        successful_query_count = len(query_results) - failed_query_count

        if ranked_articles:
            search_status = "success"
        elif successful_query_count > 0:
            search_status = "no_results"
        else:
            search_status = "error"

        return {
            "articles": ranked_articles,
            "query_results": query_results,
            "selected_queries": selected_queries,
            # Count only the articles actually retained for analysis.
            "retrieved_article_count": len(ranked_articles),
            "evaluated_query_count": len(query_results),
            "fallback_used": fallback_used,
            "search_status": search_status,
            "failed_query_count": failed_query_count,
            "successful_query_count": successful_query_count,
        }

    # --------------------------------------------------
    # 19. Main optimization pipeline
    # --------------------------------------------------

    def optimize(
        self,
        claim: str,
        documents: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(claim, str) or not claim.strip():
            return {
                "articles": [],
                "retrieved_article_count": 0,
                "evaluated_query_count": 0,
                "optimized_queries": [],
                "beam_search_results": [],
                "article_relevance": [],
                "fallback_used": False,
                "optimization_note": "Empty claim provided.",
            }

        claim = claim.strip()

        # ----------------------------------------------
        # Compatibility mode: supplied documents
        # ----------------------------------------------

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

            ranked_articles = self.rank_articles(
                claim,
                normalized_documents,
            )

            return {
                "articles": ranked_articles,
                "retrieved_article_count": len(ranked_articles),
                "evaluated_query_count": len(
                    self.generate_candidates(claim)
                ),
                "optimized_queries": [best_query],
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
                "fallback_used": False,
                "optimization_note": (
                    "Used supplied documents. "
                    "No new PubMed retrieval was performed."
                ),
            }

        # ----------------------------------------------
        # Actual PubMed retrieval mode
        # ----------------------------------------------

        search_result = self.retrieve_candidates(claim)

        articles = search_result.get("articles", [])
        query_results = search_result.get("query_results", [])
        selected_queries = search_result.get("selected_queries", [])

        optimized_queries = [
            item["query"]
            for item in selected_queries
        ]

        beam_search_results = [
            {
                "query": item["query"],
                "score": round(
                    float(item.get("score", 0.0)),
                    4,
                ),
                "article_count": item.get("article_count", 0),
                "status": item.get("status", "unknown"),
                "strategy": item.get("strategy", "unknown"),
            }
            for item in selected_queries
        ]

        fallback_used = search_result.get(
            "fallback_used",
            False,
        )
        search_status = search_result.get(
            "search_status",
            "success" if articles else "no_results",
        )

        if articles:
            optimization_note = (
                "Articles were retrieved using medical concept "
                "expansion and PubMed search strategies. "
                "Textual relevance does not establish whether "
                "the claim is true or false."
            )

            if fallback_used:
                optimization_note += (
                    " Broader fallback queries were used."
                )

        elif search_status == "error":
            optimization_note = (
                "All PubMed search attempts failed. Check network access, "
                "PubMed availability, and the recorded query errors."
            )
        else:
            optimization_note = (
                "PubMed queries completed but returned no articles. "
                "Try a shorter claim or alternative medical terminology."
            )

        return {
            "articles": articles,
            "retrieved_article_count": len(articles),
            "evaluated_query_count": search_result.get(
                "evaluated_query_count",
                len(query_results),
            ),
            "optimized_queries": optimized_queries,
            "beam_search_results": beam_search_results,
            "article_relevance": [
                article.get("relevance", {})
                for article in articles
            ],
            "fallback_used": fallback_used,
            "search_status": search_status,
            "failed_query_count": search_result.get(
                "failed_query_count", 0
            ),
            "successful_query_count": search_result.get(
                "successful_query_count", 0
            ),
            "optimization_note": optimization_note,
        }

    # --------------------------------------------------
    # 20. Resource cleanup
    # --------------------------------------------------

    def close(self):
        if self._owns_retriever:
            close_method = getattr(
                self.retriever,
                "close",
                None,
            )

            if callable(close_method):
                close_method()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()