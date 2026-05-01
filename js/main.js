// ============================================
// VERMARKTER - MAIN JAVASCRIPT
// Complete logic for marketing agency website
// ============================================

// ==================== CONSTANTS ====================
const CALCULATOR_COEFFICIENTS = {
    google: { cpc: 0.8, ctr: 3.5, conversion: 5 },
    meta: { cpc: 0.5, ctr: 2.5, conversion: 4 },
    tiktok: { cpc: 0.2, ctr: 4.5, conversion: 3 }
};

// ==================== MOBILE MENU ====================
const mobileToggle = document.getElementById('mobileToggle');
const mobileMenu = document.getElementById('mobileMenu');

// Move mobile menu outside <header> to avoid backdrop-filter
// creating a containing block that breaks position:fixed sizing
if (mobileMenu && mobileMenu.closest('header')) {
    document.body.appendChild(mobileMenu);
}

// Clone language links from header dropdown into mobile menu
if (mobileMenu) {
    const langDropdown = document.querySelector('.lang-dropdown');
    if (langDropdown) {
        const langSection = document.createElement('div');
        langSection.className = 'mobile-lang-switcher';
        langDropdown.querySelectorAll('a').forEach(link => {
            const clone = link.cloneNode(true);
            langSection.appendChild(clone);
        });
        mobileMenu.appendChild(langSection);
    }
}

if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        mobileMenu.classList.toggle('active');
        const isActive = mobileMenu.classList.contains('active');
        mobileToggle.textContent = isActive ? '✕' : '☰';
        document.body.style.overflow = isActive ? 'hidden' : '';
    });

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            mobileToggle.textContent = '☰';
            document.body.style.overflow = '';
        });
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (mobileMenu.classList.contains('active') &&
            !mobileMenu.contains(e.target) &&
            !mobileToggle.contains(e.target)) {
            mobileMenu.classList.remove('active');
            mobileToggle.textContent = '☰';
            document.body.style.overflow = '';
        }
    });
}

// ==================== THEME TOGGLE ====================
const themeToggle = document.getElementById('theme-btn');

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
    if (themeToggle) {
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

// Initialize theme on load
initTheme();

// ==================== LANGUAGE SELECTOR ====================
const langSelector = document.getElementById('langSelector');

if (langSelector) {
    langSelector.addEventListener('change', (e) => {
        const lang = e.target.value;
        const routes = {
            'UA': '/ua',
            'DE': '/de',
            'EN': '/en',
            'PL': '/pl',
            'RU': '/ru',
            'TR': '/tr'
        };
        
        if (routes[lang]) {
            window.location.href = 'https://vermarkter.vercel.app' + routes[lang];
        }
    });
}

// ==================== CALCULATOR ====================
const budgetSlider = document.getElementById('budgetSlider');
const budgetInput = document.getElementById('budgetInput');
const budgetValue = document.getElementById('budgetValue');
const platform = document.getElementById('platform');
const niche = document.getElementById('niche');
const calculateBtn = document.getElementById('calculateBtn');

// Sync slider and input
function syncBudget(value) {
    if (budgetSlider) budgetSlider.value = value;
    if (budgetInput) budgetInput.value = value;
    if (budgetValue) budgetValue.textContent = value;
}

if (budgetSlider) {
    budgetSlider.addEventListener('input', (e) => {
        syncBudget(e.target.value);
    });
}

if (budgetInput) {
    budgetInput.addEventListener('input', (e) => {
        let value = parseInt(e.target.value) || 100;
        value = Math.max(100, Math.min(10000, value));
        syncBudget(value);
    });
}

// Calculate function
function calculate() {
    const budget = parseInt(budgetSlider?.value || 1000);
    const selectedPlatform = platform?.value || 'google';
    const selectedNiche = niche?.value || 'ecommerce';
    
    const coef = CALCULATOR_COEFFICIENTS[selectedPlatform];
    
    // Calculate metrics
    const clicks = Math.floor(budget / coef.cpc);
    const impressions = Math.floor(clicks / (coef.ctr / 100));
    const leads = Math.floor(clicks * (coef.conversion / 100));
    
    // Apply niche multiplier
    const nicheMultipliers = {
        'ecommerce': 1.0,
        'services': 0.9,
        'b2b': 0.8,
        'saas': 0.85,
        'local': 1.1
    };
    
    const multiplier = nicheMultipliers[selectedNiche] || 1.0;
    const adjustedLeads = Math.floor(leads * multiplier);
    
    // Update UI with animation
    animateNumber('impressions', 0, impressions, 1000);
    animateNumber('clicks', 0, clicks, 1000);
    animateNumber('leads', 0, adjustedLeads, 1000);
}

function animateNumber(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

if (calculateBtn) {
    calculateBtn.addEventListener('click', calculate);
}

// ==================== HERO STATS ANIMATION ====================
function animateStatsOnScroll() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = parseInt(entry.target.dataset.target);
                animateCounter(entry.target, 0, target, 2000);
                entry.target.dataset.animated = 'true';
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => observer.observe(stat));
}

