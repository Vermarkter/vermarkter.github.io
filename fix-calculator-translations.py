#!/usr/bin/env python3
"""
Fix calculator translations on service pages.
Copy correct calculator from index.html to service pages for each language.
"""

import re
from pathlib import Path

# Calculator content for each language (extracted from index.html)
CALCULATORS = {
    'ua': '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Медіаплан 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Розрахуйте рентабельність вашої рекламної кампанії
                    </p>

                    <!-- БЛОК ДОВІРИ -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Це реальний інструмент медіапланування.</strong><br>
                            Ми використовуємо ті самі формули, що й великі агенції. Прозоро, чесно, без прихованих витрат.
                        </p>
                    </div>

                    <!-- БЛОК ПОПЕРЕДЖЕННЯ -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Результат є прогнозом, а не обіцянкою. Маркетинг починається з чесних цифр.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Рекламна платформа:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Ваша ніша:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Власні значення --</option>
                                <option value="ecommerce">E-Commerce / Товарка</option>
                                <option value="beauty">Beauty: Салони краси, Косметологія</option>
                                <option value="construction">Ремонт та Будівництво</option>
                                <option value="auto" selected>Автобізнес / СТО / Детейлінг</option>
                                <option value="realestate">Нерухомість</option>
                                <option value="expert">Послуги експертів / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Рекламний бюджет</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Ціна кліка (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Конверсія сайту (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Сер. вартість замовлення (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Маржа (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Трафік (Кліки)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Ліди (Заявки)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Вартість ліда)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Повернення вкладень)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Чистий прибуток</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Результат є прогнозом, а не обіцянкою. Маркетинг починається з чесних цифр.
                </p>
            </div>
        </div>
    </section>''',

    'de': '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Mediaplan 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Berechnen Sie die Rentabilität Ihrer Werbekampagne
                    </p>

                    <!-- TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Dies ist ein echtes Mediaplanungs-Tool.</strong><br>
                            Wir verwenden dieselben Formeln wie große Agenturen. Transparent, ehrlich, ohne versteckte Kosten.
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Werbeplattform:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Ihre Nische:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Eigene Werte --</option>
                                <option value="ecommerce">E-Commerce / Waren</option>
                                <option value="beauty">Beauty: Salons, Kosmetologie</option>
                                <option value="construction">Renovierung & Bau</option>
                                <option value="auto" selected>Autogeschäft / Werkstatt / Detailing</option>
                                <option value="realestate">Immobilien</option>
                                <option value="expert">Expertenleistungen / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Werbebudget</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Klickpreis (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Conversion Rate (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Ø Bestellwert (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Marge (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Traffic (Klicks)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Leads (Anfragen)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Kosten pro Lead)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Return on Ad Spend)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Nettogewinn</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.
                </p>
            </div>
        </div>
    </section>''',

    'en': '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Media Plan 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Calculate the profitability of your ad campaign
                    </p>

                    <!-- TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>This is a real media planning tool.</strong><br>
                            We use the same formulas as big agencies. Transparent, honest, no hidden costs.
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ The result is a forecast, not a promise. Marketing starts with honest numbers.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Ad Platform:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Your Niche:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Custom Values --</option>
                                <option value="ecommerce">E-Commerce / Products</option>
                                <option value="beauty">Beauty: Salons, Cosmetology</option>
                                <option value="construction">Renovation & Construction</option>
                                <option value="auto" selected>Auto Business / Service / Detailing</option>
                                <option value="realestate">Real Estate</option>
                                <option value="expert">Expert Services / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Ad Budget</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Cost Per Click (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Conversion Rate (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Avg. Order Value (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Margin (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Traffic (Clicks)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Leads (Inquiries)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Cost per Lead)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Return on Ad Spend)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Net Profit</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ The result is a forecast, not a promise. Marketing starts with honest numbers.
                </p>
            </div>
        </div>
    </section>''',

    'pl': '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Mediaplan 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Oblicz rentowność swojej kampanii reklamowej
                    </p>

                    <!-- TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>To prawdziwe narzędzie do planowania mediów.</strong><br>
                            Używamy tych samych formuł, co duże agencje. Przejrzyście, uczciwie, bez ukrytych kosztów.
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Wynik jest prognozą, nie obietnicą. Marketing zaczyna się od uczciwych liczb.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Platforma reklamowa:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Twoja nisza:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Własne wartości --</option>
                                <option value="ecommerce">E-Commerce / Produkty</option>
                                <option value="beauty">Beauty: Salony, Kosmetologia</option>
                                <option value="construction">Remonty i Budownictwo</option>
                                <option value="auto" selected>Auto Biznes / Serwis / Detailing</option>
                                <option value="realestate">Nieruchomości</option>
                                <option value="expert">Usługi eksperckie / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Budżet reklamowy</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Koszt kliknięcia (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Konwersja strony (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Śr. wartość zamówienia (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Marża (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Ruch (Kliknięcia)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Leady (Zapytania)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Koszt leada)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Zwrot z reklamy)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Zysk netto</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Wynik jest prognozą, nie obietnicą. Marketing zaczyna się od uczciwych liczb.
                </p>
            </div>
        </div>
    </section>''',

    'ru': '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Медиаплан 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Рассчитайте рентабельность вашей рекламной кампании
                    </p>

                    <!-- TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Это реальный инструмент медиапланирования.</strong><br>
                            Мы используем те же формулы, что и крупные агентства. Прозрачно, честно, без скрытых расходов.
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Результат является прогнозом, а не обещанием. Маркетинг начинается с честных цифр.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Рекламная платформа:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Ваша ниша:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Свои значения --</option>
                                <option value="ecommerce">E-Commerce / Товарка</option>
                                <option value="beauty">Beauty: Салоны, Косметология</option>
                                <option value="construction">Ремонт и Строительство</option>
                                <option value="auto" selected>Автобизнес / СТО / Детейлинг</option>
                                <option value="realestate">Недвижимость</option>
                                <option value="expert">Услуги экспертов / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Рекламный бюджет</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Цена клика (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Конверсия сайта (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Ср. стоимость заказа (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Маржа (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Трафик (Клики)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Лиды (Заявки)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Стоимость лида)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Возврат вложений)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Чистая прибыль</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Результат является прогнозом, а не обещанием. Маркетинг начинается с честных цифр.
                </p>
            </div>
        </div>
    </section>''',

    'tr': '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Medya Planı 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Reklam kampanyanızın karlılığını hesaplayın
                    </p>

                    <!-- TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Bu gerçek bir medya planlama aracıdır.</strong><br>
                            Büyük ajanslarla aynı formülleri kullanıyoruz. Şeffaf, dürüst, gizli maliyet yok.
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Sonuç bir tahmindir, söz değil. Pazarlama dürüst rakamlarla başlar.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Reklam Platformu:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Nişiniz:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Özel Değerler --</option>
                                <option value="ecommerce">E-Ticaret / Ürünler</option>
                                <option value="beauty">Güzellik: Salonlar, Kozmetoloji</option>
                                <option value="construction">Tadilat ve İnşaat</option>
                                <option value="auto" selected>Oto İşletmesi / Servis / Detailing</option>
                                <option value="realestate">Gayrimenkul</option>
                                <option value="expert">Uzman Hizmetleri / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Reklam Bütçesi</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Tıklama Maliyeti (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Dönüşüm Oranı (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Ort. Sipariş Değeri (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Kar Marjı (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Trafik (Tıklamalar)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Lead (Talepler)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Lead Maliyeti)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Reklam Getirisi)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Net Kar</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Sonuç bir tahmindir, söz değil. Pazarlama dürüst rakamlarla başlar.
                </p>
            </div>
        </div>
    </section>'''
}


def replace_calculator(content, lang):
    """Replace calculator section with the correct language version"""
    # Pattern to match calculator section
    pattern = r'<!-- CALCULATOR SECTION -->.*?</section>\s*(?=\n\s*<!--|\n\s*<section)'

    if lang in CALCULATORS:
        new_content = re.sub(pattern, CALCULATORS[lang], content, flags=re.DOTALL)
        return new_content
    return content


def process_service_pages():
    """Process service pages for each language"""
    languages = ['ua', 'de', 'en', 'pl', 'ru', 'tr']
    services = ['google-ads.html', 'meta-ads.html', 'tiktok-ads.html']

    print("="*60)
    print("FIXING CALCULATOR TRANSLATIONS ON SERVICE PAGES")
    print("="*60)

    modified = 0

    for lang in languages:
        for service in services:
            file_path = Path(f"{lang}/{service}")

            if not file_path.exists():
                print(f"SKIP: {file_path} (not found)")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if has calculator
                if 'id="calculator-section"' not in content:
                    print(f"SKIP: {file_path} (no calculator)")
                    continue

                new_content = replace_calculator(content, lang)

                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"FIXED: {file_path}")
                    modified += 1
                else:
                    print(f"OK: {file_path} (already correct)")

            except Exception as e:
                print(f"ERROR: {file_path}: {e}")

    print(f"\n{'='*60}")
    print(f"Modified: {modified} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    process_service_pages()
