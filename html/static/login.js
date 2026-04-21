document.addEventListener('DOMContentLoaded', () => {
    const homeView = document.getElementById('home-view');
    const loginView = document.getElementById('login-view');
    const loginTrigger = document.getElementById('login-trigger-btn');
    const backBtn = document.getElementById('back-btn');

    // Helper function to switch views smoothly
    const switchView = (hide, show) => {
        hide.style.display = 'none';
        hide.classList.remove('fade-in'); // Reset animation
        
        show.style.display = 'block';
        show.classList.add('fade-in');    // Trigger animation
    };

    // Switch to Login
    if (loginTrigger) {
        loginTrigger.addEventListener('click', () => {
            switchView(homeView, loginView);
        });
    }

    // Switch back to Home
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            switchView(loginView, homeView);
        });
    }

    // --- Keep your existing login/UVT logic below ---
    const loginSubmit = document.querySelector('.login-submit');
    const uvtBtn = document.querySelector('.uvt-btn');

    loginSubmit.addEventListener('click', () => {
        const user = document.getElementById('username').value;
        if (user) alert(`Attempting login for: ${user}`);
    });

    uvtBtn.addEventListener('click', () => {
        window.location.href = "https://e-uvt.ro/login"; 
    });
});