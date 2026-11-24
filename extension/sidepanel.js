const API_URL = "http://127.0.0.1:8000";

/* =========================================
   1. Translations
========================================= */

const translations = {
    en: {
        ready: "READY TO ANALYZE",
        title: "Verify Medical Information.",
        subtitle: "Analyze medical claims and discover scientific evidence across the web.",
        currentPage: "Current Page",
        mode: "Analysis Mode",
        pageScan: "Full Page Scan",
        pageScanDescription: "Automatically extract medical claims from this webpage.",
        scan: "Scan & Extract Claims",
        selectedText: "Selected Text",
        selectedTextDescription: "Select text and right-click to analyze all selected sentences.",
        rightClick: "Right-click",
        claims: "Detected Claims",
        noClaims: "No claims detected.",
        noClaimsDescription: "Scan a webpage or select text to begin.",
        analyze: "Analyze Claim",
        analyzing: "Analyzing claim...",
        extraction: "Extracting webpage content...",
        extractionFailed: "Could not extract webpage content.",
        selectionReceived: "Selected text received.",
        selectedCount: "sentences extracted from selected text.",
        detectedCount: "medical claims detected.",
        enterText: "Select a claim first.",
        result: "Analysis Results",
        category: "Medical Category",
        status: "Analysis Status",
        articles: "Analyzed Articles",
        supporting: "Supporting Evidence",
        contradicting: "Contradicting Evidence",
        neutral: "Neutral Evidence",
        insufficient: "Insufficient Evidence",
        noSentences: "No classified research sentences were returned.",
        noReferences: "No research articles were returned.",
        serverError: "Could not connect to the Python server.",
        analysisFailed: "Analysis failed. Please check the server.",
        disclaimer: "For informational purposes only. Not medical advice.",
        loading: "Loading page information...",
        restricted: "This page cannot be accessed by the extension.",
        tabNotFound: "Could not identify the current webpage.",
        viewPaper: "View Source Paper",
        journal: "Journal",
        year: "Year",
        pmid: "PMID",
        relevance: "Relevance",
        confidence: "Confidence",
        section: "Section",
        noCategorySentences: "No sentences in this category.",
        extracted: "Claim extraction completed.",
        noClaimsFound: "No medical claims were detected.",
        retrieved: "Retrieved papers",
        target: "Target",
        papersShort: "Papers below the target",
        paperErrors: "Paper analysis errors",
        searchStatus: "PubMed search status",
        noArticles: "No eligible PubMed papers with abstracts were found for this claim.",
        noClassified: "Papers were retrieved, but no classifiable evidence sentences were produced.",
        papers: "Retrieved research papers",
        paperAnalysis: "Paper processing status",
        paperAnalysisFailed: "Analysis failed",
        paperAnalysisCompleted: "Analysis completed",
        processed: "Processed",
        failed: "Failed",
        targetMet: "10-paper target reached",
        targetNotMet: "Fewer than 10 relevant papers found",
        references: "Research references",
        translateToKorean: "Translate to Korean",
        showOriginal: "Show original",
        translating: "Translating...",
        translationFailed: "Translation failed. Please try again."
    },

    ko: {
        ready: "분석 준비 완료",
        title: "의학 정보를 검증하세요.",
        subtitle: "의학적 주장을 분석하고 과학적 근거를 찾아보세요.",
        currentPage: "현재 페이지",
        mode: "분석 방식",
        pageScan: "전체 페이지 분석",
        pageScanDescription: "현재 웹페이지에서 의학적 주장 후보를 자동으로 추출합니다.",
        scan: "페이지 분석 및 주장 추출",
        selectedText: "선택 텍스트",
        selectedTextDescription: "텍스트를 선택하고 우클릭하면 선택한 모든 문장을 분석할 수 있습니다.",
        rightClick: "우클릭",
        claims: "추출된 주장",
        noClaims: "추출된 의학적 주장이 없습니다.",
        noClaimsDescription: "페이지를 분석하거나 텍스트를 선택해 시작하세요.",
        analyze: "주장 분석하기",
        analyzing: "주장을 분석하고 있습니다...",
        extraction: "웹페이지 콘텐츠 추출 중...",
        extractionFailed: "웹페이지 콘텐츠를 추출하지 못했습니다.",
        selectionReceived: "선택한 텍스트를 받았습니다.",
        selectedCount: "개의 선택 문장을 추출했습니다.",
        detectedCount: "개의 의학적 주장 후보를 찾았습니다.",
        enterText: "먼저 분석할 주장을 선택해 주세요.",
        result: "분석 결과",
        category: "의학 분야",
        status: "분석 상태",
        articles: "분석 논문 수",
        supporting: "지지하는 연구 문장",
        contradicting: "반박하는 연구 문장",
        neutral: "중립적인 연구 문장",
        insufficient: "근거 불충분",
        noSentences: "분류된 연구 문장이 반환되지 않았습니다.",
        noReferences: "반환된 연구 논문이 없습니다.",
        serverError: "Python 서버에 연결할 수 없습니다.",
        analysisFailed: "분석에 실패했습니다. 서버를 확인해 주세요.",
        disclaimer: "정보 제공 목적이며 의학적 조언을 대체하지 않습니다.",
        loading: "페이지 정보를 불러오는 중...",
        restricted: "Extension에서 이 페이지에 접근할 수 없습니다.",
        tabNotFound: "현재 웹페이지를 찾을 수 없습니다.",
        viewPaper: "해당 논문 원문 보기",
        journal: "학술지",
        year: "연도",
        pmid: "PMID",
        relevance: "관련성",
        confidence: "분류 신뢰도",
        section: "논문 섹션",
        noCategorySentences: "이 분류에 해당하는 연구 문장이 없습니다.",
        extracted: "주장 추출이 완료되었습니다.",
        noClaimsFound: "의학적 주장 후보를 찾지 못했습니다.",
        retrieved: "검색된 논문",
        target: "목표",
        papersShort: "목표 논문 수 미달",
        paperErrors: "논문 분석 오류",
        searchStatus: "PubMed 검색 상태",
        noArticles: "이 주장과 관련된 초록 포함 PubMed 논문을 찾지 못했습니다.",
        noClassified: "논문은 검색했지만 분류 가능한 근거 문장을 생성하지 못했습니다.",
        papers: "검색된 연구 논문",
        paperAnalysis: "논문 처리 상태",
        paperAnalysisFailed: "분석 실패",
        paperAnalysisCompleted: "분석 완료",
        processed: "처리 완료",
        failed: "실패",
        targetMet: "논문 10편 목표 달성",
        targetNotMet: "관련 논문 10편 미만 검색",
        references: "연구 참고문헌",
        translateToKorean: "한국어로 번역",
        showOriginal: "원문 보기",
        translating: "번역 중...",
        translationFailed: "번역에 실패했습니다. 다시 시도해 주세요."
    }
};