function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        
        // Add % or other suffix based on context
        const suffix = element.dataset.target === '7' ? '' : '%';
        element.textContent = Math.floor(current) + suffix;
    }, 16);
}

// ==================== TESTIMONIALS MARQUEE ====================
function initMarquee() {
    const marqueeContent = document.getElementById('marqueeContent');
    
    if (marqueeContent) {
        // Clone testimonials for seamless loop
        const clone = marqueeContent.cloneNode(true);
        marqueeContent.parentElement.appendChild(clone);
        
        // Pause on hover
        const marqueeElements = document.querySelectorAll('.marquee-content');
        marqueeElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.animationPlayState = 'paused';
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.animationPlayState = 'running';
            });
        });
    }
}

// ==================== COOKIE BANNER ====================
const cookieBanner = document.getElementById('cookieBanner');
const acceptCookies = document.getElementById('acceptCookies');
const declineCookies = document.getElementById('declineCookies');

function initCookieBanner() {
    const cookieConsent = localStorage.getItem('cookieConsent');
    
    if (!cookieConsent && cookieBanner) {
        setTimeout(() => {
            cookieBanner.classList.add('show');
        }, 1000);
    }
}

if (acceptCookies) {
    acceptCookies.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'accepted');
        cookieBanner?.classList.remove('show');
    });
}

if (declineCookies) {
    declineCookies.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'declined');
        cookieBanner?.classList.remove('show');
    });
}

// ==================== CHATBOT ====================
// Chatbot initialization handled by chatbot.js

// ==================== SCROLL ANIMATIONS ====================
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { 
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    elements.forEach(el => observer.observe(el));
}

// ==================== SMOOTH SCROLL ====================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ==================== PREVENT HEADER OVERLAP ====================
function preventHeaderOverlap() {
    // Ensure body has correct padding
    const header = document.querySelector('header');
    if (header) {
        const headerHeight = header.offsetHeight;
        document.body.style.paddingTop = headerHeight + 'px';
    }
}

// ==================== FORM SUBMISSIONS ====================
// Multilingual success messages
const SUCCESS_MESSAGES = {
    de: '✅ Vielen Dank! Ihre Nachricht wurde gesendet. Wir melden uns innerhalb von 24 Stunden.',
    en: '✅ Thank you! Your message has been sent. We will contact you within 24 hours.',
    ua: '✅ Дякуємо! Ваше повідомлення відправлене. Ми зв\'яжемося з вами протягом 24 годин.',
    pl: '✅ Dziękujemy! Twoja wiadomość została wysłana. Skontaktujemy się w ciągu 24 godzin.',
    ru: '✅ Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами в течение 24 часов.',
    tr: '✅ Teşekkürler! Mesajınız gönderildi. 24 saat içinde sizinle iletişime geçeceğiz.'
};

const LOADING_MESSAGES = {
    de: 'Wird gesendet...',
    en: 'Sending...',
    ua: 'Надсилаємо...',
    pl: 'Wysyłanie...',
    ru: 'Отправляем...',
    tr: 'Gönderiliyor...'
};

const ERROR_MESSAGES = {
    de: 'Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.',
    en: 'An error occurred. Please try again later.',
    ua: 'Виникла помилка. Спробуйте пізніше.',
    pl: 'Wystąpił błąd. Spróbuj ponownie później.',
    ru: 'Произошла ошибка. Попробуйте позже.',
    tr: 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
};

