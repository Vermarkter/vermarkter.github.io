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

if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
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
const themeToggle = document.getElementById('themeToggle');

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
    if (themeToggle) {
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

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
            window.location.href = 'https://vermarkter.github.io' + routes[lang];
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
const chatbotButton = document.getElementById('chatbotButton');

if (chatbotButton) {
    chatbotButton.addEventListener('click', () => {
        // Open Telegram chat or custom chatbot
        window.open('https://t.me/vermarkter', '_blank');
    });
}

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
function initForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Show success message
            alert('Дякуємо! Ми зв\'яжемося з вами найближчим часом.');
            
            // Reset form
            form.reset();
            
            // In production, send to backend
            console.log('Form submitted:', data);
        });
    });
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

if (chatbotButton) {
    chatbotButton.addEventListener('click', () => {
        trackEvent('Engagement', 'Click', 'Chatbot Opened');
    });
}

// ==================== EXPORT FOR EXTERNAL USE ====================
window.Vermarkter = {
    calculate,
    trackEvent,
    initTheme,
    animateNumber
};