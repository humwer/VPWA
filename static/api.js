document.addEventListener("DOMContentLoaded", function () {
    const cookies = document.cookie.split("; ").reduce((acc, cookie) => {
        const [name, value] = cookie.split("=");
        acc[name] = value;
        return acc;
    }, {});

    if (cookies.refresh_token) {
        sessionStorage.setItem("refresh_token", cookies.refresh_token);
        document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
    }
    if (cookies.expired) {
        sessionStorage.setItem("expired", cookies.expired);
        document.cookie = "expired=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
    }
    if (cookies.user_id) {
        sessionStorage.setItem("user_id", cookies.user_id);
        document.cookie = "user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const expired = sessionStorage.getItem("expired");

    if (expired) {
        const now = Math.floor(Date.now() / 1000);

        if (now >= parseInt(expired, 10)) {
            fetch("/api/refresh", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    refresh_token: sessionStorage.getItem("refresh_token"),
                    user_id: sessionStorage.getItem("user_id")})
            })
            .then(response => response.json())
            .then(data => {
                sessionStorage.clear();
                console.log("Ответ:", data);
            })
            .catch(error => sessionStorage.clear());
        }
    }
});
