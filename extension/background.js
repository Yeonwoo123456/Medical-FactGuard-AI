const MENU_ID = "factguard-analyze-selection";

async function createContextMenu() {
    await chrome.contextMenus.removeAll();

    chrome.contextMenus.create({
        id: MENU_ID,
        title: "Analyze with Medical FactGuard AI",
        contexts: ["selection"]
    });
}

// 설치 및 업데이트
chrome.runtime.onInstalled.addListener(async () => {
    try {
        await chrome.sidePanel.setPanelBehavior({
            openPanelOnActionClick: false
        });

        await createContextMenu();

        console.log("Medical FactGuard AI installed.");
    } catch (error) {
        console.error("Installation error:", error);
    }
});

// Chrome 시작 시 메뉴 복구
chrome.runtime.onStartup.addListener(async () => {
    try {
        await createContextMenu();
    } catch (error) {
        console.error("Context menu error:", error);
    }
});

// 확장 프로그램 아이콘 클릭
chrome.action.onClicked.addListener((tab) => {
    if (!tab?.id) return;

    // 사용자 클릭에 직접 연결된 시점에 Side Panel 열기
    chrome.sidePanel.open({
        tabId: tab.id
    }).catch(error => {
        console.error("Side panel opening error:", error);
    });

    // 분석 대상 탭 저장
    chrome.storage.local.set({
        factguardActiveTabId: tab.id
    }).catch(error => {
        console.error("Tab storage error:", error);
    });
});

// 우클릭으로 선택 텍스트 저장
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId !== MENU_ID) return;
    if (!tab?.id) return;

    const selectedText = String(info.selectionText || "").trim();

    if (!selectedText) return;

    chrome.storage.local.set({
        factguardActiveTabId: tab.id,

        latestSelectedText: {
            text: selectedText,
            pageTitle: tab.title || "",
            pageUrl: tab.url || "",
            timestamp: Date.now()
        }
    }).catch(error => {
        console.error("Selected text storage error:", error);
    });

    console.log("Selected text saved.");
});

console.log("Medical FactGuard AI background service started.");