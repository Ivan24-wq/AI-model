// Элементы интерфейса
const sendBtn = document.getElementById('send-btn');
const input = document.getElementById('user-input');
const output = document.getElementById('output-area');
const loader = document.getElementById('loader');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('image-preview-container');
const previewList = document.getElementById('preview-list');
const stars = document.querySelectorAll('.star');

let currentImages = [];

// --- ЛОГИКА АВТОРИЗАЦИИ ---
function openAuth() {
    document.getElementById('auth-overlay').classList.remove('hidden');
    switchAuth('login');
}
function closeAuth() {
    document.getElementById('auth-overlay').classList.add('hidden');
}
function switchAuth(type) {
    ['login-form', 'register-form', 'recovery-form'].forEach(id => {
        document.getElementById(id).classList.toggle('hidden', id !== `${type}-form`);
    });
}

// --- ЛОГИКА ЗВЁЗД (АНИМАЦИЯ) ---
stars.forEach(star => {
    star.addEventListener('mouseover', () => highlightStars(star.dataset.value));
    star.addEventListener('mouseout', resetStars);
    star.addEventListener('click', () => {
        alert(`Мухомор принял вашу оценку: ${star.dataset.value} звёзд.`);
        document.getElementById('rating-modal').classList.add('hidden');
    });
});

function highlightStars(count) {
    stars.forEach((s, idx) => s.classList.toggle('active', idx < count));
}
function resetStars() {
    stars.forEach(s => s.classList.remove('active'));
}

// --- ЛОГИКА ЧАТА И КАРТИНОК ---
input.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

fileInput.onchange = (e) => {
    const files = Array.from(e.target.files);
    const remaining = 10 - currentImages.length;
    files.slice(0, remaining).forEach(file => {
        const reader = new FileReader();
        reader.onload = (ev) => {
            currentImages.push({ id: Date.now() + Math.random(), data: ev.target.result });
            renderPreviews();
        };
        reader.readAsDataURL(file);
    });
    fileInput.value = '';
};

function renderPreviews() {
    previewList.innerHTML = '';
    if (currentImages.length > 0) {
        previewContainer.classList.remove('hidden');
        currentImages.forEach(img => {
            const div = document.createElement('div');
            div.className = 'relative flex-shrink-0';
            div.innerHTML = `<img src="${img.data}" class="h-12 w-12 object-cover rounded border border-pink-500/30">
                <button onclick="removeImage(${img.id})" class="absolute -top-1.5 -right-1.5 bg-pink-600 text-white rounded-full w-4 h-4 text-[10px]">×</button>`;
            previewList.appendChild(div);
        });
        document.getElementById('image-counter').innerText = `Спор загружено: ${currentImages.length}/10`;
    } else {
        previewContainer.classList.add('hidden');
    }
}

window.removeImage = (id) => {
    currentImages = currentImages.filter(img => img.id !== id);
    renderPreviews();
};

function addMessage(text, isUser = false, images = []) {
    const msg = document.createElement('div');
    msg.className = (isUser ? 'flex justify-end' : 'flex justify-start') + ' message-animation w-full';
    const bgColor = isUser ? 'bg-pink-600 text-white' : 'bg-slate-800/80 text-pink-100 border border-pink-500/20';
    
    let imgHtml = images.length > 0 ? `<div class="flex flex-wrap gap-2 mb-2">${images.map(i => `<img src="${i.data}" class="max-w-[120px] rounded border border-white/10 shadow-sm">`).join('')}</div>` : '';
    
    msg.innerHTML = `<div class="inline-block px-4 py-2 rounded-2xl ${isUser ? 'rounded-tr-none' : 'rounded-tl-none'} ${bgColor} max-w-[85%] shadow-xl">
        ${imgHtml}<span class="block text-base leading-tight">${text}</span></div>`;
    output.appendChild(msg);
    output.scrollTo({ top: output.scrollHeight, behavior: 'smooth' });
}

sendBtn.onclick = () => {
    const val = input.value.trim();
    if (!val && currentImages.length === 0) return;
    addMessage(val, true, [...currentImages]);
    input.value = ''; input.style.height = 'auto'; currentImages = []; renderPreviews();
    loader.classList.remove('hidden');
    setTimeout(() => { loader.classList.add('hidden'); addMessage("Бла бла бла...", false); }, 1000);
};

// Открытие модалок
document.getElementById('rate-btn').onclick = () => document.getElementById('rating-modal').classList.remove('hidden');
document.getElementById('close-rating').onclick = () => document.getElementById('rating-modal').classList.add('hidden');