/* =========================================
   2. DOM Elements
========================================= */

const elements = {
    languageSelect: document.getElementById("languageSelect"),
    systemStatus: document.getElementById("systemStatus"),

    welcomeTitle: document.getElementById("welcomeTitle"),
    welcomeDescription: document.getElementById("welcomeDescription"),

    pageHeading: document.getElementById("pageHeading"),
    pageTitle: document.getElementById("pageTitle"),
    pageDomain: document.getElementById("pageDomain"),

    modeHeading: document.getElementById("modeHeading"),
    pageScanTitle: document.getElementById("pageScanTitle"),
    pageScanDescription: document.getElementById("pageScanDescription"),
    pageScanButton: document.getElementById("pageScanButton"),

    selectedTextTitle: document.getElementById("selectedTextTitle"),
    selectedTextDescription: document.getElementById("selectedTextDescription"),
    contextMenuLabel: document.getElementById("contextMenuLabel"),

    claimsHeading: document.getElementById("claimsHeading"),
    claimCount: document.getElementById("claimCount"),
    claimsContainer: document.getElementById("claimsContainer"),

    resultSection: document.getElementById("resultSection"),
    resultHeading: document.getElementById("resultHeading"),
    resultContainer: document.getElementById("resultContainer"),

    disclaimer: document.getElementById("disclaimer")
};


/* =========================================
   3. Application State
========================================= */

let currentLanguage = "en";
let currentPage = null;

let selectedClaim = "";
let extractedPageText = "";
let extractedClaims = [];

let activeTabId = null;
let analysisMode = "page";

let isAnalyzing = false;


function t(key) {
    return translations[currentLanguage]?.[key] || key;
}


function setStatus(message) {
    if (elements.systemStatus) {
        elements.systemStatus.textContent = message;
    }
}


/* =========================================
   4. Language
========================================= */

function applyLanguage(language) {

    currentLanguage = translations[language]
        ? language
        : "en";

    document.documentElement.lang = currentLanguage;

    document.body.classList.toggle(
        "korean",
        currentLanguage === "ko"
    );

    if (elements.languageSelect) {
        elements.languageSelect.value = currentLanguage;
    }

    const textMap = {
        welcomeTitle: "title",
        welcomeDescription: "subtitle",
        pageHeading: "currentPage",
        modeHeading: "mode",
        pageScanTitle: "pageScan",
        pageScanDescription: "pageScanDescription",
        selectedTextTitle: "selectedText",
        selectedTextDescription: "selectedTextDescription",
        contextMenuLabel: "rightClick",
        claimsHeading: "claims",
        resultHeading: "result",
        disclaimer: "disclaimer"
    };

    Object.entries(textMap).forEach(
        ([elementKey, translationKey]) => {

            const element = elements[elementKey];

            if (element) {
                element.textContent = t(translationKey);
            }
        }
    );

    if (elements.pageScanButton) {
        elements.pageScanButton.textContent = t("scan");
    }

    renderClaimList();
}


async function loadLanguage() {

    try {

        const stored = await chrome.storage.local.get("language");

        applyLanguage(stored.language || "en");

    } catch (error) {

        console.error("Language loading error:", error);

        applyLanguage("en");
    }
}


elements.languageSelect?.addEventListener(
    "change",
    async () => {

        const language = elements.languageSelect.value;

        applyLanguage(language);

        await chrome.storage.local.set({
            language
        });
    }
);


/* =========================================
   5. Active Tab Detection
========================================= */

