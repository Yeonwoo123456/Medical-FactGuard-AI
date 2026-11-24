import re

from backend.algorithms.medical_classifier import MedicalClassifier
from backend.algorithms.local_search import LocalSearchOptimizer
from backend.algorithms.relevance_filter import RelevanceFilter
from backend.algorithms.sentence_classifier import SentenceClassifier
from backend.algorithms.statistical_evidence import StatisticalEvidenceAnalyzer
from backend.retrieval.abstract_parser import AbstractParser
from backend.retrieval.pubmed_retriever import PubMedRetriever
from backend.translation.claim_translator import ClaimTranslator


class EvidencePipeline:
    """Coordinates retrieval, sentence classification, and evidence analysis."""

    PRIMARY_SENTENCE_TYPES = {
        "Research Result",
        "Safety Result",
        "Conclusion",
    }

    def __init__(self):
        self.abstract_parser = AbstractParser()
        self.medical_classifier = MedicalClassifier()
        self.relevance_filter = RelevanceFilter()
        self.sentence_classifier = SentenceClassifier()
        self.statistical_analyzer = StatisticalEvidenceAnalyzer()
        self.claim_translator = ClaimTranslator()

        # Shared PubMed Retriever
        self.pubmed_retriever = PubMedRetriever(
            max_results=10
        )

        # Local Search Optimizer
        self.local_search_optimizer = LocalSearchOptimizer(
            retriever=self.pubmed_retriever,
            beam_width=3,
            max_results_per_query=10,
        )

        self.max_analysis_articles = 10
        self._evidence_cache = {}

        # Textual uncertainty is separate from statistical uncertainty.
        self.uncertainty_patterns = [
            r"\bcannot be excluded\b",
            r"\bcould not be excluded\b",
            r"\buncertain\b",
            r"\bunclear\b",
            r"\binsufficient evidence\b",
            r"\bno significant difference\b",
            r"\bnot statistically significant\b",
            r"\bmay be associated\b",
            r"\bpossible\b",
            r"\bpotential\b",
            r"\blimited evidence\b",
            r"\bnot enough data\b",
            r"\bno data are reported\b",
            r"\bdata were not available\b",
            r"\bremains uncertain\b",
            r"\bfurther research is needed\b",
            r"\bthe evidence is inconclusive\b",
            r"\bthe results are inconclusive\b",
        ]

        # These patterns identify a safety-related topic,
        # not a proven harm.
        self.safety_topic_patterns = [
            r"\badverse events?\b",
            r"\badverse effects?\b",
            r"\bserious adverse events?\b",
            r"\bserious adverse effects?\b",
            r"\bside effects?\b",
            r"\bvaccine-related harms?\b",
            r"\bdrug-related harms?\b",
            r"\btreatment-related harms?\b",
            r"\bmedication-related harms?\b",
            r"\bmiscarriage\b",
            r"\bstillbirth\b",
            r"\bcongenital abnormalities\b",
            r"\bpregnancy outcomes?\b",
            r"\bpregnancy complications?\b",
            r"\btoxicity\b",
            r"\bfatal adverse events?\b",
            r"\bserious harms?\b",
            r"\brare harms?\b",
            r"\bvaccine-related deaths?\b",
            r"\bdeath following vaccination\b",
            r"\btreatment-related mortality\b",
            r"\bvaccine safety\b",
            r"\bdrug safety\b",
            r"\btreatment safety\b",
            r"\bmedication safety\b",
            r"\bsafety profile\b",
            r"\blong[- ]term safety\b",
            # Common clinical-trial abbreviations.
            r"\bSAEs?\b",
            r"\bAEs?\b",
            r"\bNDCMCs?\b",
        ]

        # These patterns identify reported safety findings
        # or explicit safety conclusions.
        self.safety_result_patterns = [
            # 1. Event-level comparisons, including appeared/seemed similar.
            r"\b(?:adverse events?|adverse effects?|serious adverse events?|"
            r"serious adverse effects?|side effects?|serious harms?)\s+"
            r"(?:were|was|are|is|appeared to be|seemed to be)\s+"
            r"(?:similar|higher|lower|comparable|increased|reduced|"
            r"more common|less common|more frequent|less frequent|"
            r"low|rare)\b",

            # 2. Incidence/rate/frequency comparisons.
            r"\b(?:the )?(?:incidence|rate|frequency|proportion)\s+of\s+"
            r"(?:serious )?(?:adverse events?|adverse effects?|side effects?|"
            r"miscarriage|stillbirth|pregnancy outcomes?|pregnancy complications?)"
            r"\s+(?:was|were|is|are|appeared to be|seemed to be)\s+"
            r"(?:similar|higher|lower|comparable|increased|reduced|"
            r"not significantly different|not different|low)\b",

            # 3. Risk changes associated with safety outcomes.
            r"\b(?:increased|higher|reduced|lower|excess)\s+risk\s+of\s+"
            r"(?:serious )?(?:adverse events?|adverse effects?|side effects?|"
            r"miscarriage|stillbirth|pregnancy outcomes?|pregnancy complications?)\b",

            # 4. Risk comparison wording.
            r"\brisk\s+of\s+(?:serious )?(?:adverse events?|adverse effects?|"
            r"side effects?|miscarriage|stillbirth|pregnancy outcomes?)\s+"
            r"(?:was|were|is|are|appeared to be|seemed to be)\s+"
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",

            # 5. Participant-level reports (e.g. Eight participants experienced...).
            r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|"
            r"several|many|\d+)\s+"
            r"(?:participants?|patients?|individuals?)\s+"
            r"(?:experienced|reported|developed|had)\s+"
            r"(?:serious )?(?:adverse events?|adverse effects?|side effects?|"
            r"complications?)\b",

            # 6. Events reported or observed.
            r"\b(?:serious )?(?:adverse events?|adverse effects?|"
            r"side effects?|serious harms?)\s+"
            r"(?:occurred|were reported|was reported|were observed|"
            r"was observed|were experienced|was experienced)\b",

            # 7. Explicit participant counts.
            r"\b(?:serious )?(?:adverse events?|adverse effects?)\s+"
            r"(?:were|was)\s+reported\s+(?:in|among)\s+"
            r"(?:\d+|one|two|three|four|five|several|many)\s+"
            r"(?:participants?|patients?|individuals?)\b",

            # 8. Clinical-trial abbreviation rates, e.g. SAE and NDCMC rates.
            r"\b(?:SAE|SAEs|AE|AEs|NDCMC|NDCMCs)\s+"
            r"(?:and\s+(?:SAE|SAEs|AE|AEs|NDCMC|NDCMCs)\s+)?"
            r"rates?\s+(?:were|was|remained|appeared to be)\s+"
            r"(?:low|similar|comparable|higher|lower)\b",

            # 9. Events more/less common or frequent in a group.
            r"\b(?:adverse events?|adverse effects?|serious adverse events?|"
            r"side effects?|local reactions?|systemic events?)\b"
            r".{0,120}\b(?:were|was|are|is)\s+(?:significantly )?"
            r"(?:more common|less common|more frequent|less frequent|"
            r"higher|lower)\b",

            # 10. No meaningful/significant differences in safety outcomes.
            r"\bno\s+(?:(?:clinically|statistically)\s+)?"
            r"(?:meaningful|significant)\s+differences?\s+in\s+"
            r"(?:serious )?(?:adverse events?|adverse effects?|side effects?)\b"
            r".{0,80}\b(?:were|was|are|is)\s+(?:noted|observed|reported|found)\b",
            r"\bno\s+(?:clinically meaningful|significant)\s+"
            r"differences?\s+in\s+(?:serious )?"
            r"(?:adverse events?|adverse effects?|side effects?)\b",

            # 11. Pregnancy outcomes.
            r"\b(?:miscarriage|stillbirth|congenital abnormalities)\s+"
            r"(?:were|was|occurred|reported|observed)\b",
            r"\b(?:pregnancy outcomes?|pregnancy complications?)\s+"
            r"(?:were|was|are|is)\s+"
            r"(?:similar|higher|lower|comparable|increased|reduced)\b",

            # 12. Relationship to treatment (reported attribution only).
            r"\b(?:serious )?(?:adverse events?|adverse effects?)\b"
            r".{0,100}\b(?:were|was)\s+"
            r"(?:considered|judged|deemed)\s+related\b",
            r"\b(?:have|has|had) been judged not to be related\b",
            r"\b(?:was|were) judged not to be related\b",
            r"\b(?:was|were) not considered related\b",
            r"\b(?:was|were) not related to the vaccine\b",

            # 13. Explicitly stated possibility that risk cannot be excluded.
            r"\bcannot be excluded\b",
            r"\bcould not be excluded\b",
        ]

        # These patterns identify concerns,
        # not actual observed outcomes.
        self.safety_concern_patterns = [
            r"\bconcerns? about\b",
            r"\bconcerns? regarding\b",
            r"\bconcerns? over\b",
            r"\bdoubts? about\b",
            r"\bpossible adverse events?\b",
            r"\bpossible adverse events?\b",
            r"\bpotential adverse events?\b",
            r"\bpotential adverse effects?\b",
            r"\bpotential harms?\b",
            r"\bcannot be excluded\b",
            r"\bcould not be excluded\b",
            r"\buncertain safety\b",
            r"\bconcerns? over vaccine safety\b",
        ]

    # --------------------------------------------------
    # Utility methods
    # --------------------------------------------------

    @staticmethod
    def to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def matches_any(patterns, text):
        text = text if isinstance(text, str) else ""

        return [
            pattern
            for pattern in patterns
            if re.search(pattern, text, re.IGNORECASE)
        ]

    # --------------------------------------------------
    # Medical claim classification
    # --------------------------------------------------

    def classify_claim(self, claim):
        result = self.medical_classifier.classify(claim)

        if isinstance(result, tuple):
            category = result[0] if len(result) > 0 else "Unknown"
            confidence = result[1] if len(result) > 1 else 0.0
            keywords = result[2] if len(result) > 2 else []

        elif isinstance(result, dict):
            category = result.get("category", "Unknown")
            confidence = result.get("confidence", 0.0)

            # Support both classifier output formats.
            keywords = result.get(
                "matched_keywords",
                result.get("scores", {}),
            )

        else:
            category = str(result)
            confidence = 0.0
            keywords = []

        # Conservative fallback rules for common medical domains that the
        # base keyword classifier may not cover (e.g. vitamins and supplements).
        lowered = claim.casefold()
        if category in (None, "Unknown", "Unclassified", ""):
            if any(term in lowered for term in ("암", "암종", "종양", "소아암", "cancer", "carcinoma", "neoplasm")):
                category = "Oncology"
                confidence = max(self.to_float(confidence), 0.65)
                if not keywords:
                    keywords = ["cancer", "oncology"]
            elif any(term in lowered for term in (
                "vitamin", "ascorbic acid", "supplement", "supplementation",
                "비타민", "영양제", "보충제",
            )):
                category = "Medications & Treatments"
                confidence = max(self.to_float(confidence), 0.70)
                if isinstance(keywords, dict):
                    keywords = dict(keywords)
                    keywords["Medications & Treatments"] = max(
                        self.to_float(keywords.get("Medications & Treatments", 0)), 1.0
                    )
                elif not keywords:
                    keywords = ["vitamin", "supplementation"]

        return category, self.to_float(confidence), keywords

    # --------------------------------------------------
    # Evidence result normalization
    # --------------------------------------------------

    def normalize_evidence_result(self, result):

        if not isinstance(result, dict):
            return {
                "classification": "Insufficient",
                "relevance": 0.0,
                "confidence": 0.0,
            }

        classification = result.get(
            "classification",
            result.get("label", "Insufficient"),
        )

        allowed_labels = {
            "Supporting",
            "Contradicting",
            "Neutral",
            "Insufficient",
        }

        if classification not in allowed_labels:
            classification = "Insufficient"

        relevance_status = result.get(
            "relevance_status",
            result.get("status", "Relevant"),
        )
        if not isinstance(relevance_status, str) or not relevance_status.strip():
            relevance_status = "Relevant"

        relevance_reason = result.get(
            "relevance_reason",
            result.get("reason", ""),
        )

        return {
            "classification": classification,
            "relevance": self.to_float(
                result.get(
                    "relevance",
                    result.get("similarity", 0.0),
                )
            ),
            "confidence": self.to_float(
                result.get("confidence", 0.0)
            ),
            "relevance_status": relevance_status,
            "relevance_reason": str(relevance_reason or ""),
        }

    # --------------------------------------------------
    # Uncertainty detection
    # --------------------------------------------------

    def detect_uncertainty(self, sentence):

        matches = self.matches_any(
            self.uncertainty_patterns,
            sentence,
        )

        return {
            "is_uncertain": bool(matches),
            "matched_patterns": matches,
        }

    # --------------------------------------------------
    # Safety classification
    # --------------------------------------------------

    def detect_safety_signals(
        self,
        sentence,
        section_type="Other",
    ):
        """
        Returns separate signals for:
        - Safety topic
        - Safety finding
        - Safety concern

        section_type is retained for backward compatibility.
        """

        topic_matches = self.matches_any(
            self.safety_topic_patterns,
            sentence,
        )

        result_matches = self.matches_any(
            self.safety_result_patterns,
            sentence,
        )

        concern_matches = self.matches_any(
            self.safety_concern_patterns,
            sentence,
        )

        safety_topic = bool(topic_matches)

        safety_result = (
            safety_topic and bool(result_matches)
        )

        safety_concern = (
            safety_topic and bool(concern_matches)
        )

        return {
            "safety_topic": safety_topic,
            "safety_result": safety_result,
            "safety_concern": safety_concern,
            "topic_patterns": topic_matches,
            "result_patterns": result_matches,
            "concern_patterns": concern_matches,
        }

    def detect_safety_evidence(
        self,
        sentence,
        section_type="Other",
    ):
        """Backward-compatible alias for older code."""

        return self.detect_safety_signals(
            sentence,
            section_type,
        )["safety_topic"]

    # --------------------------------------------------
    # Evidence counting and statistical summary
    # --------------------------------------------------

    @staticmethod
    def count_classifications(results):

        counts = {
            "Supporting": 0,
            "Contradicting": 0,
            "Neutral": 0,
            "Insufficient": 0,
        }

        for result in results:
            label = result.get(
                "evidence_classification",
                "Insufficient",
            )

            if label in counts:
                counts[label] += 1

        return counts

    @staticmethod
    def summarize_statistics(results):

        summary = {
            "analyzed_sentences": 0,
            "confidence_intervals_found": 0,
            "intervals_including_null": 0,
            "intervals_excluding_null": 0,
            "sentences_without_detected_statistics": 0,
            "certainty_levels": {
                "high": 0,
                "moderate": 0,
                "low": 0,
                "very low": 0,
            },
        }

        for result in results:

            statistical = (
                result.get("statistical_analysis") or {}
            )

            if not statistical.get("available"):
                summary[
                    "sentences_without_detected_statistics"
                ] += 1
                continue

            summary["analyzed_sentences"] += 1

            if statistical.get("confidence_interval") is not None:

                summary["confidence_intervals_found"] += 1

                includes_null = statistical.get("includes_null")

                if includes_null is True:
                    summary["intervals_including_null"] += 1

                elif includes_null is False:
                    summary["intervals_excluding_null"] += 1

            certainty = statistical.get("certainty")

            if certainty in summary["certainty_levels"]:
                summary["certainty_levels"][certainty] += 1

        return summary

    # --------------------------------------------------
    # Evidence-bearing sentence fallback
    # --------------------------------------------------

    @staticmethod
    def infer_primary_sentence_type(
        sentence,
        current_type="Other",
        section_type="Other",
    ):
        """Conservatively recover outcome sentences missed by the base classifier.

        This method only decides whether a sentence is eligible for evidence
        evaluation. It never decides whether the sentence supports or contradicts
        the claim; RelevanceFilter remains responsible for that decision.
        """
        allowed_primary = {"Research Result", "Safety Result", "Conclusion"}
        if current_type in allowed_primary:
            return current_type, False, ""

        text = re.sub(r"\s+", " ", str(sentence or "")).strip()
        lower = text.casefold()
        if not text:
            return current_type or "Other", False, ""

        # Explicit conclusion language.
        conclusion_patterns = (
            r"\bwe conclude that\b",
            r"\bthese findings (?:suggest|indicate|show|demonstrate)\b",
            r"\bour results (?:suggest|indicate|show|demonstrate)\b",
            r"\bthe findings (?:suggest|indicate|show|demonstrate)\b",
            r"\bthe failure of .{0,100}\b(?:prevent|reduce|lower|decrease)\b",
            r"\b(?:there is|there was) no evidence that\b",
            r"\btherefore,? (?:routine|regular)\b",
            r"\bis not justified\b",
            r"\bdoes not support\b",
            r"\bwas not effective in\b",
        )

        # Explicitly reported outcomes, including epidemiological associations.
        # These patterns are deliberately narrower than generic medical wording.
        result_patterns = (
            # Prevention/incidence outcomes.
            r"\b(?:did not|does not|do not|failed to|was unable to) prevent\b",
            r"\b(?:prevented|prevents|preventing)\b",
            r"\b(?:incidence|occurrence|risk) of (?:the )?(?:common )?cold\b",
            r"\b(?:common )?colds? (?:were|was|are|is) (?:prevented|reduced|less frequent|more frequent)\b",
            r"\b(?:reduced|decreased|increased|lowered|raised|halved|doubled) the incidence\b",

            # Association / relationship findings. These are important for claims
            # phrased as "X is related to Y" or "X has no relationship with Y".
            r"\b(?:was|were|is|are|has been|have been) associated with\b",
            r"\b(?:was|were|is|are|has been|have been) not associated with\b",
            r"\bno (?:significant )?association between\b",
            r"\b(?:positive|negative|inverse) association between\b",
            r"\b(?:was|were|is|are) linked to\b",
            r"\b(?:was|were|is|are) related to\b",
            r"\b(?:was|were|is|are) correlated with\b",
            r"\b(?:increased|higher|reduced|lower) risk of\b",

            # Risk-factor / etiological statements that report a finding.
            r"\b(?:was|were|is|are) (?:an? )?(?:independent )?risk factor(?:s)? for\b",
            r"\b(?:primary|主要) causes? (?:were|was|include|included)\b",
            r"\b(?:main|major|leading) causes? (?:were|was|include|included)\b",
            r"\b(?:was|were) attributable to\b",
            r"\b(?:accounted for|explained)\b",

            # Quantitative/statistical outcome language.
            r"\b(?:risk|incidence|odds|rate|duration|severity|mortality|survival)\b.{0,120}"
            r"\b(?:was|were|is|are|by|from|to|compared|lower|higher|reduced|increased|similar)\b",
            r"\b(?:no significant difference|not statistically significant|"
            r"significantly (?:higher|lower|reduced|increased|improved|decreased))\b",
            r"\b(?:confidence interval|95%\s*ci|p\s*[<=>])\b",
            r"\b(?:risk ratio|relative risk|odds ratio|hazard ratio)\s*(?:was|of|=)\b",

            # Explicit result reporting.
            r"\b(?:our results|the results|results) (?:show|indicate|demonstrate|revealed|suggest)\b",
            r"\bwe found that\b",
            r"\bwas found to be\b",
            r"\bwere found to be\b",
            r"\bthe study found\b",
        )

        if any(re.search(pattern, lower) for pattern in conclusion_patterns):
            return "Conclusion", True, "explicit_conclusion_language"

        if any(re.search(pattern, lower) for pattern in result_patterns):
            if current_type == "Safety Result" or section_type == "Safety Result":
                return "Safety Result", True, "explicit_safety_or_research_finding"
            return "Research Result", True, "explicit_research_finding"

        return current_type or "Other", False, ""

    # --------------------------------------------------
    # Claim-outcome alignment
    # --------------------------------------------------

    @staticmethod
    def claim_outcome_mismatch(claim, sentence):
        """Prevent a different clinical endpoint from deciding the claim.

        Example: duration/severity findings must not decide a prevention claim.
        Returns True only when the claim's endpoint is explicit and the sentence
        clearly reports a different endpoint without mentioning the claimed one.
        """
        claim_text = str(claim or "").casefold()
        sentence_text = str(sentence or "").casefold()

        prevention_claim = bool(re.search(
            r"\b(prevent|prevents|prevented|prevention|incidence|"
            r"risk of (?:getting|developing|contracting))\b|예방|발병률",
            claim_text,
        ))
        if not prevention_claim:
            return False

        prevention_outcome = bool(re.search(
            r"\b(prevent|prevents|prevented|prevention|incidence|"
            r"occurrence|risk of (?:the )?(?:common )?cold|"
            r"develop(?:ing)? (?:a )?cold|contract(?:ing)? (?:a )?cold)\b",
            sentence_text,
        ))
        different_endpoint = bool(re.search(
            r"\b(duration|severity|symptom|symptoms|symptom score|"
            r"length of (?:the )?cold|recovery time)\b",
            sentence_text,
        ))
        return different_endpoint and not prevention_outcome

    # --------------------------------------------------
    # Analyze an individual article
    # --------------------------------------------------

    def analyze_article(self, claim, article):

        abstract = article.get("abstract", "")

        if not isinstance(abstract, str):
            abstract = str(abstract or "")

        parsed_sentences = self.abstract_parser.parse(abstract) if abstract.strip() else []
        if not isinstance(parsed_sentences, list):
            parsed_sentences = []

        sentence_results = []

        for item in parsed_sentences:

            if not isinstance(item, dict):
                continue

            sentence = item.get("sentence", "")

            if (
                not isinstance(sentence, str)
                or not sentence.strip()
            ):
                continue

            section_type = item.get("section_type", "Other")
            if not isinstance(section_type, str) or not section_type.strip():
                section_type = "Other"

            # Classify sentence content. Accept the supported classifier
            # response shapes defensively so one malformed result cannot discard
            # the entire article.
            sentence_type_result = self.sentence_classifier.classify(sentence)

            if isinstance(sentence_type_result, dict):
                final_type = sentence_type_result.get("type", "Other")
                type_confidence = self.to_float(
                    sentence_type_result.get("confidence", 0.0)
                )
            elif isinstance(sentence_type_result, (tuple, list)):
                final_type = (
                    sentence_type_result[0]
                    if sentence_type_result else "Other"
                )
                type_confidence = self.to_float(
                    sentence_type_result[1]
                    if len(sentence_type_result) > 1 else 0.0
                )
            elif isinstance(sentence_type_result, str):
                final_type = sentence_type_result
                type_confidence = 0.0
            else:
                final_type = "Other"
                type_confidence = 0.0

            if not isinstance(final_type, str) or not final_type.strip():
                final_type = "Other"

            # Use explicit abstract section metadata as a fallback first.
            if (
                final_type == "Other"
                and section_type not in {"Other", "Unstructured"}
            ):
                final_type = section_type

            # PubMed often returns unstructured abstracts. The parser may label
            # all of them "Other", and the classifier can mistake outcome
            # statements for methods. Recover clear result/conclusion wording
            # before deciding whether to run evidence comparison.
            final_type, inferred_primary_type, inference_reason = (
                self.infer_primary_sentence_type(
                    sentence, final_type, section_type
                )
            )
            if inferred_primary_type:
                type_confidence = max(type_confidence, 0.70)

            # Do not let a different clinical endpoint (e.g. symptom severity)
            # decide a prevention claim. Keep the sentence visible for audit.
            outcome_mismatch = self.claim_outcome_mismatch(claim, sentence)

            # Evaluate primary findings, including conservatively inferred ones,
            # only when they address the claim's stated endpoint.
            if final_type in self.PRIMARY_SENTENCE_TYPES and not outcome_mismatch:
                article_title = str(article.get("title") or "").strip()
                evidence_context = (
                    f"Article title: {article_title}. Evidence sentence: {sentence}"
                    if article_title else sentence
                )
                cache_key = (
                    claim.casefold().strip(),
                    evidence_context.casefold().strip(),
                )
                if cache_key not in self._evidence_cache:
                    self._evidence_cache[cache_key] = (
                        self.relevance_filter.analyze_evidence(claim, evidence_context)
                    )
                raw_evidence = self._evidence_cache[cache_key]
                evidence = self.normalize_evidence_result(raw_evidence)
                evidence_status = "Evaluated"
            else:
                evidence = {
                    "classification": "Not Evaluated",
                    "relevance": 0.0,
                    "confidence": 0.0,
                }
                evidence_status = (
                    "Not Evaluated: outcome mismatch"
                    if outcome_mismatch
                    else "Not Evaluated: non-primary sentence"
                )

            uncertainty = self.detect_uncertainty(sentence)

            safety = self.detect_safety_signals(
                sentence,
                section_type,
            )

            statistical = self.statistical_analyzer.analyze(
                sentence
            )

            if not isinstance(statistical, dict):
                statistical = {"available": False}

            sentence_results.append({
                "section": item.get("section", ""),
                "original_section_type": section_type,
                "sentence": sentence,
                "sentence_type": final_type,
                "sentence_type_inferred": inferred_primary_type,
                "sentence_type_inference_reason": inference_reason,
                "type_confidence": type_confidence,
                "evidence_classification": evidence["classification"],
                "relevance": evidence["relevance"],
                "evidence_confidence": evidence["confidence"],
                "evidence_status": evidence_status,
                "relevance_status": evidence.get("relevance_status", "Not Evaluated"),
                "relevance_reason": evidence.get("relevance_reason", ""),
                "is_uncertain": uncertainty["is_uncertain"],
                "uncertainty_patterns": uncertainty["matched_patterns"],
                "safety_topic": safety["safety_topic"],
                "safety_result": safety["safety_result"],
                "safety_concern": safety["safety_concern"],

                # Backward compatibility.
                "is_safety_evidence": safety["safety_topic"],

                "statistical_analysis": statistical,
            })

        # Only result and conclusion sentences enter summaries.
        primary_results = [
            result
            for result in sentence_results
            if (
                result["sentence_type"] in self.PRIMARY_SENTENCE_TYPES
                and result.get("evidence_status") == "Evaluated"
                and result.get("relevance_status") == "Relevant"
            )
        ]

        # Actual safety findings only.
        safety_results = [
            result
            for result in primary_results
            if result["safety_result"]
        ]

        # Exclude safety-topic sentences from effectiveness analysis.
        effectiveness_results = [
            result
            for result in primary_results
            if (
                not result["safety_topic"]
                and result["sentence_type"] != "Safety Result"
            )
        ]

        overall_counts = self.count_classifications(
            primary_results
        )

        effectiveness_counts = self.count_classifications(
            effectiveness_results
        )

        safety_counts = self.count_classifications(
            safety_results
        )

        safety_topic_count = sum(
            result["safety_topic"]
            for result in sentence_results
        )

        safety_concern_count = sum(
            result["safety_concern"]
            for result in sentence_results
        )

        uncertainty_count = sum(
            result["is_uncertain"]
            for result in primary_results
        )

        statistical_uncertainty_count = sum(
            1
            for result in primary_results
            if (
                (result.get("statistical_analysis") or {}).get(
                    "available"
                )
                and (result.get("statistical_analysis") or {}).get(
                    "includes_null"
                ) is True
            )
        )

        statistical_summary = self.summarize_statistics(
            primary_results
        )

        supporting = overall_counts["Supporting"]
        contradicting = overall_counts["Contradicting"]

        if supporting and contradicting:
            classification = "Mixed"

        elif supporting > contradicting:
            classification = "Supporting"

        elif contradicting > supporting:
            classification = "Contradicting"

        elif primary_results:
            classification = "Neutral"

        else:
            classification = "Insufficient"

        return {
            "pmid": article.get("pmid", ""),
            "title": article.get("title", ""),
            "year": article.get("year", ""),
            "journal": article.get("journal", ""),
            "url": article.get("url", ""),
            "classification": classification,
            "overall_counts": overall_counts,

            "effectiveness_analysis": {
                "sentence_count": len(effectiveness_results),
                "counts": effectiveness_counts,
            },

            "safety_analysis": {
                "sentence_count": len(safety_results),
                "counts": safety_counts,
                "safety_topic_count": safety_topic_count,
                "safety_concern_count": safety_concern_count,
            },

            "uncertainty_count": uncertainty_count,
            "statistical_uncertainty_count": (
                statistical_uncertainty_count
            ),
            "statistical_summary": statistical_summary,
            "primary_sentence_count": len(primary_results),
            "evaluated_sentence_count": sum(
                result.get("evidence_status") == "Evaluated" for result in sentence_results
            ),
            "inferred_primary_sentence_count": sum(
                result.get("sentence_type_inferred", False) for result in sentence_results
            ),
            "sentences": sentence_results,
        }

    # --------------------------------------------------
    # Analyze a medical claim
    # --------------------------------------------------

    def analyze_claim(self, claim):
        """Analyze claims in English while preserving the user's original text.

        Korean input is translated once before category classification,
        PubMed query generation, relevance evaluation, and evidence comparison.
        English input passes through unchanged.
        """
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("Claim must be a non-empty string.")

        original_claim = claim.strip()

        # Translation happens before any English-oriented keyword or search logic.
        # If translation fails, stop instead of silently searching PubMed with
        # Korean text and producing misleadingly incomplete results.
        translation = self.claim_translator.translate_to_english(original_claim)
        analysis_claim = translation["translated_text"]

        category, category_confidence, keywords = self.classify_claim(analysis_claim)

        try:
            search_result = self.local_search_optimizer.optimize(analysis_claim)
            if not isinstance(search_result, dict):
                search_result = {
                    "articles": [], "search_status": "error",
                    "optimization_note": "Search optimizer returned an invalid response.",
                }
        except Exception as error:
            search_result = {
                "articles": [],
                "retrieved_article_count": 0,
                "evaluated_query_count": 0,
                "optimized_queries": [],
                "beam_search_results": [],
                "search_status": "error",
                "failed_query_count": 0,
                "successful_query_count": 0,
                "optimization_note": f"Search pipeline failed: {type(error).__name__}: {error}",
            }

        articles = search_result.get("articles", [])
        if not isinstance(articles, list):
            articles = []
        articles = [article for article in articles if isinstance(article, dict)]
        articles = articles[:self.max_analysis_articles]

        analyzed_articles = []
        article_errors = []
        self._evidence_cache = {}
        try:
            for index, article in enumerate(articles, start=1):
                try:
                    analyzed = self.analyze_article(analysis_claim, article)
                    analyzed["analysis_status"] = (
                        "analyzed" if analyzed.get("sentences") else "no_analyzable_sentences"
                    )
                    analyzed_articles.append(analyzed)
                except Exception as error:
                    article_errors.append({
                        "index": index,
                        "pmid": str(article.get("pmid") or ""),
                        "title": str(article.get("title") or ""),
                        "error_type": type(error).__name__,
                        "error": str(error),
                    })
        finally:
            self._evidence_cache = {}

        retrieved_count = len(articles)
        retrieved_article_metadata = [
            {
                "pmid": str(article.get("pmid") or ""),
                "title": str(article.get("title") or ""),
                "journal": str(article.get("journal") or ""),
                "year": article.get("year", ""),
                "url": str(article.get("url") or ""),
            }
            for article in articles
        ]
        analyzed_count = len(analyzed_articles)
        search_status = search_result.get("search_status", "unknown")
        if analyzed_count:
            status = "Analysis completed"
        elif retrieved_count:
            status = "Articles retrieved; analysis produced no usable results"
        elif search_status == "error":
            status = "PubMed search failed"
        else:
            status = "Insufficient evidence"

        return {
            "result_schema_version": "2026-11-24.7",
            "status": status,
            # Keep the exact user-entered claim for display and audit.
            "claim": original_claim,
            # Expose translation separately so the internal query can be audited.
            "claim_translation": {
                "source_language": translation["source_language"],
                "target_language": "en",
                "translated_text": analysis_claim,
                "translation_applied": translation["translation_applied"],
                "provider": translation["provider"],
            },
            "category": category,
            "category_confidence": category_confidence,
            "matched_keywords": keywords,
            "search_summary": {
                "query_language": "en",
                "evaluated_query_count": search_result.get("evaluated_query_count", 0),
                "retrieved_article_count": search_result.get("retrieved_article_count", retrieved_count),
                "optimized_queries": search_result.get("optimized_queries", []),
                "beam_search_results": search_result.get("beam_search_results", []),
                "optimization_note": search_result.get("optimization_note", ""),
                "search_status": search_status,
                "failed_query_count": search_result.get("failed_query_count", 0),
                "successful_query_count": search_result.get("successful_query_count", 0),
                "target_article_count": search_result.get("target_article_count", self.max_analysis_articles),
                "article_target_met": search_result.get("article_target_met", retrieved_count >= self.max_analysis_articles),
                "unique_article_count_before_ranking": search_result.get("unique_article_count_before_ranking", retrieved_count),
                "rejected_for_relevance_count": search_result.get("rejected_for_relevance_count", 0),
                "rejected_without_abstract_count": search_result.get("rejected_without_abstract_count", 0),
            },
            "retrieved_articles": retrieved_count,
            "analyzed_articles": analyzed_count,
            "failed_article_count": len(article_errors),
            "article_errors": article_errors,
            "analysis_article_limit": self.max_analysis_articles,
            "search_candidate_count": search_result.get("retrieved_article_count", retrieved_count),
            "article_target_met": retrieved_count >= self.max_analysis_articles,
            "retrieved_article_metadata": retrieved_article_metadata,
            "articles": analyzed_articles,
            "evaluated_sentence_count": sum(
                article.get("evaluated_sentence_count", 0) for article in analyzed_articles
            ),
            "inferred_primary_sentence_count": sum(
                article.get("inferred_primary_sentence_count", 0) for article in analyzed_articles
            ),
        }

    # --------------------------------------------------
    # Print analysis report
    # --------------------------------------------------

    def print_report(self, result):

        print("\nMEDICAL FACTGUARD AI")
        print("=" * 75)

        print("Status:", result["status"])
        print("Claim:", result["claim"])
        print("Category:", result["category"])
        print(
            "Category Confidence:",
            result["category_confidence"],
        )

        print(
            "Retrieved Articles:",
            result["retrieved_articles"],
        )

        print(
            "Analyzed Articles:",
            result["analyzed_articles"],
        )

        # Search optimization report
        search_summary = result.get(
            "search_summary",
            {},
        )

        print("\nSEARCH OPTIMIZATION SUMMARY")
        print("-" * 75)

        print(
            "Evaluated Queries:",
            search_summary.get(
                "evaluated_query_count",
                0,
            ),
        )

        print(
            "Retrieved by Search:",
            search_summary.get(
                "retrieved_article_count",
                0,
            ),
        )

        print("\nOptimized Queries:")

        for query in search_summary.get(
            "optimized_queries",
            [],
        ):
            print("-", query)

        print(
            "\nOptimization Note:",
            search_summary.get(
                "optimization_note",
                "",
            ),
        )

        # Individual article reports
        for article in result["articles"]:

            print("\n" + "=" * 75)

            print("PMID:", article["pmid"])
            print("Title:", article["title"])
            print("Year:", article["year"])
            print("Journal:", article["journal"])
            print("URL:", article["url"])

            print(
                "\nArticle Evidence Summary:",
                article["classification"],
            )

            print("\nOverall Evidence Counts:")

            for label, count in article[
                "overall_counts"
            ].items():
                print(f"{label}: {count}")

            effectiveness = article[
                "effectiveness_analysis"
            ]

            print("\nEffectiveness Analysis:")

            print(
                "Sentence Count:",
                effectiveness["sentence_count"],
            )

            for label, count in effectiveness[
                "counts"
            ].items():
                print(f"{label}: {count}")

            safety = article["safety_analysis"]

            print("\nSafety Analysis:")

            print(
                "Actual Safety Result Count:",
                safety["sentence_count"],
            )

            print(
                "Safety Topic Count:",
                safety["safety_topic_count"],
            )

            print(
                "Safety Concern Count:",
                safety["safety_concern_count"],
            )

            for label, count in safety["counts"].items():
                print(f"{label}: {count}")

            print("\nUncertainty Analysis:")

            print(
                "Textual Uncertainty:",
                article["uncertainty_count"],
            )

            print(
                "Intervals Including Null:",
                article["statistical_uncertainty_count"],
            )

            print("\nStatistical Summary:")

            for key, value in article[
                "statistical_summary"
            ].items():
                print(f"{key}: {value}")

            print("\nSentence Details:")

            for sentence in article["sentences"]:

                print("\nSentence:", sentence["sentence"])

                print(
                    "Original Section:",
                    sentence["section"],
                )

                print(
                    "Original Section Type:",
                    sentence["original_section_type"],
                )

                print(
                    "Sentence Type:",
                    sentence["sentence_type"],
                )

                print(
                    "Evidence:",
                    sentence["evidence_classification"],
                )

                print(
                    "Relevance:",
                    round(sentence["relevance"], 4),
                )

                print(
                    "Evidence Confidence:",
                    round(
                        sentence["evidence_confidence"],
                        4,
                    ),
                )

                print(
                    "Uncertain:",
                    sentence["is_uncertain"],
                )

                print(
                    "Safety Topic:",
                    sentence["safety_topic"],
                )

                print(
                    "Safety Result:",
                    sentence["safety_result"],
                )

                print(
                    "Safety Concern:",
                    sentence["safety_concern"],
                )

                statistical = sentence[
                    "statistical_analysis"
                ]

                if statistical.get("available"):

                    print("\nStatistical Analysis:")

                    print(
                        "Measure:",
                        statistical.get("measure"),
                    )

                    print(
                        "Estimate:",
                        statistical.get("estimate"),
                    )

                    print(
                        "Confidence Interval:",
                        statistical.get("confidence_interval"),
                    )

                    print(
                        "Null Value:",
                        statistical.get("null_value"),
                    )

                    print(
                        "Includes Null:",
                        statistical.get("includes_null"),
                    )

                    print(
                        "Interpretation:",
                        statistical.get(
                            "statistical_interpretation"
                        ),
                    )

                    print(
                        "Study Certainty:",
                        statistical.get("certainty"),
                    )

                print("-" * 70)


if __name__ == "__main__":

    pipeline = EvidencePipeline()

    test_claim = (
        "Vaccines reduce the risk of infectious diseases."
    )

    try:

        result = pipeline.analyze_claim(test_claim)

        pipeline.print_report(result)

    except Exception as error:

        print("\nANALYSIS ERROR")

        print(
            f"{type(error).__name__}: {error}"
        )

    finally:
        pipeline.pubmed_retriever.close()