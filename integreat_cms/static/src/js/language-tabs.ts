const renderLanguageTabs = () => {
    const tabWrapper = document.getElementById("tab-wrapper");
    if (tabWrapper) {
        const paddingInWrapper: number =
            +window.getComputedStyle(tabWrapper).paddingLeft.replace("px", "") +
            +window.getComputedStyle(tabWrapper).paddingRight.replace("px", "");
        const languageSwitcher = document.getElementById("language-switcher").parentElement;
        const languageSwitcherList = document.getElementById("language-switcher-list");
        const availableWidth = tabWrapper.offsetWidth - paddingInWrapper - languageSwitcher.offsetWidth;
        const tabs = Array.from(tabWrapper.children).concat(Array.from(languageSwitcherList.children));

        let usedSpace = 0;
        let tabCount = 0;
        tabs.forEach((tab) => {
            const marginOfTab: number = +window.getComputedStyle(tab).marginRight.replace("px", "");
            if (
                usedSpace + tab.clientWidth + marginOfTab > availableWidth &&
                tab !== languageSwitcher &&
                tabCount > 0
            ) {
                languageSwitcherList.append(tab);
            } else {
                usedSpace += tab.clientWidth + marginOfTab;
                if (!Array.from(tabWrapper.children).includes(tab)) {
                    tabWrapper.insertBefore(tab, languageSwitcher);
                }
                tabCount += 1;
            }
        });
        if (tabCount <= 2) {
            document.getElementById("language-switcher-globe").classList.remove("hidden");
            document.getElementById("language-switcher-text").classList.add("hidden");
        } else {
            document.getElementById("language-switcher-globe").classList.add("hidden");
            document.getElementById("language-switcher-text").classList.remove("hidden");
        }
        if (tabCount == tabs.length) {
            languageSwitcher.classList.add("hidden")
        } else {
            languageSwitcher.classList.remove("hidden")
        }
    }
};

window.addEventListener("load", () => {
    renderLanguageTabs();
    window.addEventListener("resize", renderLanguageTabs);
});
