document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
});

function fetchProducts() {
    fetch("http://127.0.0.1:5000/api/products")
        .then(response => response.json())
        .then(data => {
            let productList = document.getElementById("product-list");
            productList.innerHTML = "";
            data.forEach(product => {
                let productCard = document.createElement("div");
                productCard.classList.add("product-card");
                productCard.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>${product.description}</p>
                    <p><strong>Цена:</strong> $${product.price}</p>
                    <button onclick="addToCart(${product.id})">Добавить в корзину</button>
                `;
                productList.appendChild(productCard);
            });
        })
        .catch(error => console.error("Ошибка при получении товаров:", error));
}

function addToCart(productId) {
    console.log(`Товар ${productId} добавлен в корзину (логика корзины будет позже)`);
}
