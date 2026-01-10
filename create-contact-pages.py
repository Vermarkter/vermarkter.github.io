#!/usr/bin/env python3
"""
Create contact.html for all languages based on DE version
"""

import re
from pathlib import Path
from shutil import copy2

# Translations for contact page
TRANSLATIONS = {
    'de': {
        'title': 'Kontakt — Vermarkter',
        'description': 'Kontaktieren Sie Vermarkter für Performance Marketing. Persönliche Beratung ohne Sales-Druck. Antwort innerhalb von 2 Stunden.',
        'keywords': 'Kontakt Vermarkter, Marketing Beratung, Google Ads Agentur Kontakt',
        'og_description': 'Persönliche Beratung ohne Sales-Druck',
        'nav_services': 'Leistungen',
        'nav_testimonials': 'Bewertungen',
        'nav_faq': 'FAQ',
        'nav_contact': 'Kontakt',
        'page_title': 'Kontakt',
        'page_subtitle': 'Kostenlose Beratung ohne Sales-Druck',
        'email_label': 'E-Mail',
        'telegram_btn': 'Nachricht auf Telegram',
        'whatsapp_btn': 'Chat auf WhatsApp',
        'response_time': 'Antwort innerhalb von 2 Stunden',
        'response_desc': 'Wir antworten schnell und konkret',
        'contact_form_title': 'Oder schreiben Sie uns',
        'form_name': 'Name',
        'form_email': 'Email',
        'form_phone': 'Telefon (optional)',
        'form_message': 'Nachricht',
        'form_submit': 'Nachricht senden',
        'footer_legal': 'Rechtliches',
        'footer_privacy': 'Datenschutz',
        'footer_imprint': 'Impressum',
        'footer_contact': 'Kontakt',
        'footer_copyright': '© 2025 Vermarkter. Alle Rechte vorbehalten.'
    },
    'en': {
        'title': 'Contact — Vermarkter',
        'description': 'Contact Vermarkter for Performance Marketing. Personal consultation without sales pressure. Response within 2 hours.',
        'keywords': 'Contact Vermarkter, Marketing Consultation, Google Ads Agency Contact',
        'og_description': 'Personal consultation without sales pressure',
        'nav_services': 'Services',
        'nav_testimonials': 'Reviews',
        'nav_faq': 'FAQ',
        'nav_contact': 'Contact',
        'page_title': 'Contact',
        'page_subtitle': 'Free consultation without sales pressure',
        'email_label': 'Email',
        'telegram_btn': 'Message on Telegram',
        'whatsapp_btn': 'Chat on WhatsApp',
        'response_time': 'Response within 2 hours',
        'response_desc': 'We respond quickly and concretely',
        'contact_form_title': 'Or write to us',
        'form_name': 'Name',
        'form_email': 'Email',
        'form_phone': 'Phone (optional)',
        'form_message': 'Message',
        'form_submit': 'Send message',
        'footer_legal': 'Legal',
        'footer_privacy': 'Privacy',
        'footer_imprint': 'Imprint',
        'footer_contact': 'Contact',
        'footer_copyright': '© 2025 Vermarkter. All rights reserved.'
    },
    'pl': {
        'title': 'Kontakt — Vermarkter',
        'description': 'Skontaktuj się z Vermarkter w sprawie Performance Marketing. Osobista konsultacja bez presji sprzedażowej. Odpowiedź w ciągu 2 godzin.',
        'keywords': 'Kontakt Vermarkter, Konsultacja marketingowa, Kontakt agencja Google Ads',
        'og_description': 'Osobista konsultacja bez presji sprzedażowej',
        'nav_services': 'Usługi',
        'nav_testimonials': 'Opinie',
        'nav_faq': 'FAQ',
        'nav_contact': 'Kontakt',
        'page_title': 'Kontakt',
        'page_subtitle': 'Bezpłatna konsultacja bez presji sprzedażowej',
        'email_label': 'E-mail',
        'telegram_btn': 'Wiadomość na Telegram',
        'whatsapp_btn': 'Czat na WhatsApp',
        'response_time': 'Odpowiedź w ciągu 2 godzin',
        'response_desc': 'Odpowiadamy szybko i konkretnie',
        'contact_form_title': 'Lub napisz do nas',
        'form_name': 'Imię',
        'form_email': 'Email',
        'form_phone': 'Telefon (opcjonalnie)',
        'form_message': 'Wiadomość',
        'form_submit': 'Wyślij wiadomość',
        'footer_legal': 'Prawne',
        'footer_privacy': 'Prywatność',
        'footer_imprint': 'Impressum',
        'footer_contact': 'Kontakt',
        'footer_copyright': '© 2025 Vermarkter. Wszelkie prawa zastrzeżone.'
    },
    'ru': {
        'title': 'Контакты — Vermarkter',
        'description': 'Свяжитесь с Vermarkter для Performance Marketing. Личная консультация без давления продаж. Ответ в течение 2 часов.',
        'keywords': 'Контакты Vermarkter, Маркетинговая консультация, Контакты агентства Google Ads',
        'og_description': 'Личная консультация без давления продаж',
        'nav_services': 'Услуги',
        'nav_testimonials': 'Отзывы',
        'nav_faq': 'FAQ',
        'nav_contact': 'Контакты',
        'page_title': 'Контакты',
        'page_subtitle': 'Бесплатная консультация без давления продаж',
        'email_label': 'Email',
        'telegram_btn': 'Сообщение в Telegram',
        'whatsapp_btn': 'Чат в WhatsApp',
        'response_time': 'Ответ в течение 2 часов',
        'response_desc': 'Мы отвечаем быстро и конкретно',
        'contact_form_title': 'Или напишите нам',
        'form_name': 'Имя',
        'form_email': 'Email',
        'form_phone': 'Телефон (необязательно)',
        'form_message': 'Сообщение',
        'form_submit': 'Отправить сообщение',
        'footer_legal': 'Юридическое',
        'footer_privacy': 'Конфиденциальность',
        'footer_imprint': 'Impressum',
        'footer_contact': 'Контакты',
        'footer_copyright': '© 2025 Vermarkter. Все права защищены.'
    },
    'tr': {
        'title': 'İletişim — Vermarkter',
        'description': 'Performance Marketing için Vermarkter ile iletişime geçin. Satış baskısı olmadan kişisel danışmanlık. 2 saat içinde yanıt.',
        'keywords': 'İletişim Vermarkter, Pazarlama Danışmanlığı, Google Ads Ajansı İletişim',
        'og_description': 'Satış baskısı olmadan kişisel danışmanlık',
        'nav_services': 'Hizmetler',
        'nav_testimonials': 'Yorumlar',
        'nav_faq': 'SSS',
        'nav_contact': 'İletişim',
        'page_title': 'İletişim',
        'page_subtitle': 'Satış baskısı olmadan ücretsiz danışmanlık',
        'email_label': 'E-posta',
        'telegram_btn': 'Telegram\'da mesaj',
        'whatsapp_btn': 'WhatsApp\'ta sohbet',
        'response_time': '2 saat içinde yanıt',
        'response_desc': 'Hızlı ve net yanıt veriyoruz',
        'contact_form_title': 'Ya da bize yazın',
        'form_name': 'İsim',
        'form_email': 'E-posta',
        'form_phone': 'Telefon (isteğe bağlı)',
        'form_message': 'Mesaj',
        'form_submit': 'Mesaj gönder',
        'footer_legal': 'Yasal',
        'footer_privacy': 'Gizlilik',
        'footer_imprint': 'Künye',
        'footer_contact': 'İletişim',
        'footer_copyright': '© 2025 Vermarkter. Tüm hakları saklıdır.'
    },
    'ua': {
        'title': 'Контакти — Vermarkter',
        'description': 'Зв\'яжіться з Vermarkter для Performance Marketing. Особиста консультація без тиску продажів. Відповідь протягом 2 годин.',
        'keywords': 'Контакти Vermarkter, Маркетингова консультація, Контакти агенції Google Ads',
        'og_description': 'Особиста консультація без тиску продажів',
        'nav_services': 'Послуги',
        'nav_testimonials': 'Відгуки',
        'nav_faq': 'FAQ',
        'nav_contact': 'Контакти',
        'page_title': 'Контакти',
        'page_subtitle': 'Безкоштовна консультація без тиску продажів',
        'email_label': 'Email',
        'telegram_btn': 'Повідомлення в Telegram',
        'whatsapp_btn': 'Чат у WhatsApp',
        'response_time': 'Відповідь протягом 2 годин',
        'response_desc': 'Ми відповідаємо швидко і конкретно',
        'contact_form_title': 'Або напишіть нам',
        'form_name': 'Ім\'я',
        'form_email': 'Email',
        'form_phone': 'Телефон (необов\'язково)',
        'form_message': 'Повідомлення',
        'form_submit': 'Надіслати повідомлення',
        'footer_legal': 'Юридичне',
        'footer_privacy': 'Конфіденційність',
        'footer_imprint': 'Impressum',
        'footer_contact': 'Контакти',
        'footer_copyright': '© 2025 Vermarkter. Усі права захищені.'
    }
}