async function getActiveTab() {

    let tab = null;

    try {

        const stored = await chrome.storage.local.get(
            "factguardActiveTabId"
        );

        const savedTabId = stored.factguardActiveTabId;

        if (Number.isInteger(savedTabId)) {

            try {
                tab = await chrome.tabs.get(savedTabId);
            } catch (error) {
                console.warn("Saved tab unavailable:", error.message);
            }
        }

    } catch (error) {
        console.warn("Tab storage lookup failed:", error);
    }


    if (!tab) {

        const tabs = await chrome.tabs.query({
            active: true,
            lastFocusedWindow: true
        });

        tab = tabs?.[0] || null;
    }


    if (!tab || !Number.isInteger(tab.id) || !tab.url) {
        throw new Error("No active tab");
    }


    const url = new URL(tab.url);

    if (!["http:", "https:"].includes(url.protocol)) {
        throw new Error("Restricted page");
    }


    activeTabId = tab.id;

    return tab;
}


/* =========================================
   6. Current Page
========================================= */

async function loadCurrentPage() {

    try {

        setStatus(t("loading"));

        const tab = await getActiveTab();

        const url = new URL(tab.url);

        currentPage = {
            title: tab.title || url.hostname,
            url: tab.url
        };

        if (elements.pageTitle) {
            elements.pageTitle.textContent = currentPage.title;
        }

        if (elements.pageDomain) {
            elements.pageDomain.textContent = url.hostname;
        }

        setStatus(t("ready"));

    } catch (error) {

        console.error("Page loading error:", error);

        if (elements.pageTitle) {
            elements.pageTitle.textContent =
                error.message === "Restricted page"
                    ? t("restricted")
                    : t("tabNotFound");
        }

        if (elements.pageDomain) {
            elements.pageDomain.textContent = "---";
        }
    }
}


/* =========================================
   7. Page Content Extraction
========================================= */

async function extractPageContent() {

    const tab = await getActiveTab();

    await chrome.scripting.executeScript({

        target: {
            tabId: tab.id
        },

        files: ["content.js"]
    });


    const results = await chrome.scripting.executeScript({

        target: {
            tabId: tab.id
        },

        func: () => globalThis.__FACTGUARD_PAGE_DATA__ || null
    });


    const pageData = results?.[0]?.result;

    if (!pageData || !pageData.text) {
        throw new Error("No readable content");
    }

    return pageData;
}


/* =========================================
   8. Medical Claim Extraction
========================================= */

const medicalKeywords = [

    "vaccine", "vaccines", "vaccination", "immunization",
    "medicine", "medication", "drug", "drugs",
    "treatment", "treatments", "therapy", "therapies",
    "cancer", "tumor", "tumour", "disease", "diseases",
    "infection", "infections", "virus", "viruses",
    "bacteria", "bacterial", "symptom", "symptoms",
    "side effect", "side effects", "cure",
    "clinical trial", "antibiotic", "antibiotics",
    "health", "medical", "patient", "patients",
    "blood pressure", "heart disease",
    "immune system", "immunity",
    "nutrition", "food poisoning", "bloating",
    "digestive system", "respiratory",

    "백신", "예방접종", "면역", "면역력",
    "약", "의약품", "약물", "복용", "섭취",
    "치료", "치료제", "항생제",
    "암", "종양", "질병", "질환",
    "감염", "바이러스", "세균", "박테리아",
    "증상", "부작용", "합병증",
    "혈압", "심장병", "심혈관",
    "건강", "의학", "의료", "환자",
    "식중독", "소화", "위장", "호흡기",
    "염증", "통증", "알레르기",
    "영양", "음식", "식품",
    "체온", "발열", "설사", "구토",
    "세균 번식", "세균 감염"
];


const claimIndicators = [

    "cause", "causes", "caused", "causing",
    "prevent", "prevents", "prevented",
    "cure", "cures", "cured",
    "increase", "increases", "decrease", "decreases",
    "reduce", "reduces", "improve", "improves",
    "lead to", "leads to", "result in", "results in",
    "effective", "ineffective",
    "safe", "unsafe", "harmful", "beneficial",
    "proven", "evidence", "study", "studies",
    "associated with", "linked to",
    "suggest", "suggests", "show", "shows",
    "indicate", "indicates",
    "risk", "risks", "develop", "develops",
    "transmit", "transmits", "effectiveness",
    "confirmed", "fails", "failed", "works",
    "not effective", "no evidence", "not proven",
    "cannot prevent", "recommend", "recommended",
    "should", "must", "avoid", "side effects",

    "유발", "발생", "예방", "치료",
    "증가", "감소", "감소시", "높인다",
    "낮춘다", "줄인다", "늘린다",
    "개선", "악화", "완화",
    "효과", "효능", "효과적", "비효과적", "무효",
    "안전", "위험", "유해", "부작용", "합병증",
    "원인", "관련", "연관", "때문", "초래",
    "이어진다", "전염", "전파", "감염",
    "도움", "도움이 된다",
    "증상을 완화", "증상을 악화",
    "위험이 있다", "위험이 높다",
    "가능성이 있다", "가능하다",
    "나타난다", "나타날 수",
    "권장", "추천", "주의", "피해야",
    "금물", "삼가야", "섭취해야", "복용해야",
    "해야 한다", "해서는 안 된다",
    "필요하다", "필수적",
    "확인됐다", "밝혀졌다",
    "연구에 따르면", "연구 결과",
    "입증", "증명", "보고됐다"
];


function containsKeyword(sentence, keywords) {

    const lower = sentence.toLowerCase();

    return keywords.some(keyword => {

        if (/[가-힣]/.test(keyword)) {
            return sentence.includes(keyword);
        }

        const escaped = keyword.replace(
            /[.*+?^${}()|[\]\\]/g,
            "\\$&"
        );

        return new RegExp(
            `\\b${escaped}\\b`,
            "i"
        ).test(lower);
    });
}


