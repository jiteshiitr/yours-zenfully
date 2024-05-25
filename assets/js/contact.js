document.addEventListener('DOMContentLoaded', function() {
    const formSteps = document.querySelectorAll('.form-step');
    const nextStepButtons = document.querySelectorAll('.next-step');
    const prevStepButtons = document.querySelectorAll('.prev-step');
    const progressBar = document.querySelector('.progress-bar');
    const phoneInputField = document.querySelector("#phone");
    const countryCodeDropdown = document.querySelector("#country-code");
    const contactForm = document.getElementById('contact-form');
    let currentStep = 0;

    const phoneInput = window.intlTelInput(phoneInputField, {
      initialCountry: "in",
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js"
    });

    phoneInputField.addEventListener('countrychange', function() {
      countryCodeDropdown.value = phoneInput.getSelectedCountryData().dialCode;
    });

    function updateProgressBar() {
        const stepPercentage = (currentStep + 1) / formSteps.length * 100;
        progressBar.style.width = stepPercentage + '%';
        progressBar.setAttribute('aria-valuenow', stepPercentage);
    }

    function validateField(field, showPopupOnFail = false) {
        const value = field.value.trim();
        const errorMessage = field.closest('.form-group').querySelector('.error-message');
        let isValid = true;

        if (value === '') {
            field.classList.add('is-invalid');
            errorMessage.textContent = 'This field is required';
            isValid = false;
        } else if (field.id === 'phone' && !/^\d{10}$/.test(value)) {
            field.classList.add('is-invalid');
            errorMessage.textContent = 'Phone number must be 10 digits long';
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            errorMessage.textContent = '';
        }

        if (!isValid && showPopupOnFail) {
            showPopup(errorMessage.textContent);
        }

        return isValid;
    }

    function showPopup(message) {
        const popup = document.createElement('div');
        popup.classList.add('popup');
        popup.innerHTML = `
            <button class="close-btn" onclick="this.parentElement.classList.add('hide'); setTimeout(() => this.parentElement.remove(), 300);">&times;</button>
            <p>${message}</p>
        `;
        contactForm.appendChild(popup);
        setTimeout(() => {
            popup.classList.add('show');
        }, 10);
        setTimeout(() => {
            popup.classList.add('hide');
            setTimeout(() => contactForm.removeChild(popup), 300);
        }, 3000);
    }

    function showSubmissionPopup(message) {
        const submissionPopup = document.createElement('div');
        submissionPopup.classList.add('submission-popup', 'success-popup');
        submissionPopup.innerHTML = `
            <button class="close-btn" onclick="this.parentElement.classList.add('hide'); setTimeout(() => this.parentElement.remove(), 300);">&times;</button>
            <p>${message}</p>
        `;
        contactForm.appendChild(submissionPopup);
        setTimeout(() => {
            submissionPopup.classList.add('show');
        }, 10);
        setTimeout(() => {
            submissionPopup.classList.add('hide');
            setTimeout(() => contactForm.removeChild(submissionPopup), 300);
        }, 3000);
    }

    nextStepButtons.forEach(button => {
        button.addEventListener('click', () => {
            const currentFormStep = formSteps[currentStep];
            const inputs = currentFormStep.querySelectorAll('input, textarea');
            let allValid = true;

            inputs.forEach(input => {
                if (!validateField(input, true)) {
                    allValid = false;
                }
            });

            if (allValid) {
                formSteps[currentStep].classList.remove('active');
                currentStep++;
                formSteps[currentStep].classList.add('active');
                updateProgressBar();
            }
        });
    });

    prevStepButtons.forEach(button => {
        button.addEventListener('click', () => {
            formSteps[currentStep].classList.remove('active');
            currentStep--;
            formSteps[currentStep].classList.add('active');
            updateProgressBar();
        });
    });

    document.getElementById('contact-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(this);
        const data = {
            properties: {
                email: '',
                firstname: formData.get('name'),
                lastname: '',
                phone: document.getElementById('country-code').value + formData.get('phone'),
                message: formData.get('message')
            }
        };

        fetch('https://omj33xy5jl.execute-api.ap-southeast-1.amazonaws.com/dev/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(result => {
            showSubmissionPopup('Thank you for Choosing us to help with your mental health journey!');
            document.getElementById('contact-form').reset();
            currentStep = 0;
            formSteps.forEach(step => step.classList.remove('active'));
            formSteps[currentStep].classList.add('active');
            updateProgressBar();
        })
        .catch(error => {
            showSubmissionPopup('There was an error submitting the form. Please try again.');
        });
    });

    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('input', () => validateField(input));
    });

    updateProgressBar();
});
