const savedTheme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", savedTheme);

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    if (!themeToggle) return;

    const applyTheme = (theme) => {
        document.documentElement.setAttribute("data-theme", theme);
        themeToggle.checked = theme === "dark";
        localStorage.setItem("theme", theme);
    };

    applyTheme(savedTheme);
    themeToggle.addEventListener("change", () => {
        applyTheme(themeToggle.checked ? "dark" : "light");
    });
});
