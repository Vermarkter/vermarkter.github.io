// База даних середніх показників по нішах (Європа)
const NICHES = {
    'custom': { cpc: 0.8, cr: 3.0, aov: 150, margin: 40, label: "Свій варіант" },
    'ecommerce': { cpc: 0.45, cr: 2.8, aov: 65, margin: 30, label: "E-commerce (Товари)" },
    'services': { cpc: 1.20, cr: 4.5, aov: 200, margin: 60, label: "Послуги (Ремонт, Бьюті)" },
    'realestate': { cpc: 3.50, cr: 0.8, aov: 5000, margin: 15, label: "Нерухомість" },
    'b2b': { cpc: 2.50, cr: 1.5, aov: 1500, margin: 40, label: "B2B / Опт" },
    'infobiz': { cpc: 0.90, cr: 3.5, aov: 300, margin: 80, label: "Інфобізнес / Курси" }
};

class ROICalculator {
    constructor() {
        this.inputs = {
            budget: { slider: 'budgetSlider', input: 'budgetInput', value: 'budgetValue' },
            cpc: { slider: 'cpcSlider', input: 'cpcInput', value: 'cpcValue' },
            cr: { slider: 'crSlider', input: 'crInput', value: 'crValue' },
            aov: { slider: 'aovSlider', input: 'aovInput', value: 'aovValue' },
            margin: { slider: 'marginSlider', input: 'marginInput', value: 'marginValue' }
        };
        this.init();
    }

    init() {
        // 1. Обробка вибору Ніші
        const nicheSelector = document.getElementById('nicheSelector');
        if (nicheSelector) {
            nicheSelector.addEventListener('change', (e) => {
                this.applyNichePreset(e.target.value);
            });
        }

        // 2. Обробка слайдерів та інпутів
        Object.keys(this.inputs).forEach(key => {
            const config = this.inputs[key];
            const slider = document.getElementById(config.slider);
            const input = document.getElementById(config.input);
            const inputGroup = document.querySelector(`[data-input="${key}"]`);

            if (!slider || !input) return;

            // Slider change
            slider.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                input.value = value;
                this.updateValue(key, value);
                this.calculate();
                if(inputGroup) this.highlightGroup(inputGroup);
                // Якщо користувач рухає повзунки, скидаємо селект на "Свій варіант"
                if (key !== 'budget' && nicheSelector) nicheSelector.value = 'custom';
            });

            // Input change
            input.addEventListener('input', (e) => {
                let value = parseFloat(e.target.value);
                // Валідація меж
                const min = parseFloat(slider.min);
                const max = parseFloat(slider.max);
                if (!isNaN(value)) {
                    // Дозволяємо вводити, але обмежуємо для слайдера
                    slider.value = Math.max(min, Math.min(max, value));
                    this.updateValue(key, value);
                    this.calculate();
                }
            });
        });

        // Перший розрахунок
        this.calculate();
    }

    applyNichePreset(nicheKey) {
        const data = NICHES[nicheKey];
        if (!data) return;

        // Оновлюємо значення (окрім бюджету, бюджет залишаємо як є)
        this.updateInputPair('cpc', data.cpc);
        this.updateInputPair('cr', data.cr);
        this.updateInputPair('aov', data.aov);
        this.updateInputPair('margin', data.margin);
        
        this.calculate();
    }

    updateInputPair(key, value) {
        const config = this.inputs[key];
        const slider = document.getElementById(config.slider);
        const input = document.getElementById(config.input);
        
        if (slider && input) {
            slider.value = value;
            input.value = value;
            this.updateValue(key, value);
        }
    }

    updateValue(key, value) {
        const config = this.inputs[key];
        const valueElement = document.getElementById(config.value);
        if (!valueElement) return;
        
        if (key === 'budget' || key === 'aov') {
            valueElement.textContent = Math.round(value).toLocaleString();
        } else if (key === 'cpc') {
            valueElement.textContent = value.toFixed(2);
        } else {
            valueElement.textContent = value.toFixed(1);
        }
    }

    highlightGroup(group) {
        document.querySelectorAll('.calculator__input-group').forEach(g => {
            g.classList.remove('calculator__input-group--active');
        });
        group.classList.add('calculator__input-group--active');
    }

    calculate() {
        const getVal = (id) => parseFloat(document.getElementById(id)?.value || 0);

        const budget = getVal('budgetInput');
        const cpc = getVal('cpcInput');
        const cr = getVal('crInput');
        const aov = getVal('aovInput');
        const margin = getVal('marginInput');

        if (cpc === 0) return;

        const clicks = Math.floor(budget / cpc);
        const leads = Math.floor(clicks * (cr / 100));
        const cpa = leads > 0 ? budget / leads : 0;
        const revenue = leads * aov;
        const roas = budget > 0 ? (revenue / budget) * 100 : 0;
        const netProfit = (revenue * (margin / 100)) - budget;

        this.renderResults({ clicks, leads, cpa, revenue, roas, netProfit });
    }

    renderResults(res) {
        const setTxt = (id, txt) => {
            const el = document.getElementById(id);
            if(el) el.textContent = txt;
        };

        setTxt('resultClicks', res.clicks.toLocaleString());
        setTxt('resultLeads', res.leads.toLocaleString());
        setTxt('resultCPA', '€' + res.cpa.toFixed(2));
        setTxt('resultRevenue', '€' + res.revenue.toLocaleString());
        setTxt('resultROAS', res.roas.toFixed(0) + '%');

        // ROAS Visuals
        const roasFill = document.getElementById('roasFill');
        const roasStatus = document.getElementById('roasStatus');
        const roasCard = document.getElementById('roasCard');

        if(roasFill && roasStatus && roasCard) {
            const roasPercent = Math.min(res.roas / 5, 100); 
            roasFill.style.width = roasPercent + '%';

            roasCard.className = 'calculator__result-card'; // reset
            if (res.roas < 100) {
                roasStatus.textContent = 'Збитки';
                roasFill.style.background = '#EF4444';
                roasCard.classList.add('calculator__result-card--negative');
            } else if (res.roas < 300) {
                roasStatus.textContent = 'Нормально';
                roasFill.style.background = '#F59E0B';
            } else {
                roasStatus.textContent = 'Відмінно';
                roasFill.style.background = '#10B981';
                roasCard.classList.add('calculator__result-card--highlight');
            }
        }

        // Net Profit Visuals
        const profitEl = document.getElementById('resultProfit');
        if(profitEl) {
            profitEl.textContent = (res.netProfit >= 0 ? '+' : '') + '€' + res.netProfit.toLocaleString();
            profitEl.style.color = res.netProfit > 0 ? '#10B981' : '#EF4444';
        }
    }
}

// Ініціалізація
// Ми додаємо перевірку, чи існує елемент калькулятора, щоб не було помилок на інших сторінках
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('calculator')) {
        new ROICalculator();
        console.log("Calculator initialized"); // Це для перевірки
    }
});
