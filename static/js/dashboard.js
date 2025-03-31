document.addEventListener("DOMContentLoaded", async () => {
    await loadProfile();

    // Adding a click handler to top up your balance
    document.getElementById("depositButton").addEventListener("click", depositMoney);

    const goToHomeBtn = document.getElementById("goToHome");
    if (goToHomeBtn) {
        goToHomeBtn.addEventListener("click", () => {
            window.location.href = "/index"; // Redirect to home page
        });
    };

    // Account logout handler
    const logoutBtn = document.getElementById("logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            window.location.href = "/";
        });
    } else {
        console.error("Exit button is not found!");
    };
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

        // Check if balance exists before calling toFixed()
        console.log("Balance:", data.balance);
        let balance = data.balance !== undefined ? data.balance.toFixed(2) : "0.00";
        document.getElementById("balance").innerText = `${balance}`;
        
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
        console.log("Sending amount:", amount);
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


