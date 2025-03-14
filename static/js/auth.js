document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");

    // Регистрация
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

    // Вход
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document.getElementById("loginUsername").value.trim();
        const password = document.getElementById("loginPassword").value.trim();
        
        console.log("Введенные данные:", { username, password }); // Проверка данных

        if (!username || !password) {
            document.getElementById("loginMessage").innerText = "Введите логин и пароль";
            return;
        }

        try {
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            // Проверка, что сервер действительно вернул JSON
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                console.error("Ошибка: ответ не JSON:", await response.text());
                return;
            }

            const result = await response.json();
            console.log("Ответ сервера:", result);
            
            if (response.ok) {
                localStorage.setItem("access_token", result.access_token);
                console.log("Logged in successfully");
                window.location.href = "/dashboard";  // Редирект на страницу после логина
            } else {
                document.getElementById("loginMessage").innerText = result.error || result.msg || "Ошибка авторизации";
            }
        } catch (error) {
            console.error("Ошибка сети:", error);
            alert("Ошибка сети");
        }
    });
});
