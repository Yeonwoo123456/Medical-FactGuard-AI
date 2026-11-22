
/* =============================================
   Medical FactGuard AI
   Content Extraction Engine
   Chrome Extension - Manifest V3
============================================= */

(() => {
    "use strict";

    // Avoid unnecessary duplicate extraction
    const MAX_TEXT_LENGTH = 50000;
    const MIN_TEXT_LENGTH = 30;

    // Elements that usually contain irrelevant content
    const EXCLUDED_SELECTORS = [
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "button",
        "input",
        "textarea",
        "[aria-hidden='true']",
        "[hidden]",
        "[role='navigation']",
        "[role='banner']",
        "[role='complementary']"
    ];

    // Main content selectors used by common websites
    const CONTENT_SELECTORS = [
        "main",
        "article",
        "[role='main']",
        "[data-testid='post-container']",
        "[data-testid='tweetText']",
        ".post-content",
        ".article-content",
        ".entry-content",
        ".markdown-body",
        ".blog-post"
    ];

    // =========================================
    // Text Normalization
    // =========================================

    function normalizeText(text) {
        return text
            .replace(/\u00a0/g, " ")
            .replace(/[ \t]+/g, " ")
            .replace(/\n{3,}/g, "\n\n")
            .trim();
    }

    // =========================================
    // Visibility Check
    // =========================================

    function isVisible(element) {
        if (!element || !element.isConnected) {
            return false;
        }

        const style = window.getComputedStyle(element);

        if (
            style.display === "none" ||
            style.visibility === "hidden"
        ) {
            return false;
        }

        return element.getClientRects().length > 0;
    }

    // =========================================
    // Remove Unnecessary Elements
    // =========================================

    function getCleanClone(element) {
        const clone = element.cloneNode(true);

        EXCLUDED_SELECTORS.forEach(selector => {
            clone.querySelectorAll(selector).forEach(node => {
                node.remove();
            });
        });

        return clone;
    }

    // =========================================
    // Extract Candidate Content
    // =========================================

    function extractFromMainContent() {
        const candidates = [];

        CONTENT_SELECTORS.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                if (!isVisible(element)) {
                    return;
                }

                const clone = getCleanClone(element);
                const text = normalizeText(clone.innerText || "");

                if (text.length >= MIN_TEXT_LENGTH) {
                    candidates.push({
                        text,
                        length: text.length,
                        source: selector
                    });
                }
            });
        });

        // Prefer the longest candidate to avoid collecting
        // several nested copies of the same article.
        candidates.sort((a, b) => b.length - a.length);

        if (candidates.length > 0) {
            return candidates[0];
        }

        return null;
    }

    // =========================================
    // Fallback Extraction
    // =========================================

    function extractFromBody() {
        if (!document.body) {
            return "";
        }

        const clone = getCleanClone(document.body);

        return normalizeText(clone.innerText || "");
    }

    // =========================================
    // Collect Page Metadata
    // =========================================

    function getPageMetadata() {
        return {
            title: document.title || "Untitled Page",
            url: window.location.href,
            domain: window.location.hostname,
            language: document.documentElement.lang || "unknown",
            extractedAt: new Date().toISOString()
        };
    }

    // =========================================
    // Main Extraction Function
    // =========================================

    function extractPageContent() {
        const metadata = getPageMetadata();

        const mainContent = extractFromMainContent();

        let extractedText = "";
        let extractionMethod = "";

        if (mainContent) {
            extractedText = mainContent.text;
            extractionMethod = mainContent.source;
        } else {
            extractedText = extractFromBody();
            extractionMethod = "body-fallback";
        }

        extractedText = extractedText.slice(0, MAX_TEXT_LENGTH);

        return {
            ...metadata,

            text: extractedText,

            characterCount: extractedText.length,

            extractionMethod,

            success: extractedText.length >= MIN_TEXT_LENGTH
        };
    }

    // =========================================
    // Expose Result to Extension Isolated World
    // =========================================

    globalThis.__FACTGUARD_PAGE_DATA__ = extractPageContent();

})();
