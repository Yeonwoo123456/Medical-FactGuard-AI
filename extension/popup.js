
const translations = {
    en: {
        ready: "READY TO ANALYZE",
        title: "Verify Medical Information.",
        subtitle: "Discover scientific evidence behind health claims across the web.",
        currentPage: "Current Page",
        analysis: "Claim Analysis",
        analysisDescription: "Extract medical content from the current webpage.",
        analyze: "Analyze Current Page",
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
        domain: "Website"
    },

    ko: {
        ready: "분석 준비 완료",
        title: "의학 정보를 검증하세요.",
        subtitle: "웹상의 건강 관련 주장에 대한 과학적 근거를 찾아보세요.",
        currentPage: "현재 페이지",
        analysis: "주장 분석",
        analysisDescription: "현재 웹페이지에서 의학 관련 콘텐츠를 추출합니다.",
        analyze: "현재 페이지 분석",
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
        error: "콘텐츠 추출에 실패했습니다. 다시 시도해 주세요.",
        characters: "수집한 글자 수",
        domain: "웹사이트"
    }
};

const languageSelect = document.getElementById("languageSelect");
const pageTitle = document.getElementById("pageTitle");
const pageDomain = document.getElementById("pageDomain");
const analyzeButton = document.getElementById("analyzeButton");
const statusMessage = document.getElementById("statusMessage");

let currentLanguage = "en";

function applyLanguage(language) {
    currentLanguage = language;

    document.body.classList.toggle("korean", language === "ko");
    document.documentElement.lang = language;
    languageSelect.value = language;

    document.querySelectorAll("[data-i18n]").forEach(element => {
        const key = element.dataset.i18n;
        const translated = translations[language][key];

        if (translated) {
            element.textContent = translated;
        }
    });
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
    const language = languageSelect.value;
    applyLanguage(language);

    try {
        await chrome.storage.local.set({ language });
    } catch (error) {
        console.error("Language saving error:", error);
    }
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

// Inject content.js and retrieve its extraction result.
async function extractPageContent(tabId) {
    // First, execute the content extraction script.
    await chrome.scripting.executeScript({
        target: { tabId },
        files: ["content.js"]
    });

    // Then retrieve the result from the same isolated world.
    const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => globalThis.__FACTGUARD_PAGE_DATA__ || null
    });

    if (!results || !results[0] || !results[0].result) {
        throw new Error("Extraction result unavailable");
    }

    return results[0].result;
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

        await chrome.storage.local.set({
            latestPageData: {
                title: pageData.title,
                url: pageData.url,
                domain: pageData.domain,
                language: pageData.language,
                text: pageData.text,
                characterCount: pageData.characterCount,
                extractionMethod: pageData.extractionMethod,
                extractedAt: pageData.extractedAt
            }
        });

        showStatus(
            `${translations[currentLanguage].success} ` +
            `(${translations[currentLanguage].characters}: ` +
            `${pageData.characterCount.toLocaleString()})`
        );

        console.log("FactGuard extraction result:", pageData);

    } catch (error) {
        console.error("FactGuard extraction error:", error);

        if (error.message === "Restricted page") {
            showStatus(translations[currentLanguage].restricted);
        } else {
            showStatus(translations[currentLanguage].error);
        }

    } finally {
        analyzeButton.disabled = false;
    }
});

async function initializePopup() {
    await loadLanguage();
    await loadCurrentPage();
}

initializePopup();
