var usernamePointer = document.querySelector('#usernamePointer');
var passwordPointer = document.querySelector('#passwordPointer');
var repasswordPointer = document.querySelector('#repasswordPointer');
var fnamePointer = document.querySelector('#fnamePointer');
var lnamePointer = document.querySelector('#lnamePointer');
var emailPointer = document.querySelector('#emailPointer');

usernamePointer.style.display = 'none';
passwordPointer.style.display = 'none';
repasswordPointer.style.display = 'none';
fnamePointer.style.display = 'none';
lnamePointer.style.display = 'none';
emailPointer.style.display = 'none';

window.onload = function (event) {

    // Simulate login click when user presses Enter/Return key
    document.querySelector('#mainForm').addEventListener('keydown', function (event) {
        if (event.keyCode === 13) {
            document.querySelector('#nextButton').click();
        }
    });

    function isValidEmailAddress(emailAddress) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
        return pattern.test(emailAddress);
    }

    function isValidUsername(username) {
        var pattern = /^[a-zA-Z0-9.\-_$@*!]{3,30}$/;
        return pattern.test(username);
    }


    function validateCredentialsFormat(loginCreds) {
        var passedCheck = true;
        var passwordField = document.querySelector('#passwordField');
        var userField = document.querySelector('#userField');
        var fnameField = document.querySelector('#fnameField');
        var lnameField = document.querySelector('#lnameField');
        var emailField = document.querySelector('#emailField');
        if (loginCreds.password.length < 6) {

            passwordPointer.style.display = '';

            passwordField.classList.add('error');
            passedCheck = false;

        } else {
            passwordField.classList.remove('error');
            passwordPointer.style.display = 'none';
        }

        if (loginCreds.repassword != loginCreds.password) {

            repasswordPointer.style.display = '';

            repasswordField.classList.add('error');
            passedCheck = false;
        } else {
            repasswordPointer.style.display = 'none';
            repasswordField.classList.remove('error');
        }

        if (!isValidUsername(loginCreds.username)) {
            usernamePointer.style.display = '';

            userField.classList.add('error');
            passedCheck = false;
        } else {
            usernamePointer.style.display = 'none';
            userField.classList.remove('error');
        }

        if (loginCreds.fname === '') {
            fnamePointer.style.display = '';

            fnameField.classList.add('error');
            passedCheck = false;
        } else {
            fnamePointer.style.display = 'none';
            fnameField.classList.remove('error');
        }

        if (loginCreds.lname === '') {
            lnamePointer.style.display = '';

            lnameField.classList.add('error');
            passedCheck = false;
        } else {
            lnamePointer.style.display = 'none';
            lnameField.classList.remove('error');
        }

        if (!isValidEmailAddress(loginCreds.email)) {
            emailPointer.style.display = '';

            emailField.classList.add('error');
            passedCheck = false;
        } else {
            emailPointer.style.display = 'none';
            emailField.classList.remove('error');
        }

        // console.log("passCheck : ", passedCheck)
        return passedCheck;
    }

    document.querySelector('#nextButton').addEventListener('click', function () {
        var us = document.querySelector('input[name="username"]').value;
        var pass = document.querySelector('input[name="password"]').value;
        var repass = document.querySelector('input[name="repassword"]').value;

        var fname = document.querySelector('input[name="fname"]').value;
        var lname = document.querySelector('input[name="lname"]').value;
        var email = document.querySelector('input[name="email"]').value;

        var loginCreds = {
            username: us,
            password: pass,
            repassword: repass,
            fname: fname,
            lname: lname,
            email: email
        };

        if (validateCredentialsFormat(loginCreds)) {
            console.log("Valid Credentials have been entered ...\n Proceeding to sending data");

            var xhr = new XMLHttpRequest();

            xhr.onreadystatechange = function () {
                if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
                    console.log("(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200)")

                    if (xhr.response == 'OK007') {
                        window.location.href = '/voice';
                    } else if (xhr.response == 'ERR001') {
                        Swal.fire({
                            icon: 'error',
                            title: 'ขออภัย',
                            text: 'ชื่อผู้ใช้นี้ไม่พร้อมใช้งาน กรุณาลองใหม่อีกครั้ง'
                        });
                        // window.location.href = '/?error=E002';
                    }
                }
            }

            xhr.open("POST", "/enroll", true);
            xhr.setRequestHeader("Content-type", "application/json");

            xhr.send(JSON.stringify(loginCreds));

            console.log("Your http message has been sent.");
        } else {
            console.log("Invalid credentials have been entered ...\nPlease try again ...");
        }

        console.log("username : ", us)
        // console.log("password : ", pass)
        // console.log("password : ", repass)

        console.log("You clicked the login Next button");
    });

    document.querySelector('#backButton').addEventListener('click', function () {
        window.location.href = '/?ref=cancelled';
    });

};
