// --- 1. DARK/LIGHT MODE TOGGLE ---
const themeToggleBtn = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

// Set initial theme
document.documentElement.setAttribute('data-theme', currentTheme);

themeToggleBtn.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    let targetTheme = theme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', targetTheme);
    localStorage.setItem('theme', targetTheme);
});

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    // Theme Toggle Logic
    themeToggle.addEventListener('change', () => {
        if (themeToggle.checked) {
            document.body.setAttribute('data-theme', 'dark');
            // Optional: Save preference
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
    });

    // Check for saved theme on load
    if (localStorage.getItem('theme') === 'dark') {
        themeToggle.checked = true;
        document.body.setAttribute('data-theme', 'dark');
    }
});

// --- 2. LANGUAGE SWITCHER ---
const translations = {
    en: {
        greeting: "Welcome to UVT Branding App",
        description: "Login to your account",
        toggle_theme: "Toggle Dark Mode",
        toggle_lang: "Switch to Romanian"
    },
    ro: {
        greeting: "Bine ai venit pe UVT Branding App",
        description: "Loghează-te în contul tău",
        toggle_theme: "Schimbă modul întunecat",
        toggle_lang: "Schimbă în Engleză"
    } 
};

const langToggleBtn = document.getElementById('lang-toggle');
let currentLang = localStorage.getItem('lang') || 'en';

function updateContent(lang) {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        // Add a tiny fade-out/fade-in effect for text change
        element.style.opacity = 0;
        setTimeout(() => {
            element.textContent = translations[lang][key];
            element.style.opacity = 1;
        }, 200); // Wait for fade out to finish
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const langToggle = document.getElementById('lang-toggle');
    const themeToggle = document.getElementById('theme-toggle');

    // --- Language Toggle (Flag Swap) ---
    langToggle.addEventListener('click', () => {
        if (langToggle.textContent === '🇺🇸') {
            langToggle.textContent = '🇷🇴';
            // Trigger Romanian translations here
            console.log("Language switched to Romanian");
            // updateTranslations('ro'); 
        } else {
            langToggle.textContent = '🇺🇸';
            // Trigger English translations here
            console.log("Language switched to English");
            // updateTranslations('en');
        }
    });

    // --- Theme Toggle (Checkbox Switch) ---
    themeToggle.addEventListener('change', () => {
        if (themeToggle.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    });
});

// Set initial language
updateContent(currentLang);
document.querySelectorAll('[data-i18n]').forEach(el => el.style.transition = "opacity 0.2s ease");

langToggleBtn.addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'ro' : 'en';
    localStorage.setItem('lang', currentLang);
    updateContent(currentLang);
});