// Chat responses in multiple languages
const chatResponses = {
    de: {
        greetings: [
            "Hallo! Wie kann ich Ihnen heute helfen?",
            "Guten Tag! Was kann ich für Sie tun?",
            "Willkommen! Haben Sie Fragen zu unseren Leistungen?"
        ],
        services: [
            "Wir bieten Webseiten-Erstellung, SEO, Social Media Marketing und Performance Marketing. Welcher Bereich interessiert Sie?",
            "Unsere Hauptleistungen sind: Website-Entwicklung, Suchmaschinenoptimierung, Social Media und Google Ads. Wobei kann ich Ihnen helfen?",
            "Gerne erkläre ich Ihnen unsere Services: Webentwicklung, SEO, Social Media Marketing und bezahlte Werbung. Was interessiert Sie am meisten?"
        ],
        pricing: [
            "Unsere Preise richten sich nach Ihrem spezifischen Projekt. Können Sie mir mehr über Ihre Anforderungen erzählen?",
            "Jedes Projekt ist individuell. Gerne erstellen wir Ihnen ein maßgeschneidertes Angebot. Welche Services benötigen Sie?",
            "Die Kosten hängen vom Umfang ab. Lassen Sie uns über Ihre Ziele sprechen, dann kann ich Ihnen eine Einschätzung geben."
        ],
        contact: [
            "Sie können uns unter info@vermarkter.de erreichen oder +49 123 456 789 anrufen. Wann passt Ihnen ein Beratungsgespräch?",
            "Kontaktieren Sie uns gerne per E-Mail oder Telefon. Soll ich einen Termin für ein kostenloses Beratungsgespräch vereinbaren?",
            "Am besten sprechen wir persönlich über Ihr Projekt. Wann hätten Sie Zeit für ein unverbindliches Gespräch?"
        ],
        default: [
            "Das ist eine interessante Frage. Können Sie mir mehr Details geben?",
            "Gerne helfe ich Ihnen weiter. Können Sie Ihre Frage präzisieren?",
            "Entschuldigung, können Sie das nochmal erklären? Dann kann ich Ihnen besser helfen."
        ]
    },
    ua: {
        greetings: [
            "Привіт! Як я можу вам допомогти сьогодні?",
            "Добрий день! Що я можу для вас зробити?",
            "Ласкаво просимо! Маєте питання про наші послуги?"
        ],
        services: [
            "Ми пропонуємо створення веб-сайтів, SEO, маркетинг в соціальних мережах та performance маркетинг. Що вас цікавить?",
            "Наші основні послуги: розробка сайтів, пошукова оптимізація, соціальні мережі та Google Ads. З чим можу допомогти?",
            "Охоче розповім про наші сервіси: веб-розробка, SEO, маркетинг в соцмережах та платна реклама. Що найбільше цікавить?"
        ],
        pricing: [
            "Наші ціни залежать від специфіки вашого проекту. Розкажіте більше про ваші вимоги?",
            "Кожен проект індивідуальний. Охоче створимо персональну пропозицію. Які сервіси вам потрібні?",
            "Вартість залежить від обсягу. Давайте поговоримо про ваші цілі, тоді зможу дати оцінку."
        ],
        contact: [
            "Ви можете зв'язатися з нами на info@vermarkter.de або подзвонити +49 123 456 789. Коли вам зручно для консультації?",
            "Зв'яжіться з нами електронною поштою або телефоном. Призначити безкоштовну консультацію?",
            "Краще поговорити особисто про ваш проект. Коли б ви мали час для необов'язкової розмови?"
        ],
        default: [
            "Це цікаве питання. Можете дати більше деталей?",
            "Охоче допоможу. Можете уточнити ваше питання?",
            "Вибачте, можете пояснити ще раз? Тоді зможу краще допомогти."
        ]
    },
    en: {
        greetings: [
            "Hello! How can I help you today?",
            "Good day! What can I do for you?",
            "Welcome! Do you have questions about our services?"
        ],
        services: [
            "We offer website creation, SEO, social media marketing and performance marketing. What interests you?",
            "Our main services are: website development, search engine optimization, social media and Google Ads. How can I help?",
            "Happy to explain our services: web development, SEO, social media marketing and paid advertising. What interests you most?"
        ],
        pricing: [
            "Our prices depend on your specific project requirements. Can you tell me more about your needs?",
            "Each project is individual. We're happy to create a tailored offer. Which services do you need?",
            "Costs depend on scope. Let's talk about your goals, then I can give you an estimate."
        ],
        contact: [
            "You can reach us at info@vermarkter.de or call +49 123 456 789. When would a consultation suit you?",
            "Contact us by email or phone. Shall I schedule a free consultation?",
            "It's best to discuss your project personally. When would you have time for a non-binding conversation?"
        ],
        default: [
            "That's an interesting question. Can you give me more details?",
            "Happy to help you further. Can you clarify your question?",
            "Sorry, could you explain that again? Then I can help you better."
        ]
    },
    pl: {
        greetings: [
            "Cześć! Jak mogę Ci dziś pomóc?",
            "Dzień dobry! Co mogę dla Ciebie zrobić?",
            "Witamy! Masz pytania dotyczące naszych usług?"
        ],
        services: [
            "Oferujemy tworzenie stron internetowych, SEO, marketing w mediach społecznościowych i performance marketing. Co Cię interesuje?",
            "Nasze główne usługi to: rozwój stron internetowych, optymalizacja dla wyszukiwarek, media społecznościowe i Google Ads. W czym mogę pomóc?",
            "Chętnie wyjaśnię nasze usługi: tworzenie stron, SEO, marketing w social media i płatną reklamę. Co Cię najbardziej interesuje?"
        ],
        pricing: [
            "Nasze ceny zależą od specyfiki Twojego projektu. Możesz opowiedzieć więcej o Twoich wymaganiach?",
            "Każdy projekt jest indywidualny. Chętnie stworzymy spersonalizowaną ofertę. Jakich usług potrzebujesz?",
            "Koszty zależą od zakresu. Porozmawiajmy o Twoich celach, wtedy będę mógł podać szacunek."
        ],
        contact: [
            "Możesz skontaktować się z nami na info@vermarkter.de lub zadzwonić +49 123 456 789. Kiedy pasowałaby Ci konsultacja?",
            "Skontaktuj się z nami mailem lub telefonem. Umówić bezpłatną konsultację?",
            "Najlepiej porozmawiać osobiście o Twoim projekcie. Kiedy miałbyś czas na niezobowiązującą rozmowę?"
        ],
        default: [
            "To interesujące pytanie. Możesz podać więcej szczegółów?",
            "Chętnie Ci pomogę. Możesz sprecyzować swoje pytanie?",
            "Przepraszam, możesz wyjaśnić to jeszcze raz? Wtedy będę mógł lepiej pomóc."
        ]
    },
    ru: {
        greetings: [
            "Привет! Как я могу вам помочь сегодня?",
            "Добрый день! Что я могу для вас сделать?",
            "Добро пожаловать! У вас есть вопросы по нашим услугам?"
        ],
        services: [
            "Мы предлагаем создание веб-сайтов, SEO, маркетинг в социальных сетях и performance маркетинг. Что вас интересует?",
            "Наши основные услуги: разработка сайтов, поисковая оптимизация, социальные сети и Google Ads. Чем могу помочь?",
            "С удовольствием расскажу о наших сервисах: веб-разработка, SEO, маркетинг в соцсетях и платная реклама. Что больше всего интересует?"
        ],
        pricing: [
            "Наши цены зависят от специфики вашего проекта. Расскажите больше о ваших требованиях?",
            "Каждый проект индивидуален. С удовольствием создадим персональное предложение. Какие сервисы вам нужны?",
            "Стоимость зависит от объёма. Давайте поговорим о ваших целях, тогда смогу дать оценку."
        ],
        contact: [
            "Вы можете связаться с нами по адресу info@vermarkter.de или позвонить +49 123 456 789. Когда вам удобно для консультации?",
            "Свяжитесь с нами по электронной почте или телефону. Назначить бесплатную консультацию?",
            "Лучше поговорить лично о вашем проекте. Когда у вас было бы время для необязательного разговора?"
        ],
        default: [
            "Это интересный вопрос. Можете дать больше деталей?",
            "С удовольствием помогу. Можете уточнить ваш вопрос?",
            "Извините, можете объяснить ещё раз? Тогда смогу лучше помочь."
        ]
    }
};

