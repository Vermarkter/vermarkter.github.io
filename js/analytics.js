/*!
 * VERMARKTER — Google Analytics 4 Module
 * GA4 ID: G-Q707N1FHS1
 *
 * GDPR logic:
 *   - gtag.js завантажується одразу, але з consent 'denied' (за замовчуванням)
 *   - Після підтвердження cookie-банера consent.js викликає window.vermarkterAnalytics.enable()
 *   - До підтвердження жодні дані користувача НЕ передаються в Google
 */

(function () {
    'use strict';

    var GA_ID = 'G-Q707N1FHS1';

    /* ── 1. Завантажуємо gtag.js асинхронно ── */
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(script);

    /* ── 2. Ініціалізуємо dataLayer та gtag ── */
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;

    gtag('js', new Date());

    /* ── 3. За замовчуванням — consent DENIED (GDPR ЄС) ── */
    gtag('consent', 'default', {
        analytics_storage: 'denied',
        ad_storage:        'denied',
        wait_for_update:   500
    });

    /* ── 4. Конфігурація GA4 (анонімна до consent) ── */
    gtag('config', GA_ID, {
        anonymize_ip: true,
        send_page_view: false   /* Page view надішлемо лише після consent */
    });

    /* ── 5. Публічний API — викликається з consent.js ── */
    window.vermarkterAnalytics = {

        /**
         * Викликати після натискання "Прийняти" на cookie-банері.
         * Оновлює consent → granted, надсилає перший page_view.
         */
        enable: function () {
            gtag('consent', 'update', {
                analytics_storage: 'granted',
                ad_storage:        'granted'
            });
            gtag('event', 'page_view', {
                page_title:    document.title,
                page_location: window.location.href
            });
        },

        /**
         * Відправка довільної події.
         * Якщо consent ще не надано — gtag збереже подію та відправить після надання.
         */
        track: function (eventName, params) {
            gtag('event', eventName, params || {});
        }
    };

})();
