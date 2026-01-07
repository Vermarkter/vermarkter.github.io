# -*- coding: utf-8 -*-

# Turkish translation script for CRM Integration page

# Read German version
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Turkish translations dictionary
translations = {
    # Language switcher - Turkish flag (red with white crescent and star)
    '''<svg width="16" height="12">
                            <rect width="16" height="4" fill="#000"/>
                            <rect y="4" width="16" height="4" fill="#D00"/>
                            <rect y="8" width="16" height="4" fill="#FFCE00"/>
                        </svg>
                        DE ▼''': '''<svg width="16" height="12">
                            <rect width="16" height="12" fill="#E30A17"/>
                            <circle cx="5" cy="6" r="2.5" fill="#fff"/>
                            <circle cx="6" cy="6" r="2" fill="#E30A17"/>
                            <polygon points="10,3 10.5,4.5 12,4.5 10.8,5.5 11.3,7 10,6 8.7,7 9.2,5.5 8,4.5 9.5,4.5" fill="#fff"/>
                        </svg>
                        TR ▼''',

    # Meta tags
    '<html lang="de">': '<html lang="tr">',
    '<title>CRM-Integration | Keine verlorenen Leads mehr | Vermarkter</title>': '<title>CRM Entegrasyonu | Artık Kayıp Lead Yok | Vermarkter</title>',
    'content="CRM-Integration für Marketing-Agenturen': 'content="Pazarlama ajansları için CRM entegrasyonu',

    # Navigation
    'Startseite': 'Ana Sayfa',
    'Dienstleistungen': 'Hizmetler',
    'Über uns': 'Hakkımızda',
    'Kontakt': 'İletişim',

    # Hero section
    'CRM-Integration': 'CRM Entegrasyonu',
    'Keine verlorenen Leads mehr': 'Artık Kayıp Lead Yok',
    'Leads aus Google Ads & Meta landen automatisch in Ihrem CRM. Ihr Sales-Team bekommt sofort eine Benachrichtigung. Kein Lead geht verloren.': 'Google Ads ve Meta\'dan gelen lead\'ler otomatik olarak CRM\'inize düşer. Satış ekibiniz anında bildirim alır. Hiçbir lead kaybolmaz.',
    'Jetzt CRM verbinden': 'Şimdi CRM Bağla',
    'Kostenlose Beratung': 'Ücretsiz Danışmanlık',

    # Problems section
    'Die häufigsten Probleme ohne CRM-Integration': 'CRM Entegrasyonu Olmadan En Yaygın Sorunlar',

    'Chaos in den Leads': 'Lead\'lerde Kaos',
    'Ihre Leads landen in unübersichtlichen Tabellen. Manager müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Lead\'leriniz karmaşık tablolara düşer. Yöneticiler manuel olarak sıralamak, önceliklendirmek ve takip etmek zorunda. <strong style="color: #EF4444;">Zaman kaybı + kaçırılan fırsatlar.</strong>',

    'Manager reagieren zu spät': 'Yöneticiler Çok Geç Tepki Veriyor',
    'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Lead gelir → Yönetici saatler sonra görür → Lead rakipten satın alır. <strong style="color: #EF4444;">Anında bildirim olmadan lead\'lerin %50\'sini kaybedersiniz.</strong>',

    'Kein Feedback an Google Ads': 'Google Ads\'e Geri Bildirim Yok',
    'Google sieht nur Klicks, aber nicht, ob daraus ein Kunde wurde. <strong style="color: #EF4444;">Ihre Kampagnen optimieren auf Leads statt auf Umsatz.</strong>': 'Google sadece tıklamaları görür, ancak bunun müşteriye dönüşüp dönüşmediğini görmez. <strong style="color: #EF4444;">Kampanyalarınız ciro yerine lead\'lere optimize olur.</strong>',

    # Solution section
    'Unsere <span class="text-gradient">Lösung</span>': 'Bizim <span class="text-gradient">Çözümümüz</span>',

    'Automatisierung': 'Otomasyon',
    'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Lead web sitesinden gelir → anında CRM\'e düşer → Yönetici Telegram bildirimi alır → 5 dakika içinde arama.',
    'Formulare → CRM (Zapier/Make)': 'Formlar → CRM (Zapier/Make)',
    'Telegram/Slack/WhatsApp-Benachrichtigungen': 'Telegram/Slack/WhatsApp Bildirimleri',
    'Auto-Tagging nach Quelle': 'Kaynağa Göre Otomatik Etiketleme',

    'Offline Conversions': 'Çevrimdışı Dönüşümler',
    'Wir senden Verkaufsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Satış verilerini Google Ads ve Meta\'ya geri gönderiyoruz. Algoritmalar hangi tıklamaların gerçek müşteriye dönüştüğünü öğrenir. <strong>Otomatik olarak daha iyi ROAS.</strong>',
    'Google Ads Offline Conversions': 'Google Ads Çevrimdışı Dönüşümleri',
    'Meta CAPI (Conversions API)': 'Meta CAPI (Dönüşüm API\'si)',
    'Event-Tracking (Kauf, Rechnung, etc.)': 'Etkinlik Takibi (Satın alma, Fatura vb.)',

    'Sales Pipeline': 'Satış Süreci',
    'Strukturierte Verkaufsprozesse: Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen. Kein Lead geht verloren.': 'Yapılandırılmış satış süreci: Yeni Lead → İletişim → Teklif → Müzakere → Kazanıldı. Hiçbir lead kaybolmaz.',
    'Automatische Status-Updates': 'Otomatik Durum Güncellemeleri',
    'E-Mail-Sequenzen (Follow-ups)': 'E-posta Dizileri (Takipler)',
    'Deal-Prognosen & Reports': 'Anlaşma Tahminleri ve Raporlar',

    # Pricing section
    'Preise & Pakete': 'Fiyatlar ve Paketler',
    'Einmalige Einrichtung. Keine monatlichen Kosten (außer CRM-Lizenz).': 'Tek seferlik kurulum. Aylık maliyet yok (CRM lisansı hariç).',

    'BASIC': 'TEMEL',
    'Für Einsteiger': 'Yeni Başlayanlar İçin',
    'einmalig': 'bir kez',
    'Website-Formulare → CRM': 'Web Sitesi Formları → CRM',
    'Telegram/Slack-Benachrichtigungen': 'Telegram/Slack Bildirimleri',
    'Basis-Pipeline Setup': 'Temel Süreç Kurulumu',
    'E-Mail-Support': 'E-posta Desteği',
    'Setup-Zeit: 3-5 Werktage': 'Kurulum Süresi: 3-5 iş günü',
    'Jetzt buchen': 'Şimdi Rezervasyon Yap',

    'ADVANCED': 'GELİŞMİŞ',
    'Für professionelle Teams': 'Profesyonel Ekipler İçin',
    'Beliebteste Wahl': 'En Popüler Seçim',
    'Alles aus BASIC +': 'TEMEL\'deki Her Şey +',
    'Offline Conversions (Google Ads)': 'Çevrimdışı Dönüşümler (Google Ads)',
    'Meta CAPI Integration': 'Meta CAPI Entegrasyonu',
    'Zapier/Make Automations (5 Flows)': 'Zapier/Make Otomasyonları (5 Akış)',
    'Custom Sales Pipeline': 'Özel Satış Süreci',
    'Email Sequences (Follow-ups)': 'E-posta Dizileri (Takipler)',
    'Priority Support (24h Response)': 'Öncelikli Destek (24 saat yanıt)',
    'Setup-Zeit: 5-7 Werktage': 'Kurulum Süresi: 5-7 iş günü',

    'CUSTOM': 'ÖZEL',
    'Für Unternehmen': 'Şirketler İçin',
    'Preis auf Anfrage': 'Talep Üzerine Fiyat',
    'Alles aus ADVANCED +': 'GELİŞMİŞ\'teki Her Şey +',
    'Custom API Integrations': 'Özel API Entegrasyonları',
    'Unbegrenzte Automations': 'Sınırsız Otomasyon',
    'Dedicated Account Manager': 'Özel Hesap Yöneticisi',
    'SLA + Priority Support': 'SLA + Öncelikli Destek',
    'Individuelle Setup-Zeit': 'Bireysel Kurulum Süresi',
    'Kontaktieren Sie uns': 'Bize Ulaşın',

    'Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': 'Fiyatlar KDV hariçtir. CRM lisans maliyetleri (HubSpot, Pipedrive vb.) DAHİL DEĞİLDİR. Size uygun planı seçmenizde yardımcı oluruz.',

    # FAQ section
    'Häufige Fragen (FAQ)': 'Sık Sorulan Sorular (SSS)',

    '💰 Welches CRM soll ich wählen?': '💰 Hangi CRM\'i seçmeliyim?',
    '<strong>HubSpot:</strong> Am besten für Marketing + Vertrieb zusammen. Kostenlose Version verfügbar, später ab €50/Monat.<br><br><strong>Pipedrive:</strong> Einfaches Sales-CRM. €14/Monat pro Nutzer. Perfekt für kleine Teams.<br><br><strong>Zoho CRM:</strong> Günstigste Option. Ab €14/Monat. Gut für Startups.<br><br><strong>GoHighLevel:</strong> All-in-One für Agenturen. Ab €97/Monat.<br><br>Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': '<strong>HubSpot:</strong> Pazarlama + satış birlikte için en iyi. Ücretsiz sürüm mevcut, daha sonra ayda 50€\'dan başlayan.<br><br><strong>Pipedrive:</strong> Basit Satış CRM\'i. Kullanıcı başına ayda 14€. Küçük ekipler için mükemmel.<br><br><strong>Zoho CRM:</strong> En uygun fiyatlı seçenek. Ayda 14€\'dan başlayan. Startup\'lar için iyi.<br><br><strong>GoHighLevel:</strong> Ajanslar için hepsi bir arada. Ayda 97€\'dan başlayan.<br><br>Hangi sistemin bütçenize ve sürecinize uygun olduğu konusunda ücretsiz danışmanlık veriyoruz.',

    '⏱️ Wie lange dauert das Setup?': '⏱️ Kurulum ne kadar sürer?',
    '<strong>BASIC:</strong> 3-5 Werktage.<br><strong>ADVANCED:</strong> 5-7 Werktage (wegen Offline Conversions & Automations).<br><strong>CUSTOM:</strong> Je nach Anforderungen.<br><br>Nach Zahlung starten wir sofort. Sie bekommen regelmäßige Updates per E-Mail oder Telegram.': '<strong>TEMEL:</strong> 3-5 iş günü.<br><strong>GELİŞMİŞ:</strong> 5-7 iş günü (Çevrimdışı Dönüşümler ve Otomasyonlar nedeniyle).<br><strong>ÖZEL:</strong> Gereksinimlere bağlı olarak.<br><br>Ödeme sonrası hemen başlıyoruz. E-posta veya Telegram ile düzenli güncellemeler alırsınız.',

    '📊 Was sind Offline Conversions?': '📊 Çevrimdışı Dönüşümler nedir?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Verkauf passiert offline (Anruf, Meeting, Rechnung). <strong>Offline Conversions</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads normalde sadece tıklamaları ve form gönderimlerini görür. Ancak gerçek satış çevrimdışı gerçekleşir (arama, toplantı, fatura). <strong>Çevrimdışı Dönüşümler</strong> bu verileri Google\'a geri gönderir. Sonuç: Google hangi tıklamaların gerçek müşterilere yol açtığını bilir ve kampanyalarınızı sadece lead\'ler yerine ciro için otomatik olarak optimize eder. <strong>ROAS ortalama %30-50 artar.</strong>',

    '💬 Wie funktionieren Telegram-Benachrichtigungen?': '💬 Telegram bildirimleri nasıl çalışır?',
    'Sobald ein Lead von Ihrer Website kommt, bekommt Ihr Sales-Manager eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Telefon, Quelle (Google Ads/Meta/etc.). Manager kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Web sitenizden bir lead gelir gelmez, satış yöneticiniz Telegram\'da (veya Slack/WhatsApp) bir mesaj alır. Mesaj şunları içerir: İsim, E-posta, Telefon, Kaynak (Google Ads/Meta/vb.). Yönetici hemen tepki verebilir. <strong>Ortalama yanıt süresi: 5 dakikanın altında.</strong>',

    '🔧 Brauche ich laufende Wartung?': '🔧 Devam eden bakıma ihtiyacım var mı?',
    'Das Setup ist einmalig. Danach arbeitet alles automatisch. Falls Sie später weitere Automations, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Kurulum tek seferlik. Sonrasında her şey otomatik çalışır. Daha sonra ek otomasyonlar, ekstra entegrasyonlar veya optimizasyonlar gerekirse, bizi istediğiniz zaman görevlendirebilirsiniz. Saatlik ücret: 99€/saat.',

    # CTA section
    'Bereit für mehr Umsatz?': 'Daha Fazla Ciro İçin Hazır mısınız?',
    'Buchen Sie jetzt eine kostenlose Beratung. Wir analysieren Ihren aktuellen Prozess und zeigen Ihnen, wie CRM-Integration Ihren Sales-Funnel optimiert.': 'Şimdi ücretsiz bir danışmanlık rezervasyonu yapın. Mevcut sürecinizi analiz eder ve CRM entegrasyonunun satış huninizi nasıl optimize ettiğini gösteririz.',
    'Kostenlose Beratung buchen': 'Ücretsiz Danışmanlık Rezervasyonu',

    # Contact form
    'Ihr Name': 'Adınız',
    'Ihre E-Mail': 'E-postanız',
    'Ihre Telefonnummer (optional)': 'Telefon Numaranız (isteğe bağlı)',
    'Ihre Nachricht': 'Mesajınız',
    'Nachricht senden': 'Mesaj Gönder',

    # Footer
    'Schnelllinks': 'Hızlı Bağlantılar',
    'Google Ads': 'Google Ads',
    'Meta Ads': 'Meta Ads',
    'TikTok Ads': 'TikTok Ads',
    'SEO': 'SEO',

    'Rechtliches': 'Yasal',
    'Datenschutz': 'Gizlilik Politikası',
    'Impressum': 'Yasal Uyarı',

    '&copy; 2025 Vermarkter. Alle Rechte vorbehalten.': '&copy; 2025 Vermarkter. Tüm hakları saklıdır.',

    # Chatbot
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Merhaba! 👋 CRM entegrasyonu hakkında sorularınız mı var?',
    'Schreiben Sie Ihre Frage...': 'Sorunuzu yazın...',
}

# Apply translations
for de, tr in translations.items():
    content = content.replace(de, tr)

# Write Turkish version
with open('tr/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Turkish CRM page created successfully!")
print("Translated phrases:", len(translations))
