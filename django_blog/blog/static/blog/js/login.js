// Login Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Login page loaded successfully');

    // Get login form elements
    const loginForm = document.querySelector('.login-form form');
    const usernameField = document.querySelector('#id_username');
    const passwordField = document.querySelector('#id_password');
    const submitButton = document.querySelector('.login-form button[type="submit"]');
    
    // Add loading animation to login button
    if (loginForm && submitButton) {
        loginForm.addEventListener('submit', function(e) {
            // Add loading state
            submitButton.innerHTML = 'Logging in...';
            submitButton.disabled = true;
            
            // Add spinner animation
            const spinner = document.createElement('span');
            spinner.innerHTML = ' ⟳';
            spinner.style.animation = 'spin 1s linear infinite';
            submitButton.appendChild(spinner);
            
            // Add CSS for spinner animation
            if (!document.getElementById('login-spinner-style')) {
                const style = document.createElement('style');
                style.id = 'login-spinner-style';
                style.textContent = `
                    @keyframes spin {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
        });
    }

    // Add real-time validation feedback for login form
    if (usernameField) {
        usernameField.addEventListener('input', function() {
            validateField(this, this.value.length >= 3, 'Username must be at least 3 characters');
        });
        
        usernameField.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                showFieldError(this, 'Username is required');
            }
        });
    }

    if (passwordField) {
        passwordField.addEventListener('input', function() {
            validateField(this, this.value.length >= 1, 'Password is required');
        });
        
        passwordField.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                showFieldError(this, 'Password is required');
            }
        });
    }

    // Login form validation helper functions
    function validateField(field, isValid, errorMessage) {
        const errorElement = field.parentNode.querySelector('.field-error');
        
        if (isValid) {
            field.style.borderColor = '#28a745';
            field.style.boxShadow = '0 0 0 3px rgba(40, 167, 69, 0.1)';
            if (errorElement) {
                errorElement.remove();
            }
        } else {
            showFieldError(field, errorMessage);
        }
    }

    function showFieldError(field, message) {
        // Remove existing error
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        field.style.borderColor = '#dc3545';
        field.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.1)';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = `
            color: #dc3545;
            font-size: 13px;
            margin-top: 5px;
            font-weight: 600;
        `;
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    // Add smooth focus transitions to login form fields
    const loginInputs = document.querySelectorAll('.login-form input[type="text"], .login-form input[type="password"]');
    loginInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.15)';
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
            }
        });
    });

    // Add keyboard navigation for login form
    document.addEventListener('keydown', function(e) {
        // Enter key submission
        if (e.key === 'Enter' && (e.target === usernameField || e.target === passwordField)) {
            if (usernameField.value && passwordField.value) {
                loginForm.submit();
            }
        }

        // Tab navigation enhancement
        if (e.key === 'Tab') {
            const currentField = document.activeElement;
            if (currentField === usernameField && !e.shiftKey) {
                e.preventDefault();
                passwordField.focus();
            } else if (currentField === passwordField && e.shiftKey) {
                e.preventDefault();
                usernameField.focus();
            }
        }
    });

    // Add login form animation on load
    const loginContainer = document.querySelector('.login-form');
    if (loginContainer) {
        loginContainer.style.opacity = '0';
        loginContainer.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            loginContainer.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            loginContainer.style.opacity = '1';
            loginContainer.style.transform = 'translateY(0)';
        }, 100);
    }

    // Add focus to first field on page load
    setTimeout(() => {
        if (usernameField && !usernameField.value) {
            usernameField.focus();
        }
    }, 700);

    // Add remember me functionality (if checkbox exists)
    const rememberCheckbox = document.querySelector('#id_remember_me');
    if (rememberCheckbox) {
        // Load saved username if remember me was checked
        const savedUsername = localStorage.getItem('rememberedUsername');
        if (savedUsername && usernameField) {
            usernameField.value = savedUsername;
            rememberCheckbox.checked = true;
            if (passwordField) {
                passwordField.focus();
            }
        }

        // Save username if remember me is checked
        if (loginForm) {
            loginForm.addEventListener('submit', function() {
                if (rememberCheckbox.checked && usernameField.value) {
                    localStorage.setItem('rememberedUsername', usernameField.value);
                } else {
                    localStorage.removeItem('rememberedUsername');
                }
            });
        }
    }

    console.log('Login page JavaScript initialized');
});