function containsMedicalKeyword(sentence) {
    return containsKeyword(sentence, medicalKeywords);
}


function containsClaimIndicator(sentence) {
    return containsKeyword(sentence, claimIndicators);
}


/* =========================================
   9. Sentence Splitting
========================================= */

function splitPageIntoSentences(text) {

    if (typeof text !== "string" || !text.trim()) {
        return [];
    }

    const normalized = text

        .replace(/\r\n?/g, "\n")

        .replace(
            /[◆◇♦▪●■▶►]+/g,
            "\n"
        )

        .replace(
            /(?<=[.!?。！？])\s+/g,
            "\n"
        )

        .replace(
            /[;；]+/g,
            "\n"
        );


    return normalized

        .split(/\n+/)

        .map(sentence => sentence
            .replace(/^\s*[-–—•*]+\s*/, "")
            .replace(/\s+/g, " ")
            .trim()
        )

        .filter(sentence => sentence.length >= 12);
}


/* =========================================
   10. Full Page Claim Extraction
========================================= */

function extractMedicalClaimsFromText(text) {

    const sentences = splitPageIntoSentences(text);

    const claims = [];
    const seen = new Set();

    for (const sentence of sentences) {

        if (
            !containsMedicalKeyword(sentence) ||
            !containsClaimIndicator(sentence)
        ) {
            continue;
        }

        const normalized = sentence
            .toLowerCase()
            .replace(/\s+/g, " ")
            .trim();

        if (!seen.has(normalized)) {
            claims.push(sentence);
            seen.add(normalized);
        }
    }

    return claims;
}


/* =========================================
   11. Selected Text Extraction
   Keep every selected sentence.
========================================= */

function extractAllSelectedSentences(text) {

    if (typeof text !== "string" || !text.trim()) {
        return [];
    }

    const sentences = splitPageIntoSentences(text);

    const results = [];
    const seen = new Set();

    for (const sentence of sentences) {

        const normalized = sentence
            .toLowerCase()
            .replace(/\s+/g, " ")
            .trim();

        if (!normalized || seen.has(normalized)) {
            continue;
        }

        results.push(sentence);
        seen.add(normalized);
    }

    return results;
}


/* =========================================
   12. UI Helpers
========================================= */

function createInfoCard(title, description) {

    const card = document.createElement("div");
    card.className = "result-card";

    const heading = document.createElement("h4");
    heading.textContent = title;

    const paragraph = document.createElement("p");
    paragraph.textContent = description;

    card.append(heading, paragraph);

    return card;
}


function createElement(tag, className, text) {

    const element = document.createElement(tag);

    if (className) {
        element.className = className;
    }

    if (text !== undefined && text !== null) {
        element.textContent = String(text);
    }

    return element;
}


/* =========================================
   13. Full Page Scan
========================================= */

elements.pageScanButton?.addEventListener(
    "click",
    async () => {

        elements.pageScanButton.disabled = true;
        elements.pageScanButton.textContent = "...";

        setStatus(t("extraction"));

        try {

            const pageData = await extractPageContent();

            extractedPageText = pageData.text;

            analysisMode = "page";

            extractedClaims = extractMedicalClaimsFromText(
                extractedPageText
            );

            selectedClaim = "";

            elements.resultSection.hidden = true;
            elements.resultContainer.replaceChildren();

            await chrome.storage.local.set({

                latestPageData: pageData,

                latestExtractedClaims: extractedClaims,

                latestSelectedText: null,

                latestSelectionMode: "page",

                factguardActiveTabId: activeTabId
            });

            renderClaimList();

            setStatus(
                extractedClaims.length
                    ? `${extractedClaims.length} ${t("detectedCount")}`
                    : t("noClaimsFound")
            );

            console.log(
                "Full page extracted claims:",
                extractedClaims
            );

        } catch (error) {

            console.error("Page extraction error:", error);

            setStatus(
                error.message === "Restricted page"
                    ? t("restricted")
                    : t("extractionFailed")
            );

        } finally {

            elements.pageScanButton.disabled = false;
            elements.pageScanButton.textContent = t("scan");
        }
    }
);


/* =========================================
   14. Selected Text Processing
========================================= */

function addSelectedClaim(text) {

    const cleanText = String(text || "").trim();

    if (!cleanText) {
        return;
    }

    analysisMode = "selected_text";

    // No medical keyword or claim-indicator filtering here.
    extractedClaims = extractAllSelectedSentences(cleanText);

    if (extractedClaims.length === 0) {
        extractedClaims = [cleanText];
    }

    selectedClaim = extractedClaims[0];

    elements.resultSection.hidden = true;
    elements.resultContainer.replaceChildren();

    renderClaimList();

    chrome.storage.local.set({

        latestExtractedClaims: extractedClaims,

        latestSelectionMode: "selected_text"

    }).catch(error => {
        console.warn("Selection storage error:", error);
    });

    setStatus(
        currentLanguage === "ko"
            ? `${extractedClaims.length}${t("selectedCount")}`
            : `${extractedClaims.length} ${t("selectedCount")}`
    );

    elements.claimsContainer.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });

    console.log("Selected text:", cleanText);
    console.log("Extracted selected sentences:", extractedClaims);
}


