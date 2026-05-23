document.addEventListener('DOMContentLoaded', () => {
 
    // =========================================================================
    // 1. THEME SWITCHER LOGIC
    // =========================================================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const rootElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'light';
    rootElement.setAttribute('data-theme', savedTheme);
    updateThemeIconStyle(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = rootElement.getAttribute('data-theme');
            const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
     
            rootElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('theme', nextTheme);
            updateThemeIconStyle(nextTheme);
        });
    }

    function updateThemeIconStyle(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'dark') {
            themeToggleBtn.className = 'fa-solid fa-moon';
            themeToggleBtn.style.color = '#f59e0b'; // Warm moon gold highlight
        } else {
            themeToggleBtn.className = 'fa-solid fa-sun';
            themeToggleBtn.style.color = 'inherit';
        }
    }

    // =========================================================================
    // 2. DOM ELEMENT SELECTORS (AUTH MODAL & ROLE MANAGEMENT)
    // =========================================================================
    const authModal = document.getElementById('auth-modal');
    const signupNavBtn = document.getElementById('signup-nav-btn');
    const loginNavBtn = document.getElementById('login-nav-btn');
    const closeModalBtn = document.getElementById('close-modal');
 
    const modalTitle = document.getElementById('modal-title');
    const authForm = document.getElementById('auth-form');
    const submitAuthBtn = document.getElementById('submit-auth-btn');
    const switchFormLink = document.getElementById('switch-form-link');
    const switchText = document.getElementById('switch-text');
    const signupOnlyFields = document.querySelectorAll('.signup-only');
    
    // Form Input Specific Fields
    const phoneInput = document.getElementById('user-phone'); 
    const emailLabel = document.querySelector('label[for="user-email"]');
    const emailInput = document.getElementById('user-email');

    // Dropdown Item Paths
    const targetCandidate = document.getElementById('target-candidate');
    const targetRecruiter = document.getElementById('target-recruiter');

    // Global State Memory Trackers
    let isSignUpMode = true;
    let currentRole = 'candidate'; // Memory safe holder for 'candidate' or 'recruiter'

    // =========================================================================
    // 3. UI CLICK EVENT ROUTING HANDLERS
    // =========================================================================

    // Top Header Navigation Bar Triggers
    if (signupNavBtn) {
        signupNavBtn.addEventListener('click', () => {
            configureModalMode(true, 'candidate');
            authModal.style.display = 'flex';
        });
    }

    if (loginNavBtn) {
        loginNavBtn.addEventListener('click', () => {
            configureModalMode(false);
            authModal.style.display = 'flex';
        });
    }

    // Hover Dropdown Options Event Listeners
    if (targetCandidate) {
        targetCandidate.addEventListener('click', () => {
            configureModalMode(true, 'candidate');
            authModal.style.display = 'flex';
        });
    }

    if (targetRecruiter) {
        targetRecruiter.addEventListener('click', () => {
            configureModalMode(true, 'recruiter');
            authModal.style.display = 'flex';
        });
    }

    // Closing Operations
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => authModal.style.display = 'none');
    }

    window.addEventListener('click', (event) => {
        if (event.target === authModal) authModal.style.display = 'none';
    });

    if (switchFormLink) {
        switchFormLink.addEventListener('click', (event) => {
            event.preventDefault();
            configureModalMode(!isSignUpMode, currentRole);
        });
    }

    // =========================================================================
    // 4. CONFIGURATION ENGINE (MODE & ROLE MATRIX MUTATOR)
    // =========================================================================
    function configureModalMode(targetIsSignUp, role = 'candidate') {
        isSignUpMode = targetIsSignUp;
        currentRole = role; // Persist active role tier
        authForm.reset();

        if (isSignUpMode) {
            modalTitle.textContent = 'Create an account';
            submitAuthBtn.textContent = 'Sign Up';
            switchText.textContent = 'Already have an account?';
            switchFormLink.textContent = 'Login';
     
            if (phoneInput) {
                phoneInput.placeholder = '+977 98XXXXXXXX';
            }
     
            signupOnlyFields.forEach(field => {
                field.style.display = 'flex';
                const input = field.querySelector('input');
                if (input) input.required = true;
            });

            // Dynamically morph email labels and fields based on selected role tier
            if (currentRole === 'recruiter') {
                if (emailLabel) emailLabel.textContent = "Company Email*";
                if (emailInput) emailInput.placeholder = "eg. bruce@wayne.enterprises";
            } else {
                if (emailLabel) emailLabel.textContent = "Email*";
                if (emailInput) emailInput.placeholder = "eg. janecopper@xyz.com";
            }

        } else {
            modalTitle.textContent = 'Log In';
            submitAuthBtn.textContent = 'Welcome Back';
            switchText.textContent = "Don't have an account?";
            switchFormLink.textContent = 'Sign Up';
            
            signupOnlyFields.forEach(field => {
                field.style.display = 'none';
                const input = field.querySelector('input');
                if (input) input.required = false;
            });

            // Restore basic login context presentation rules
            if (emailLabel) emailLabel.textContent = "Email Address";
            if (emailInput) emailInput.placeholder = "name@gmail.com";
        }
    }

    // =========================================================================
    // 5. CLIENT-SIDE FORM SUBMISSION HANDLING
    // =========================================================================
    if (authForm) {
        authForm.addEventListener('submit', (event) => {
            event.preventDefault();
     
            const emailValue = document.getElementById('user-email').value;
            const passwordValue = document.getElementById('user-password').value;

            if (isSignUpMode) {
                const nameValue = document.getElementById('user-name').value;
                const phoneValue = document.getElementById('user-phone').value;
         
                console.log(`Saving ${currentRole} profile metrics securely...`, { nameValue, phoneValue, emailValue });
                alert(`Registration Complete! Welcome to HireNest, ${nameValue}. Role: ${currentRole}`);
            } else {
                console.log("Verifying credentials against user storage tables...", { emailValue });
                alert(`Logged in successfully as: ${emailValue}`);
            }

            authModal.style.display = 'none';
            authForm.reset();
        });
    }
});
