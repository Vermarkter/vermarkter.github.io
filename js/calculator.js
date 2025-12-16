<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROI/ROAS Calculator - Vermarkter</title>
    <style>
        /* Assuming existing CSS variables from styles.css */
        :root {
            --bg-body: #0F172A;
            --bg-card: rgba(30, 41, 59, 0.7);
            --bg-secondary: #1E293B;
            --text-main: #FFFFFF;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --brand: #3B82F6;
            --brand-secondary: #8B5CF6;
            --accent: #10B981;
            --error: #EF4444;
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --glass-blur: blur(12px);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.2);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);
            --shadow-glow: 0 0 24px rgba(59, 130, 246, 0.4);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 20px;
            --spacing-sm: 1rem;
            --spacing-md: 2rem;
            --spacing-lg: 4rem;
            --transition-base: 0.3s ease;
        }

        /* Calculator Section Styles (BEM Naming) */
        .calculator-section {
            padding: var(--spacing-lg) 0;
            background: rgba(0, 0, 0, 0.2);
        }

        .calculator {
            background: var(--glass-bg);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-lg);
            max-width: 1200px;
            margin: 0 auto;
        }

        .calculator__header {
            text-align: center;
            margin-bottom: var(--spacing-md);
        }

        .calculator__title {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--brand), var(--brand-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .calculator__subtitle {
            color: var(--text-secondary);
            font-size: 1.125rem;
        }

        .calculator__grid {
            display: grid;
            grid-template-columns: 55fr 45fr;
            gap: var(--spacing-lg);
        }

        /* Left Column - Inputs */
        .calculator__inputs {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-md);
        }

        .calculator__input-group {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            transition: all var(--transition-base);
        }

        .calculator__input-group:hover {
            border-color: var(--brand);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
        }

        .calculator__input-group--active {
            border-color: var(--brand);
            box-shadow: var(--shadow-glow);
        }

        .calculator__label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            font-weight: 600;
            color: var(--text-main);
        }

        .calculator__label-text {
            font-size: 0.9375rem;
        }

        .calculator__label-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--brand);
            font-family: 'Courier New', monospace;
        }

        .calculator__controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .calculator__range {
            -webkit-appearance: none;
            flex: 1;
            height: 6px;
            background: var(--bg-secondary);
            border-radius: 10px;
            outline: none;
            transition: all var(--transition-base);
        }

        .calculator__range::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: linear-gradient(135deg, var(--brand), var(--brand-secondary));
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.5);
            transition: all var(--transition-base);
        }

        .calculator__range::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 0 16px rgba(59, 130, 246, 0.8);
        }

        .calculator__range::-moz-range-thumb {
            width: 20px;
            height: 20px;
            background: linear-gradient(135deg, var(--brand), var(--brand-secondary));
            border-radius: 50%;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.5);
        }

        .calculator__number-input {
            width: 120px;
            padding: 0.5rem 0.75rem;
            background: var(--bg-secondary);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-sm);
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 600;
            text-align: center;
            font-family: 'Courier New', monospace;
            transition: all var(--transition-base);
        }

        .calculator__number-input:focus {
            outline: none;
            border-color: var(--brand);
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
        }

        /* Right Column - Results */
        .calculator__results {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .calculator__result-card {
            background: var(--bg-secondary);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            transition: all var(--transition-base);
            position: relative;
            overflow: hidden;
        }

        .calculator__result-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, var(--brand), var(--brand-secondary));
            opacity: 0;
            transition: opacity var(--transition-base);
        }

        .calculator__result-card:hover::before {
            opacity: 1;
        }

        .calculator__result-card:hover {
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }

        .calculator__result-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .calculator__result-value {
            font-size: 2rem;
            font-weight: 900;
            font-family: 'Courier New', monospace;
            color: var(--text-main);
        }

        .calculator__result-value--primary {
            background: linear-gradient(135deg, var(--brand), var(--brand-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .calculator__result-value--success {
            color: var(--accent);
            text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        }

        .calculator__result-value--error {
            color: var(--error);
            text-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
        }

        .calculator__result-card--highlight {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 182, 212, 0.1));
            border: 2px solid var(--accent);
        }

        .calculator__result-card--negative {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
            border: 2px solid var(--error);
        }

        .calculator__result-description {
            margin-top: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        /* ROAS Indicator */
        .calculator__roas-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .calculator__roas-bar {
            flex: 1;
            height: 8px;
            background: var(--bg-secondary);
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }

        .calculator__roas-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), #06B6D4);
            border-radius: 10px;
            transition: width var(--transition-base);
        }

        .calculator__roas-fill--low {
            background: linear-gradient(90deg, var(--error), #DC2626);
        }

        .calculator__roas-text {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-secondary);
        }

        /* Info Tooltip */
        .calculator__info {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            background: rgba(59, 130, 246, 0.2);
            border-radius: 50%;
            font-size: 0.75rem;
            color: var(--brand);
            cursor: help;
            margin-left: 0.5rem;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .calculator__grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .calculator {
                padding: var(--spacing-md);
            }

            .calculator__title {
                font-size: 2rem;
            }

            .calculator__controls {
                flex-direction: column;
                align-items: stretch;
            }

            .calculator__number-input {
                width: 100%;
            }

            .calculator__result-value {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body style="background: #0F172A; padding: 2rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">

    <!-- Calculator Section -->
    <section class="calculator-section" id="calculator">
        <div class="calculator">
            <div class="calculator__header">
                <h2 class="calculator__title">ROI/ROAS Калькулятор</h2>
                <p class="calculator__subtitle">Професійний інструмент медіапланування для прогнозування рекламної кампанії</p>
            </div>

            <div class="calculator__grid">
                <!-- Left Column: Inputs -->
                <div class="calculator__inputs">
                    <!-- Budget -->
                    <div class="calculator__input-group" data-input="budget">
                        <div class="calculator__label">
                            <span class="calculator__label-text">
                                Рекламний бюджет
                                <span class="calculator__info" title="Скільки ви плануєте витратити на рекламу">ℹ</span>
                            </span>
                            <span class="calculator__label-value">$<span id="budgetValue">5000</span></span>
                        </div>
                        <div class="calculator__controls">
                            <input type="range" class="calculator__range" id="budgetSlider" 
                                   min="500" max="50000" step="100" value="5000">
                            <input type="number" class="calculator__number-input" id="budgetInput" 
                                   min="500" max="50000" step="100" value="5000">
                        </div>
                    </div>

                    <!-- CPC -->
                    <div class="calculator__input-group" data-input="cpc">
                        <div class="calculator__label">
                            <span class="calculator__label-text">
                                Середня ціна кліка (CPC)
                                <span class="calculator__info" title="Вартість одного кліку по оголошенню">ℹ</span>
                            </span>
                            <span class="calculator__label-value">$<span id="cpcValue">0.80</span></span>
                        </div>
                        <div class="calculator__controls">
                            <input type="range" class="calculator__range" id="cpcSlider" 
                                   min="0.1" max="5" step="0.1" value="0.8">
                            <input type="number" class="calculator__number-input" id="cpcInput" 
                                   min="0.1" max="5" step="0.1" value="0.8">
                        </div>
                    </div>

                    <!-- Conversion Rate -->
                    <div class="calculator__input-group" data-input="cr">
                        <div class="calculator__label">
                            <span class="calculator__label-text">
                                Конверсія сайту (CR)
                                <span class="calculator__info" title="% відвідувачів, які здійснюють цільову дію">ℹ</span>
                            </span>
                            <span class="calculator__label-value"><span id="crValue">3.0</span>%</span>
                        </div>
                        <div class="calculator__controls">
                            <input type="range" class="calculator__range" id="crSlider" 
                                   min="0.5" max="10" step="0.1" value="3">
                            <input type="number" class="calculator__number-input" id="crInput" 
                                   min="0.5" max="10" step="0.1" value="3">
                        </div>
                    </div>

                    <!-- AOV -->
                    <div class="calculator__input-group" data-input="aov">
                        <div class="calculator__label">
                            <span class="calculator__label-text">
                                Середній чек (AOV)
                                <span class="calculator__info" title="Середня вартість замовлення">ℹ</span>
                            </span>
                            <span class="calculator__label-value">$<span id="aovValue">150</span></span>
                        </div>
                        <div class="calculator__controls">
                            <input type="range" class="calculator__range" id="aovSlider" 
                                   min="10" max="500" step="5" value="150">
                            <input type="number" class="calculator__number-input" id="aovInput" 
                                   min="10" max="500" step="5" value="150">
                        </div>
                    </div>

                    <!-- Margin -->
                    <div class="calculator__input-group" data-input="margin">
                        <div class="calculator__label">
                            <span class="calculator__label-text">
                                Маржинальність
                                <span class="calculator__info" title="% прибутку з кожного продажу">ℹ</span>
                            </span>
                            <span class="calculator__label-value"><span id="marginValue">40</span>%</span>
                        </div>
                        <div class="calculator__controls">
                            <input type="range" class="calculator__range" id="marginSlider" 
                                   min="10" max="100" step="1" value="40">
                            <input type="number" class="calculator__number-input" id="marginInput" 
                                   min="10" max="100" step="1" value="40">
                        </div>
                    </div>
                </div>

                <!-- Right Column: Results -->
                <div class="calculator__results">
                    <!-- Clicks -->
                    <div class="calculator__result-card">
                        <div class="calculator__result-label">Трафік (кліки)</div>
                        <div class="calculator__result-value calculator__result-value--primary" id="resultClicks">6,250</div>
                        <div class="calculator__result-description">Очікувана кількість відвідувачів</div>
                    </div>

                    <!-- Leads -->
                    <div class="calculator__result-card">
                        <div class="calculator__result-label">Кількість продажів</div>
                        <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">188</div>
                        <div class="calculator__result-description">Конверсія з трафіку в продажі</div>
                    </div>

                    <!-- CPA -->
                    <div class="calculator__result-card">
                        <div class="calculator__result-label">Вартість ліда (CPA)</div>
                        <div class="calculator__result-value" id="resultCPA">$26.60</div>
                        <div class="calculator__result-description">Ціна залучення одного клієнта</div>
                    </div>

                    <!-- Revenue -->
                    <div class="calculator__result-card">
                        <div class="calculator__result-label">Виручка</div>
                        <div class="calculator__result-value calculator__result-value--primary" id="resultRevenue">$28,200</div>
                        <div class="calculator__result-description">Загальний дохід від продажів</div>
                    </div>

                    <!-- ROAS -->
                    <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                        <div class="calculator__result-label">ROAS (Return on Ad Spend)</div>
                        <div class="calculator__result-value calculator__result-value--success" id="resultROAS">564%</div>
                        <div class="calculator__roas-indicator">
                            <div class="calculator__roas-bar">
                                <div class="calculator__roas-fill" id="roasFill" style="width: 100%;"></div>
                            </div>
                            <span class="calculator__roas-text" id="roasStatus">Відмінно</span>
                        </div>
                    </div>

                    <!-- Net Profit -->
                    <div class="calculator__result-card calculator__result-card--highlight" id="profitCard">
                        <div class="calculator__result-label">Чистий прибуток</div>
                        <div class="calculator__result-value calculator__result-value--success" id="resultProfit">$6,280</div>
                        <div class="calculator__result-description">Прибуток після вирахування витрат</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script>
        // ROI/ROAS Calculator Logic
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
                // Attach event listeners to all inputs
                Object.keys(this.inputs).forEach(key => {
                    const config = this.inputs[key];
                    const slider = document.getElementById(config.slider);
                    const input = document.getElementById(config.input);
                    const inputGroup = document.querySelector(`[data-input="${key}"]`);

                    // Slider change
                    slider.addEventListener('input', (e) => {
                        const value = parseFloat(e.target.value);
                        input.value = value;
                        this.updateValue(key, value);
                        this.calculate();
                        this.highlightGroup(inputGroup);
                    });

                    // Input change
                    input.addEventListener('input', (e) => {
                        let value = parseFloat(e.target.value);
                        const min = parseFloat(slider.min);
                        const max = parseFloat(slider.max);
                        value = Math.max(min, Math.min(max, value || min));
                        slider.value = value;
                        this.updateValue(key, value);
                        this.calculate();
                    });

                    // Focus/blur effects
                    input.addEventListener('focus', () => this.highlightGroup(inputGroup));
                    input.addEventListener('blur', () => inputGroup.classList.remove('calculator__input-group--active'));
                });

                // Initial calculation
                this.calculate();
            }

            updateValue(key, value) {
                const config = this.inputs[key];
                const valueElement = document.getElementById(config.value);
                
                // Format based on type
                if (key === 'budget' || key === 'aov') {
                    valueElement.textContent = Math.round(value);
                } else if (key === 'cpc') {
                    valueElement.textContent = value.toFixed(2);
                } else {
                    valueElement.textContent = value.toFixed(1);
                }
            }

            highlightGroup(group) {
                // Remove active from all
                document.querySelectorAll('.calculator__input-group').forEach(g => {
                    g.classList.remove('calculator__input-group--active');
                });
                // Add to current
                group.classList.add('calculator__input-group--active');
            }

            calculate() {
                // Get values
                const budget = parseFloat(document.getElementById('budgetSlider').value);
                const cpc = parseFloat(document.getElementById('cpcSlider').value);
                const cr = parseFloat(document.getElementById('crSlider').value);
                const aov = parseFloat(document.getElementById('aovSlider').value);
                const margin = parseFloat(document.getElementById('marginSlider').value);

                // Calculations
                const clicks = Math.floor(budget / cpc);
                const leads = Math.floor(clicks * (cr / 100));
                const cpa = leads > 0 ? budget / leads : 0;
                const revenue = leads * aov;
                const roas = budget > 0 ? (revenue / budget) * 100 : 0;
                const netProfit = (revenue * (margin / 100)) - budget;

                // Update results
                this.updateResults({
                    clicks,
                    leads,
                    cpa,
                    revenue,
                    roas,
                    netProfit
                });
            }

            updateResults(results) {
                // Clicks
                document.getElementById('resultClicks').textContent = results.clicks.toLocaleString();

                // Leads
                document.getElementById('resultLeads').textContent = results.leads.toLocaleString();

                // CPA
                document.getElementById('resultCPA').textContent = '$' + results.cpa.toFixed(2);

                // Revenue
                document.getElementById('resultRevenue').textContent = '$' + results.revenue.toLocaleString();

                // ROAS
                const roasElement = document.getElementById('resultROAS');
                const roasCard = document.getElementById('roasCard');
                const roasFill = document.getElementById('roasFill');
                const roasStatus = document.getElementById('roasStatus');

                roasElement.textContent = results.roas.toFixed(0) + '%';

                // ROAS indicator logic
                const roasPercent = Math.min(results.roas / 5, 100); // Scale: 500% = 100%
                roasFill.style.width = roasPercent + '%';

                if (results.roas < 100) {
                    roasStatus.textContent = 'Збитки';
                    roasFill.classList.add('calculator__roas-fill--low');
                    roasCard.classList.remove('calculator__result-card--highlight');
                    roasCard.classList.add('calculator__result-card--negative');
                } else if (results.roas < 200) {
                    roasStatus.textContent = 'Низький';
                    roasFill.classList.remove('calculator__roas-fill--low');
                    roasCard.classList.remove('calculator__result-card--negative');
                    roasCard.classList.add('calculator__result-card--highlight');
                } else if (results.roas < 400) {
                    roasStatus.textContent = 'Добре';
                    roasFill.classList.remove('calculator__roas-fill--low');
                    roasCard.classList.add('calculator__result-card--highlight');
                } else {
                    roasStatus.textContent = 'Відмінно';
                    roasFill.classList.remove('calculator__roas-fill--low');
                    roasCard.classList.add('calculator__result-card--highlight');
                }

                // Net Profit
                const profitElement = document.getElementById('resultProfit');
                const profitCard = document.getElementById('profitCard');

                profitElement.textContent = (results.netProfit >= 0 ? '+' : '') + '$' + results.netProfit.toLocaleString();

                if (results.netProfit > 0) {
                    profitElement.className = 'calculator__result-value calculator__result-value--success';
                    profitCard.classList.remove('calculator__result-card--negative');
                    profitCard.classList.add('calculator__result-card--highlight');
                } else {
                    profitElement.className = 'calculator__result-value calculator__result-value--error';
                    profitCard.classList.remove('calculator__result-card--highlight');
                    profitCard.classList.add('calculator__result-card--negative');
                }
            }
        }

        // Initialize calculator
        document.addEventListener('DOMContentLoaded', () => {
            new ROICalculator();
        });
    </script>
</body>
</html>