/* =========================================
   15. Claim List
========================================= */

function renderClaimList() {

    if (!elements.claimsContainer) {
        return;
    }

    elements.claimsContainer.replaceChildren();

    const claims = extractedClaims.length
        ? extractedClaims
        : (selectedClaim ? [selectedClaim] : []);

    elements.claimCount.textContent = String(claims.length);

    if (claims.length === 0) {

        const empty = createElement("div", "empty-state");

        empty.append(
            createElement("div", "", t("noClaims")),
            createElement("p", "", t("noClaimsDescription"))
        );

        elements.claimsContainer.appendChild(empty);

        return;
    }

    claims.forEach((claim, index) => {

        const card = createElement("div", "claim-card");

        const header = createElement("div", "claim-card-header");

        const number = createElement(
            "span",
            "claim-number",
            `CLAIM ${String(index + 1).padStart(2, "0")}`
        );

        const tag = createElement(
            "span",
            "claim-tag",
            analysisMode === "selected_text"
                ? t("selectedText")
                : t("pageScan")
        );

        header.append(number, tag);

        const claimText = createElement(
            "p",
            "claim-text",
            claim
        );

        const analyzeButton = createElement(
            "button",
            "claim-action",
            t("analyze")
        );

        analyzeButton.type = "button";

        analyzeButton.addEventListener("click", () => {
            analyzeSelectedClaim(claim);
        });

        card.append(
            header,
            claimText,
            analyzeButton
        );

        elements.claimsContainer.appendChild(card);
    });
}


/* =========================================
   16. Storage Changes
========================================= */

chrome.storage.onChanged.addListener(
    (changes, areaName) => {

        if (areaName !== "local") {
            return;
        }

        if (changes.latestSelectedText) {

            const newValue =
                changes.latestSelectedText.newValue;

            if (newValue?.text) {
                addSelectedClaim(newValue.text);
            }
        }

        if (changes.factguardActiveTabId) {

            const newTabId =
                changes.factguardActiveTabId.newValue;

            if (Number.isInteger(newTabId)) {
                activeTabId = newTabId;
                loadCurrentPage();
            }
        }
    }
);


/* =========================================
   17. Evidence Classification
========================================= */

const evidenceLabels = [
    "Supporting",
    "Contradicting",
    "Neutral",
    "Insufficient"
];


function normalizeEvidenceLabel(value) {

    const label = String(value || "")
        .trim()
        .toLowerCase()
        .replace(/[_-]+/g, " ");

    if (["supporting", "support", "supports", "positive", "supports claim"].includes(label)) {
        return "Supporting";
    }

    if (["contradicting", "contradiction", "contradictory", "opposing", "against", "refuting"].includes(label)) {
        return "Contradicting";
    }

    if (["neutral", "mixed", "uncertain", "inconclusive"].includes(label)) {
        return "Neutral";
    }

    if (["insufficient", "insufficient evidence", "not enough evidence", "low relevance", "unclassified", "not evaluated"].includes(label)) {
        return "Insufficient";
    }

    return null;
}

function collectEvidenceSentences(articles) {

    const groups = {
        Supporting: [],
        Contradicting: [],
        Neutral: [],
        Insufficient: []
    };

    const seen = new Set();

    articles.forEach(article => {

        if (!article || typeof article !== "object") {
            return;
        }

        const sentenceSource =
            Array.isArray(article.sentences) ? article.sentences :
            Array.isArray(article.sentence_results) ? article.sentence_results :
            Array.isArray(article.sentence_details) ? article.sentence_details :
            Array.isArray(article.evidence_sentences) ? article.evidence_sentences :
            [];

        const sentences = sentenceSource;

        sentences.forEach(sentenceData => {

            if (
                !sentenceData ||
                typeof sentenceData.sentence !== "string" ||
                !sentenceData.sentence.trim()
            ) {
                return;
            }

            const label = normalizeEvidenceLabel(
                sentenceData.evidence_classification ||
                sentenceData.classification ||
                sentenceData.evidence
            );

            if (!label) {
                return;
            }

            const sentenceText = sentenceData.sentence.trim();

            const pmid = String(article.pmid || "");

            const uniqueKey = [
                pmid,
                label,
                sentenceText.toLowerCase()
            ].join("|");

            if (seen.has(uniqueKey)) {
                return;
            }

            seen.add(uniqueKey);

            groups[label].push({

                sentence: sentenceText,

                section:
                    sentenceData.section ||
                    sentenceData.original_section_type ||
                    "",

                sentenceType:
                    sentenceData.sentence_type || "",

                relevance:
                    sentenceData.relevance,

                confidence:
                    sentenceData.evidence_confidence,

                title:
                    article.title || "",

                journal:
                    article.journal || "",

                year:
                    article.year || "",

                pmid,

                url:
                    article.url || ""
            });
        });
    });

    return groups;
}


/* =========================================
   18. Evidence Counts
========================================= */

function getEvidenceCounts(groups) {

    const counts = {};

    evidenceLabels.forEach(label => {
        counts[label] = groups[label].length;
    });

    return counts;
}


