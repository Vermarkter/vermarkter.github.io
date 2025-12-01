document.addEventListener('DOMContentLoaded', () => {
    
    // 1. ТЕМА (Light/Dark)
    const themeBtn = document.getElementById('theme-btn');
    const body = document.body;
    
    // Перевірка збереженої теми
    if(localStorage.getItem('theme') === 'light') {
        body.setAttribute('data-theme', 'light');
    }

    themeBtn.addEventListener('click', () => {
        if(body.hasAttribute('data-theme')) {
            body.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            body.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    // 2. КАЛЬКУЛЯТОР
    const budgetInput = document.getElementById('budget');
    const budgetRange = document.getElementById('budget-range');
    const platformSelect = document.getElementById('platform');
    
    function calculate() {
        const budget = parseInt(budgetInput.value);
        const multiplier = parseFloat(platformSelect.value);
        
        // Проста формула для демо
        const clicks = Math.floor((budget / 0.6) * multiplier);
        const impressions = clicks * 28;
        const leads = Math.floor(clicks * 0.045); // 4.5% конверсія

        // Анімація чисел (можна просто текст)
        document.getElementById('res-clicks').innerText = clicks.toLocaleString();
        document.getElementById('res-impr').innerText = impressions.toLocaleString();
        document.getElementById('res-leads').innerText = leads.toLocaleString();
    }

    // Синхронізація
    budgetInput.addEventListener('input', (e) => {
        budgetRange.value = e.target.value;
        calculate();
    });
    budgetRange.addEventListener('input', (e) => {
        budgetInput.value = e.target.value;
        calculate();
    });
    platformSelect.addEventListener('change', calculate);
    
    // Запуск при старті
    calculate();


    // 3. АНІМАЦІЯ ЦИФР В HERO
    const counters = document.querySelectorAll('.stat-num');
    const speed = 200;
    
    const animateCounters = () => {
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const updateCount = () => {
                const count = +counter.innerText.replace(/\D/g,''); // Прибрати % або +
                const inc = target / speed;
                if(count < target) {
                    counter.innerText = Math.ceil(count + inc) + (counter.innerText.includes('%') ? '%' : '+');
                    setTimeout(updateCount, 20);
                } else {
                    counter.innerText = target + (counter.getAttribute('data-suffix') || '');
                }
            }
            updateCount();
        });
    }
    // Запуск через 1с
    setTimeout(animateCounters, 1000);


    // 4. МОБІЛЬНЕ МЕНЮ
    const mobileBtn = document.querySelector('.mobile-toggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    mobileBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        const icon = mobileBtn.querySelector('i');
        if(mobileMenu.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.add('fa-bars');
            icon.classList.remove('fa-times');
        }
    });

});
