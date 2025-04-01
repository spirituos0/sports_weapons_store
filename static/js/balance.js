document.addEventListener("DOMContentLoaded", () => {
    showUserBalance();
});

async function showUserBalance() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
        const response = await fetch("/auth/profile", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) throw new Error("Unable to load user data");

        const data = await response.json();
        const balanceElem = document.getElementById("balance");
        if (balanceElem && data.balance !== undefined) {
            balanceElem.innerText = data.balance.toFixed(2);
        }
    } catch (error) {
        console.error("Error loading balance:", error.message);
    }
}