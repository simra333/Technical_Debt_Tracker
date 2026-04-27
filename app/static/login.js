document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })    
    })
    .then(response => {
        return response.json().then(data => ({ response, data }));
    })
    .then(({ response, data }) => {
        if (response.ok) {
            window.location.href = "/";
        } else {
            document.getElementById("error").innerText = data.message;
        }
    })
    .catch(error => {
        console.error("Login error:", error);
        document.getElementById("error").innerText = "Error. Please try again.";
    });
});