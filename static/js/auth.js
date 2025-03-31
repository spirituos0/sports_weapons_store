document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");

    // Registration
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const username = document.getElementById("regUsername").value;
        const email = document.getElementById("regEmail").value;
        const password = document.getElementById("regPassword").value;

        const response = await fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();
        document.getElementById("registerMessage").innerText = data.message || data.error;
    });

    // Login
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document.getElementById("loginUsername").value.trim();
        const password = document.getElementById("loginPassword").value.trim();
        
        console.log("Insert data:", { username, password }); // Checking the data

        if (!username || !password) {
            document.getElementById("loginMessage").innerText = "Insert login and password";
            return;
        }

        try {
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            // Checking that the server returned exactly JSON
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                console.error("Error: response is not JSON", await response.text());
                return;
            }

            const result = await response.json();
            console.log("Server response:", result);
            
            if (response.ok) {
                localStorage.setItem("access_token", result.access_token);
                console.log("Logged in successfully");
                window.location.href = "/dashboard";  // Redirect on the page after login
            } else {
                document.getElementById("loginMessage").innerText = result.error || result.msg || "Authorization error";
            }
        } catch (error) {
            console.error("Network error:", error);
            alert("Network error");
        }
    });
});
