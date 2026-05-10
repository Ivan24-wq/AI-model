// Вспомогательная функция для поиска элементов (безопасно)
const el = (id) => document.getElementById(id);

// --- ЛОГИКА СТРАНИЦЫ ВХОДА ---
const loginForm = el('login-form');
if (loginForm) {
    loginForm.onsubmit = async (e) => {
        e.preventDefault();

        const email = document.querySelector('#email').value;
        const password = document.querySelector('#password').value;

        const res = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password
            })
        });
    const data = await res.json();

    if (res.ok) {
        window.location.href = '/frontend/chat.html';
    } else {
        alert(data.detail || 'Ошибка входа');
    }
};
}

// --- ЛОГИКА СТРАНИЦЫ РЕГИСТРАЦИИ ---
const regForm = el('register-form');

if (regForm) {
    regForm.onsubmit = async (e) => {
        e.preventDefault();

        const data = {
            username: el('username').value,
            email: el('email').value,
            password: el('password').value
        };

        try {
            const res = await fetch('http://127.0.0.1:8000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (!res.ok) {
                alert(result.detail || "Ошибка регистрации");
                return;
            }

            alert("Подтвердите почту!");

        } catch (err) {
            console.error("REGISTER ERROR:", err);
            alert("Сервер недоступен");
        }
    };
}

// --- ЛОГИКА ЧАТА (выполнится только на chat.html) ---
const sendBtn = el('send-btn');
if (sendBtn) {
    const input = el('user-input');
    const output = el('output-area');
    const fileInput = el('file-input');
    const previewList = el('preview-list');
    const previewContainer = el('image-preview-container');
    const stars = document.querySelectorAll('.star');
    let currentImages = [];

    // Анимация и логика звёзд
    stars.forEach(star => {
        star.addEventListener('mouseover', () => {
            const val = star.dataset.value;
            stars.forEach((s, idx) => s.classList.toggle('active', idx < val));
        });
        star.addEventListener('mouseout', () => {
            stars.forEach(s => s.classList.remove('active'));
        });
        star.addEventListener('click', () => {
            alert(`Мухомор запомнил вашу оценку: ${star.dataset.value}`);
            el('rating-modal').classList.add('hidden');
        });
    });

    // Управление модальным окном рейтинга
    el('rate-btn').onclick = () => el('rating-modal').classList.remove('hidden');
    el('close-rating').onclick = () => el('rating-modal').classList.add('hidden');

    // Авто-высота текстового поля
    input.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Обработка картинок
    fileInput.onchange = (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) previewContainer.classList.remove('hidden');
        
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (ev) => {
                const imgWrap = document.createElement('div');
                imgWrap.className = 'relative flex-shrink-0';
                imgWrap.innerHTML = `<img src="${ev.target.result}" class="h-12 w-12 object-cover rounded border border-gray-600 shadow-sm">`;
                previewList.appendChild(imgWrap);
            };
            reader.readAsDataURL(file);
        });
    };
    // Отправка сообщений
    sendBtn.onclick = async () => {

    const text = input.value.trim();

    const files = fileInput.files;

    if (files.length === 0) {
        alert("Выберите изображение");
        return;
    }

    const file = files[0];

    // FormData
    const formData = new FormData();

    formData.append("file", file);

    formData.append("model_type", "baseline");

    try {

        // запрос к FastAPI
        const response = await fetch(
            "http://127.0.0.1:8000/api/predict",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        console.log(data);

        // сообщение пользователя
        const userMsg = document.createElement("div");

        userMsg.className =
            "flex justify-end message-animation w-full";

        userMsg.innerHTML = `
            <div class="bg-violet-600 text-white px-3 py-2 rounded-xl rounded-tr-none max-w-[85%] shadow-lg">
                <span>${text || "📷 Изображение отправлено"}</span>
            </div>
        `;

        output.appendChild(userMsg);

        // ответ AI
        const aiMsg = document.createElement("div");

        aiMsg.className =
            "flex justify-start message-animation w-full";

        aiMsg.innerHTML = `
            <div class="bg-gray-700 text-white px-3 py-2 rounded-xl rounded-tl-none max-w-[85%] shadow-lg">
                <div><b>Класс:</b> ${data["Класс"]}</div>
                <div><b>Confidence:</b> ${(data["Вероятность"] * 100).toFixed(2)}%</div>
            </div>
        `;

        output.appendChild(aiMsg);

        // очистка
        input.value = "";

        previewList.innerHTML = "";

        previewContainer.classList.add("hidden");

        fileInput.value = "";

        output.scrollTo({
            top: output.scrollHeight,
            behavior: "smooth"
        });

    } catch (err) {

        console.error(err);

        alert("Ошибка запроса к серверу");

    }
};
};
// --- ВОССТАНОВЛЕНИЕ ПАРОЛЯ ---
const requestForm = el('reset-request-form');

if (requestForm) {
    requestForm.onsubmit = async (e) => {
        e.preventDefault();

        const email = el('reset-email').value;
        

        try {
            const res = await fetch('http://127.0.0.1:8000/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            const data = await res.json();

            console.log("RESET RESPONSE:", res.status, data);

            if (!res.ok) {
                alert(data.detail || "Ошибка отправки письма");
                return;
            }

            alert("Письмо отправлено! Проверь почту.");

        
            window.location.href = `/frontend/reset_confirm.html?token=${data.token || ""}`;

        } catch (err) {
            console.error("RESET ERROR:", err);
            alert("Сервер недоступен");
        }
    };
}

const confirmForm = el('reset-confirm-form');

if (confirmForm) {
    confirmForm.onsubmit = async (e) => {
        e.preventDefault();

        const newPass = el('new-password').value;
        const confirmPass = el('confirm-password').value;

        if (newPass !== confirmPass) {
            alert("Пароли не совпадают");
            return;
        }
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');

        if (!token) {
            alert("Токен отсутствует в ссылке");
            return;
        }

        const res = await fetch('http://127.0.0.1:8000/reset/confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: token,
                new_password: newPass
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "Ошибка смены пароля");
            return;
        }

        alert("Пароль успешно обновлен!");
        window.location.href = '/frontend/index.html';
    };
}

//ВЫХОД
const logoutBtn = document.getElementById('logout-btn');

if (logoutBtn) {
    logoutBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        try {
            const res = await fetch('http://127.0.0.1:8000/logout', {
                method: 'POST',
                credentials: 'include' 
            });

            if (!res.ok) {
                console.warn('Logout failed');
            }

        } catch (err) {
            console.error('LOGOUT ERROR:', err);
        }

        
        window.location.href = '/frontend/index.html';
    });
}   