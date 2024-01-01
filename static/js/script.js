// Javascript to check names and display errors on front end

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".custom-form").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the form from submitting

        var firstName = document.querySelector("[name='first name']").value;
        var lastName = document.querySelector("[name='last name']").value;

        // Example AJAX request to check names
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/check_names", true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);

                if (response.valid == false) {
                    // Display an error message
                    var errorMessage = "Sorry, please try a different member of your party.";
                    document.getElementById("error-message").innerHTML = errorMessage;
                } else {
                    // Names are correct, submit the form or perform other actions
                    document.getElementById("error-message").innerHTML = "";
                    document.querySelector(".custom-form").submit();
                }
            }
        };

        // Send JSON data to the server
        xhr.send(JSON.stringify({ firstName: firstName, lastName: lastName }));
    });
});
