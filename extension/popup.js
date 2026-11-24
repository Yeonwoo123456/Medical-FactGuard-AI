const API_URL = "http://127.0.0.1:8000";

const translations = {
    en: {
        ready: "READY TO ANALYZE",
        title: "Verify Medical Information.",
        subtitle: "Discover scientific evidence behind health claims across the web.",
        currentPage: "Current Page",
        analysis: "Claim Analysis",
        analysisDescription: "Extract medical content and enter a claim to analyze.",
        analyze: "Extract Page Content",
        features: "Analysis Features",
        research: "Research Evidence",
        statistics: "Statistical Analysis",
        safety: "Safety Analysis",
        reliability: "Evidence Evaluation",
        disclaimer: "For informational purposes only. Not medical advice.",
        loading: "Loading page information...",
        noPage: "No accessible page found.",
        extracting: "Extracting webpage content...",
        success: "Content extracted successfully.",
        empty: "No readable content found.",
        restricted: "Chrome does not allow access to this page.",
        error: "Extraction failed. Please try again.",
        characters: "Characters collected",
        claimLabel: "Medical claim to analyze",
        claimPlaceholder: "Enter a medical claim...",
        submit: "Analyze Claim",
        sending: "Sending claim to AI engine...",
        analyzing: "AI analysis is running. Please wait...",
        analysisSuccess: "Analysis completed successfully.",
        analysisError: "Analysis failed. Check the server.",
        enterClaim: "Please enter a medical claim.",
        serverError: "Cannot connect to the Python server.",
        resultTitle: "Analysis Result",
        resultCategory: "Category",
        resultArticles: "Analyzed Articles",
        resultStatus: "Status",
        resultSupporting: "Supporting",
        resultContradicting: "Contradicting",
        resultNeutral: "Neutral",
        resultInsufficient: "Insufficient"
    },

    ko: {
        ready: "분석 준비 완료",
        title: "의학 정보를 검증하세요.",
        subtitle: "웹상의 건강 관련 주장에 대한 과학적 근거를 찾아보세요.",
        currentPage: "현재 페이지",
        analysis: "주장 분석",
        analysisDescription: "웹페이지 내용을 추출하고 분석할 주장을 입력하세요.",
        analyze: "페이지 콘텐츠 추출",
        features: "분석 기능",
        research: "연구 근거",
        statistics: "통계 분석",
        safety: "안전성 분석",
        reliability: "근거 평가",
        disclaimer: "정보 제공 목적이며 의학적 조언을 대체하지 않습니다.",
        loading: "페이지 정보 불러오는 중...",
        noPage: "접근 가능한 페이지가 없습니다.",
        extracting: "웹페이지 콘텐츠 추출 중...",
        success: "콘텐츠 추출에 성공했습니다.",
        empty: "읽을 수 있는 콘텐츠가 없습니다.",
        restricted: "Chrome에서 이 페이지에 접근할 수 없습니다.",
        error: "콘텐츠 추출에 실패했습니다.",
        characters: "수집한 글자 수",
        claimLabel: "분석할 의학적 주장",
        claimPlaceholder: "분석할 의학적 주장을 입력하세요...",
        submit: "주장 분석하기",
        sending: "AI 엔진으로 주장을 전송하는 중...",
        analyzing: "AI 분석이 진행 중입니다. 잠시 기다려 주세요...",
        analysisSuccess: "분석이 성공적으로 완료되었습니다.",
        analysisError: "분석에 실패했습니다. 서버를 확인하세요.",
        enterClaim: "분석할 의학적 주장을 입력해 주세요.",
        serverError: "Python 서버에 연결할 수 없습니다.",
        resultTitle: "분석 결과",
        resultCategory: "분류",
        resultArticles: "분석 논문 수",
        resultStatus: "상태",
        resultSupporting: "지지",
        resultContradicting: "반박",
        resultNeutral: "중립",
        resultInsufficient: "근거 불충분"
    }
};

const languageSelect = document.getElementById("languageSelect");
const pageTitle = document.getElementById("pageTitle");
const pageDomain = document.getElementById("pageDomain");
const analyzeButton = document.getElementById("analyzeButton");
const statusMessage = document.getElementById("statusMessage");

let currentLanguage = "en";
let latestPageData = null;

function applyLanguage(language) {
    currentLanguage = language;

    document.body.classList.toggle("korean", language === "ko");
    document.documentElement.lang = language;
    languageSelect.value = language;

    document.querySelectorAll("[data-i18n]").forEach(element => {
        const key = element.dataset.i18n;

        if (translations[language][key]) {
            element.textContent = translations[language][key];
        }
    });

    const claimInput = document.getElementById("claimInput");
    const claimLabel = document.getElementById("claimLabel");
    const submitButton = document.getElementById("submitClaimButton");

    if (claimInput) {
        claimInput.placeholder = translations[language].claimPlaceholder;
    }

    if (claimLabel) {
        claimLabel.textContent = translations[language].claimLabel;
    }

    if (submitButton) {
        submitButton.textContent = translations[language].submit;
    }
}

async function loadLanguage() {
    try {
        const result = await chrome.storage.local.get("language");
        applyLanguage(result.language || "en");
    } catch (error) {
        console.error("Language loading error:", error);
        applyLanguage("en");
    }
}

languageSelect.addEventListener("change", async () => {
    applyLanguage(languageSelect.value);

    await chrome.storage.local.set({
        language: languageSelect.value
    });
});

function showStatus(message) {
    statusMessage.textContent = message;
}

