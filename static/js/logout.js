document.addEventListener("DOMContentLoaded", () => {
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
})
