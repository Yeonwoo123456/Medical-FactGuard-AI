import re


class SentenceClassifier:

    def __init__(self):

        self.patterns = {

            "Research Objective": [
                r"\bthe aim of this (?:study|review|paper|research)\b",
                r"\bthe objective of this (?:study|review|paper)\b",
                r"\bthis study aims? to\b",
                r"\bthis review aims? to\b",
                r"\bwe aimed to\b",
                r"\bwe sought to\b",
                r"\bto evaluate\b",
                r"\bto investigate\b",
                r"\bto assess\b",
                r"\bto examine\b",
                r"\bto determine\b",
                r"\bto identify\b",
                r"\bto compare\b",
                r"\bto summarize\b",
                r"\bto explore\b",
                r"\bto estimate\b",
                r"\bto analyze\b",
                r"\bto analyse\b",
                r"\bto measure\b",
            ],

            "Research Method": [
                r"\bwe included\b",
                r"\bwere included in this study\b",
                r"\bparticipants were enrolled\b",
                r"\bpatients were recruited\b",
                r"\bparticipants were recruited\b",
                r"\ba total of \d+ participants\b",
                r"\b\d+ participants\b",
                r"\b\d+ patients\b",
                r"\b\d+ trials\b",
                r"\b\d+ studies\b",
                r"\bthe study included\b",
                r"\bthe analysis included\b",
                r"\bdata were collected\b",
                r"\bwe searched\b",
                r"\bwe conducted\b",
                r"\bwe performed\b",
                r"\brandomized controlled trial\b",
                r"\brandomised controlled trial\b",
                r"\bsystematic review\b",
                r"\bmeta-analysis\b",
                r"\bcohort study\b",
                r"\bcase-control study\b",
                r"\bcross-sectional study\b",
                r"\bfollow-up period\b",
                r"\bmedian follow-up\b",
                r"\bsearch strategy\b",
                r"\beligibility criteria\b",
                r"\bprimary outcome was\b",
                r"\bsecondary outcomes? included\b",
                r"\bwe extracted data\b",
                r"\bwe assessed the quality\b",
                r"\bthe data were analyzed\b",
                r"\bthe data were analysed\b",
            ],

            "Research Result": [
                r"\bthe results showed\b",
                r"\bresults showed\b",
                r"\bour results indicate\b",
                r"\bthe findings showed\b",
                r"\bfindings suggest\b",
                r"\bwas associated with\b",
                r"\bwere associated with\b",
                r"\bshowed a potential benefit\b",
                r"\bpotential benefit for\b",
                r"\breduced the risk\b",
                r"\breduced risk\b",
                r"\bincreased the risk\b",
                r"\bincreased risk\b",
                r"\blower risk\b",
                r"\bhigher risk\b",
                r"\bsignificantly reduced\b",
                r"\bsignificantly increased\b",
                r"\bno significant difference\b",
                r"\bnot significantly different\b",
                r"\bdid not differ significantly\b",
                r"\bno difference was observed\b",
                r"\bsimilar between\b",
                r"\bthe risk of\b",
                r"\breduction in\b",
                r"\bincrease in\b",
                r"\bdecreased by\b",
                r"\bincreased by\b",
                r"\bwas lower than\b",
                r"\bwas higher than\b",
                r"\bwere lower than\b",
                r"\bwere higher than\b",
                r"\bconfidence interval\b",
                r"\b\d{1,2}(?:\.\d+)?%\s*CI\b",
                r"\bhigh-certainty evidence\b",
                r"\bmoderate-certainty evidence\b",
                r"\blow-certainty evidence\b",
                r"\bvery low-certainty evidence\b",
                r"\bthe evidence suggests\b",
                r"\bthe analysis found\b",
                r"\bwe found that\b",
                r"\bthe study found\b",
                r"\bthe results indicate\b",
                r"\bthe results suggest\b",
                r"\bwas effective\b",
                r"\bwere effective\b",
                r"\bshowed effectiveness\b",
                r"\bwas protective against\b",
                r"\bwere protective against\b",
                r"\bwas observed\b",
                r"\bwere observed\b",
                r"\bwas reported\b",
                r"\bwere reported\b",
                r"\bwas reduced\b",
                r"\bwere reduced\b",
                r"\bwas increased\b",
                r"\bwere increased\b",
                r"\bthe incidence was\b",
                r"\bthe prevalence was\b",
                r"\bthe rate was\b",
                r"\bthe proportion was\b",
                r"\bthe hazard ratio was\b",
                r"\bthe odds ratio was\b",
                r"\bthe risk ratio was\b",
                r"\bthe mean difference was\b",

                # General outcome changes
                r"\b(?:reduced|decreased|increased|improved|worsened)\s+\w+",
            ],

            "Safety Result": [
                r"\badverse events?\b",
                r"\badverse effects?\b",
                r"\bserious adverse events?\b",
                r"\bserious adverse effects?\b",
                r"\bside effects?\b",
                r"\bvaccine-related harms?\b",
                r"\bdrug-related harms?\b",
                r"\btreatment-related\b",
                r"\bmedication-related\b",
                r"\bdrug-induced\b",
                r"\bmiscarriage\b",
                r"\bstillbirth\b",
                r"\bcongenital abnormalities\b",
                r"\bpregnancy outcomes?\b",
                r"\bpregnancy complications?\b",
                r"\btoxicity\b",
                r"\bserious complications?\b",
            ],

            "Background": [
                r"\bprevious studies\b",
                r"\bprior studies\b",
                r"\bprevious research\b",
                r"\bprior research\b",
                r"\bexisting evidence\b",
                r"\ba growing body of evidence\b",
                r"\bprospective studies and meta-analyses\b",
                r"\bhas shown the impact of\b",
                r"\bhave shown the impact of\b",
                r"\bit is well established that\b",
                r"\bis known to\b",
                r"\bare known to\b",
                r"\bhas been associated with\b",
                r"\bhave been associated with\b",
                r"\bis associated with\b",
                r"\bare associated with\b",
                r"\bremains a major\b",
                r"\bcontinues to be\b",
                r"\bthe prevalence of\b",
                r"\bthe incidence of\b",
                r"\bvaccination rates remain\b",
                r"\bsub-optimal in this population\b",
                r"\bdoubts about\b",
                r"\bconcerns about\b",
                r"\bconcerns regarding\b",
                r"\bthere is uncertainty about\b",
                r"\buncertainty surrounding\b",
                r"\bvaccine hesitancy\b",
                r"\bbeyond the burden of\b",
                r"\bin recent years\b",
                r"\bincreasingly important\b",
                r"\bhas become an important\b",
                r"\bpublic health concern\b",
                r"\bthe burden of\b",
            ],

            "Conclusion": [
                r"\bin conclusion\b",
                r"\bwe conclude that\b",
                r"\bthe authors conclude\b",
                r"\bthese findings suggest\b",
                r"\bthese results suggest\b",
                r"\bthe findings indicate\b",
                r"\bour findings demonstrate\b",
                r"\bour results demonstrate\b",
                r"\boverall\b",
                r"\bthe evidence indicates\b",
                r"\bthe evidence supports\b",
                r"\bthe findings support\b",
                r"\bthe results support\b",
                r"\bprovides evidence that\b",
                r"\bthere is evidence that\b",
                r"\bthe study suggests that\b",
                r"\bthe review suggests that\b",
            ],

            "Recommendation": [
                r"\bwe recommend\b",
                r"\bit is recommended that\b",
                r"\bshould be considered\b",
                r"\bshould be implemented\b",
                r"\bshould be incorporated\b",
                r"\bshould be encouraged\b",
                r"\bshould be offered\b",
                r"\bshould be evaluated\b",
                r"\bfurther studies are needed\b",
                r"\bfurther research is needed\b",
                r"\bfurther studies are recommended\b",
                r"\bfuture research should\b",
                r"\bfuture studies should\b",
                r"\badditional research is required\b",
                r"\blong-term follow-up is needed\b",
                r"\bmore research is required\b",
                r"\badditional studies are needed\b",
                r"\bmore studies are needed\b",
                r"\bneeds further investigation\b",
                r"\brequires further investigation\b",
                r"\bshould be investigated\b",
                r"\bshould be examined\b",
                r"\bto guide future research\b",
            ],
        }

        self.compiled_patterns = {
            category: [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]
            for category, patterns in self.patterns.items()
        }

        self.safety_terms = re.compile(
            r"\b("
            r"adverse events?|adverse effects?|"
            r"serious adverse events?|serious adverse effects?|"
            r"side effects?|vaccine-related harms?|"
            r"drug-related harms?|treatment-related harms?|"
            r"medication-related harms?|miscarriage|stillbirth|"
            r"congenital abnormalities|pregnancy outcomes?|"
            r"pregnancy complications?|toxicity|"
            r"serious complications?|vaccine safety|drug safety|"
            r"treatment safety|medication safety|safety profile|"
            r"SAEs?|AEs?"
            r")\b",
            re.IGNORECASE,
        )

        self.safety_result_expressions = re.compile(
            r"\b("
            r"was|were|is|are|showed|shows|found|"
            r"occurred|reported|observed|recorded|"
            r"experienced|developed|similar|comparable|"
            r"higher|lower|increased|decreased|reduced|remained|"
            r"appeared|seemed|did not differ|no increase|"
            r"no difference|not significantly different|"
            r"significantly different|cannot be excluded|"
            r"could not be excluded"
            r")\b",
            re.IGNORECASE,
        )

    # --------------------------------------------------
    # Classify Sentence
    # --------------------------------------------------

    def classify(self, sentence):

        if not isinstance(sentence, str) or not sentence.strip():

            return {
                "type": "Other",
                "matched_patterns": [],
                "confidence": 0.0,
                "scores": {}
            }

        sentence = sentence.strip()

        scores = {}
        matched_patterns = {}

        for category, patterns in self.compiled_patterns.items():

            matches = [
                pattern.pattern
                for pattern in patterns
                if pattern.search(sentence)
            ]

            scores[category] = len(matches)
            matched_patterns[category] = matches

        total_score = sum(scores.values())

        if total_score == 0:

            return {
                "type": "Other",
                "matched_patterns": [],
                "confidence": 0.0,
                "scores": scores
            }

        # Priority 1: Recommendations

        if scores["Recommendation"] > 0:
            selected_category = "Recommendation"

        # Priority 2: Research objectives

        elif scores["Research Objective"] > 0:
            selected_category = "Research Objective"

        # Priority 3: Research methods

        elif scores["Research Method"] > 0:
            selected_category = "Research Method"

        else:

            has_safety_term = bool(
                self.safety_terms.search(sentence)
            )

            has_safety_result = bool(
                self.safety_result_expressions.search(sentence)
            )

            if has_safety_term and has_safety_result:

                selected_category = "Safety Result"

            else:

                # Conclusion takes priority over Research Result
                # when a conclusion pattern is explicitly detected.

                priority_order = [
                    "Conclusion",
                    "Research Result",
                    "Background"
                ]

                selected_category = max(
                    priority_order,
                    key=lambda category: scores[category]
                )

                if scores[selected_category] == 0:
                    selected_category = "Other"

        selected_score = scores.get(selected_category, 0)

        confidence = (
            selected_score / total_score
            if total_score > 0
            else 0.0
        )

        return {
            "type": selected_category,
            "matched_patterns": matched_patterns.get(
                selected_category, []
            ),
            "confidence": round(confidence, 4),
            "scores": scores
        }