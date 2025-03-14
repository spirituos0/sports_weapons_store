document.addEventListener("DOMContentLoaded", async () => {
    await loadProfile();

    // ✅ Добавляем обработчик клика для пополнения баланса
    document.getElementById("depositButton").addEventListener("click", depositMoney);
});

async function loadProfile() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("No token found, please log in again.");
        window.location.href = "/login";
        return;
    }

    try {
        const response = await fetch("/auth/profile", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error("Error loading profile");
        }

        const data = await response.json();
        document.getElementById("username").innerText = data.username || "Unknown";
        document.getElementById("email").innerText = data.email || "Unknown";
        document.getElementById("userId").innerText = data.id || "Unknown";
        document.getElementById("role").innerText = data.role || "User";
        document.getElementById("created_at").innerText = data.created_at || "Unknown";

        // ✅ Проверяем, существует ли баланс перед вызовом toFixed()
        let balance = data.balance !== undefined ? data.balance.toFixed(2) : "0.00";
        document.getElementById("balance").innerText = `$${balance}`;
        
    } catch (error) {
        console.error("Error:", error.message);
        alert("Network error: " + error.message);
        window.location.href = "/login";
    }
}

async function depositMoney() {
    const token = localStorage.getItem("access_token");
    const amount = parseFloat(document.getElementById("depositAmount").value);

    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount!");
        return;
    }

    try {
        const response = await fetch("/auth/profile/deposit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ amount: amount })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Failed to deposit money");
            return;
        }

        document.getElementById("balance").innerText = data.new_balance.toFixed(2);
        alert("Balance successfully updated!");
    } catch (error) {
        console.error("Error depositing money:", error);
        alert("Network error, please try again later.");
    }
}






document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Нет токена, авторизуйтесь снова!");
        window.location.href = "/login";
        return;
    }

    try {
        const response = await fetch("/auth/profile", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка загрузки профиля: ${response.status} ${response.statusText}`);
        }

        let data;
        try {
            data = await response.json();
        } catch (jsonError) {
            throw new Error("Ошибка парсинга JSON ответа сервера");
        }

        // Проверяем существование элементов перед присвоением значений
        const usernameElem = document.getElementById("username");
        const emailElem = document.getElementById("email");
        const userIdElem = document.getElementById("userId");
        const roleElem = document.getElementById("role");
        const createdAtElem = document.getElementById("created_at");

        if (usernameElem) usernameElem.innerText = data.username || "Неизвестно";
        if (emailElem) emailElem.innerText = data.email || "Неизвестно";
        if (userIdElem) userIdElem.innerText = data.id || "Неизвестно";
        if (roleElem) roleElem.innerText = data.role || "Пользователь";
        if (createdAtElem) createdAtElem.innerText = data.created_at || "Неизвестно";
        
    } catch (error) {
        console.error("Ошибка:", error.message);
        alert("Ошибка сети: " + error.message);
        window.location.href = "/login";
    }

    // Обработчик выхода из аккаунта
    const logoutBtn = document.getElementById("logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            window.location.href = "/";
        });
    } else {
        console.error("Кнопка выхода не найдена!");
    }
});
document.addEventListener("DOMContentLoaded", async () => {
    const goToHomeBtn = document.getElementById("goToHome");
    if (goToHomeBtn) {
        goToHomeBtn.addEventListener("click", () => {
            window.location.href = "/index"; // Перенаправление на главную страницу
        });
    }
});
