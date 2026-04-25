// --- 1. DARK/LIGHT MODE TOGGLE ---
const themeToggleBtn = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

// Set initial theme
document.documentElement.setAttribute('data-theme', currentTheme);

// Added safety null-check to prevent cross-page crashes
if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
        let theme = document.documentElement.getAttribute('data-theme');
        let targetTheme = theme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', targetTheme);
        localStorage.setItem('theme', targetTheme);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    if (themeToggle) {
        // Theme Toggle Logic
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                document.body.setAttribute('data-theme', 'dark');
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
    }
});

// --- 2. LANGUAGE SWITCHER ---
const translations = {
    en: {
        // Login Page
        greeting: "Welcome to UVT Branding App",
        description: "Login to your account",
        toggle_theme: "Toggle Dark Mode",
        toggle_lang: "Switch to Romanian",
        login_title: "Sign In",
        
        // Sidebar Navigation
        app_title: "Branding App",
        nav_dashboard: "Dashboard",
        nav_inventory: "Inventory",
        nav_loans: "Loans",
        nav_returns: "Returns",
        nav_reports: "Reports",
        nav_notifications: "Notifications",
        nav_users: "Users",

        // Dashboard KPIs
        dashboard_title: "Dashboard Overview",
        kpi_total: "Total materials",
        kpi_total_desc: "in inventory",
        kpi_available: "Available",
        kpi_available_desc: "ready for loan",
        kpi_borrowed: "Borrowed",
        kpi_borrowed_desc: "active right now",
        kpi_overdue: "Overdue",
        kpi_overdue_desc: "past deadline",
        kpi_pending: "Pending returns",
        kpi_pending_desc: "awaiting confirmation",
        kpi_low: "Low stock",
        kpi_low_desc: "quantity under 20"
    },
    ro: {
        // Login Page
        greeting: "Bine ai venit pe UVT Branding App",
        description: "Loghează-te în contul tău",
        toggle_theme: "Schimbă modul întunecat",
        toggle_lang: "Schimbă în Engleză",
        login_title: "Autentificare",

        // Sidebar Navigation
        app_title: "Branding App",
        nav_dashboard: "Dashboard",
        nav_inventory: "Inventar",
        nav_loans: "Împrumuturi",
        nav_returns: "Predare",
        nav_reports: "Rapoarte",
        nav_notifications: "Notificări",
        nav_users: "Utilizatori",

        // Dashboard KPIs
        dashboard_title: "Prezentare Generală",
        kpi_total: "Total materiale",
        kpi_total_desc: "în inventar",
        kpi_available: "Disponibile",
        kpi_available_desc: "gata de împrumut",
        kpi_borrowed: "Împrumutate",
        kpi_borrowed_desc: "active acum",
        kpi_overdue: "Overdue",
        kpi_overdue_desc: "depășit deadline",
        kpi_pending: "Predări pending",
        kpi_pending_desc: "așteaptă confirmare",
        kpi_low: "Stoc mic",
        kpi_low_desc: "cantitate sub 20"
    } 
};

let currentLang = localStorage.getItem('lang') || 'en';

// Completely removed the `setTimeout` and opacity manipulation
function updateContent(lang) {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        
        if (translations[lang] && translations[lang][key]) {
            // Update text instantly without animations
            element.textContent = translations[lang][key];
            
            // Clear any stuck inline opacity styles
            element.style.opacity = ''; 
            element.style.transition = '';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const langToggle = document.getElementById('lang-toggle');

    // --- Language Toggle (Flag Swap) ---
    if (langToggle) {
        langToggle.textContent = currentLang === 'en' ? '🇺🇸' : '🇷🇴';

        langToggle.addEventListener('click', () => {
            if (langToggle.textContent === '🇺🇸') {
                langToggle.textContent = '🇷🇴';
                currentLang = 'ro';
            } else {
                langToggle.textContent = '🇺🇸';
                currentLang = 'en';
            }
            localStorage.setItem('lang', currentLang);
            updateContent(currentLang);
        });
    }
});

// Initialize text instantly on page load
updateContent(currentLang);