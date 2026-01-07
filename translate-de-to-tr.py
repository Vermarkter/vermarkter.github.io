# -*- coding: utf-8 -*-

# Turkish translation script for CRM Integration page

# Read German version
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Turkish translations dictionary
translations = {
    # Language switcher - Turkish flag
    '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#000"/>
                                <rect y="4" width="16" height="4" fill="#D00"/>
                                <rect y="8" width="16" height="4" fill="#FFCE00"/>
                            </svg>
                            DE ▼''': '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
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
    'content="CRM Entegrasyonu für Marketing & Sales. HubSpot, Pipedrive, Zoho. Lead-Tracking, Çevrimdışı Dönüşümler, Telegram Bildirimleri. Keine verlorenen Leads mehr.': 'content="Pazarlama ve satış için CRM entegrasyonu. HubSpot, Pipedrive, Zoho. Lead takibi, çevrimdışı dönüşümler, Telegram bildirimleri. Artık kayıp lead yok.',
    'content="Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb. Lead-Tracking, Otomasyon, echtes ROAS.': 'content="Pazarlama kampanyalarınızı satışla birleştirin. Lead takibi, otomasyon, gerçek ROAS.',
    'content="Verbinden Sie Marketing und Sales': 'content="Pazarlama ve satışı birleştirin',

    # Navigation
    'Startseite': 'Ana Sayfa',
    'Leistungen': 'Hizmetler',
    'Dienstleistungen': 'Hizmetler',
    'Über uns': 'Hakkımızda',
    'Kontakt': 'İletişim',
    'Probleme': 'Sorunlar',
    'Lösung': 'Çözüm',
    'Preise': 'Fiyatlar',

    # Hero section
    'CRM-Integration': 'CRM Entegrasyonu',
    'Marketing <span class="text-gradient">+ Vertrieb</span><br>\n                    in einem System': 'Pazarlama <span class="text-gradient">+ Satış</span><br>\n                    Tek Sistemde',
    '<strong style="color: var(--text-primary);">Keine verlorenen Leads mehr.</strong> Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.<br>\n                    Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': '<strong style="color: var(--text-primary);">Artık kayıp lead yok.</strong> Google Ads, Meta Ads ve TikTok\'u HubSpot, Pipedrive veya Zoho CRM ile bağlayın.<br>\n                    Otomatik bildirimler, satış takibi, gerçek ROAS.',
    'Setup ab €499': '€499\'dan başlayan kurulum',
    'Demo buchen': 'Demo Talep Et',
    'Website': 'Web Sitesi',
    'Manager': 'Yönetici',
    'Verkauf': 'Satış',
    'Unterstützte CRM-Systeme:': 'Desteklenen CRM Sistemleri:',

    # Problems section
    '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Bu size tanıdık geliyor mu?</span>',
    'Die häufigsten Probleme ohne CRM-Integration': 'CRM entegrasyonu olmadan yaşanan en yaygın sorunlar',
    'Leads in Excel-Tabellen': 'Excel tablolarında Lead\'ler',
    'Ihre Leads landen in unübersichtlichen Tabellen. Manager müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Lead\'leriniz karmaşık tablolara düşer. Yöneticiler manuel olarak sıralamak, önceliklendirmek ve takip etmek zorunda. <strong style="color: #EF4444;">Zaman kaybı + kaçırılan fırsatlar.</strong>',
    'Ihre Leads landen in unübersichtlichen Tabellen. Yönetici müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Lead\'leriniz karmaşık tablolara düşer. Yöneticiler manuel olarak sıralamak, önceliklendirmek ve takip etmek zorunda. <strong style="color: #EF4444;">Zaman kaybı + kaçırılan fırsatlar.</strong>',
    'Manager reagieren zu spät': 'Yöneticiler çok geç tepki veriyor',
    'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Lead gelir → Yönetici saatler sonra görür → Lead rakipten satın alır. <strong style="color: #EF4444;">Anında bildirim olmadan lead\'lerin %50\'sini kaybedersiniz.</strong>',
    'Lead kommt rein → Yönetici sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Lead gelir → Yönetici saatler sonra görür → Lead rakipten satın alır. <strong style="color: #EF4444;">Anında bildirim olmadan lead\'lerin %50\'sini kaybedersiniz.</strong>',
    'Welche Werbung funktioniert?': 'Hangi reklam işe yarıyor?',
    'Google Ads zeigt Klicks, aber nicht Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. <strong style="color: #EF4444;">Ohne Offline Conversions verbrennen Sie Budget.</strong>': 'Google Ads tıklamaları gösterir, satışları değil. Hangi kampanyaların gerçek müşteri getirdiğini bilemezsiniz. <strong style="color: #EF4444;">Çevrimdışı dönüşümler olmadan bütçe yakarsınız.</strong>',
    'Google Ads zeigt Klicks, aber keine Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. <strong style="color: #EF4444;">Ohne Çevrimdışı Dönüşümler verbrennen Sie Budget.</strong>': 'Google Ads tıklamaları gösterir, satışları değil. Hangi kampanyaların gerçek müşteri getirdiğini bilemezsiniz. <strong style="color: #EF4444;">Çevrimdışı dönüşümler olmadan bütçe yakarsınız.</strong>',

    # Solution section
    '✅ Unsere <span class="text-gradient">Lösung</span>': '✅ Bizim <span class="text-gradient">Çözümümüz</span>',
    'Was wir für Sie einrichten': 'Sizin için ne kuruyoruz',
    'Automatisierung': 'Otomasyon',
    'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Web sitesinden lead gelir → anında CRM\'e düşer → Yönetici Telegram bildirimi alır → 5 dakika içinde arama.',
    'Formulare → CRM (Zapier/Make)': 'Formlar → CRM (Zapier/Make)',
    'Telegram/Slack/WhatsApp-Benachrichtigungen': 'Telegram/Slack/WhatsApp Bildirimleri',
    'Auto-Tagging nach Quelle': 'Kaynağa göre otomatik etiketleme',
    'Skvoznaya Analytics': 'Uçtan Uca Analitik',
    'Offline Conversions': 'Çevrimdışı Dönüşümler',
    'Wir senden Verkaufsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Satış verilerini Google Ads ve Meta\'ya geri gönderiyoruz. Algoritmalar hangi tıklamaların gerçek müşteriye dönüştüğünü öğrenir. <strong>Otomatik olarak daha iyi ROAS.</strong>',
    'Offline-Conversions (Google)': 'Çevrimdışı Dönüşümler (Google)',
    'CAPI für Meta Ads': 'Meta Ads için CAPI',
    'Echtes ROAS pro Kampagne': 'Kampanya başına gerçek ROAS',
    'Sales Funnels': 'Satış Hunileri',
    'Sales Pipeline': 'Satış Süreci',
    'Strukturierte Verkaufsprozesse: Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen. Kein Lead geht verloren.': 'Yapılandırılmış satış süreçleri: Yeni Lead → İletişim → Teklif → Müzakere → Kazanıldı. Hiçbir lead kaybolmaz.',
    'Custom Funnel-Stufen': 'Özel huni aşamaları',
    'Automatische Follow-ups': 'Otomatik takipler',
    'Lead-Scoring': 'Lead Puanlama',

    # Pricing section
    'Preise <span class="text-gradient">CRM-Integration</span>': 'Fiyatlar <span class="text-gradient">CRM Entegrasyonu</span>',
    'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Tek seferlik kurulum ücreti. Çalışmamız için aylık maliyet yok.',
    'BASIC SETUP': 'TEMEL KURULUM',
    'Für Starter': 'Başlangıç İçin',
    'einmalig': 'tek seferlik',
    'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'CRM Kurulumu (HubSpot/Pipedrive/Zoho)',
    'Website-Formulare → CRM': 'Web Sitesi Formları → CRM',
    'Telegram-Benachrichtigungen': 'Telegram Bildirimleri',
    'Basis-Funnel (3 Stufen)': 'Temel Huni (3 aşama)',
    '1 Stunde Schulung': '1 saat eğitim',
    'Jetzt starten': 'Şimdi Başla',

    '🔥 EMPFOHLEN': '🔥 ÖNERİLEN',
    'ADVANCED': 'GELİŞMİŞ',
    'Für wachsende Unternehmen': 'Büyüyen Şirketler İçin',
    'Alles aus BASIC +': 'TEMEL\'deki Her Şey +',
    'Offline Conversions (Google Ads)': 'Çevrimdışı Dönüşümler (Google Ads)',
    'Meta CAPI Integration': 'Meta CAPI Entegrasyonu',
    'Zapier/Make Automations (5 Flows)': 'Zapier/Make Otomasyonları (5 Akış)',
    'Custom Sales Pipeline': 'Özel Satış Süreci',
    'Email Sequences (Follow-ups)': 'E-posta Dizileri (Takipler)',
    'Priority Support (24h Response)': 'Öncelikli Destek (24 saat yanıt)',
    '2 Stunden Schulung + 30 Tage Support': '2 saat eğitim + 30 gün destek',

    'CUSTOM': 'ÖZEL',
    'Für Unternehmen': 'Kurumsal',
    'Preis auf Anfrage': 'Fiyat İsteyin',
    'Alles aus ADVANCED +': 'GELİŞMİŞ\'teki Her Şey +',
    'Custom API Integrations': 'Özel API Entegrasyonları',
    'Unbegrenzte Automations': 'Sınırsız Otomasyonlar',
    'Dedicated Account Manager': 'Özel Hesap Yöneticisi',
    'SLA + Priority Support': 'SLA + Öncelikli Destek',
    'Individuelle Schulung + Onboarding': 'Özel Eğitim + Oryantasyon',
    'Kontaktieren Sie uns': 'İletişime Geçin',

    '* Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': '* Fiyatlara KDV dahil değildir. CRM lisans maliyetleri (HubSpot, Pipedrive vb.) DAHİL DEĞİLDİR. Size uygun planı seçmenizde yardımcı oluruz.',

    # FAQ section
    'Häufig <span class="text-gradient">gestellte Fragen</span>': 'Sık Sorulan <span class="text-gradient">Sorular</span>',
    '💰 Welches CRM soll ich wählen?': '💰 Hangi CRM\'i seçmeliyim?',
    '<strong>HubSpot:</strong> Am besten für Marketing + Vertrieb zusammen. Kostenlose Version verfügbar, später ab €50/Monat.<br><br><strong>Pipedrive:</strong> Einfaches Sales-CRM. €14/Monat pro Nutzer. Perfekt für kleine Teams.<br><br><strong>Zoho CRM:</strong> Günstigste Option. Ab €14/Monat. Gut für Startups.<br><br><strong>GoHighLevel:</strong> All-in-One für Agenturen. Ab €97/Monat.<br><br>Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': '<strong>HubSpot:</strong> Pazarlama + satış birlikte için en iyi. Ücretsiz sürüm mevcut, daha sonra ayda 50€\'dan başlayan.<br><br><strong>Pipedrive:</strong> Basit Satış CRM\'i. Kullanıcı başına ayda 14€. Küçük ekipler için mükemmel.<br><br><strong>Zoho CRM:</strong> En uygun fiyatlı seçenek. Ayda 14€\'dan başlayan. Startup\'lar için iyi.<br><br><strong>GoHighLevel:</strong> Ajanslar için hepsi bir arada. Ayda 97€\'dan başlayan.<br><br>Hangi sistemin bütçenize ve sürecinize uygun olduğu konusunda ücretsiz danışmanlık veriyoruz.',

    '⏱️ Wie lange dauert die Einrichtung?': '⏱️ Kurulum ne kadar sürer?',
    '<strong>Basic Setup:</strong> 3-5 Werktage<br><strong>Advanced Setup:</strong> 7-10 Werktage<br><br>Nach dem Kick-off-Call starten wir sofort. Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen.': '<strong>Temel Kurulum:</strong> 3-5 iş günü<br><strong>Gelişmiş Kurulum:</strong> 7-10 iş günü<br><br>Başlangıç görüşmesinden hemen sonra başlarız. Haftalık güncellemeler alırsınız ve istediğiniz zaman soru sorabilirsiniz.',

    '🔧 Brauche ich technische Kenntnisse?': '🔧 Teknik bilgiye ihtiyacım var mı?',
    '<strong>Nein.</strong> Wir richten alles schlüsselfertig ein. Sie bekommen Training, wie Sie das CRM nutzen, Leads bearbeiten und Reports ansehen. Nach dem Setup läuft alles automatisch.': '<strong>Hayır.</strong> Her şeyi anahtar teslim kuruyoruz. CRM\'i nasıl kullanacağınız, lead\'leri nasıl işleyeceğiniz ve raporları nasıl görüntüleyeceğiniz konusunda eğitim alırsınız. Kurulumdan sonra her şey otomatik çalışır.',

    '📊 Was sind Offline Conversions?': '📊 Çevrimdışı Dönüşümler nedir?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Verkauf passiert offline (Anruf, Meeting, Rechnung). <strong>Offline Conversions</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads normalde sadece tıklamaları ve form gönderimlerini görür. Ancak gerçek satış çevrimdışı gerçekleşir (arama, toplantı, fatura). <strong>Çevrimdışı Dönüşümler</strong> bu verileri Google\'a geri gönderir. Sonuç: Google hangi tıklamaların gerçek müşterilere yol açtığını bilir ve kampanyalarınızı sadece lead\'ler yerine ciro için otomatik olarak optimize eder. <strong>ROAS ortalama %30-50 artar.</strong>',

    '💬 Wie funktionieren Telegram-Benachrichtigungen?': '💬 Telegram bildirimleri nasıl çalışır?',
    'Sobald ein Lead von Ihrer Website kommt, bekommt Ihr Sales-Manager eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Telefon, Quelle (Google Ads/Meta/etc.). Manager kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Web sitenizden bir lead gelir gelmez, satış yöneticiniz Telegram\'da (veya Slack/WhatsApp) bir mesaj alır. Mesaj şunları içerir: İsim, E-posta, Telefon, Kaynak (Google Ads/Meta/vb.). Yönetici hemen tepki verebilir. <strong>Ortalama yanıt süresi: 5 dakikanın altında.</strong>',

    '🔄 Bietet ihr auch laufende Betreuung?': '🔄 Devam eden destek sunuyor musunuz?',
    'Das Setup ist einmalig. Danach arbeitet alles automatisch. Falls Sie später weitere Automations, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Kurulum tek seferliktir. Sonrasında her şey otomatik çalışır. Daha sonra ek otomasyonlar, ekstra entegrasyonlar veya optimizasyonlar gerekirse, bizi istediğiniz zaman görevlendirebilirsiniz. Saatlik ücret: 99€/saat.',

    # CTA section
    'Bereit, Ihr CRM zu verbinden?': 'CRM\'inizi bağlamaya hazır mısınız?',
    'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Ücretsiz Danışmanlık — doğru CRM\'i seçmenize yardım edelim',

    # Contact form
    'Ihr Name': 'Adınız',
    'Ihre E-Mail': 'E-postanız',
    'Ihre Telefonnummer (optional)': 'Telefon Numaranız (isteğe bağlı)',
    'Ihre Nachricht': 'Mesajınız',
    'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Şu an hangi CRM\'i kullanıyorsunuz? Ayda kaç lead alıyorsunuz?',
    'Kostenlose Beratung anfragen': 'Ücretsiz Danışmanlık Talep Et',
    'Antwort innerhalb von 24 Stunden. Keine Verpflichtung.': '24 saat içinde yanıt. Yükümlülük yok.',

    # Footer
    'Leistungen': 'Hizmetler',
    'Rechtliches': 'Yasal',
    'Datenschutz': 'Gizlilik Politikası',
    'Impressum': 'Künye',
    '&copy; 2025 Vermarkter. Alle Rechte vorbehalten.': '&copy; 2025 Vermarkter. Tüm hakları saklıdır.',
    'Ihre Marketing-Agentur für den DACH-Raum und Osteuropa.': 'DACH ve Doğu Avrupa için Pazarlama Ajansınız.',

    # Chatbot
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Merhaba! 👋 CRM entegrasyonu hakkında sorularınız mı var?',
    'Schreiben Sie Ihre Frage...': 'Sorunuzu yazın...',

    # Mixed German-Turkish patterns that need fixing
    'CRM Entegrasyonu für Marketing & Sales. HubSpot, Pipedrive, Zoho. Lead-Tracking, Çevrimdışı Dönüşümler, Telegram Bildirimleri. Keine verlorenen Leads mehr.': 'Pazarlama ve satış için CRM entegrasyonu. HubSpot, Pipedrive, Zoho. Lead takibi, çevrimdışı dönüşümler, Telegram bildirimleri. Artık kayıp lead yok.',
    'Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb. Lead-Tracking, Otomasyon, echtes ROAS.': 'Pazarlama kampanyalarınızı satışla birleştirin. Lead takibi, otomasyon, gerçek ROAS.',
    'Hallo! 👋 Haben Sie Fragen zur CRM Entegrasyonu?': 'Merhaba! 👋 CRM entegrasyonu hakkında sorularınız mı var?',
    'Ihre Marketing-Agentur für DACH und Osteuropa.': 'DACH ve Doğu Avrupa için Pazarlama Ajansınız.',
    'Das Setup ist tek seferlik. Danach arbeitet alles automatisch. Falls Sie später weitere Otomasyonen, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Kurulum tek seferliktir. Sonrasında her şey otomatik çalışır. Daha sonra ek otomasyonlar, ekstra entegrasyonlar veya optimizasyonlar gerekirse, bizi istediğiniz zaman görevlendirebilirsiniz. Saatlik ücret: 99€/saat.',
    'İletişimieren Sie uns': 'İletişime Geçin',
    'Fiyatlar zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': 'Fiyatlara KDV dahil değildir. CRM lisans maliyetleri (HubSpot, Pipedrive vb.) DAHİL DEĞİLDİR. Size uygun planı seçmenizde yardımcı oluruz.',
    '<strong>HubSpot:</strong> Am besten für Marketing + Sales zusammen. Kostenlose Version verfügbar, später ab €50/Monat.<br><br>': '<strong>HubSpot:</strong> Pazarlama + satış birlikte için en iyi. Ücretsiz sürüm mevcut, daha sonra ayda 50€\'dan başlayan.<br><br>',
    '<strong>Pipedrive:</strong> Einfaches Sales-CRM. €14/Monat pro User. Perfekt für kleine Teams.<br><br>': '<strong>Pipedrive:</strong> Basit Satış CRM\'i. Kullanıcı başına ayda 14€. Küçük ekipler için mükemmel.<br><br>',
    '<strong>Zoho CRM:</strong> Günstigste Option. Ab €14/Monat. Gut für Startups.<br><br>': '<strong>Zoho CRM:</strong> En uygun fiyatlı seçenek. Ayda 14€\'dan başlayan. Startup\'lar için iyi.<br><br>',
    '<strong>GoHighLevel:</strong> All-in-One für Agenturen. Ab €97/Monat.<br><br>': '<strong>GoHighLevel:</strong> Ajanslar için hepsi bir arada. Ayda 97€\'dan başlayan.<br><br>',
    'Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': 'Hangi sistemin bütçenize ve sürecinize uygun olduğu konusunda ücretsiz danışmanlık veriyoruz.',
    'Nach dem Kick-off-Call starten wir sofort. Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen.': 'Başlangıç görüşmesinden hemen sonra başlarız. Haftalık güncellemeler alırsınız ve istediğiniz zaman soru sorabilirsiniz.',
    '<strong>Nein.</strong> Wir richten alles für Sie ein. Sie bekommen eine Schulung, wie Sie das CRM nutzen, Leads bearbeiten und Reports ansehen. Nach dem Setup arbeitet alles automatisch.': '<strong>Hayır.</strong> Her şeyi biz kuruyoruz. CRM\'i nasıl kullanacağınız, lead\'leri nasıl işleyeceğiniz ve raporları nasıl görüntüleyeceğiniz konusunda eğitim alırsınız. Kurulumdan sonra her şey otomatik çalışır.',
    '📊 Was sind Çevrimdışı Dönüşümler?': '📊 Çevrimdışı Dönüşümler nedir?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Satış passiert offline (Anruf, Meeting, Rechnung). <strong>Çevrimdışı Dönüşümler</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads normalde sadece tıklamaları ve form gönderimlerini görür. Ancak gerçek satış çevrimdışı gerçekleşir (arama, toplantı, fatura). <strong>Çevrimdışı Dönüşümler</strong> bu verileri Google\'a geri gönderir. Sonuç: Google hangi tıklamaların gerçek müşterilere yol açtığını bilir ve kampanyalarınızı sadece lead\'ler yerine ciro için otomatik olarak optimize eder. <strong>ROAS ortalama %30-50 artar.</strong>',
    'Sobald ein Lead von Ihrer Web Sitesi kommt, bekommt Ihr Sales-Yönetici eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Telefon, Quelle (Google Ads/Meta/etc.). Yönetici kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Web sitenizden bir lead gelir gelmez, satış yöneticiniz Telegram\'da (veya Slack/WhatsApp) bir mesaj alır. Mesaj şunları içerir: İsim, E-posta, Telefon, Kaynak (Google Ads/Meta/vb.). Yönetici hemen tepki verebilir. <strong>Ortalama yanıt süresi: 5 dakikanın altında.</strong>',

    # Last remaining mixed patterns
    'Google Ads zeigt Klicks, aber keine Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. <strong style="color: #EF4444;">Ohne Çevrimdışı Dönüşümler verbrennen Sie Budget.</strong>': 'Google Ads tıklamaları gösterir, satışları değil. Hangi kampanyaların gerçek müşteri getirdiğini bilemezsiniz. <strong style="color: #EF4444;">Çevrimdışı dönüşümler olmadan bütçe yakarsınız.</strong>',
    'Lead kommt von der Web Sitesi → landet sofort im CRM → Yönetici bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Web sitesinden lead gelir → anında CRM\'e düşer → Yönetici Telegram bildirimi alır → 5 dakika içinde arama.',
    'Wir senden Satışsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Satış verilerini Google Ads ve Meta\'ya geri gönderiyoruz. Algoritmalar hangi tıklamaların gerçek müşteriye dönüştüğünü öğrenir. <strong>Otomatik olarak daha iyi ROAS.</strong>',
}

# Apply translations
for de, tr in translations.items():
    content = content.replace(de, tr)

# Write Turkish version
with open('tr/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Turkish CRM page created successfully!")
print("Translated phrases:", len(translations))
