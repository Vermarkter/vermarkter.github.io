// Vermarkter - Global JavaScript

// Language Switcher
function changeLang(lang) {
    const routes = {
        'UA': '/ua',
        'DE': '/de',
        'EN': '/en',
        'PL': '/pl',
        'RU': '/ru',
        'TR': '/tr'
    };
    
    if (routes[lang]) {
        const baseUrl = 'https://vermarkter.github.io';
        // Check if we're on a service page
        const currentPath = window.location.pathname;
        const serviceMatch = currentPath.match(/\/services\/([^\/]+)/);
        
        if (serviceMatch) {
            // Redirect to service page in new language
            window.location.href = `${baseUrl}${routes[lang]}/services/${serviceMatch[1]}`;
        } else {
            // Redirect to homepage in new language
            window.location.href = baseUrl + routes[lang];
        }
    }
}

// Sync all language selectors
function syncLangSelectors() {
    const selectors = document.querySelectorAll('.lang-selector');
    selectors.forEach(selector => {
        selector.addEventListener('change', function() {
            selectors.forEach(s => s.value = this.value);
        });
    });
}

// Mobile Menu Toggle
function toggleMobileMenu() {
    const menu = document.querySelector('.mobile-menu');
    const btn = document.querySelector('.mobile-menu-btn');
    
    if (menu) {
        menu.classList.toggle('active');
        document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
    }
}

// Close mobile menu when clicking links
function closeMobileMenu() {
    const menu = document.querySelector('.mobile-menu');
    if (menu) {
        menu.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Theme Toggle
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Form Submission
function submitForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Here you would normally send data to backend
    // For now, just show success message
    alert('Дякуємо! Ми зв\'яжемося з вами протягом 24 годин.');
    
    // Reset form
    form.reset();
    
    return false;
}

// Calculator Logic
function calculate() {
    const budget = parseFloat(document.getElementById('budget')?.value || 0);
    const avgCheck = parseFloat(document.getElementById('avgCheck')?.value || 0);
    const platform = document.getElementById('platform')?.value || 'google';
    
    if (!budget || budget <= 0) {
        alert('Будь ласка, введіть коректний бюджет');
        return;
    }
    
    let cpc, ctr;
    if (platform === 'google') {
        cpc = 0.5;
        ctr = 3.5;
    } else if (platform === 'meta') {
        cpc = 0.3;
        ctr = 2.5;
    } else {
        cpc = 0.2;
        ctr = 4.5;
    }
    
    const clicks = Math.floor(budget / cpc);
    const reach = Math.floor(clicks / (ctr / 100));
    const conversionRate = 5;
    const leads = Math.floor(clicks * (conversionRate / 100));
    const revenue = avgCheck ? Math.floor(leads * avgCheck) : 0;
    
    // Update results
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        document.getElementById('reach').textContent = reach.toLocaleString();
        document.getElementById('clicks').textContent = clicks.toLocaleString();
        document.getElementById('ctr').textContent = ctr.toFixed(1);
        document.getElementById('cpc').textContent = cpc.toFixed(2);
        document.getElementById('leads').textContent = leads;
        if (document.getElementById('revenue')) {
            document.getElementById('revenue').textContent = revenue.toLocaleString();
        }
        
        resultsDiv.style.display = 'grid';
    }
}

// Stats Animation
function animateValue(element, start, end, duration) {
    if (!element) return;
    
    const range = end - start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = current;
        if (current === end) clearInterval(timer);
    }, stepTime);
}

function initStatsAnimation() {
    const stats = document.querySelectorAll('.stat strong, .stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const targetValue = parseInt(entry.target.textContent);
                if (!isNaN(targetValue)) {
                    animateValue(entry.target, 0, targetValue, 2000);
                    entry.target.dataset.animated = 'true';
                }
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
}

// FAQ Toggle Animation
function initFAQ() {
    document.querySelectorAll('details').forEach(detail => {
        detail.addEventListener('toggle', function() {
            const icon = this.querySelector('summary span');
            if (icon) {
                icon.textContent = this.open ? '−' : '+';
            }
        });
    });
}

// Smooth Scroll
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                closeMobileMenu();
            }
        });
    });
}

// Intersection Observer for Animations
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .service-card, .stat').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Close mobile menu when clicking outside
function initClickOutside() {
    document.addEventListener('click', function(e) {
        const menu = document.querySelector('.mobile-menu');
        const toggle = document.querySelector('.mobile-menu-btn');
        
        if (menu && menu.classList.contains('active') && 
            !menu.contains(e.target) && 
            !toggle.contains(e.target)) {
            closeMobileMenu();
        }
    });
}

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    
    // Update theme toggle icon
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
    
    // Initialize features
    syncLangSelectors();
    initStatsAnimation();
    initFAQ();
    initSmoothScroll();
    initScrollAnimations();
    initClickOutside();
    
    // Attach mobile menu toggle to buttons
    const mobileToggle = document.querySelector('.mobile-menu-btn');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Attach theme toggle
    const themeBtn = document.querySelector('.theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
    
    // Attach to mobile links
    const mobileLinks = document.querySelectorAll('.mobile-links a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    // Calculator button
    const calcBtn = document.querySelector('[onclick*="calculate"]');
    if (calcBtn) {
        calcBtn.onclick = calculate;
    }
    
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', submitForm);
    });
});

// Export functions for inline use
window.changeLang = changeLang;
window.toggleMobileMenu = toggleMobileMenu;
window.closeMobileMenu = closeMobileMenu;
window.submitForm = submitForm;
window.calculate = calculate;
window.toggleTheme = toggleTheme;