function detectLanguage() {
    const path = window.location.pathname;
    if (path.includes('/ua/')) return 'ua';
    if (path.includes('/de/')) return 'de';
    if (path.includes('/en/')) return 'en';
    if (path.includes('/pl/')) return 'pl';
    if (path.includes('/ru/')) return 'ru';
    if (path.includes('/tr/')) return 'tr';
    return 'de';
}

function initForms() {
    const contactForm = document.getElementById('contactForm');
    const formSuccess = document.getElementById('form-success') || document.getElementById('formSuccess');
    const lang = detectLanguage();

    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Get form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData);

            // Check honeypot (bot protection)
            if (data.honeypot && data.honeypot.trim() !== '') {
                console.log('🤖 Bot detected via honeypot');
                return;
            }

            // Validate email
            if (!data.email || !data.email.includes('@')) {
                alert(lang === 'de' ? 'Bitte geben Sie eine gültige E-Mail-Adresse ein.' : 'Please enter a valid email address.');
                return;
            }

            // Show loading state
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = LOADING_MESSAGES[lang] || LOADING_MESSAGES.de;
            submitBtn.disabled = true;

            try {
                console.log('📤 Submitting form data:', data);

                // Send via Telegram Service
                let result = { success: false };

                if (window.telegramService && typeof window.telegramService.sendFormSubmission === 'function') {
                    result = await window.telegramService.sendFormSubmission({
                        name: data.name,
                        email: data.email,
                        phone: data.phone || '',
                        message: data.message,
                        honeypot: data.honeypot
                    });
                } else {
                    console.warn('⚠️ telegramService not available, simulating success');
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    result = { success: true };
                }

                console.log('📥 Form submission result:', result);

                // Track event
                if (typeof trackEvent === 'function') {
                    trackEvent('Contact', 'Submit', 'Contact Form Submission');
                }

                if (result.success) {
                    // Hide form and show success message
                    contactForm.style.display = 'none';

                    // Create or update success message
                    let successDiv = formSuccess;
                    if (!successDiv) {
                        successDiv = document.createElement('div');
                        successDiv.id = 'form-success';
                        successDiv.className = 'form-success-message';
                        contactForm.parentNode.insertBefore(successDiv, contactForm.nextSibling);
                    }

                    successDiv.innerHTML = `
                        <div class="success-icon">✅</div>
                        <p class="success-text">${SUCCESS_MESSAGES[lang] || SUCCESS_MESSAGES.de}</p>
                    `;
                    successDiv.style.display = 'block';

                    // Reset form for potential re-use
                    contactForm.reset();

                    // Show form again after 10 seconds (optional)
                    setTimeout(() => {
                        contactForm.style.display = 'block';
                        successDiv.style.display = 'none';
                    }, 10000);
                } else {
                    throw new Error(result.error || 'Unknown error');
                }

            } catch (error) {
                console.error('❌ Form submission error:', error);
                alert(ERROR_MESSAGES[lang] || ERROR_MESSAGES.de);
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
}

// ==================== CTA BUTTONS ====================
function initCTAButtons() {
    const ctaButtons = document.querySelectorAll('.btn-primary, .btn-secondary');
    
    ctaButtons.forEach(button => {
        if (!button.getAttribute('href') && button.tagName === 'BUTTON') {
            button.addEventListener('click', () => {
                // Scroll to contact or open modal
                const contactSection = document.getElementById('contact');
                if (contactSection) {
                    contactSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    });
}

// ==================== PERFORMANCE OPTIMIZATION ====================
// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimize scroll events
const optimizedScroll = debounce(() => {
    // Add scroll-based animations or effects here
}, 100);

window.addEventListener('scroll', optimizedScroll);

// ==================== INIT ON LOAD ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Vermarkter website initialized');
    
    // Initialize all features
    initTheme();
    initCookieBanner();
    initMarquee();
    animateStatsOnScroll();
    initScrollAnimations();
    initSmoothScroll();
    preventHeaderOverlap();
    initForms();
    initCTAButtons();
    
    // Add loaded class for animations
    document.body.classList.add('loaded');
});

// Recalculate on resize
window.addEventListener('resize', debounce(() => {
    preventHeaderOverlap();
}, 250));

// ==================== ANALYTICS (Optional) ====================
function trackEvent(category, action, label) {
    // Google Analytics or custom analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': category,
            'event_label': label
        });
    }
    console.log('Event tracked:', { category, action, label });
}

