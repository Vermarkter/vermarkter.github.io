#!/usr/bin/env python3
"""
Fix incomplete translations in contact.html files
"""

import re
from pathlib import Path

# Main text blocks that need translation
HERO_TRANSLATIONS = {
    'en': {
        'title': 'Let\'s talk about your <span class="text-gradient">growth</span>.',
        'subtitle': 'Personal consultation without sales pressure.'
    },
    'pl': {
        'title': 'Porozmawiajmy o Twoim <span class="text-gradient">wzroście</span>.',
        'subtitle': 'Osobista konsultacja bez presji sprzedażowej.'
    },
    'ru': {
        'title': 'Давайте поговорим о вашем <span class="text-gradient">росте</span>.',
        'subtitle': 'Личная консультация без давления продаж.'
    },
    'tr': {
        'title': '<span class="text-gradient">Büyümeniz</span> hakkında konuşalım.',
        'subtitle': 'Satış baskısı olmadan kişisel danışmanlık.'
    },
    'ua': {
        'title': 'Давайте поговоримо про ваше <span class="text-gradient">зростання</span>.',
        'subtitle': 'Персональна консультація без тиску продажів.'
    }
}

CONTACT_INFO_TRANSLATIONS = {
    'en': {
        'contact_me': 'Contact Me',
        'telegram_btn': 'Write to Telegram',
        'whatsapp_btn': 'Write to WhatsApp',
        'response_time': '⏱️ Response Time',
        'response_desc': 'Usually within 2 hours'
    },
    'pl': {
        'contact_me': 'Skontaktuj się',
        'telegram_btn': 'Napisz na Telegram',
        'whatsapp_btn': 'Napisz na WhatsApp',
        'response_time': '⏱️ Czas odpowiedzi',
        'response_desc': 'Zazwyczaj w ciągu 2 godzin'
    },
    'ru': {
        'contact_me': 'Свяжитесь со мной',
        'telegram_btn': 'Написать в Telegram',
        'whatsapp_btn': 'Написать в WhatsApp',
        'response_time': '⏱️ Время ответа',
        'response_desc': 'Обычно в течение 2 часов'
    },
    'tr': {
        'contact_me': 'Benimle İletişime Geçin',
        'telegram_btn': 'Telegram\'a Yaz',
        'whatsapp_btn': 'WhatsApp\'a Yaz',
        'response_time': '⏱️ Yanıt Süresi',
        'response_desc': 'Genellikle 2 saat içinde'
    },
    'ua': {
        'contact_me': 'Зв\'яжіться зі мною',
        'telegram_btn': 'Написати в Telegram',
        'whatsapp_btn': 'Написати в WhatsApp',
        'response_time': '⏱️ Час відповіді',
        'response_desc': 'Зазвичай протягом 2 годин'
    }
}

PROFILE_TRANSLATIONS = {
    'en': {
        'role': 'Founder & Performance Marketer',
        'bio1': 'With over 5 years of experience in performance marketing, I have helped more than 100 companies increase their revenue through targeted Google Ads, Meta Ads, and TikTok campaigns.',
        'bio2': 'My focus: <strong style="color: var(--text-primary);">Transparent results, no hidden costs, and a partnership on equal footing.</strong>',
        'projects': 'Projects',
        'avg_roas': 'Avg. ROAS'
    },
    'pl': {
        'role': 'Założyciel & Performance Marketer',
        'bio1': 'Z ponad 5-letnim doświadczeniem w performance marketingu pomogłem ponad 100 firmom zwiększyć przychody poprzez ukierunkowane kampanie Google Ads, Meta Ads i TikTok.',
        'bio2': 'Mój priorytet: <strong style="color: var(--text-primary);">Przejrzyste wyniki, brak ukrytych kosztów i partnerstwo na równych zasadach.</strong>',
        'projects': 'Projektów',
        'avg_roas': 'Śr. ROAS'
    },
    'ru': {
        'role': 'Основатель и Performance маркетолог',
        'bio1': 'Имея более 5 лет опыта в performance-маркетинге, я помог более чем 100 компаниям увеличить доходы с помощью целевых кампаний в Google Ads, Meta Ads и TikTok.',
        'bio2': 'Мой фокус: <strong style="color: var(--text-primary);">Прозрачные результаты, никаких скрытых затрат и партнерство на равных.</strong>',
        'projects': 'Проектов',
        'avg_roas': 'Ср. ROAS'
    },
    'tr': {
        'role': 'Kurucu & Performance Pazarlamacı',
        'bio1': '5 yıldan fazla performance marketing deneyimiyle, hedefli Google Ads, Meta Ads ve TikTok kampanyaları aracılığıyla 100\'den fazla şirketin gelirini artırmalarına yardımcı oldum.',
        'bio2': 'Odak noktam: <strong style="color: var(--text-primary);">Şeffaf sonuçlar, gizli maliyet yok ve eşit ortaklık.</strong>',
        'projects': 'Proje',
        'avg_roas': 'Ort. ROAS'
    },
    'ua': {
        'role': 'Засновник & Performance маркетолог',
        'bio1': 'Маючи понад 5 років досвіду в performance-маркетингу, я допоміг понад 100 компаніям збільшити дохід за допомогою цільових кампаній у Google Ads, Meta Ads та TikTok.',
        'bio2': 'Мій фокус: <strong style="color: var(--text-primary);">Прозорі результати, без прихованих витрат і партнерство на рівних.</strong>',
        'projects': 'Проектів',
        'avg_roas': 'Сер. ROAS'
    }
}

