#!/usr/bin/env python3
"""
Embed calculators directly into ALL google-ads.html service pages.
Insert between Bundle and FAQ sections.
"""

import re
from pathlib import Path

# Calculator HTML for each language
CALCULATORS = {
    'ua': '''
    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">ROI Калькулятор 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Розрахуйте рентабельність вашої рекламної кампанії
                    </p>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Це реальний інструмент медіапланування.</strong><br>
                            Ми використовуємо ті самі формули, що й великі агенції.
                        </p>
                    </div>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Результат є прогнозом, а не обіцянкою.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <div class="calculator__inputs">
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Рекламна платформа:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google" selected>Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Ваша ніша:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Власні значення --</option>
                                <option value="ecommerce">E-Commerce / Товарка</option>
                                <option value="beauty">Beauty: Салони краси</option>
                                <option value="construction">Ремонт та Будівництво</option>
                                <option value="auto" selected>Автобізнес / СТО / Детейлінг</option>
                                <option value="realestate">Нерухомість</option>
                                <option value="expert">Послуги експертів / B2B</option>
                            </select>
                        </div>

                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Бюджет</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

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

                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Конверсія (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Сер. чек (€)</label>
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
                            <div class="calculator__result-label">ROAS</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Прибуток</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Результат є прогнозом, а не обіцянкою. Маркетинг починається з чесних цифр.
                </p>
            </div>
        </div>
    </section>
''',

    'en': '''
    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">ROI Calculator 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Calculate the profitability of your ad campaign
                    </p>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>This is a real media planning tool.</strong><br>
                            We use the same formulas as big agencies.
                        </p>
                    </div>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ The result is a forecast, not a promise.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <div class="calculator__inputs">
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Ad Platform:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google" selected>Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

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

                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Budget</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>CPC (Cost Per Click)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

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

                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Avg. Order (€)</label>
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
                            <div class="calculator__result-label">ROAS</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Profit</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ The result is a forecast, not a promise. Marketing starts with honest numbers.
                </p>
            </div>
        </div>
    </section>
''',

    'pl': '''
    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Kalkulator ROI 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Oblicz rentowność swojej kampanii reklamowej
                    </p>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>To prawdziwe narzędzie do planowania mediów.</strong><br>
                            Używamy tych samych formuł, co duże agencje.
                        </p>
                    </div>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Wynik jest prognozą, nie obietnicą.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <div class="calculator__inputs">
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Platforma reklamowa:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google" selected>Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

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

                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Budżet</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>CPC (Koszt kliknięcia)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Konwersja (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Śr. zamówienie (€)</label>
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
                            <div class="calculator__result-label">ROAS</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Zysk</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Wynik jest prognozą, nie obietnicą. Marketing zaczyna się od uczciwych liczb.
                </p>
            </div>
        </div>
    </section>
''',

    'ru': '''
    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">ROI Калькулятор 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Рассчитайте рентабельность вашей рекламной кампании
                    </p>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Это реальный инструмент медиапланирования.</strong><br>
                            Мы используем те же формулы, что и крупные агентства.
                        </p>
                    </div>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Результат является прогнозом, а не обещанием.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <div class="calculator__inputs">
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Рекламная платформа:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google" selected>Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

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

                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Бюджет</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>CPC (Цена клика)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Конверсия (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Ср. чек (€)</label>
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
                            <div class="calculator__result-label">ROAS</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Прибыль</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Результат является прогнозом, а не обещанием. Маркетинг начинается с честных цифр.
                </p>
            </div>
        </div>
    </section>
''',

    'tr': '''
    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">ROI Hesaplayici 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Reklam kampanyanizin karliligini hesaplayin
                    </p>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Bu gercek bir medya planlama aracidir.</strong><br>
                            Buyuk ajanslarla ayni formulleri kullaniyoruz.
                        </p>
                    </div>

                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Sonuc bir tahmindir, soz degil.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <div class="calculator__inputs">
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Reklam Platformu:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google" selected>Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Nisiniz:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Ozel Degerler --</option>
                                <option value="ecommerce">E-Ticaret / Urunler</option>
                                <option value="beauty">Guzellik: Salonlar, Kozmetoloji</option>
                                <option value="construction">Tadilat ve Insaat</option>
                                <option value="auto" selected>Oto Isletmesi / Servis / Detailing</option>
                                <option value="realestate">Gayrimenkul</option>
                                <option value="expert">Uzman Hizmetleri / B2B</option>
                            </select>
                        </div>

                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Butce</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>TBM (Tiklama Maliyeti)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Donusum Orani (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Ort. Siparis (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Kar Marji (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Trafik (Tiklamalar)</div>
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
                            <div class="calculator__result-label">ROAS</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Kar</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Sonuc bir tahmindir, soz degil. Pazarlama durust rakamlarla baslar.
                </p>
            </div>
        </div>
    </section>
'''
}


def embed_calculator(file_path, lang):
    """Embed calculator into a service page between Bundle and FAQ"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if already has embedded calculator
        if 'id="calculator-section"' in content and 'class="calculator__grid"' in content:
            print(f"SKIP: {file_path} (already has embedded calculator)")
            return False

        # Find the FAQ section to insert before it
        faq_match = re.search(r'(\s*<!-- FAQ SECTION -->\s*<section)', content, re.IGNORECASE)

        if not faq_match:
            # Try alternate pattern
            faq_match = re.search(r'(\s*<section[^>]*id=["\']faq["\'])', content, re.IGNORECASE)

        if not faq_match:
            print(f"WARNING: {file_path} - FAQ section not found")
            return False

        # Get calculator for this language
        calculator = CALCULATORS.get(lang, CALCULATORS['en'])

        # Insert calculator before FAQ
        insert_pos = faq_match.start()
        new_content = content[:insert_pos] + calculator + content[insert_pos:]

        # Remove old redirect links to index.html#calculator-section
        new_content = new_content.replace('href="index.html#calculator-section"', 'href="#calculator-section"')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"EMBEDDED: {file_path}")
        return True

    except Exception as e:
        print(f"ERROR: {file_path}: {e}")
        return False


def main():
    """Embed calculators into all google-ads.html service pages"""
    languages = ['ua', 'en', 'pl', 'ru', 'tr']  # de already has it

    print("="*60)
    print("EMBEDDING CALCULATORS INTO GOOGLE-ADS SERVICE PAGES")
    print("="*60)

    modified = 0

    for lang in languages:
        file_path = Path(f"{lang}/google-ads.html")
        if file_path.exists():
            if embed_calculator(file_path, lang):
                modified += 1
        else:
            print(f"NOT FOUND: {file_path}")

    print(f"\n{'='*60}")
    print(f"Embedded calculators into {modified} google-ads.html files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