function createEvidenceCounts(counts) {

    const container = createElement(
        "div",
        "evidence-counts"
    );

    const labels = {
        Supporting: t("supporting"),
        Contradicting: t("contradicting"),
        Neutral: t("neutral"),
        Insufficient: t("insufficient")
    };

    evidenceLabels.forEach(label => {

        const item = createElement(
            "div",
            `evidence-count evidence-count-${label.toLowerCase()}`
        );

        const name = createElement(
            "span",
            "",
            labels[label]
        );

        const number = createElement(
            "strong",
            "",
            counts[label]
        );

        item.append(name, number);

        container.appendChild(item);
    });

    return container;
}


/* =========================================
   19. Evidence Section
========================================= */

function getEvidenceSectionTitle(label) {

    const labels = {
        Supporting: t("supporting"),
        Contradicting: t("contradicting"),
        Neutral: t("neutral"),
        Insufficient: t("insufficient")
    };

    return labels[label] || label;
}


function createSafePaperUrl(article) {

    const rawUrl = String(article.url || "").trim();

    if (rawUrl) {

        try {

            const parsed = new URL(rawUrl);

            if (
                parsed.protocol === "https:" &&
                (
                    parsed.hostname === "pubmed.ncbi.nlm.nih.gov" ||
                    parsed.hostname.endsWith(".nih.gov")
                )
            ) {
                return parsed.href;
            }

        } catch (error) {
            console.warn("Invalid article URL:", rawUrl);
        }
    }

    const pmid = String(article.pmid || "").trim();

    if (/^\d+$/.test(pmid)) {
        return `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`;
    }

    return "";
}


const koreanTranslationCache = new Map();

async function translateEvidenceToKorean(text) {
    const sourceText = String(text || "").trim();

    if (!sourceText) {
        throw new Error("No text to translate.");
    }

    if (koreanTranslationCache.has(sourceText)) {
        return koreanTranslationCache.get(sourceText);
    }

    const endpoint = new URL(
        "https://translate.googleapis.com/translate_a/single"
    );

    endpoint.search = new URLSearchParams({
        client: "gtx",
        sl: "auto",
        tl: "ko",
        dt: "t",
        q: sourceText
    }).toString();

    const response = await fetch(endpoint.toString(), {
        method: "GET",
        headers: { "Accept": "application/json" }
    });

    if (!response.ok) {
        throw new Error(`Translation service returned ${response.status}.`);
    }

    const payload = await response.json();
    const translated = Array.isArray(payload?.[0])
        ? payload[0]
            .map(part => Array.isArray(part) ? part[0] : "")
            .filter(Boolean)
            .join("")
            .trim()
        : "";

    if (!translated) {
        throw new Error("Empty translation response.");
    }

    koreanTranslationCache.set(sourceText, translated);
    return translated;
}


function createEvidenceSentenceCard(item, label) {

    const card = createElement(
        "article",
        `result-card evidence-sentence-card evidence-${label.toLowerCase()}`
    );

    // The actual abstract sentence is the main content.
    const sentence = createElement(
        "p",
        "evidence-sentence",
        item.sentence
    );

    card.appendChild(sentence);

    // Optional Korean translation. The original English sentence remains visible.
    const translationControls = createElement(
        "div",
        "evidence-translation-controls"
    );

    const translateButton = createElement(
        "button",
        "evidence-translate-button",
        t("translateToKorean")
    );
    translateButton.type = "button";

    const translatedSentence = createElement(
        "p",
        "evidence-sentence evidence-sentence-translation"
    );
    translatedSentence.hidden = true;
    translatedSentence.lang = "ko";

    let isTranslatedVisible = false;
    let isTranslationLoading = false;

    translateButton.addEventListener("click", async () => {
        if (isTranslationLoading) return;

        if (isTranslatedVisible) {
            translatedSentence.hidden = true;
            isTranslatedVisible = false;
            translateButton.textContent = t("translateToKorean");
            return;
        }

        isTranslationLoading = true;
        translateButton.disabled = true;
        translateButton.textContent = t("translating");

        try {
            const koreanText = await translateEvidenceToKorean(item.sentence);
            translatedSentence.textContent = koreanText;
            translatedSentence.hidden = false;
            isTranslatedVisible = true;
            translateButton.textContent = t("showOriginal");
        } catch (error) {
            console.error("Evidence translation error:", error);
            translateButton.textContent = t("translationFailed");
        } finally {
            isTranslationLoading = false;
            translateButton.disabled = false;
        }
    });

    translationControls.appendChild(translateButton);
    card.append(translationControls, translatedSentence);


    // Metadata.
    const metadataParts = [];

    if (item.journal) {
        metadataParts.push(item.journal);
    }

    if (item.year) {
        metadataParts.push(String(item.year));
    }

    if (item.pmid) {
        metadataParts.push(`PMID: ${item.pmid}`);
    }

    if (metadataParts.length > 0) {

        const metadata = createElement(
            "p",
            "evidence-metadata",
            metadataParts.join(" · ")
        );

        card.appendChild(metadata);
    }


    // Section, relevance, and confidence.
    const detailParts = [];

    if (item.section) {
        detailParts.push(
            `${t("section")}: ${item.section}`
        );
    }

    const relevance = Number(item.relevance);

    if (Number.isFinite(relevance)) {
        detailParts.push(
            `${t("relevance")}: ${relevance.toFixed(3)}`
        );
    }

    const confidence = Number(item.confidence);

    if (Number.isFinite(confidence)) {
        detailParts.push(
            `${t("confidence")}: ${confidence.toFixed(3)}`
        );
    }

    if (detailParts.length > 0) {

        const details = createElement(
            "p",
            "evidence-details",
            detailParts.join(" · ")
        );

        card.appendChild(details);
    }


    // Direct link to the paper.
    const paperUrl = createSafePaperUrl(item);

    if (paperUrl) {

        const link = createElement(
            "a",
            "evidence-source-link",
            `↗ ${t("viewPaper")}`
        );

        link.href = paperUrl;
        link.target = "_blank";
        link.rel = "noopener noreferrer";

        card.appendChild(link);
    }

    return card;
}


