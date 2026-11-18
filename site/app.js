/**
 * Resmi Gazete CLI & FastMCP Documentation Site Logic
 * Compliant with antislop, hallmark, and modern-web-guidance
 */

document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();
  initTabs();
  initCopyButtons();
  initCommandPlayground();
  initMobileNav();
});

/**
 * 1. Theme Toggle (Modern Web Guidance compliant)
 * Divergence checked at storage time, synced with <meta name="color-scheme">
 */
function initThemeToggle() {
  const themeBtn = document.getElementById("theme-toggle");
  const metaColorScheme = document.querySelector('meta[name="color-scheme"]');
  if (!themeBtn || !metaColorScheme) return;

  function getSystemPreference() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function getRenderedScheme() {
    const metaContent = metaColorScheme.content;
    if (metaContent === "light" || metaContent === "dark") {
      return metaContent;
    }
    return getSystemPreference();
  }

  function applyTheme(targetScheme) {
    const systemPref = getSystemPreference();
    if (targetScheme === systemPref) {
      // Reverting to system preference
      try {
        localStorage.removeItem("color-scheme");
      } catch (e) {}
      metaColorScheme.content = "light dark";
    } else {
      // Pinning explicit override
      try {
        localStorage.setItem("color-scheme", targetScheme);
      } catch (e) {}
      metaColorScheme.content = targetScheme;
    }
  }

  themeBtn.addEventListener("click", () => {
    const current = getRenderedScheme();
    const target = current === "dark" ? "light" : "dark";
    applyTheme(target);
  });

  // Cross-tab synchronization
  window.addEventListener("storage", (e) => {
    if (e.key === "color-scheme") {
      metaColorScheme.content = e.newValue ?? "light dark";
    }
  });
}

/**
 * 2. Accessible Tablists (Modern Web Guidance compliant)
 * Roving focus, keyboard navigation (Arrow keys, Home, End), aria-selected sync
 */
function initTabs() {
  const tablists = document.querySelectorAll('[role="tablist"], [focusgroup*="tablist"]');

  tablists.forEach((tablist) => {
    const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => selectTab(tab, tabs));

      tab.addEventListener("keydown", (e) => {
        const index = tabs.indexOf(tab);
        let targetTab = null;

        if (e.key === "ArrowRight") {
          targetTab = tabs[(index + 1) % tabs.length];
        } else if (e.key === "ArrowLeft") {
          targetTab = tabs[(index - 1 + tabs.length) % tabs.length];
        } else if (e.key === "Home") {
          targetTab = tabs[0];
        } else if (e.key === "End") {
          targetTab = tabs[tabs.length - 1];
        }

        if (targetTab) {
          e.preventDefault();
          targetTab.focus();
          selectTab(targetTab, tabs);
        }
      });
    });
  });

  function selectTab(selectedTab, allTabs) {
    allTabs.forEach((tab) => {
      const isSelected = tab === selectedTab;
      tab.setAttribute("aria-selected", isSelected ? "true" : "false");
      tab.toggleAttribute("focusgroupstart", isSelected);

      const panelId = tab.getAttribute("aria-controls") || tab.dataset.panel;
      if (panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
          if (isSelected) {
            panel.removeAttribute("hidden");
            panel.setAttribute("tabindex", "0");
          } else {
            panel.setAttribute("hidden", "until-found");
            panel.removeAttribute("tabindex");
          }
        }
      }
    });
  }
}

/**
 * 3. Copy-to-Clipboard with visual confirmation feedback
 */
