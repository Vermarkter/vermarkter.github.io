// Theme Management
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        themeIcon.className = 'fas fa-sun';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-moon';
        localStorage.setItem('theme', 'dark');
    }
}

// Initialize theme on page load
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-moon';
    } else {
        themeIcon.className = 'fas fa-sun';
    }
}

// Language Management (Враховуючи, що в HTML викликається changeLanguage(this.value))
function changeLanguage(langValue) {
    // Якщо langValue передано (з HTML), використовуємо його. Якщо ні, спробуємо знайти елемент.
    const language = langValue || document.getElementById('lang-footer')?.value || 'de';
    
    localStorage.setItem('language', language);
    // Тут має бути логіка для фактичної зміни контенту на сторінці
    console.log('Language changed to:', language);
}

// Initialize language on page load
function initLanguage() {
    // Припускаємо, що селект має ID 'lang-footer'
    const langSelect = document.getElementById('lang-footer');
    if (langSelect) {
        const savedLanguage = localStorage.getItem('language') || 'UA'; // Змінив 'de' на 'UA' згідно з index.html
        langSelect.value = savedLanguage;
    }
}

// Reviews Data
const reviewsData = [
    // ... (Ваші відгуки залишаються тут) ...
    {
        text: "CPA in drei Monaten um 32% gesenkt und Online-Bestellungen verdoppelt. Transparente wöchentliche Berichte.",
        author: "Michael Weber",
        company: "E-Commerce GmbH",
        initials: "MW"
    },
    {
        text: "Website Speed Optimierung hat Bounce Rate halbiert. User Experience deutlich verbessert.",
        author: "Claudia Huber",
        company: "News Portal",
        initials: "CH"
    }
];

function generateReviews() {
    const reviewsContainer = document.getElementById('reviewsScroll');
    
    if (!reviewsContainer) return; // Захист від помилки, якщо контейнера немає

    reviewsData.forEach(review => {
        const reviewCard = document.createElement('div');
        reviewCard.className = 'review-card';
        
        reviewCard.innerHTML = `
            <p class="review-text">"${review.text}"</p>
            <div class="review-author">
                <div class="author-avatar">${review.initials}</div>
                <div class="author-info">
                    <h4>${review.author}</h4>
                    <p class="author-company">${review.company}</p>
                </div>
            </div>
        `;
        
        reviewsContainer.appendChild(reviewCard);
    });
}

// Reviews scrolling functionality
function scrollReviews(direction) {
    const container = document.getElementById('reviewsScroll');
    if (!container) return; // Захист від помилки
    const scrollAmount = 370; // card width + gap
    
    if (direction === 'left') {
        container.scrollLeft -= scrollAmount;
    } else {
        container.scrollLeft += scrollAmount;
    }
}

// Chat functionality (залишаю як було)
let chatOpen = false;
function toggleChat() {
    const chatBody = document.getElementById('chatBody');
    chatOpen = !chatOpen;
    
    if (chatOpen) {
        chatBody.classList.add('active');
        chatBody.style.display = 'flex';
    } else {
        chatBody.classList.remove('active');
        chatBody.style.display = 'none';
    }
}
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message) {
        addChatMessage(message, 'user');
        input.value = '';
        
        // Use chat.js for response
        if (window.generateResponse) {
            const response = window.generateResponse(message);
            setTimeout(() => {
                addChatMessage(response, 'bot');
            }, 1000);
        }
    }
}
function addChatMessage(message, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.textContent = message;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}


// Telegram Form Submission Function (Перенесена на початок, щоб бути доступною)
async function sendToTelegram(formData) {
    const token = '7522018067:AAEdFn-SeXkYvFW6Xm81gK4ZUqVDeRKKBNQ';
    const chatId = '766286196';
    const text = `
🚀 Нова заявка (Ads):
👤 Ім'я: ${formData.get('name')}
📧 Email: ${formData.get('email')}
✈️ Telegram: ${formData.get('telegram') || 'Не вказано'}
📝 Повідомлення: ${formData.get('message')}
    `;

    try {
        const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, text: text })
        });
        return response.ok; // Перевірка статусу відповіді
    } catch (e) {
        console.error('❌ Помилка при надсиланні в Telegram:', e);
        return false;
    }
}


// ======== ІНІЦІАЛІЗАЦІЯ ПІСЛЯ ЗАВАНТАЖЕННЯ DOM =========
document.addEventListener('DOMContentLoaded', function() {
    // 1. Ініціалізація теми та мови
    initTheme();
    initLanguage();
    generateReviews();

    // 2. Обробка форми
    const form = document.getElementById('lead-form');
    const status = document.getElementById('form-status');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            status.textContent = 'Відправляємо...';
            status.className = 'status';

            const formData = new FormData(form);

            try {
                const success = await sendToTelegram(formData);
                if (success) {
                    status.textContent = '✅ Дякуємо! Ми відповімо протягом 2 годин.';
                    status.classList.add('success');
                    form.reset();
                } else {
                    throw new Error('Не вдалося відправити');
                }
            } catch (error) {
                status.textContent = '❌ Помилка. Напишіть нам у Telegram або на email.';
                status.classList.add('error');
                console.error(error);
            }
        });
    }


    // 3. Плавний скролінг
    // Використовую клас .service-nav a[href^="#"] для service сторінок
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"], .service-nav a[href^="#"]'); 

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                // Використовуємо .service-nav замість .header, як у index.html
                const header = document.querySelector('header'); 
                const headerHeight = header ? header.offsetHeight : 0;
                
                window.scrollTo({
                    top: targetElement.offsetTop - headerHeight,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Header background on scroll
window.addEventListener('scroll', function() {
    // Використовую tag header, як у index.html, замість класу .header
    const header = document.querySelector('header'); 
    
    if (header) {
        if (window.scrollY > 50) {
            header.style.background = document.body.getAttribute('data-theme') === 'dark' 
                ? 'rgba(17, 24, 39, 0.98)' 
                : 'rgba(255, 255, 255, 0.98)';
        } else {
            header.style.background = document.body.getAttribute('data-theme') === 'dark' 
                ? 'rgba(17, 24, 39, 0.95)' 
                : 'rgba(255, 255, 255, 0.95)';
        }
    }
});