FOOTER_TRANSLATIONS = {
    'en': {
        'about_us': 'About Us',
        'about_desc': 'Performance marketing agency for small and medium-sized businesses in Europe.',
        'privacy': 'Privacy Policy',
        'imprint': 'Imprint',
        'copyright': 'Performance Marketing for Growth'
    },
    'pl': {
        'about_us': 'O nas',
        'about_desc': 'Agencja performance marketingu dla małych i średnich firm w Europie.',
        'privacy': 'Polityka Prywatności',
        'imprint': 'Nota Prawna',
        'copyright': 'Performance Marketing dla Wzrostu'
    },
    'ru': {
        'about_us': 'О нас',
        'about_desc': 'Агентство performance-маркетинга для малого и среднего бизнеса в Европе.',
        'privacy': 'Политика конфиденциальности',
        'imprint': 'Выходные данные',
        'copyright': 'Performance-маркетинг для роста'
    },
    'tr': {
        'about_us': 'Hakkımızda',
        'about_desc': 'Avrupa\'daki küçük ve orta ölçekli işletmeler için performance marketing ajansı.',
        'privacy': 'Gizlilik Politikası',
        'imprint': 'Künye',
        'copyright': 'Büyüme için Performance Marketing'
    },
    'ua': {
        'about_us': 'Про нас',
        'about_desc': 'Агентство performance-маркетингу для малого та середнього бізнесу в Європі.',
        'privacy': 'Політика конфіденційності',
        'imprint': 'Вихідні дані',
        'copyright': 'Performance-маркетинг для зростання'
    }
}

def fix_translations(content, lang):
    """Fix incomplete translations"""

    # Fix hero section
    content = re.sub(
        r'Lassen Sie uns über Ihr <span class="text-gradient">Wachstum</span> sprechen\.',
        HERO_TRANSLATIONS[lang]['title'],
        content
    )
    content = content.replace(
        'Personal consultation without sales pressure.',
        HERO_TRANSLATIONS[lang]['subtitle']
    )

    # Fix contact info section
    content = content.replace('Kontaktieren Sie mich', CONTACT_INFO_TRANSLATIONS[lang]['contact_me'])
    content = content.replace('Schreiben Sie mir auf Telegram', CONTACT_INFO_TRANSLATIONS[lang]['telegram_btn'])
    content = content.replace('Schreiben Sie mir auf WhatsApp', CONTACT_INFO_TRANSLATIONS[lang]['whatsapp_btn'])
    content = content.replace('⏱️ Antwortzeit', CONTACT_INFO_TRANSLATIONS[lang]['response_time'])
    content = content.replace('In der Regel innerhalb von 2 Stunden', CONTACT_INFO_TRANSLATIONS[lang]['response_desc'])

    # Fix profile section
    content = content.replace('Gründer & Performance Marketer', PROFILE_TRANSLATIONS[lang]['role'])
    content = re.sub(
        r'Mit über 5 Jahren Erfahrung im Performance Marketing habe ich mehr als 100 Unternehmen dabei geholfen,\s*ihren Umsatz durch gezielte Google Ads, Meta Ads und TikTok Kampagnen zu steigern\.',
        PROFILE_TRANSLATIONS[lang]['bio1'],
        content
    )
    content = re.sub(
        r'Mein Fokus: <strong style="color: var\(--text-primary\);">Transparente Ergebnisse, keine versteckten Kosten,\s*und eine Partnerschaft auf Augenhöhe\.</strong>',
        PROFILE_TRANSLATIONS[lang]['bio2'],
        content
    )
    content = content.replace('>Projekte<', f'>{PROFILE_TRANSLATIONS[lang]["projects"]}<')

    # Fix footer
    content = content.replace('>Über uns<', f'>{FOOTER_TRANSLATIONS[lang]["about_us"]}<')
    content = content.replace(
        'Performance Marketing Agentur für kleine und mittelständische Unternehmen in Europa.',
        FOOTER_TRANSLATIONS[lang]['about_desc']
    )
    content = content.replace('>Datenschutz<', f'>{FOOTER_TRANSLATIONS[lang]["privacy"]}<')
    content = content.replace('>Impressum<', f'>{FOOTER_TRANSLATIONS[lang]["imprint"]}<')
    content = content.replace('Performance Marketing für Wachstum', FOOTER_TRANSLATIONS[lang]['copyright'])

    return content

def process_file(file_path, lang):
    """Fix translations in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = fix_translations(content, lang)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix translations in all contact pages"""
    base_dir = Path('.')
    modified_count = 0

    languages = ['en', 'pl', 'ru', 'tr', 'ua']

    for lang in languages:
        contact_file = base_dir / lang / 'contact.html'

        if contact_file.exists():
            if process_file(contact_file, lang):
                print(f"[OK] Fixed: {contact_file}")
                modified_count += 1
        else:
            print(f"[SKIP] Not found: {contact_file}")

    print(f"\n{'='*60}")
    print(f"Fixed {modified_count} files")
    print(f"All German text replaced with proper translations")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