function initCopyButtons() {
  const copyButtons = document.querySelectorAll(".copy-btn");

  copyButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      let textToCopy = "";
      const targetId = btn.dataset.copyTarget;
      const targetText = btn.dataset.copyText;

      if (targetId) {
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          textToCopy = targetEl.textContent.trim();
        }
      } else if (targetText) {
        textToCopy = targetText;
      }

      if (!textToCopy) return;

      try {
        await navigator.clipboard.writeText(textToCopy);
        const originalText = btn.innerHTML;
        btn.classList.add("copied");
        btn.textContent = "Kopyalandı!";

        setTimeout(() => {
          btn.classList.remove("copied");
          btn.innerHTML = originalText;
        }, 2000);
      } catch (err) {
        console.error("Kopyalama başarısız:", err);
      }
    });
  });
}

/**
 * 4. Interactive CLI Command Generator (Playground)
 * Dynamically computes actual syntax-valid CLI invocation in real-time
 */
function initCommandPlayground() {
  const cmdTypeSelect = document.getElementById("pg-command-type");
  const dailyOptions = document.getElementById("pg-daily-options");
  const searchOptions = document.getElementById("pg-search-options");
  const previewBox = document.getElementById("pg-command-preview");
  const copyBtn = document.getElementById("pg-copy-btn");

  if (!cmdTypeSelect || !previewBox) return;

  function updateCommand() {
    const cmdType = cmdTypeSelect.value;
    let parts = ["resmi-gazete-cli", cmdType];

    if (cmdType === "daily") {
      dailyOptions.removeAttribute("hidden");
      searchOptions.setAttribute("hidden", "true");

      const dateVal = document.getElementById("pg-daily-date").value.trim();
      const mukerrerVal = document.getElementById("pg-daily-mukerrer").checked;
      const catVal = document.getElementById("pg-daily-category").value.trim();
      const jsonVal = document.getElementById("pg-daily-json").checked;

      if (dateVal) {
        parts.push(`-d "${dateVal}"`);
      }
      if (mukerrerVal) {
        parts.push("-m");
      }
      if (catVal) {
        parts.push(`-c "${catVal}"`);
      }
      if (jsonVal) {
        parts.push("--json-output");
      }
    } else {
      dailyOptions.setAttribute("hidden", "true");
      searchOptions.removeAttribute("hidden");

      const kelimeVal = document.getElementById("pg-search-kelime").value.trim();
      const baslangicVal = document.getElementById("pg-search-baslangic").value.trim();
      const bitisVal = document.getElementById("pg-search-bitis").value.trim();
      const turVal = document.getElementById("pg-search-tur").value;
      const formatVal = document.getElementById("pg-search-format").value;

      if (kelimeVal) {
        parts.push(`-k "${kelimeVal}"`);
      }
      if (baslangicVal) {
        parts.push(`-b "${baslangicVal}"`);
      }
      if (bitisVal) {
        parts.push(`-e "${bitisVal}"`);
      }
      if (turVal) {
        parts.push(`-t ${turVal}`);
      }
      if (formatVal && formatVal !== "table") {
        parts.push(`-f ${formatVal}`);
      }
    }

    const fullCmd = parts.join(" ");
    previewBox.textContent = fullCmd;
    if (copyBtn) {
      copyBtn.dataset.copyText = fullCmd;
    }
  }

  cmdTypeSelect.addEventListener("change", updateCommand);

  const inputs = document.querySelectorAll(".pg-input");
  inputs.forEach((input) => {
    input.addEventListener("input", updateCommand);
    input.addEventListener("change", updateCommand);
  });

  updateCommand();
}

/**
 * 5. Mobile Navigation Menu Toggle
 */
function initMobileNav() {
  const toggleBtn = document.querySelector(".mobile-nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (!toggleBtn || !navLinks) return;

  toggleBtn.addEventListener("click", () => {
    const isExpanded = toggleBtn.getAttribute("aria-expanded") === "true";
    toggleBtn.setAttribute("aria-expanded", String(!isExpanded));
    navLinks.classList.toggle("is-open", !isExpanded);
  });

  // Close when clicking nav link
  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      toggleBtn.setAttribute("aria-expanded", "false");
      navLinks.classList.remove("is-open");
    });
  });
}