// Track important interactions
if (calculateBtn) {
    calculateBtn.addEventListener('click', () => {
        trackEvent('Calculator', 'Calculate', 'Budget Calculator Used');
    });
}

const chatbotButtonForAnalytics = document.getElementById('chatbotButton');
if (chatbotButtonForAnalytics) {
    chatbotButtonForAnalytics.addEventListener('click', () => {
        trackEvent('Engagement', 'Click', 'Chatbot Opened');
    });
}

// ==================== SCROLL TO TOP BUTTON ====================
const scrollToTopBtn = document.getElementById('scrollToTop');

if (scrollToTopBtn) {
    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.classList.add('visible');
        } else {
            scrollToTopBtn.classList.remove('visible');
        }
    });

    // Scroll to top when clicked
    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        trackEvent('Navigation', 'Click', 'Scroll to Top');
    });
}

// ==================== EXPORT FOR EXTERNAL USE ====================
window.Vermarkter = {
    calculate,
    trackEvent,
    initTheme,
    animateNumber
};

// ============================================
// KINETIC UI v3.1 — Electric Neon Glass (60FPS)
// Bold + saturated + GPU-optimized.
// ============================================

// === MATRIX RAIN — delegated to matrix.js (high-density engine) ===
// Capture base path at parse time so loading works from any subdirectory
var _kineticBase = (function () {
    var s = document.currentScript;
    return s ? s.src.replace(/[^/]*$/, '') : '../js/';
}());

function loadMatrixScript() {
    var tag = document.createElement('script');
    tag.src = _kineticBase + 'matrix.js';
    document.head.appendChild(tag);
}

function loadFxScript() {
    var tag = document.createElement('script');
    tag.src = _kineticBase + 'fx.js';
    document.head.appendChild(tag);
}

// === CRISP SCROLL REVEAL (GPU-composited) ===
function initKineticReveal() {
    const sections = document.querySelectorAll(
        'section, .services-section, .calculator-section, .testimonials-section'
    );

    sections.forEach(section => {
        const isHero = section.classList.contains('hero') ||
                       section.querySelector('.hero') ||
                       section.closest('.hero');
        const isHeader = section.tagName === 'HEADER';
        if (isHero || isHeader) return;

        section.classList.add('kinetic-hidden');
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                requestAnimationFrame(() => {
                    entry.target.classList.add('is-visible');
                });
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.06,
        rootMargin: '0px 0px -60px 0px'
    });

    sections.forEach(section => {
        if (section.classList.contains('kinetic-hidden')) {
            observer.observe(section);
        }
    });
}

// ==================== PAIN CARDS PEEK EFFECT (MOBILE) ====================
// On mobile: horizontal scroll so ~40px of next card peeks from the right
function initPainPeek() {
    if (window.innerWidth >= 768) return;

    var firstCard = document.querySelector('.pain-card');
    if (!firstCard) return;

    var wrap = firstCard.parentElement;
    if (!wrap) return;

    // Convert grid container to horizontal scroll row
    wrap.style.display        = 'flex';
    wrap.style.flexDirection  = 'row';
    wrap.style.overflowX      = 'scroll';
    wrap.style.overflowY      = 'visible';
    wrap.style.scrollSnapType = 'x mandatory';
    wrap.style.gap            = '1rem';
    wrap.style.paddingRight   = '50px';  // peek space
    wrap.style.WebkitOverflowScrolling = 'touch';
    // Remove conflicting inline grid styles
    wrap.style.gridTemplateColumns = '';

    var cards = wrap.querySelectorAll('.pain-card');
    cards.forEach(function (card) {
        card.style.minWidth       = 'calc(100vw - 90px)';
        card.style.maxWidth       = 'calc(100vw - 90px)';
        card.style.flex           = '0 0 auto';
        card.style.scrollSnapAlign = 'start';
        card.style.boxSizing      = 'border-box';
    });
}

// === INIT ===
document.addEventListener('DOMContentLoaded', function () {
    loadMatrixScript();
    loadFxScript();      // parallax + blur-reveal
    initKineticReveal(); // existing section-level reveal (kept for compat)
    initPainPeek();
    console.log('⚡ Kinetic UI v3.2 + Digital Rain v2.0 + fx.js');
});