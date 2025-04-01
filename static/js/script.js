document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    loadCart();
});

function fetchProducts() {
    fetch("/api/products")
        .then(response => response.json())
        .then(data => {
            let productList = document.getElementById("product-list");
            productList.innerHTML = "";
            data.forEach(product => {
                let productCard = document.createElement("div");
                productCard.classList.add("product-card");
                productCard.id = `product-${product.id}`; // Adding an ID to the card

                productCard.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>${product.description}</p>
                    <p><strong>Price:</strong> $${product.price}</p>
                    <button class="add-to-cart" onclick="addToCart(${product.id})">Add to Cart</button>
                `;
                productList.appendChild(productCard);
            });
        })
        .catch(error => console.error("Error loading products:", error));
}

function addToCart(productId) {
    fetch("/cart/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
    })
    .then(response => {
        return response.json().then(data => ({
            status: response.status,
            body: data
        }));
    })
    .then(({ status, body }) => {
        let productCard = document.getElementById(`product-${productId}`);
        let errorMessage = productCard.querySelector(".cart-error-message");

        // If there is already a message, delete it before adding a new one
        if (errorMessage) {
            errorMessage.remove();
        }

        if (status === 400 && body.error) {
            // If the limit is exceeded, we add a message about it
            let errorText = document.createElement("p");
            errorText.classList.add("cart-error-message");
            errorText.innerText = body.error;
            productCard.appendChild(errorText);

            // Instead of an error in the console, we simply log a message
            console.warn(`Attempted to add more than available: ${body.error}`);
        } else if (status === 201) {
            console.log("Product added:", body);
            loadCart(); // Updating the cart
        }
    })
    .catch(error => console.error("Unexpected error adding to cart:", error));
}


async function loadCart() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("You must be logged in!");
        window.location.href = "/";
        return;
    }

    try {
    const response = await fetch("/cart", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (response.status === 401) {
        alert("Session expired. Please log in again.");
        localStorage.removeItem("access_token");
        window.location.href = "/";
        return;
    }

    const data = await response.json();

    let cartList = document.getElementById("cart-list");
    cartList.innerHTML = "";

    if (data.message) {
        cartList.innerHTML = `<p>${data.message}</p>`;
        return;
    }

    if (!Array.isArray(data)) {
        throw new Error("Unexpected cart data format.");
    }

    data.forEach(item => {
        let cartItem = document.createElement("div");
        cartItem.classList.add("cart-item");
        cartItem.innerHTML = `
            <p>${item.product_name} - ${item.quantity} pcs - $${item.price}</p>
            <button class="remove-from-cart" onclick="removeFromCart(${item.product_id})">Remove</button>
        `;
        cartList.appendChild(cartItem);
    });
    }catch(error) {
        console.error("Error loading cart:", error);
        alert("Failed to load cart. Please try again.");
    }
}

function removeFromCart(productId) {
    fetch("/cart/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Product removed:", data);
        loadCart();  // Updating the cart
    })
    .catch(error => console.error("Error removing from cart:", error));
}

function clearCart() {
    fetch("/cart/clear", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Cart cleared:", data);
        loadCart();
    })
    .catch(error => console.error("Error clearing cart:", error));
}

async function purchaseCart() {
    const token = localStorage.getItem("access_token");

    const response = await fetch("/cart", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const cartItems = await response.json();

    if (cartItems.message) {
        alert("Cart is empty!");
        return;
    }

    const products = cartItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
    }));

    const purchaseResponse = await fetch("/api/purchase", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ products })
    });

    const data = await purchaseResponse.json();

    if (purchaseResponse.ok) {
        alert(`Purchase successful! Order ID: ${data.order_id}, Remaining balance: $${data.remaining_balance.toFixed(2)}`);

        const balanceElem = document.getElementById("balance");
        if (balanceElem) {
            balanceElem.innerText = data.remaining_balance.toFixed(2);
        }

        clearCart(); // Clear the cart visually
    } else {
        alert(data.error || "Purchase failed.");
    }
}