// Get current language
function getCurrentLanguage() {
    const languageSelector = document.getElementById('language');
    return languageSelector ? languageSelector.value : 'de';
}

// Get random response from category
function getRandomResponse(category) {
    const lang = getCurrentLanguage();
    const responses = chatResponses[lang] || chatResponses.de;
    const categoryResponses = responses[category] || responses.default;
    return categoryResponses[Math.floor(Math.random() * categoryResponses.length)];
}

// Analyze message intent
function analyzeIntent(message) {
    const lowerMessage = message.toLowerCase();
    
    // Greetings in multiple languages
    const greetingKeywords = [
        'hallo', 'hi', 'hey', 'guten', 'tag', 'morgen', 'abend',
        'привет', 'привіт', 'добро', 'доброго', 'день', 'вечер',
        'hello', 'good', 'morning', 'evening', 'afternoon',
        'cześć', 'dzień', 'dobry', 'witaj',
        'здравствуй', 'добрый'
    ];
    
    // Services keywords
    const serviceKeywords = [
        'website', 'webseite', 'seo', 'social', 'media', 'marketing', 'google', 'ads',
        'веб', 'сайт', 'реклама', 'продвижение', 'оптимизация',
        'strona', 'reklama', 'optymalizacja', 'promocja',
        'сайт', 'реклама', 'продвижение'
    ];
    
    // Pricing keywords
    const pricingKeywords = [
        'preis', 'kosten', 'price', 'cost', 'budget', 'money',
        'цена', 'стоимость', 'бюджет', 'деньги', 'ціна', 'вартість', 'гроші',
        'cena', 'koszt', 'budżet', 'pieniądze',
        'цена', 'стоимость', 'бюджет'
    ];
    
    // Contact keywords
    const contactKeywords = [
        'kontakt', 'contact', 'email', 'telefon', 'phone', 'termin', 'appointment',
        'контакт', 'связь', 'телефон', 'почта', 'встреча',
        'kontakt', 'spotkanie', 'telefon', 'email',
        'контакт', 'связь', 'телефон'
    ];
    
    if (greetingKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'greetings';
    } else if (serviceKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'services';
    } else if (pricingKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'pricing';
    } else if (contactKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'contact';
    } else {
        return 'default';
    }
}

// Main response generation function
function generateResponse(message) {
    const intent = analyzeIntent(message);
    return getRandomResponse(intent);
}

// Make functions available globally
window.generateResponse = generateResponse;
window.analyzeIntent = analyzeIntent;
window.getCurrentLanguage = getCurrentLanguage;

// Initialize chat with welcome message
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (typeof addChatMessage === 'function') {
            addChatMessage(getRandomResponse('greetings'), 'bot');
        }
    }, 2000);
});