function renderEvidenceSection(label, sentences) {

    const section = createElement(
        "section",
        `evidence-section evidence-section-${label.toLowerCase()}`
    );

    const header = createElement(
        "div",
        "evidence-section-header"
    );

    const title = createElement(
        "h3",
        "evidence-section-title",
        getEvidenceSectionTitle(label)
    );

    const count = createElement(
        "span",
        "evidence-section-count",
        sentences.length
    );

    header.append(title, count);

    section.appendChild(header);


    if (sentences.length === 0) {

        const empty = createElement(
            "p",
            "empty-evidence",
            t("noCategorySentences")
        );

        section.appendChild(empty);

        return section;
    }


    sentences.forEach(item => {

        section.appendChild(
            createEvidenceSentenceCard(item, label)
        );
    });

    return section;
}


/* =========================================
   20. Analysis Result Display
========================================= */

function displayAnalysisResult(result) {

    elements.resultContainer.replaceChildren();

    if (result?.result && typeof result.result === "object") {
        result = result.result;
    }

    const articles = Array.isArray(result?.articles) ? result.articles : [];
    const retrievedPapers = Array.isArray(result?.retrieved_article_metadata)
        ? result.retrieved_article_metadata
        : articles;
    const searchSummary = result?.search_summary || {};
    const failedPmids = new Set(
        (Array.isArray(result?.article_errors) ? result.article_errors : [])
            .map(item => String(item?.pmid || "").trim())
            .filter(Boolean)
    );
    const analyzedPmids = new Set(
        articles.map(item => String(item?.pmid || "").trim()).filter(Boolean)
    );
    const retrievedCount = Number(
        result.retrieved_article_count ??
        result.retrieved_articles ??
        searchSummary.retrieved_article_count ??
        retrievedPapers.length
    );
    const analyzedCount = Number(
        result.analyzed_article_count ??
        result.analyzed_articles ??
        articles.filter(article => article && article.analysis_status !== "failed").length
    );
    const failedCount = Number(
        result.failed_article_count ??
        (Array.isArray(result.article_errors) ? result.article_errors.length : 0)
    );
    const targetCount = Number(
        result.target_article_count ?? searchSummary.target_article_count ?? 10
    );
    const targetMet = Boolean(
        result.article_target_met ?? searchSummary.article_target_met ??
        (retrievedCount >= targetCount)
    );

    const summary = createElement("div", "result-card analysis-summary");
    summary.appendChild(createElement("h3", "analysis-summary-title", t("result")));
    summary.appendChild(createElement(
        "p", "analysis-summary-line",
        `${t("category")}: ${result.category || "Unclassified"}`
    ));
    summary.appendChild(createElement(
        "p", "analysis-summary-line",
        `${t("status")}: ${result.status || "Completed"}`
    ));
    summary.appendChild(createElement(
        "p", "analysis-summary-line",
        `${t("retrieved")}: ${Number.isFinite(retrievedCount) ? retrievedCount : articles.length} / ${targetCount}`
    ));
    summary.appendChild(createElement(
        "p", "analysis-summary-line",
        `${t("articles")}: ${Number.isFinite(analyzedCount) ? analyzedCount : 0}`
    ));
    summary.appendChild(createElement(
        "p", "analysis-summary-line",
        `${t("paperErrors")}: ${Number.isFinite(failedCount) ? failedCount : 0}`
    ));
    summary.appendChild(createElement(
        "p", "analysis-summary-line",
        targetMet ? t("targetMet") : t("targetNotMet")
    ));
    if (searchSummary.search_status || result.search_status) {
        summary.appendChild(createElement(
            "p", "analysis-summary-line",
            `${t("searchStatus")}: ${searchSummary.search_status || result.search_status}`
        ));
    }
    elements.resultContainer.appendChild(summary);

    // Always show each retrieved paper independently of sentence classification.
    const papersSection = createElement("section", "evidence-section retrieved-papers-section");
    const papersHeader = createElement("div", "evidence-section-header");
    papersHeader.append(
        createElement("h3", "evidence-section-title", t("papers")),
        createElement("span", "evidence-section-count", retrievedPapers.length)
    );
    papersSection.appendChild(papersHeader);

    if (retrievedPapers.length === 0) {
        papersSection.appendChild(createElement("p", "empty-evidence", t("noArticles")));
    } else {
        retrievedPapers.forEach((article, index) => {
            if (!article || typeof article !== "object") return;
            const card = createElement("article", "result-card research-paper-card");
            const title = article.title || article.article_title || `Paper ${index + 1}`;
            card.appendChild(createElement("h4", "research-paper-title", title));
            const meta = [];
            if (article.journal) meta.push(article.journal);
            if (article.year) meta.push(String(article.year));
            if (article.pmid) meta.push(`PMID: ${article.pmid}`);
            if (meta.length) card.appendChild(createElement("p", "evidence-metadata", meta.join(" · ")));
            const pmid = String(article.pmid || "").trim();
            const state = article.analysis_status || article.status ||
                (pmid && failedPmids.has(pmid) ? t("paperAnalysisFailed") :
                    (pmid && analyzedPmids.has(pmid) ? t("paperAnalysisCompleted") : "Retrieved"));
            card.appendChild(createElement("p", "evidence-details", `${t("paperAnalysis")}: ${state}`));
            const url = createSafePaperUrl(article);
            if (url) {
                const link = createElement("a", "evidence-source-link", `↗ ${t("viewPaper")}`);
                link.href = url;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                card.appendChild(link);
            }
            papersSection.appendChild(card);
        });
    }
    elements.resultContainer.appendChild(papersSection);

    const groups = collectEvidenceSentences(articles);
    const counts = getEvidenceCounts(groups);
    elements.resultContainer.appendChild(createEvidenceCounts(counts));

    const totalClassifiedSentences = evidenceLabels.reduce(
        (sum, label) => sum + groups[label].length, 0
    );

    if (totalClassifiedSentences === 0) {
        elements.resultContainer.appendChild(createInfoCard(
            t("references"),
            retrievedPapers.length ? t("noClassified") : t("noArticles")
        ));
    }

    evidenceLabels.forEach(label => {
        elements.resultContainer.appendChild(
            renderEvidenceSection(label, groups[label])
        );
    });

    // Surface per-paper failures returned by the backend.
    const errors = Array.isArray(result.article_errors) ? result.article_errors : [];
    if (errors.length) {
        const errorSection = createElement("section", "evidence-section article-errors-section");
        errorSection.appendChild(createElement("h3", "evidence-section-title", t("paperErrors")));
        errors.forEach(error => {
            const description = [
                error.title || error.pmid || `Paper ${error.index ?? ""}`,
                error.error_type || "Error",
                error.error || error.message || ""
            ].filter(Boolean).join(" · ");
            errorSection.appendChild(createElement("p", "evidence-details", description));
        });
        elements.resultContainer.appendChild(errorSection);
    }
}

