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
        nav_section_modules: "MODULES",
        nav_section_reports: "REPORTS",
        nav_section_admin: "ADMIN",
        nav_dashboard: "Dashboard",
        nav_inventory: "Inventory",
        nav_loans: "Loans",
        nav_handover: "Handover",
        nav_returns: "Returns",
        nav_reports: "Reports",
        nav_notifications: "Notifications",
        nav_users: "User Management",

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
        kpi_low_desc: "quantity under 20",

        // Inventory page
        inv_title: "Inventory Management",
        inv_subtitle: "Track and manage all branding materials.",
        inv_add: "+ Add Item",
        inv_search_placeholder: "Search by name, code, or category...",
        inv_filter_all_status: "All Statuses",
        inv_col_code: "Code",
        inv_col_name: "Name",
        inv_col_category: "Category",
        inv_col_qty: "Qty",
        inv_col_status: "Status",
        inv_col_location: "Location",
        inv_col_responsible: "Responsible",
        inv_col_actions: "Actions",
        inv_empty: "No items found.",
        inv_loading: "Loading...",
        inv_status_new: "New",
        inv_status_good: "Good",
        inv_status_worn: "Worn",
        inv_modal_add_title: "Add Inventory Item",
        inv_modal_edit_title: "Edit Inventory Item",
        inv_field_name: "Name",
        inv_field_category: "Category",
        inv_field_code: "Inventory Code",
        inv_field_qty: "Quantity",
        inv_field_status: "Status",
        inv_field_location: "Location",
        inv_field_responsible: "Responsible Person",
        inv_del_confirm: "Delete this item? This cannot be undone.",
        btn_edit: "Edit",
        btn_delete: "Delete",
        btn_cancel: "Cancel",
        btn_save: "Save",
        btn_create: "Create",
        inv_toast_created: "Item created!",
        inv_toast_updated: "Item updated!",
        inv_toast_deleted: "Item deleted.",
        inv_err_required: "All fields are required.",
        inv_err_qty: "Quantity must be ≥ 0."
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
        nav_section_modules: "MODULE",
        nav_section_reports: "RAPOARTE",
        nav_section_admin: "ADMIN",
        nav_dashboard: "Dashboard",
        nav_inventory: "Inventar",
        nav_loans: "Împrumuturi",
        nav_handover: "Predare",
        nav_returns: "Returnări",
        nav_reports: "Rapoarte",
        nav_notifications: "Notificări",
        nav_users: "Gestionare Utilizatori",

        // Dashboard KPIs
        dashboard_title: "Prezentare Generală",
        kpi_total: "Total materiale",
        kpi_total_desc: "în inventar",
        kpi_available: "Disponibile",
        kpi_available_desc: "gata de împrumut",
        kpi_borrowed: "Împrumutate",
        kpi_borrowed_desc: "active acum",
        kpi_overdue: "Depășite",
        kpi_overdue_desc: "depășit deadline",
        kpi_pending: "Predări pending",
        kpi_pending_desc: "așteaptă confirmare",
        kpi_low: "Stoc mic",
        kpi_low_desc: "cantitate sub 20",

        // Inventory page
        inv_title: "Gestionar Inventar",
        inv_subtitle: "Urmărește și gestionează toate materialele de branding.",
        inv_add: "+ Adaugă Element",
        inv_search_placeholder: "Caută după nume, cod sau categorie...",
        inv_filter_all_status: "Toate Stările",
        inv_col_code: "Cod",
        inv_col_name: "Nume",
        inv_col_category: "Categorie",
        inv_col_qty: "Cant.",
        inv_col_status: "Stare",
        inv_col_location: "Locație",
        inv_col_responsible: "Responsabil",
        inv_col_actions: "Acțiuni",
        inv_empty: "Nu s-au găsit elemente.",
        inv_loading: "Se încarcă...",
        inv_status_new: "Nou",
        inv_status_good: "Bun",
        inv_status_worn: "Uzat",
        inv_modal_add_title: "Adaugă Element în Inventar",
        inv_modal_edit_title: "Editează Elementul din Inventar",
        inv_field_name: "Nume",
        inv_field_category: "Categorie",
        inv_field_code: "Cod Inventar",
        inv_field_qty: "Cantitate",
        inv_field_status: "Stare",
        inv_field_location: "Locație",
        inv_field_responsible: "Persoana Responsabilă",
        inv_del_confirm: "Ștergi acest element? Acțiunea nu poate fi anulată.",
        btn_edit: "Editează",
        btn_delete: "Șterge",
        btn_cancel: "Anulează",
        btn_save: "Salvează",
        btn_create: "Creează",
        inv_toast_created: "Element creat!",
        inv_toast_updated: "Element actualizat!",
        inv_toast_deleted: "Element șters.",
        inv_err_required: "Toate câmpurile sunt obligatorii.",
        inv_err_qty: "Cantitatea trebuie să fie ≥ 0."
    }
};

window.i18n = translations;

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