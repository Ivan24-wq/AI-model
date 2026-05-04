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
    sendBtn.onclick = () => {
        const text = input.value.trim();
        if (!text) return;

        const msg = document.createElement('div');
        msg.className = 'flex justify-end message-animation w-full';
        msg.innerHTML = `
            <div class="bg-violet-600 text-white px-3 py-2 rounded-xl rounded-tr-none max-w-[85%] shadow-lg">
                <span class="block text-base leading-tight">${text}</span>
            </div>
        `;
        output.appendChild(msg);
        
        // Очистка
        input.value = '';
        input.style.height = 'auto';
        previewList.innerHTML = '';
        previewContainer.classList.add('hidden');
        output.scrollTo({ top: output.scrollHeight, behavior: 'smooth' });
    };
	

}
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

            if (!res.ok) {
                alert(data.detail || "Ошибка");
                return;
            }

            window.location.href = '/frontend/reset_confirm.html';

        } catch (err) {
            console.error(err);
            alert("Сервер недоступен");
        }
    };
}

const confirmForm = el('reset-confirm-form');
if (confirmForm) {
    confirmForm.onsubmit = (e) => {
        e.preventDefault();

        const newPass = el('new-password').value;
        const confirmPass = el('confirm-password').value;

        alert('Пароль успешно обновлен!');
        window.location.href = '/frontend/index.html';
    };
}