/* =========================================
   21. Analysis Request
========================================= */

async function analyzeSelectedClaim(claim = selectedClaim) {

    if (!claim || isAnalyzing) {
        return;
    }

    selectedClaim = claim;

    isAnalyzing = true;

    const buttons =
        elements.claimsContainer.querySelectorAll("button");

    buttons.forEach(button => {
        button.disabled = true;
    });

    elements.resultSection.hidden = false;

    elements.resultContainer.replaceChildren();

    elements.resultContainer.appendChild(
        createInfoCard(
            t("analyzing"),
            selectedClaim
        )
    );

    setStatus(t("analyzing"));

    try {

        const response = await fetch(
            `${API_URL}/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    claim: selectedClaim
                })
            }
        );


        let data;

        try {
            data = await response.json();
        } catch (error) {
            throw new Error("Invalid JSON response from server.");
        }


        if (!response.ok) {
            throw new Error(
                data.detail || "API request failed"
            );
        }


        if (
            !data.success ||
            !data.result ||
            typeof data.result !== "object"
        ) {
            throw new Error("Invalid API response");
        }


        await chrome.storage.local.set({

            latestAnalysis: data.result,

            latestAnalyzedClaim: selectedClaim
        });


        console.log(
            "FACTGUARD API RESPONSE:",
            data
        );

        console.log(
            "FACTGUARD ANALYZED CLAIM:",
            selectedClaim
        );


        displayAnalysisResult(data.result);

        setStatus(t("ready"));

    } catch (error) {

        console.error("Analysis error:", error);

        elements.resultContainer.replaceChildren();

        elements.resultContainer.appendChild(
            createInfoCard(
                t("analysisFailed"),
                error.name === "TypeError"
                    ? t("serverError")
                    : error.message || t("analysisFailed")
            )
        );

        setStatus(t("analysisFailed"));

    } finally {

        isAnalyzing = false;

        buttons.forEach(button => {
            button.disabled = false;
        });
    }
}


/* =========================================
   22. Initialize Side Panel
========================================= */

async function initializeSidePanel() {

    await loadLanguage();

    await loadCurrentPage();

    try {

        const stored = await chrome.storage.local.get([

            "latestSelectedText",

            "latestPageData",

            "latestExtractedClaims",

            "latestSelectionMode",

            "factguardActiveTabId"
        ]);


        if (Number.isInteger(stored.factguardActiveTabId)) {
            activeTabId = stored.factguardActiveTabId;
        }


        if (stored.latestPageData?.text) {
            extractedPageText = stored.latestPageData.text;
        }


        if (
            stored.latestSelectionMode === "selected_text" &&
            stored.latestSelectedText?.text
        ) {

            addSelectedClaim(
                stored.latestSelectedText.text
            );

        } else if (
            Array.isArray(stored.latestExtractedClaims) &&
            stored.latestExtractedClaims.length > 0
        ) {

            analysisMode = "page";

            extractedClaims = stored.latestExtractedClaims;

            selectedClaim = "";

            renderClaimList();

        } else {

            renderClaimList();
        }

    } catch (error) {

        console.error(
            "Storage initialization error:",
            error
        );
    }

    await loadCurrentPage();
}


/* =========================================
   23. Start Application
========================================= */

initializeSidePanel();