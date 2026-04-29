document.addEventListener('DOMContentLoaded', () => {
    // --- 1. VIEW SWITCHING LOGIC ---
    const homeView = document.getElementById('home-view');
    const loginView = document.getElementById('login-view');
    const loginTrigger = document.getElementById('login-trigger-btn');
    const backBtn = document.getElementById('back-btn');

    const switchView = (hide, show) => {
        hide.style.display = 'none';
        hide.classList.remove('fade-in'); 
        show.style.display = 'block';
        show.classList.add('fade-in');  
    };

    if (loginTrigger) loginTrigger.addEventListener('click', () => switchView(homeView, loginView));
    if (backBtn) backBtn.addEventListener('click', () => switchView(loginView, homeView));

    // --- 2. ELEMENTS FOR LOGIN ---
    const loginSubmit = document.querySelector('.login-submit');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    // Toast Elements
    const toastError = document.getElementById('toast-error');
    const closeToastBtn = document.getElementById('close-toast-btn');
    let toastTimeout;

    // --- 3. TOAST NOTIFICATION FUNCTION ---
    function showErrorToast(message = "Invalid email or password!") {
        if (!toastError) {
            console.error("Toast HTML is missing from the page!");
            return;
        }
        
        // Update the text and show the toast
        toastError.querySelector('span').textContent = message;
        toastError.style.display = 'flex';
        
        // Reset timer
        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toastError.style.display = 'none';
        }, 5000); 
    }

    // Manual Toast Close
    if (closeToastBtn) {
        closeToastBtn.addEventListener('click', () => {
            toastError.style.display = 'none';
            clearTimeout(toastTimeout);
        });
    }

    // --- 4. ENTER KEY LOGIC ---
    const handleEnterKey = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); 
            loginSubmit.click(); // Triggers the click event below   
        }
    };

    if (emailInput) emailInput.addEventListener('keypress', handleEnterKey);
    if (passwordInput) passwordInput.addEventListener('keypress', handleEnterKey);

    // --- 5. MAIN LOGIN LOGIC ---
    loginSubmit.addEventListener('click', async () => {
        const email = emailInput.value.trim();
        const pass = passwordInput.value;

        // Front-end validation: Ensure fields aren't empty
        if (!email || !pass) {
            showErrorToast("Please enter both email and password!");
            return;
        }

        try {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email, password: pass })
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = "/home";
            } else {
                // Backend rejected the login (e.g., 401 Unauthorized)
                showErrorToast("Invalid email or password!");
            }
        } catch (error) {
            console.error("Server communication error:", error);
            showErrorToast("Server is offline or unreachable.");
        }
    });

    // --- 6. EXTERNAL UVT LOGIN ---
    const uvtBtn = document.querySelector('.uvt-btn');
    if (uvtBtn) {
        uvtBtn.addEventListener('click', () => {
            window.location.href = "https://e-uvt.ro/login";
        });
    }
});