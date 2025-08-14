// Register Page Specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Register page loaded successfully');

    // Get register form elements
    const registerForm = document.querySelector('.register-form form');
    const usernameField = document.querySelector('#id_username');
    const emailField = document.querySelector('#id_email');
    const password1Field = document.querySelector('#id_password1');
    const password2Field = document.querySelector('#id_password2');
    const submitButton = document.querySelector('.register-form button[type="submit"]');
    
    // Add loading animation to register button
    if (registerForm && submitButton) {
        registerForm.addEventListener('submit', function(e) {
            // Add loading state
            submitButton.innerHTML = 'Creating Account...';
            submitButton.disabled = true;
            
            // Add spinner animation
            const spinner = document.createElement('span');
            spinner.innerHTML = ' ⟳';
            spinner.style.animation = 'spin 1s linear infinite';
            submitButton.appendChild(spinner);
            
            // Add CSS for spinner animation
            if (!document.getElementById('register-spinner-style')) {
                const style = document.createElement('style');
                style.id = 'register-spinner-style';
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

    // Real-time validation for register form
    if (usernameField) {
        usernameField.addEventListener('input', function() {
            const username = this.value;
            let isValid = true;
            let message = '';

            if (username.length < 3) {
                isValid = false;
                message = 'Username must be at least 3 characters long';
            } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
                isValid = false;
                message = 'Username can only contain letters, numbers, and underscores';
            }

            validateField(this, isValid, message);
        });
    }

    if (emailField) {
        emailField.addEventListener('input', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            validateField(this, emailRegex.test(email), 'Please enter a valid email address');
        });
    }

    if (password1Field) {
        password1Field.addEventListener('input', function() {
            validatePassword(this.value);
            // Also check password confirmation if it has value
            if (password2Field && password2Field.value) {
                checkPasswordMatch();
            }
        });
    }

    if (password2Field) {
        password2Field.addEventListener('input', function() {
            checkPasswordMatch();
        });
    }

    // Password validation function
    function validatePassword(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
        };

        const strength = Object.values(requirements).filter(Boolean).length;
        let strengthText = '';
        let strengthColor = '';

        if (strength <= 2) {
            strengthText = 'Weak';
            strengthColor = '#dc3545';
        } else if (strength <= 3) {
            strengthText = 'Medium';
            strengthColor = '#fd7e14';
        } else if (strength <= 4) {
            strengthText = 'Strong';
            strengthColor = '#28a745';
        } else {
            strengthText = 'Very Strong';
            strengthColor = '#20c997';
        }

        // Update password strength indicator
        updatePasswordStrength(password1Field, strengthText, strengthColor, requirements);

        return strength >= 3; // Require at least medium strength
    }

    function updatePasswordStrength(field, strengthText, strengthColor, requirements) {
        // Remove existing strength indicator
        const existingIndicator = field.parentNode.querySelector('.password-strength');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        if (field.value) {
            const strengthDiv = document.createElement('div');
            strengthDiv.className = 'password-strength';
            strengthDiv.style.cssText = `
                margin-top: 8px;
                padding: 10px 12px;
                background: rgba(0, 0, 0, 0.05);
                border-radius: 8px;
                font-size: 13px;
                line-height: 1.4;
            `;

            const strengthLabel = document.createElement('div');
            strengthLabel.style.cssText = `
                color: ${strengthColor};
                font-weight: bold;
                margin-bottom: 5px;
            `;
            strengthLabel.textContent = `Password Strength: ${strengthText}`;
            strengthDiv.appendChild(strengthLabel);

            // Add requirements checklist
            const requirementsList = document.createElement('div');
            const reqText = [
                { key: 'length', text: 'At least 8 characters' },
                { key: 'lowercase', text: 'One lowercase letter' },
                { key: 'uppercase', text: 'One uppercase letter' },
                { key: 'number', text: 'One number' }
            ];

            reqText.forEach(req => {
                const reqDiv = document.createElement('div');
                reqDiv.style.cssText = `
                    color: ${requirements[req.key] ? '#28a745' : '#6c757d'};
                    font-size: 12px;
                `;
                reqDiv.innerHTML = `${requirements[req.key] ? '✓' : '○'} ${req.text}`;
                requirementsList.appendChild(reqDiv);
            });

            strengthDiv.appendChild(requirementsList);
            field.parentNode.appendChild(strengthDiv);
        }
    }

    function checkPasswordMatch() {
        if (password1Field && password2Field) {
            const password1 = password1Field.value;
            const password2 = password2Field.value;
            
            if (password2) {
                const isMatch = password1 === password2;
                validateField(password2Field, isMatch, 'Passwords do not match');
                
                if (isMatch && password2) {
                    // Add success indicator
                    const successDiv = password2Field.parentNode.querySelector('.password-match-success');
                    if (!successDiv) {
                        const successIndicator = document.createElement('div');
                        successIndicator.className = 'password-match-success';
                        successIndicator.style.cssText = `
                            color: #28a745;
                            font-size: 13px;
                            margin-top: 5px;
                            font-weight: 600;
                        `;
                        successIndicator.innerHTML = '✓ Passwords match';
                        password2Field.parentNode.appendChild(successIndicator);
                    }
                } else {
                    // Remove success indicator
                    const successDiv = password2Field.parentNode.querySelector('.password-match-success');
                    if (successDiv) {
                        successDiv.remove();
                    }
                }
            }
        }
    }

    // Register form validation helper functions
    function validateField(field, isValid, errorMessage) {
        const errorElement = field.parentNode.querySelector('.field-error');
        
        if (isValid) {
            field.style.borderColor = '#28a745';
            field.style.boxShadow = '0 0 0 4px rgba(40, 167, 69, 0.1)';
            if (errorElement) {
                errorElement.remove();
            }
        } else if (errorMessage) {
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
        field.style.boxShadow = '0 0 0 4px rgba(220, 53, 69, 0.1)';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = `
            color: #dc3545;
            font-size: 13px;
            margin-top: 5px;
            font-weight: 600;
            padding: 5px 8px;
            background: rgba(220, 53, 69, 0.1);
            border-radius: 5px;
        `;
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    // Add smooth focus transitions to register form fields
    const registerInputs = document.querySelectorAll('.register-form input[type="text"], .register-form input[type="password"], .register-form input[type="email"]');
    registerInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 10px 30px rgba(118, 75, 162, 0.15)';
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 3px 15px rgba(0, 0, 0, 0.05)';
            }
        });
    });

    // Add register form animation on load
    const registerContainer = document.querySelector('.register-form');
    if (registerContainer) {
        registerContainer.style.opacity = '0';
        registerContainer.style.transform = 'translateY(40px)';
        
        setTimeout(() => {
            registerContainer.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            registerContainer.style.opacity = '1';
            registerContainer.style.transform = 'translateY(0)';
        }, 150);
    }

    // Add focus to first field on page load
    setTimeout(() => {
        if (usernameField && !usernameField.value) {
            usernameField.focus();
        }
    }, 800);

    // Add form validation before submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            let isFormValid = true;
            const fields = [usernameField, emailField, password1Field, password2Field];
            
            fields.forEach(field => {
                if (field && !field.value.trim()) {
                    isFormValid = false;
                    showFieldError(field, 'This field is required');
                }
            });

            // Check password strength
            if (password1Field && password1Field.value) {
                const passwordValid = validatePassword(password1Field.value);
                if (!passwordValid) {
                    isFormValid = false;
                    showFieldError(password1Field, 'Password does not meet requirements');
                }
            }

            // Check password match
            if (password1Field && password2Field && password1Field.value !== password2Field.value) {
                isFormValid = false;
                showFieldError(password2Field, 'Passwords do not match');
            }

            if (!isFormValid) {
                e.preventDefault();
                submitButton.innerHTML = 'Sign Up';
                submitButton.disabled = false;
                
                // Remove spinner
                const spinner = submitButton.querySelector('span');
                if (spinner) {
                    spinner.remove();
                }
            }
        });
    }

    console.log('Register page JavaScript initialized');
});