def translate_contact_page(content, from_lang, to_lang):
    """Translate contact page from DE to target language"""

    t_from = TRANSLATIONS[from_lang]
    t_to = TRANSLATIONS[to_lang]

    # Replace meta tags
    content = content.replace(t_from['description'], t_to['description'])
    content = content.replace(t_from['keywords'], t_to['keywords'])
    content = content.replace(t_from['og_description'], t_to['og_description'])
    content = content.replace(f'<title>{t_from["title"]}</title>', f'<title>{t_to["title"]}</title>')

    # Replace navigation
    content = content.replace(f'>{t_from["nav_services"]}<', f'>{t_to["nav_services"]}<')
    content = content.replace(f'>{t_from["nav_testimonials"]}<', f'>{t_to["nav_testimonials"]}<')
    content = content.replace(f'>{t_from["nav_faq"]}<', f'>{t_to["nav_faq"]}<')
    content = content.replace(f'>{t_from["nav_contact"]}<', f'>{t_to["nav_contact"]}<')

    # Replace page content
    content = content.replace(f'<h1 style="font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 900; margin-bottom: 1.5rem; line-height: 1.1;">{t_from["page_title"]}</h1>',
                            f'<h1 style="font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 900; margin-bottom: 1.5rem; line-height: 1.1;">{t_to["page_title"]}</h1>')

    content = content.replace(f'<p style="font-size: 1.25rem; color: var(--text-secondary); max-width: 600px;">{t_from["page_subtitle"]}</p>',
                            f'<p style="font-size: 1.25rem; color: var(--text-secondary); max-width: 600px;">{t_to["page_subtitle"]}</p>')

    content = content.replace(f'<p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">{t_from["email_label"]}</p>',
                            f'<p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">{t_to["email_label"]}</p>')

    content = content.replace(t_from['telegram_btn'], t_to['telegram_btn'])
    content = content.replace(t_from['whatsapp_btn'], t_to['whatsapp_btn'])
    content = content.replace(t_from['response_time'], t_to['response_time'])
    content = content.replace(t_from['response_desc'], t_to['response_desc'])

    # Replace form
    content = content.replace(t_from['contact_form_title'], t_to['contact_form_title'])
    content = content.replace(f'for="contactName" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_from["form_name"]}<',
                            f'for="contactName" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_to["form_name"]}<')
    content = content.replace(f'for="contactEmail" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_from["form_email"]}',
                            f'for="contactEmail" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_to["form_email"]}')
    content = content.replace(f'for="contactPhone" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_from["form_phone"]}<',
                            f'for="contactPhone" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_to["form_phone"]}<')
    content = content.replace(f'for="contactMessage" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_from["form_message"]}<',
                            f'for="contactMessage" style="display: block; margin-bottom: 0.5rem; color: var(--text-primary); font-weight: 600;">{t_to["form_message"]}<')
    content = content.replace(f'type="submit" class="btn btn-primary" style="width: 100%; padding: 1rem; font-size: 1.1rem;">{t_from["form_submit"]}<',
                            f'type="submit" class="btn btn-primary" style="width: 100%; padding: 1rem; font-size: 1.1rem;">{t_to["form_submit"]}<')

    # Replace footer
    content = content.replace(f'<h4 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary);">{t_from["footer_legal"]}</h4>',
                            f'<h4 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary);">{t_to["footer_legal"]}</h4>')
    content = content.replace(f'<h4 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary);">{t_from["footer_contact"]}</h4>',
                            f'<h4 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary);">{t_to["footer_contact"]}</h4>')
    content = content.replace(t_from['footer_privacy'], t_to['footer_privacy'])
    content = content.replace(t_from['footer_imprint'], t_to['footer_imprint'])
    content = content.replace(t_from['footer_copyright'], t_to['footer_copyright'])

    # Update language selector and links
    # Change current language flag/text
    if to_lang == 'en':
        flag_html = '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                    <rect width="16" height="12" fill="#012169"/>
                                    <path d="M0,0 L16,12 M16,0 L0,12" stroke="#fff" stroke-width="2.4"/>
                                    <path d="M0,0 L16,12 M16,0 L0,12" stroke="#C8102E" stroke-width="1.6"/>
                                    <path d="M8,0 V12 M0,6 H16" stroke="#fff" stroke-width="4"/>
                                    <path d="M8,0 V12 M0,6 H16" stroke="#C8102E" stroke-width="2.4"/>
                                </svg> EN'''
    elif to_lang == 'pl':
        flag_html = '<span class="flag">🇵🇱</span> PL'
    elif to_lang == 'ru':
        flag_html = '<span class="flag">🇷🇺</span> RU'
    elif to_lang == 'tr':
        flag_html = '<span class="flag">🇹🇷</span> TR'
    elif to_lang == 'ua':
        flag_html = '<span class="flag">🇺🇦</span> UA'

    # Update lang button (will need manual check, but attempt replacement)
    content = re.sub(r'<span class="flag">🇩🇪</span> DE', flag_html, content)

    # Update language dropdown links to point to correct contact pages
    content = re.sub(r'href="\.\./de/contact\.html"', 'href="../de/contact.html"', content)
    content = re.sub(r'href="\.\./en/contact\.html"', 'href="../en/contact.html"', content)
    content = re.sub(r'href="\.\./pl/contact\.html"', 'href="../pl/contact.html"', content)
    content = re.sub(r'href="\.\./ru/contact\.html"', 'href="../ru/contact.html"', content)
    content = re.sub(r'href="\.\./tr/contact\.html"', 'href="../tr/contact.html"', content)
    content = re.sub(r'href="\.\./ua/contact\.html"', 'href="../ua/contact.html"', content)

    return content

def main():
    """Create contact.html for EN, PL, RU, TR, UA based on DE"""
    base_dir = Path('.')
    de_contact = base_dir / 'de' / 'contact.html'

    if not de_contact.exists():
        print("Error: de/contact.html not found!")
        return

    # Read DE contact page
    with open(de_contact, 'r', encoding='utf-8') as f:
        de_content = f.read()

    langs_to_create = ['en', 'pl', 'ru', 'tr', 'ua']
    created_count = 0

    for lang in langs_to_create:
        lang_dir = base_dir / lang
        if not lang_dir.exists():
            print(f"Warning: {lang} directory doesn't exist")
            continue

        contact_file = lang_dir / 'contact.html'

        if contact_file.exists():
            print(f"Skipped (already exists): {contact_file}")
            continue

        # Translate content
        translated = translate_contact_page(de_content, 'de', lang)

        # Write file
        with open(contact_file, 'w', encoding='utf-8') as f:
            f.write(translated)

        print(f"[OK] Created: {contact_file}")
        created_count += 1

    print(f"\n{'='*60}")
    print(f"Created {created_count} contact pages")
    print(f"Based on: de/contact.html")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
