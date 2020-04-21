var usernamePointer = document.querySelector('#usernamePointer');
var passwordPointer = document.querySelector('#passwordPointer');


usernamePointer.style.display = 'none';
passwordPointer.style.display = 'none';

window.onload = function (event) {

    // Simulate login click when user presses Enter/Return key
    document.querySelector('#mainForm').addEventListener('keydown', function (event) {
        if (event.keyCode === 13) {
            document.querySelector('#nextButton').click();
        }
    });

    function isValidUsername(username) {
        var pattern = /^[a-zA-Z0-9.\-_$@*!]{3,30}$/;
        return pattern.test(username);
    }

    function validateCredentialsFormat(loginCreds) {
        var passedCheck = true;
        var passwordField = document.querySelector('#passwordField');
        var userField = document.querySelector('#userField');

        if (loginCreds.password.length < 6) {

            passwordPointer.style.display = '';

            passwordField.classList.add('error');
            passedCheck = false;

        } else {
            passwordField.classList.remove('error');
            passwordPointer.style.display = 'none';
        }

        if (!isValidUsername(loginCreds.username)) {
            usernamePointer.style.display = '';

            userField.classList.add('error');
            passedCheck = false;
        } else {
            usernamePointer.style.display = 'none';
            userField.classList.remove('error');
        }

        // console.log("passCheck : ", passedCheck)
        return passedCheck;
    }

    document.querySelector('#nextButton').addEventListener('click', function () {
        var us = document.querySelector('input[name="username"]').value;
        var pass = document.querySelector('input[name="password"]').value;

        var loginCreds = {
            username: us,
            password: pass
        };

        if (validateCredentialsFormat(loginCreds)) {

            var xhr = new XMLHttpRequest();

            xhr.onreadystatechange = function () {
                if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
                    console.log("Response : ", xhr.response);

                    if (xhr.response == "ERR001") {
                        passwordPointer.style.display = '';

                    } else if (xhr.response == "ERR002") {
                        usernamePointer.style.display = '';
                    } else if (xhr.response == "OK007") {
                        // window.location.href = '/voice';
                        window.location.href = '/identify';
                    }
                }
            }

            // xhr.open("GET", "/voice", true);
            // xhr.setRequestHeader("Content-type", "application/json");

            // xhr.send();

            // console.log("The enroll button works!");

            xhr.open("POST", "/auth", true);
            xhr.setRequestHeader("Content-type", "application/json");

            xhr.send(JSON.stringify(loginCreds));

            console.log("Your http message has been sent.");
        } else {
            console.log("Invalid credentials have been entered ...\nPlease try again ...");
        }
        console.log("You clicked the login Next button");
    });

    document.querySelector('#backButton').addEventListener('click', function () {
        window.location.href = '/?ref=cancelled';
    });

};
//
// function hideElement(elSelector) {
//   document.querySelector(elSelector).style.display = 'none';
// }
//
// function showElement(elSelector) {
//   document.querySelector(elSelector).style.display = '';
// }