async function getActiveTab() {
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    const tab = tabs[0];

    if (!tab || !tab.id || !tab.url) {
        throw new Error("No active tab");
    }

    const url = new URL(tab.url);

    if (!["http:", "https:"].includes(url.protocol)) {
        throw new Error("Restricted page");
    }

    return tab;
}

async function loadCurrentPage() {
    try {
        const tab = await getActiveTab();
        const url = new URL(tab.url);

        pageTitle.textContent = tab.title || url.hostname;
        pageDomain.textContent = url.hostname;

    } catch (error) {
        pageTitle.textContent = translations[currentLanguage].noPage;
        pageDomain.textContent = "---";
    }
}

async function extractPageContent(tabId) {
    await chrome.scripting.executeScript({
        target: { tabId },
        files: ["content.js"]
    });

    const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => globalThis.__FACTGUARD_PAGE_DATA__ || null
    });

    if (!results?.[0]?.result) {
        throw new Error("Extraction result unavailable");
    }

    return results[0].result;
}

function createClaimInterface() {
    if (document.getElementById("claimAnalysisPanel")) {
        return;
    }

    const panel = document.createElement("section");
    panel.id = "claimAnalysisPanel";
    panel.className = "analysis-section";

    panel.innerHTML = `
        <div class="section-heading">
            <span class="section-icon">✦</span>
            <h3 id="claimPanelTitle">Claim Analysis</h3>
        </div>

        <label id="claimLabel" for="claimInput"></label>

        <textarea
            id="claimInput"
            rows="4"
            style="width:100%; box-sizing:border-box; margin-top:8px; padding:10px; border:1px solid #d5dce5; border-radius:8px; resize:vertical;"
        ></textarea>

        <button
            id="submitClaimButton"
            class="primary-button"
            style="width:100%; margin-top:12px;"
        ></button>

        <div id="analysisResult" style="margin-top:16px;"></div>
    `;

    const main = document.querySelector("main");

    if (main) {
        main.appendChild(panel);
    } else {
        document.body.appendChild(panel);
    }

    applyLanguage(currentLanguage);

    document
        .getElementById("submitClaimButton")
        .addEventListener("click", submitClaim);
}

analyzeButton.addEventListener("click", async () => {
    analyzeButton.disabled = true;
    showStatus(translations[currentLanguage].extracting);

    try {
        const tab = await getActiveTab();
        const pageData = await extractPageContent(tab.id);

        if (!pageData.success || !pageData.text) {
            showStatus(translations[currentLanguage].empty);
            return;
        }

        latestPageData = pageData;

        await chrome.storage.local.set({
            latestPageData: pageData
        });

        showStatus(
            `${translations[currentLanguage].success} ` +
            `(${translations[currentLanguage].characters}: ` +
            `${pageData.characterCount.toLocaleString()})`
        );

        createClaimInterface();

    } catch (error) {
        console.error("Extraction error:", error);

        showStatus(
            error.message === "Restricted page"
                ? translations[currentLanguage].restricted
                : translations[currentLanguage].error
        );

    } finally {
        analyzeButton.disabled = false;
    }
});

async function submitClaim() {
    const claimInput = document.getElementById("claimInput");
    const resultContainer = document.getElementById("analysisResult");
    const submitButton = document.getElementById("submitClaimButton");

    const claim = claimInput.value.trim();

    if (!claim) {
        showStatus(translations[currentLanguage].enterClaim);
        return;
    }

    submitButton.disabled = true;
    resultContainer.textContent = translations[currentLanguage].analyzing;
    showStatus(translations[currentLanguage].sending);

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ claim })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed");
        }

        if (!data.success || !data.result) {
            throw new Error("Invalid API response");
        }

        await chrome.storage.local.set({
            latestAnalysis: data.result
        });

        displayAnalysisResult(data.result);

        showStatus(translations[currentLanguage].analysisSuccess);

    } catch (error) {
        console.error("Analysis request error:", error);

        resultContainer.textContent =
            error.name === "TypeError"
                ? translations[currentLanguage].serverError
                : translations[currentLanguage].analysisError;

    } finally {
        submitButton.disabled = false;
    }
}

function displayAnalysisResult(result) {
    const container = document.getElementById("analysisResult");
    const t = translations[currentLanguage];

    const articles = result.articles || [];

    const counts = {
        Supporting: 0,
        Contradicting: 0,
        Neutral: 0,
        Insufficient: 0
    };

    articles.forEach(article => {
        const articleCounts = article.overall_counts || {};

        Object.keys(counts).forEach(key => {
            counts[key] += Number(articleCounts[key] || 0);
        });
    });

    container.innerHTML = `
        <div style="padding:14px; background:#f3f7fa; border-radius:10px;">
            <h3>${t.resultTitle}</h3>

            <p><strong>${t.resultStatus}:</strong>
                ${result.status || "Completed"}
            </p>

            <p><strong>${t.resultCategory}:</strong>
                ${result.category || "Unclassified"}
            </p>

            <p><strong>${t.resultArticles}:</strong>
                ${result.analyzed_articles ?? articles.length}
            </p>

            <hr>

            <p>${t.resultSupporting}: ${counts.Supporting}</p>
            <p>${t.resultContradicting}: ${counts.Contradicting}</p>
            <p>${t.resultNeutral}: ${counts.Neutral}</p>
            <p>${t.resultInsufficient}: ${counts.Insufficient}</p>
        </div>
    `;
}

async function initializePopup() {
    await loadLanguage();
    await loadCurrentPage();
}

initializePopup();