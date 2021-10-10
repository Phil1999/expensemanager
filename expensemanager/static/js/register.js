// User Vars
const usernameField = document.querySelector("#usernameField");
const userFeedBackArea = document.querySelector(".invalid-user");
const usernameSuccess = document.querySelector(".username-success");
// Email Vars
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".invalid-email");
const emailSuccess = document.querySelector(".email-success");
// Password Vars
const showPasswordToggle = document.querySelector(".show-password-toggle")
const passwordField = document.querySelector("#passwordField");

// Submit button var
const submitBtn = document.querySelector('.submit-btn')

// Validating usernameField
usernameField.addEventListener('keyup', (e) => { // Whenever user types something
    
    const usernameVal = e.target.value; // Log what the user is typing
    usernameField.classList.remove("is-invalid");
    userFeedBackArea.style.display = "none";
    
    usernameSuccess.style.display = "block";
    usernameSuccess.textContent = `Testing ${usernameVal}`

    if (usernameVal.length > 0) { // User has typed something
    fetch('/authentication/validate-username', {
        body: JSON.stringify({ username: usernameVal }), // We have to stringify our objects
        method: "POST",
    })
        .then((res) => res.json())
        .then((data) => {
            usernameSuccess.style.display = "none";
            if (data.username_error) {
                submitBtn.disabled = true;
                usernameField.classList.add("is-invalid");
                userFeedBackArea.style.display = "block";
                userFeedBackArea.innerHTML = `<p>${data.username_error}</p>`;
            } else {
                submitBtn.removeAttribute('disabled');
                
            }
    });
}
});

// Validating emailField 

emailField.addEventListener('keyup', (e) => {

    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = "none";

    emailSuccess.style.display = "block";
    emailSuccess.textContent = `Testing ${emailVal}`

    if (emailVal.length > 0) {
        fetch('/authentication/validate-email', {
            body: JSON.stringify({ email: emailVal }), // We have to stringify our objects
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                emailSuccess.style.display = "none";
                if (data.email_error) {
                    submitBtn.setAttribute('disabled', 'disabled');
                    submitBtn.disabled = true;
                    emailField.classList.add("is-invalid"); // This is a bootstrap class
                    emailFeedBackArea.style.display = "block";
                    emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
                } else {

                    submitBtn.removeAttribute('disabled');
                }
        });
    }

});

// Password Toggle
const handleToggleInput = (e) => {

    if (showPasswordToggle.textContent === "SHOW") {
        showPasswordToggle.textContent = "HIDE";

        passwordField.setAttribute('type', 'password');

    } else {
        showPasswordToggle.textContent = "SHOW";

        passwordField.setAttribute('type', 'text');
    }
}

showPasswordToggle.addEventListener('click', handleToggleInput);

