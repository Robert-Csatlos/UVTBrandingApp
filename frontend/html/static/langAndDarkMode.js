const savedTheme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", savedTheme);

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");

    const applyTheme = (theme) => {
        document.documentElement.setAttribute("data-theme", theme);
        if (themeToggle) themeToggle.checked = theme === "dark";
        localStorage.setItem("theme", theme);
    };

    applyTheme(savedTheme);
    if (themeToggle) {
        themeToggle.addEventListener("change", () => {
            applyTheme(themeToggle.checked ? "dark" : "light");
        });
    }

    refreshNotificationBadge();
    setInterval(refreshNotificationBadge, 60000);
});

async function refreshNotificationBadge() {
    const badge = document.getElementById("badge-notifs");
    if (!badge) return;

    try {
        const res = await fetch("/notifications/unread-count");
        if (!res.ok) {
            badge.style.display = "none";
            return;
        }
        const data = await res.json();
        const count = Number(data.count || 0);
        badge.style.display = count > 0 ? "inline-block" : "none";
        badge.textContent = count > 0 ? String(count) : "";
    } catch (_) {
        badge.style.display = "none";
    }
}
