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

        await loadUserOrders();
        
    } catch (error) {
        console.error("Error:", error.message);
        alert("Network error: " + error.message);
        window.location.href = "/";
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

async function loadUserOrders() {
    const token = localStorage.getItem("access_token");
    const container = document.getElementById("ordersContainer");
    container.innerHTML = ""; // Clear initial message

    try {
        const response = await fetch("/api/orders/user", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            container.innerHTML = "<p>Failed to load orders.</p>";
            return;
        }

        const orders = await response.json();

        if (orders.length === 0) {
            container.innerHTML = "<p>You have no orders yet.</p>";
            return;
        }

        orders.forEach(order => {
            const orderDiv = document.createElement("div");
            orderDiv.classList.add("order-box");

            const productList = order.products.map(p => 
                `<li>${p.name} — Quantity: ${p.quantity}</li>`
            ).join("");

            const countdownId = `countdown-${order.id}`;
            const createdAt = new Date(order.created_at + 'Z');
            if (isNaN(createdAt.getTime())) {
                console.warn("Invalid created_at date:", order.created_at);
                return;
            }

            orderDiv.innerHTML = `
                <h3>Order #${order.user_order_number}</h3>
                <p>Total Price: $${order.total_price.toFixed(2)}</p>
                <p>Status: <span id="status-${order.id}">${order.status}</span></p>
                <ul>${productList}</ul>
                <p>Time left: <span id="${countdownId}">Loading...</span></p>
                <button onclick="deleteOrder(${order.id})">Delete Order</button>
                <hr>
            `;
            container.appendChild(orderDiv);

            // Start countdown
            startCountdown(countdownId, createdAt, order.id);
        });

    } catch (error) {
        console.error("Error loading orders:", error);
        container.innerHTML = "<p>Error fetching order data.</p>";
    }
}

async function deleteOrder(orderId) {
    const token = localStorage.getItem("access_token");
    if (!confirm("Are you sure you want to delete this order?")) return;

    try {
        const response = await fetch(`/api/orders/${orderId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message || "Order deleted successfully!");
            await loadUserOrders(); // Refresh the list
            await showUserBalance();
        } else {
            alert(result.error || "Failed to delete order.");
        }
    } catch (error) {
        console.error("Error deleting order:", error);
        alert("Network error, try again later.");
    }
}

function startCountdown(elementId, createdAt, orderId) {
    const countdownElement = document.getElementById(elementId);
    const statusElement = document.getElementById(`status-${orderId}`);

    console.log("Order ID:", orderId);
    console.log("Created At (raw):", createdAt);
    console.log("Parsed Created At:", createdAt.toISOString());
    console.log("Countdown Element ID:", elementId, "Found:", !!countdownElement);
    console.log("Status Element ID:", `status-${orderId}`, "Found:", !!statusElement);

    const deliveryDuration = 120 * 1000; //2 minutes
    const endTime = new Date(createdAt.getTime() + deliveryDuration);
    let timer;

    const updateCountdown = async () => {
        const now = new Date(new Date().toISOString()); // forces UTC parsing
        const remaining = endTime - now;

        console.log("Remaining time (ms):", remaining);
        console.log("Now:", now.toISOString(), "| EndTime:", endTime.toISOString());

        if (remaining <= 0) {
            countdownElement.innerText = "0";
            clearInterval(timer);

            if (statusElement && statusElement.innerText !== "Shipped") {
                statusElement.innerText = "Shipped";

                try {
                    const token = localStorage.getItem("access_token");
                    await fetch(`/api/orders/${orderId}`, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify({ status: "Shipped"})
                    });
                } catch (err) {
                    console.error("Failed to update order status:", err);
                }
            }


        } else {
            const minutes = Math.floor(remaining / 60000);
            const seconds = Math.floor((remaining % 60000) / 1000);
            countdownElement.innerText = `${minutes}:${seconds.toString().padStart(2, "0")}`;
        }
    };

    updateCountdown(); // Run immediately once
    timer = setInterval(updateCountdown, 1000);
}
