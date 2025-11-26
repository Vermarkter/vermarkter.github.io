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

// Language Management
function changeLanguage() {
    const language = document.getElementById('language').value;
    localStorage.setItem('language', language);
    // Here you would implement actual language switching logic
    console.log('Language changed to:', language);
}

// Initialize language on page load
function initLanguage() {
    const savedLanguage = localStorage.getItem('language') || 'de';
    document.getElementById('language').value = savedLanguage;
}

// Reviews Management
const reviewsData = [
    {
        text: "CPA in drei Monaten um 32% gesenkt und Online-Bestellungen verdoppelt. Transparente wöchentliche Berichte.",
        author: "Michael Weber",
        company: "E-Commerce GmbH",
        initials: "MW"
    },
    {
        text: "Die Website lädt sofort, die Leads sind stabil. Das Team spricht die Sprache des Geschäfts.",
        author: "Sarah Schmidt",
        company: "TechStart AG",
        initials: "SS"
    },
    {
        text: "YouTube und Remarketing haben die Markenbekanntheit gesteigert. Es besteht eine klare Verbindung zwischen Inhalten und Verkäufen.",
        author: "Thomas Müller",
        company: "Fashion Brand",
        initials: "TM"
    },
    {
        text: "ROI hat sich innerhalb von 6 Monaten verdoppelt. Professionelle Betreuung und messbare Ergebnisse.",
        author: "Lisa Hoffmann",
        company: "Local Services",
        initials: "LH"
    },
    {
        text: "Organischer Traffic um 150% gestiegen. SEO-Strategie war genau das, was wir brauchten.",
        author: "Alexander Koch",
        company: "Consulting Firm",
        initials: "AK"
    },
    {
        text: "Social Media Kampagnen haben unsere Zielgruppe perfekt erreicht. Engagement um 200% gestiegen.",
        author: "Julia Becker",
        company: "Beauty Brand",
        initials: "JB"
    },
    {
        text: "Website-Conversion um 45% verbessert. Design und Funktionalität sind erstklassig.",
        author: "Robert Wagner",
        company: "Tech Solutions",
        initials: "RW"
    },
    {
        text: "Google Ads Performance übertrifft alle Erwartungen. ROAS von 4.2 erreicht.",
        author: "Marina Fischer",
        company: "Online Shop",
        initials: "MF"
    },
    {
        text: "Content Marketing Strategie hat unsere Expertenmeinung etabliert. Qualitäts-Leads konstant.",
        author: "David Richter",
        company: "B2B Services",
        initials: "DR"
    },
    {
        text: "Mobile-first Ansatz war genau richtig. 70% unserer Kunden kommen über mobile Geräte.",
        author: "Anna Braun",
        company: "Restaurant Chain",
        initials: "AB"
    },
    {
        text: "Analytics Setup gibt uns endlich klare Einblicke in Kundenverhalten. Datenbasierte Entscheidungen möglich.",
        author: "Stefan Lange",
        company: "Retail Business",
        initials: "SL"
    },
    {
        text: "Remarketing Kampagnen haben unsere Conversion Rate um 60% gesteigert. Geniale Strategie.",
        author: "Christina Wolf",
        company: "SaaS Startup",
        initials: "CW"
    },
    {
        text: "Lokale SEO hat unser Geschäft transformiert. 3x mehr Anfragen aus der Region.",
        author: "Frank Peters",
        company: "Local Business",
        initials: "FP"
    },
    {
        text: "E-Mail Marketing Automatisierung spart Zeit und generiert konstant Umsatz. ROI von 12:1.",
        author: "Sabine Schulz",
        company: "Online Course",
        initials: "SS"
    },
    {
        text: "Influencer Marketing Kampagne war ein voller Erfolg. Reichweite um 300% gesteigert.",
        author: "Patrick Zimmermann",
        company: "Lifestyle Brand",
        initials: "PZ"
    },
    {
        text: "A/B Testing hat unsere Landing Page Conversion verdoppelt. Datengesteuerte Optimierung funktioniert.",
        author: "Nicole Meyer",
        company: "Lead Generation",
        initials: "NM"
    },
    {
        text: "Video Marketing auf YouTube bringt qualifizierte Leads. 5x bessere Conversion als Display Ads.",
        author: "Lars Schulze",
        company: "B2B Software",
        initials: "LS"
    },
    {
        text: "Multi-Channel Strategie koordiniert alle Touchpoints perfekt. Customer Journey ist optimiert.",
        author: "Petra Krüger",
        company: "E-Commerce",
        initials: "PK"
    },
    {
        text: "Conversion Tracking endlich richtig implementiert. Wissen genau, welche Kanäle funktionieren.",
        author: "Markus Neumann",
        company: "Agency",
        initials: "MN"
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
    const scrollAmount = 370; // card width + gap
    
    if (direction === 'left') {
        container.scrollLeft -= scrollAmount;
    } else {
        container.scrollLeft += scrollAmount;
    }
}

// Chat functionality
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
    
    // Add smooth scrolling to navigation links
    const navLinks = document.querySelectorAll('.nav a[href^="#"]');
    document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initLanguage();
    generateReviews();

    // ======== Обробка форми =========
    const form = document.getElementById('lead-form');
    const status = document.getElementById('form-status');

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

    // Add smooth scrolling to navigation links
    const navLinks = document.querySelectorAll('.nav a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Header background on scroll
window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    if (window.scrollY > 50) {
        header.style.background = document.body.getAttribute('data-theme') === 'dark' 
            ? 'rgba(17, 24, 39, 0.98)' 
            : 'rgba(255, 255, 255, 0.98)';
    } else {
        header.style.background = document.body.getAttribute('data-theme') === 'dark' 
            ? 'rgba(17, 24, 39, 0.95)' 
            : 'rgba(255, 255, 255, 0.95)';
    }
});
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
        await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, text: text })
        });
        return true;
    } catch (e) {
        console.error('❌ Помилка при надсиланні в Telegram:', e);
        return false;
    }
}
