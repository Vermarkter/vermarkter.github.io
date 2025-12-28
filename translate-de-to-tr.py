# -*- coding: utf-8 -*-
import re

# Read DE version (from tr/index.html which was copied from de)
with open('tr/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Dictionary of German → Turkish translations
translations = {
    # Meta and basic
    'lang="de"': 'lang="tr"',
    'Performance-Marketing für kleine Unternehmen in Europa. Google Ads, Meta Ads, TikTok. Transparente Ergebnisse, professioneller Support.': 'Avrupa\'daki küçük işletmeler için performans pazarlama. Google Ads, Meta Ads, TikTok. Şeffaf sonuçlar, profesyonel destek.',
    'Marketing Deutschland, Google Ads Europa, Meta Ads, Performance Marketing, ROI Hesaplayıcı': 'Türkiye Pazarlama, Avrupa Google Ads, Meta Ads, Performans Pazarlama, ROI Hesaplayıcı',

    # Navigation
    'Leistungen': 'Hizmetler',
    'Rechner': 'Hesaplayıcı',
    'Bewertungen': 'Yorumlar',
    'Kontakt': 'İletişim',

    # Hero Section
    'Für kleine Unternehmen in der EU': 'AB\'deki küçük işletmeler için',
    'Werbestart in der EU': 'AB\'de reklam başlat',
    'in 48 Stunden': '48 saat içinde',
    'Google Ads & Meta Ads für Ihr Business in Europa': 'Avrupa\'da işiniz için Google Ads ve Meta Ads',
    'Erste Leads in 7 Tagen': '7 günde ilk potansiyel müşteriler',
    'Technischer Manager in Ihrer Sprache': 'Kendi dilinizde teknik yönetici',
    'Wöchentliche Reports': 'Haftalık raporlar',
    'Gewinn berechnen': 'Kârı hesapla',
    'Unsere Cases': 'Projelerimiz',

    # Stats
    '% durchschn. ROAS': '% ortalama ROAS',
    '% Kunden kehren zurück': '% müşteri geri dönüyor',
    'Tage bis Launch': 'başlamaya kadar gün',

    # Problem Section
    'Warum verschwinden 80% des Budgets': 'Bütçenin %80\'i neden kayboluyor',
    'im Nichts': 'boşa',
    '% der Kampagnen scheitern': '% kampanya başarısız oluyor',
    'fehlende Transparenz': 'şeffaflık eksikliği',
    'Budget verbrannt ohne ROI': 'getiri olmadan yakılan bütçe',
    'Die drei häufigsten Gründe für gescheiterte Werbekampagnen': 'Başarısız reklam kampanyalarının üç ana nedeni',
    'Falsche Keywords': 'Yanlış anahtar kelimeler',
    'Sie zahlen für Klicks von Nutzern, die nie kaufen werden. 70% des Traffics sind "informationelle" Suchanfragen ohne Kaufabsicht.': 'Asla satın almayacak kullanıcıların tıklamaları için ödeme yapıyorsunuz. Trafiğin %70\'i satın alma niyeti olmayan "bilgi" aramaları.',
    'Breiter Match-Type – Sie zahlen für alles Mögliche': 'Geniş eşleşme türü – her şey için ödeme yapıyorsunuz',
    'Keine negativen Keywords – Budget läuft aus': 'Negatif anahtar kelime yok – bütçe tükeniyor',
    'Werbung für Konkurrenten statt Zielgruppe': 'Hedef kitle yerine rakipler için reklam',
    'Fehlendes End-to-End Tracking': 'Uçtan uca izleme eksikliği',
    'Ohne korrektes Tracking wissen Sie nicht, welche Anzeige/Keywords Verkäufe bringen. Sie steuern blind.': 'Doğru izleme olmadan hangi reklam/anahtar kelimelerin satış getirdiğini bilemezsiniz. Kör bir şekilde yönetiyorsunuz.',
    'Google Analytics falsch konfiguriert': 'Google Analytics yanlış yapılandırılmış',
    'Conversions werden nicht an Ads übermittelt': 'Dönüşümler Ads\'e iletilmiyor',
    'Keine Attribution – Customer Journey unklar': 'Atfetme yok – müşteri yolculuğu belirsiz',
    'Schwache Creatives': 'Zayıf kreatifler',
    'Niedrige CTR = hoher CPC. Schlechte Texte und Banner senken den Quality Score und Sie zahlen für jeden Klick mehr.': 'Düşük TO = yüksek TBM. Kötü metinler ve banner\'lar Kalite Puanını düşürür ve her tıklama için daha fazla ödeme yaparsınız.',
    'Generische Texte ohne USP – niemand klickt': 'UÖN olmadan genel metinler – kimse tıklamıyor',
    'Banner in Paint erstellt – sieht aus wie Spam': 'Paint\'te oluşturulan banner\'lar – spam gibi görünüyor',
    'Keine A/B-Tests – Sie bleiben beim ersten Entwurf': 'A/B testi yok – ilk taslakta kalıyorsunuz',

    # Method Section
    'Unsere Methodik: 3-Stufen-System': 'Metodolojimiz: 3 Aşamalı Sistem',
    'SCHRITT 1': 'ADIM 1',
    'SCHRITT 2': 'ADIM 2',
    'SCHRITT 3': 'ADIM 3',
    'Tiefgehende Analyse': 'Derinlemesine analiz',
    'Wir finden, wo Ihr Budget verschwindet. Analyse von Wettbewerbern, Semantik und technischen Fehlern.': 'Bütçenizin nerede kaybolduğunu buluyoruz. Rakiplerin, semantiğin ve teknik hataların analizi.',
    'Nischenanalyse': 'Niş analizi',
    'Suche nach "Gold"-Keywords': '"Altın" anahtar kelimelerin aranması',
    'Technisches Audit': 'Teknik denetim',
    'Wettbewerber-Mapping': 'Rakip haritalama',
    'Kampagnen Launch': 'Kampanya başlatma',
    'Struktur und Launch': 'Yapı ve başlatma',
    'Wir erstellen Kampagnen mit +8% CTR und Conversion-Tracking ab Tag 1. Keine Experimente.': '+%8 TO ve 1. günden dönüşüm izleme ile kampanyalar oluşturuyoruz. Deney yok.',
    'Strukturierung nach Intent': 'Amaca göre yapılandırma',
    'Conversion-Setup (GA4 + Ads)': 'Dönüşüm kurulumu (GA4 + Ads)',
    'Creatives (Texte + Banner)': 'Kreatifler (metinler + banner\'lar)',
    'Erster Traffic in 48h': '48 saatte ilk trafik',
    'Wöchentliche Optimierung': 'Haftalık optimizasyon',
    'Optimierung': 'Optimizasyon',
    'Wir analysieren jeden €, pausieren teure Keywords und skalieren profitable Kampagnen.': 'Her €\'yu analiz ediyor, pahalı anahtar kelimeleri duraklatıyor ve kârlı kampanyaları ölçeklendiriyoruz.',
    'Search Terms Analyse': 'Arama terimlerini analiz',
    'Bid-Anpassungen': 'Teklif ayarlamaları',
    'Creative-Tests (A/B)': 'Kreatif testleri (A/B)',
    'A/B-Testing': 'A/B testi',
    'Reporting': 'Raporlama',
    'Analytics-Setup': 'Analitik kurulumu',
    'Anzeigenerstellung': 'Reklam oluşturma',
    'Kampagnen-Launch': 'Kampanya başlatma',
    'Bereit zu wachsen?': 'Büyümeye hazır mısınız?',
    'Lassen Sie uns Ihr Business skalieren': 'İşinizi ölçeklendirmemize izin verin',
    'Wir bauen Kampagnen nach SKAG-Prinzip. Klares Conversion-Tracking.': 'SKAG ilkesine göre kampanyalar oluşturuyoruz. Net dönüşüm izleme.',

    # Services Section
    'Full Stack Marketing Services': 'Tam Yığın Pazarlama Hizmetleri',
    'Full Stack <span class="text-gradient">Marketing Services</span>': 'Tam Yığın <span class="text-gradient">Pazarlama Hizmetleri</span>',
    'Von der Strategie bis zur Umsetzung – alles aus einer Hand': 'Stratejiden uygulamaya – hepsi tek elden',
    'Heißer Traffic aus der Suche. Performance Max für E-Commerce. Shopping Ads für Produkte.': 'Aramadan sıcak trafik. E-ticaret için Performance Max. Ürünler için Shopping Ads.',
    'Heißer Traffic aus der Suche. Performance Max für E-Commerce. Shopping Ads für Produkte. 48 saat içinde başlatma.': 'Aramadan sıcak trafik. E-ticaret için Performance Max. Ürünler için Shopping Ads. 48 saatte başlatma.',
    'Performance Max (KI-Optimierung)': 'Performance Max (YZ optimizasyonu)',
    'Shopping Ads (für Online-Shops)': 'Shopping Ads (çevrimiçi mağazalar için)',
    'Local SEO (Google Business Profile)': 'Yerel SEO (Google İşletme Profili)',
    'Meta Ads (FB + IG)': 'Meta Ads (FB + IG)',
    'Lead-Generierung und Verkäufe über Facebook und Instagram. Lookalike Audiences, Remarketing, Messenger Ads.': 'Facebook ve Instagram üzerinden potansiyel müşteri oluşturma ve satışlar. Benzer Kitleler, Yeniden Pazarlama, Messenger Reklamları.',
    'TikTok Ads': 'TikTok Ads',
    'Viraler Content und junge Zielgruppe. In-Feed Ads, Spark Ads, Shopping Ads. Günstiger Traffic für E-Commerce.': 'Viral içerik ve genç hedef kitle. In-Feed Reklamlar, Spark Reklamlar, Shopping Reklamlar. E-ticaret için ucuz trafik.',
    'SEO Optimierung': 'SEO Optimizasyonu',
    'Organischer Traffic aus Google. Lokales SEO für die EU. Content-Marketing und Linkbuilding. Langfristige Ergebnisse.': 'Google\'dan organik trafik. AB için yerel SEO. İçerik pazarlama ve bağlantı oluşturma. Uzun vadeli sonuçlar.',
    'CRM Integration': 'CRM Entegrasyonu',
    'Integracja CRM': 'CRM Entegrasyonu',
    'Alle Leads automatisch in Telegram/Google Sheets. Email/SMS Auto-Funnels. Volle Kontrolle über Ihren Sales Funnel.': 'Tüm potansiyel müşteriler otomatik olarak Telegram/Google Sheets\'te. E-posta/SMS Oto-Hunileri. Satış huniniz üzerinde tam kontrol.',
    'Telegram Bot für Leads (sofortige Benachrichtigungen)': 'Potansiyel müşteriler için Telegram Botu (anında bildirimler)',
    'Email Marketing (Mailchimp, SendGrid)': 'E-posta Pazarlama (Mailchimp, SendGrid)',
    'Zapier/Make.com Integrationen': 'Zapier/Make.com entegrasyonları',
    'Web Analytics': 'Web Analitiği',
    'Analityka webowa': 'Web Analitiği',
    'GA4, GTM, Hotjar, Microsoft Clarity. Vollständiges Verständnis des Nutzerverhaltens. Dashboards in Looker Studio.': 'GA4, GTM, Hotjar, Microsoft Clarity. Kullanıcı davranışının tam anlayışı. Looker Studio\'da panolar.',
    'GA4 Setup (Enhanced Ecommerce)': 'GA4 Kurulumu (Gelişmiş E-ticaret)',
    'Heatmaps & Session Recordings (Hotjar)': 'Isı Haritaları ve Oturum Kayıtları (Hotjar)',
    'Custom Dashboards (Looker Studio)': 'Özel Panolar (Looker Studio)',
    'Tägliche Gebotsanpassungen. Budget-Skalierung nur bei positivem ROAS.': 'Günlük teklif ayarlamaları. Yalnızca pozitif ROAS ile bütçe ölçeklendirme.',

    # Pricing Section
    'Transparente Preise': 'Şeffaf Fiyatlar',
    'Cennik <span class="text-gradient">i pakiety</span>': 'Fiyatlandırma <span class="text-gradient">ve paketler</span>',
    'Transparente Cennik ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Gizli maliyet olmayan şeffaf fiyatlandırma. İşletmeniz için mükemmel paketi seçin.',
    'Starter': 'Başlangıç',
    'Perfekt für den Einstieg': 'Başlangıç için mükemmel',
    'Pro Monat': 'Aylık',
    'Was ist enthalten:': 'Neler dahil:',
    'Strategie-Call': 'Strateji görüşmesi',
    'Keyword-Recherche': 'Anahtar kelime araştırması',
    'Campaign Setup': 'Kampanya kurulumu',
    'Wöchentliches Reporting': 'Haftalık raporlama',
    'Monatliche Optimierung': 'Aylık optimizasyon',
    'Jetzt starten': 'Şimdi başla',
    'Wachstum': 'Büyüme',
    'Tägliche Optimierung': 'Günlük optimizasyon',
    'Dedicated Account Manager': 'Özel Hesap Yöneticisi',
    'Erstellung von Anzeigen-Creatives': 'Reklam kreatiflerinin oluşturulması',
    'Business': 'İş',
    'Rechtliche Unterstützung für EU': 'AB için yasal destek',
    'Kontakt aufnehmen': 'İletişime geçin',

    # Calculator Section
    'ROI-Rechner': 'ROI Hesaplayıcı',
    'Berechnen Sie die Rentabilität Ihrer Werbekampagne': 'Reklam kampanyanızın kârlılığını hesaplayın',
    'Dies ist ein echtes Mediaplanungs-Tool.': 'Bu gerçek bir medya planlama aracıdır.',
    'Dieselben Formeln, die große Agenturen verwenden. Transparent, ehrlich, ohne versteckte Kosten.': 'Büyük ajansların kullandığı aynı formüller. Şeffaf, dürüst, gizli maliyet yok.',
    'Wählen Sie Ihre Branche:': 'Sektörünüzü seçin:',
    'Monatliches Budget': 'Aylık bütçe',
    'Kosten pro Klick': 'Tıklama başına maliyet',
    'Conversion Rate': 'Dönüşüm oranı',
    'Durchschnittlicher Bestellwert': 'Ortalama sipariş değeri',
    'Gewinnmarge': 'Kâr marjı',
    'Klicks': 'Tıklamalar',
    'Leads': 'Potansiyel Müşteriler',
    'Gewinn': 'Kâr',
    'Strategie für diese Zahlen erhalten': 'Bu rakamlar için strateji edinin',
    'Das Ergebnis ist eine Prognose, kein Versprechen.': 'Sonuç bir tahmindir, söz değil.',
    'Marketing beginnt mit ehrlichen Zahlen.': 'Pazarlama dürüst rakamlarla başlar.',

    # Testimonials
    'Kundenbewertungen': 'Müşteri Yorumları',
    'Über 100 erfolgreiche Projekte für kleine Unternehmen in der EU': 'AB\'deki küçük işletmeler için 100\'den fazla başarılı proje',
    'München': 'Münih',
    'Berlin': 'Berlin',
    'Warschau': 'Varşova',
    'Düsseldorf': 'Düsseldorf',
    'Bau': 'İnşaat',
    'Kosmetik': 'Kozmetik',
    'E-commerce': 'E-ticaret',

    # FAQ
    'Häufig gestellte Fragen': 'Sıkça Sorulan Sorular',
    'Alles, was Sie über unsere Dienstleistungen wissen müssen': 'Hizmetlerimiz hakkında bilmeniz gereken her şey',
    'Wie schnell kann ich mit Ergebnissen rechnen?': 'Ne kadar çabuk sonuç bekleyebilirim?',
    'Erste Ergebnisse sehen Sie in der Regel innerhalb von 48-72 Stunden nach dem Launch. Optimale Performance erreichen Kampagnen nach 2-4 Wochen Optimierung.': 'İlk sonuçları genellikle başlatmadan 48-72 saat içinde görürsünüz. Optimal performans, 2-4 haftalık optimizasyondan sonra kampanyalara ulaşır.',
    'Benötige ich eine eigene Website?': 'Kendi web siteme ihtiyacım var mı?',
    'Nicht unbedingt. Wir können für Sie eine konversionsstarke Landing Page erstellen oder Sie können unsere vorgefertigten Templates verwenden.': 'Mutlaka değil. Sizin için yüksek dönüşümlü bir açılış sayfası oluşturabiliriz veya hazır şablonlarımızı kullanabilirsiniz.',
    'Gibt es eine Mindestvertragslaufzeit?': 'Minimum sözleşme süresi var mı?',
    'Ja, die Mindestvertragslaufzeit beträgt 3 Monate. Dies gibt uns genügend Zeit, um Ihre Kampagnen zu optimieren und echte Ergebnisse zu liefern. Danach keine Bindung.': 'Evet, minimum sözleşme süresi 3 aydır. Bu bize kampanyalarınızı optimize etmek ve gerçek sonuçlar sunmak için yeterli zaman verir. Sonrasında bağlayıcılık yok.',
    'In welchen Ländern arbeiten Sie?': 'Hangi ülkelerde çalışıyorsunuz?',
    'Wir sind auf den EU-Markt spezialisiert: Deutschland, Polen, Tschechien, Österreich und andere EU-Länder. Wir kennen die lokalen Besonderheiten jedes Marktes.': 'AB pazarında uzmanız: Almanya, Polonya, Çekya, Avusturya ve diğer AB ülkeleri. Her pazarın yerel özelliklerini biliyoruz.',
    'Welches Budget sollte ich für Werbung einplanen?': 'Reklam için ne kadar bütçe planlamalıyım?',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen: €1.000-1.500/Monat. Nutzen Sie unseren ROI-Kalkulator oben für eine genaue Prognose.': 'Bu, nişinize ve hedeflerinize bağlıdır. Etkili kampanyalar için minimum bütçe: ayda €1.000-1.500. Kesin bir tahmin için yukarıdaki ROI hesaplayıcımızı kullanın.',

    # Contact Section
    'Bereit zu starten?': 'Başlamaya hazır mısınız?',
    'Kontaktieren Sie uns für ein technisches Audit oder eine Erstberatung': 'Teknik denetim veya ilk danışmanlık için bizimle iletişime geçin',
    'Sprechen Sie mit einem Experten': 'Bir uzmanla konuşun',
    'Ihr Name': 'Adınız',
    'Ihre E-Mail': 'E-postanız',
    'Ihre Nachricht': 'Mesajınız',
    'Beschreiben Sie Ihr Projekt...': 'Projenizi açıklayın...',
    'Nachricht senden': 'Mesaj gönder',
    'Vielen Dank! Wir melden uns in Kürze bei Ihnen.': 'Teşekkürler! Kısa sürede sizinle iletişime geçeceğiz.',
    'Oder kontaktieren Sie uns direkt:': 'Veya doğrudan bizimle iletişime geçin:',

    # Footer
    'Marketing-Agentur für kleine Unternehmen in der Europäischen Union.': 'Avrupa Birliği\'ndeki küçük işletmeler için pazarlama ajansı.',
    'Folgen Sie uns': 'Bizi takip edin',
    'Rechtliches': 'Yasal Bilgiler',
    'Datenschutz': 'Gizlilik Politikası',
    'Impressum': 'Yasal Uyarı',

    # Additional missing translations
    'Performance-Marketing für Unternehmen. Transparente Ergebnisse, professioneller Support.': 'İşletmeler için performans pazarlama. Şeffaf sonuçlar, profesyonel destek.',
    'Die SEO-Strategie funktioniert! In 4 Monaten sind wir in den Top 3 für alle Keywords. Organischer Traffic ist um 300% gestiegen.': 'SEO stratejisi çalışıyor! 4 ayda tüm anahtar kelimeler için ilk 3\'teyiz. Organik trafik %300 arttı.',
    'Transparente Preise ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Gizli maliyet olmadan şeffaf fiyatlar. İşletmeniz için mükemmel paketi seçin.',
    'Şeffaf Fiyatlar ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Gizli maliyet olmadan şeffaf fiyatlar. İşletmeniz için mükemmel paketi seçin.',
    'ohne versteckte Kosten': 'gizli maliyet olmadan',
    'Wählen Sie das perfekte Paket für Ihr Unternehmen': 'İşletmeniz için mükemmel paketi seçin',
    'für Ihr Unternehmen': 'işletmeniz için',
    'für alle Keywords': 'tüm anahtar kelimeler için',
    'für effektive Kampagnen': 'etkili kampanyalar için',
    'für ein technisches Audit': 'teknik denetim için',
    'für eine Erstberatung': 'ilk danışmanlık için',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen': 'Bu, nişinize ve hedeflerinize bağlıdır. Etkili kampanyalar için minimum bütçe',
}

# Apply translations
for de, tr in translations.items():
    content = content.replace(de, tr)

# Write result
with open('tr/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Turkish translation completed!")
