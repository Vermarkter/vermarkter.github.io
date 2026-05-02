#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
elite_patch_berlin.py — One-shot patch: upload Director's elite messages + compliment_detail.

Reads the two datasets (VIP 10 + full 41) provided by the Director,
picks the best message for each ID (VIP B-variant first, then full A-variant),
strips all hyperlinks per CTO security order, validates style,
then PATCHes: custom_message + compliment_detail + status='READY TO SEND'.

Usage:
  python scripts/elite_patch_berlin.py              # live write
  python scripts/elite_patch_berlin.py --dry-run    # preview only
"""

import sys, io, json, re, argparse, os, urllib.request, urllib.parse, configparser

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

# ---------------------------------------------------------------------------
# Dataset A — VIP 10 (Director's final messages, already B-variant quality)
# Key: id → msg
# ---------------------------------------------------------------------------
VIP_MESSAGES = {
    171: "Hallo Shibaar Team! Euer Ruf kommt von eurer Arbeit – nicht von eurem Internetauftritt. Das Problem: Genau das kostet euch jeden Monat neue Kunden. Wer euch nicht persönlich kennt, findet keine sichere Buchungsmöglichkeit. 23 Berliner Betriebe haben diesen Schritt bereits gemacht. Antworte mit „Video", wenn ich dir zeigen soll, wie das konkret aussieht.",
    172: "Hey Josh Flagg Team! 💈 Euer Fade-Finish auf Instagram ist handwerklich auf einem Level, das in Berlin nur wenige erreichen. Und trotzdem: josh-flagg.de hat kein SSL. Browser zeigen Neukunden 'Nicht sicher' – bevor sie überhaupt den Buchungsbutton sehen. 23 Berliner Salons haben genau das geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll.",
    173: "Hey Remz! ✂️ Deine Skin Fades auf @barberremz sind das, wofür Kunden aus ganz Berlin extra fahren. Aber berlin-barber.de hat kein SSL-Zertifikat. Wer dich auf Insta entdeckt, sieht eine Browserwarnung statt deines Terminformulars. 23 Berliner Salons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll.",
    174: "Hallo Team von Tommy Shelby Barber! 💈 Der Name allein hat Klasse. Das Problem: Jeder Termin läuft über Treatwell – das bedeutet Provision für jeden Kunden, den ihr selbst aufgebaut habt. Eure Kunden, fremde Plattform, eure Rechnung. 23 Berliner Salons sind bereits unabhängig. Antworte mit „Video", wenn ich dir zeigen soll, wie du dich befreist.",
    186: "Hey Nail! ✂️ Meistertitel in Köln, Training in Rotterdam – dein Handwerk ist Weltklasse. Und trotzdem: shapes.salon hat kein SSL. Kunden, die dich über Empfehlung finden, sehen sofort eine Browserwarnung. Dieser Kontrast ist vermeidbar. 23 Berliner Salons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll.",
    197: "Sehr geehrter Herr Schewe, Ihr Instagram mit 11.000 Followern zeigt Balayage-Verläufe auf höchstem Niveau. Aber ich habe zeitraum.berlin getestet: kein aktives SSL. Bei 1.500+ Bewertungen ist das ein Widerspruch, den Kunden sofort bemerken. 23 Berliner Top-Salons haben diesen Kontrast bereits eliminiert. Antworten Sie mit „Video", wenn ich Ihnen das Beispiel zeigen soll.",
    206: "Sehr geehrter Herr Pelz, Ihr Salon hat den iF Design Award gewonnen – das ist einzigartig in Berlin. Aber michapelz.de hat aktuell ein SSL-Problem. Die Sorgfalt, die Sie in jeden Cut stecken, fehlt online. 23 Berliner Spitzensalons haben diesen Standard bereits korrigiert. Antworten Sie mit „Video", wenn ich Ihnen zeigen darf, wie wir das lösen.",
    208: "Sehr geehrte Frau Nieschke, Ihre Karriere von Udo Walz bis zu den Bambi-Stylings verdient höchsten Respekt. Aber coiffeur-paluselli.com hat kein SSL. Für ein Konzept auf Ihrem Niveau ist die Browser-Warnung 'Nicht sicher' ein kritischer Widerspruch. 23 Berliner Premiumsalons haben das bereits behoben. Antworten Sie mit „Video", wenn ich Ihnen die Lösung zeigen darf.",
    209: "Sehr geehrtes FINE & DANDY Team, eure Balayage-Looks mit AVEDA sind seit 2008 eine Institution in Berlin. Aber fineanddandy.de hat ein SSL-Problem. Browser zeigen eine Sicherheitswarnung – das passt nicht zu eurem Qualitätsanspruch. 23 Berliner Premiumsalons haben das gelöst. Antworten Sie mit „Video", wenn ich Ihnen das Video-Demo zusenden darf.",
    211: "Sehr geehrtes St Leonard Team, @stleonardberlin zeigt echte Londoner Barbering-Tradition. Aber stleonard.de hat kein SSL-Zertifikat. Kunden, die euren Ruf kennen, sehen beim Öffnen der Seite eine Warnung. 23 Berliner Salons dieser Klasse haben das bereits behoben. Antworten Sie mit „Video", wenn ich Ihnen zeigen darf, wie wir eure Unabhängigkeit sichern.",
}

# ---------------------------------------------------------------------------
# Dataset B — Full 41 leads (A-variant, Director's JSON)
# We use variant A for all non-VIP leads; VIP IDs are overridden by VIP_MESSAGES above.
# compliment_detail extracted from the A-text opening (before first '. ')
# ---------------------------------------------------------------------------
FULL_DATA = [
    {"id": 171, "salon": "Friseur Shibaar", "instagram": None, "A": "Hey Friseur Shibaar! Ich habe euren Salon durch Berliner Empfehlungen gefunden – Stammkunden, die seit Jahren kommen, sprechen für sich. Aber ich habe festgestellt: Wer euch googelt, sieht keine sichere Website. Das bedeutet, jemand der euch empfohlen bekommt, verlässt die Seite nach 3 Sekunden. Schon 23 Berliner Salons haben das Problem gelöst und berichten von messbarem Wachstum bei Neukunden. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 172, "salon": "Josh Flagg Barbershop", "instagram": "@joshflaggbarbershop", "A": "Hey Josh Flagg Team! 💈 Euer Fade-Finish auf Instagram ist handwerklich auf einem Level, das in Berlin nur wenige erreichen – der Übergang am Nacken in eurem letzten Reel ist absolut sauber. Und trotzdem: kein SSL. Browser zeigen Neukunden 'Nicht sicher' – bevor sie überhaupt den Buchungsbutton sehen. 23 Berliner Salons haben genau das geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 173, "salon": "Barberremz", "instagram": "@barberremz", "A": "Hey Remz! ✂️ Deine Skin Fades auf @barberremz sind das, wofür Kunden aus ganz Berlin extra fahren – die Kanten-Arbeit ist auf einem anderen Level. Aber kein SSL-Zertifikat. Wer dich auf Instagram entdeckt und direkt buchen will, sieht eine Browserwarnung statt eines Terminformulars. 23 Berliner Salons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 174, "salon": "Tommy Shelby Barber", "instagram": None, "A": "Hey Tommy Shelby Barber! 💈 Der Name allein hat Klasse – und wer Peaky-Blinders-Flair in den Barberstuhl bringt, hat einen klaren Stil. Das Problem: Jeder Termin läuft über Treatwell – das bedeutet Provision für jeden Kunden, den ihr selbst aufgebaut habt. 23 Berliner Salons sind bereits unabhängig. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 175, "salon": "Barber Brothers 2", "instagram": "@brothers_barbershop_berlin", "A": "Hey Barber Brothers 2! ✂️ Euer Instagram zeigt ein Team, das aufeinander eingespielt ist – saubere Textured Crops, konsistente Fades, jeder Cut auf gleichem Niveau. Das verdient eine Online-Präsenz, die genauso verlässlich ist. Aber keine eigene Website gefunden. 23 Berliner Betriebe haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 176, "salon": "MBC Barbershop Berlin", "instagram": "@mbcfriseur", "A": "Hey MBC Barbershop! 👋 @mbcfriseur zeigt Vielseitigkeit – von Damen-Styling bis klassischem Herrenschnitt, das Team beherrscht beides. Aber kein SSL. Neukunden, die euch entdecken, sehen als erstes eine Browserwarnung statt eurer Arbeit. 23 Berliner Salons haben diesen ersten Eindruck geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 177, "salon": "Mado Barbershop", "instagram": "@madobarbershop", "A": "Hey Mado Barbershop! 💈 @madobarbershop zeigt immer wieder diese Skin Fades mit Rasiermesser-Finish – die Präzision an der Schläfe ist in Berlin eine Seltenheit. Das ist Handwerk auf höchstem Niveau. Und trotzdem kein gültiges SSL. Wer euren Reel sieht und dann eure Seite öffnet, sieht eine rote Warnung. 23 Berliner Salons haben das bereits geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 178, "salon": "Al-Kabir Barber Berlin", "instagram": None, "A": "Hey Al-Kabir Barber! 👋 Eure Google-Bewertungen erzählen von sauberer Arbeit, persönlichem Service und Kunden, die immer wiederkommen. Das ist echter Ruf – aufgebaut durch Können. Aber kein SSL, keine sichere Webpräsenz. Neukunden sehen eine technische Warnung statt eurer Qualität. 23 Berliner Salons haben diesen Schritt gemacht. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 179, "salon": "Sabri Berber Coiffeur", "instagram": None, "A": "Hallo Sabri Berber Coiffeur! 💈 Traditionelle türkische Rasur mitten in Berlin – das ist ein Handwerk, das nicht jeder beherrscht. Eure Stammkunden wissen das. Aber online findet man euch kaum: keine Webseite, kein Instagram. Wer durch Empfehlung von euch hört und googelt, findet keine Möglichkeit zu buchen. 23 Berliner Salons haben diesen Schritt gemacht. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 180, "salon": "RIDVAN's BARBERSHOP", "instagram": None, "A": "Hey RIDVAN'S BARBERSHOP! ✂️ Eure Kunden kommen wegen persönlicher Betreuung und verlässlicher Qualität – das zeigen eure Bewertungen klar. Aber keine eigene Website, kein SSL. Wer euch online sucht, landet auf einer Seite mit Sicherheitswarnung – und klickt sofort weg. 23 Berliner Salons haben diesen Standard bereits. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 181, "salon": "Çetin's GENTLEMEN'S BARBER", "instagram": None, "A": "Hey Çetin's GENTLEMEN'S BARBER! 🎩 Der Anspruch ist im Namen: Gentlemen-Niveau. Eure Stammkunden kennen das. Aber: keine eigene Website, keine Instagram-Präsenz. Wer euch durch Empfehlung findet und googelt, sieht keinen Buchungsbutton – und wählt den nächsten Salon, der online verfügbar ist. 23 Berliner Betriebe haben diesen Schritt gemacht. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 182, "salon": "Haircut Barbershop Berlin", "instagram": None, "A": "Hey Haircut Barbershop Berlin! ✂️ Eure Google-Bewertungen zeigen einen Salon, dem Stammkunden treu bleiben – das ist das stärkste Qualitätssignal. Aber kein SSL. Mobile Nutzer sehen beim ersten Besuch der Seite eine Sicherheitswarnung. Das ist ein Problem, das ihr nicht sehen könnt, aber eure Kunden schon. 23 Berliner Salons haben es behoben. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 183, "salon": "BERBERIUM", "instagram": None, "A": "Hey BERBERIUM! 💈 Der Name klingt wie eine Marke mit Zukunft. Aber online findet man euch nicht – keine Website, kein Instagram. In Berlin eröffnen jeden Monat neue Barbershops, die alle auf Social Media aktiv sind. Wer heute unsichtbar ist, verliert morgen die Kunden, die er noch nicht kennt. 23 Berliner Betriebe haben ihre Online-Präsenz aufgebaut. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 184, "salon": "Berberlin", "instagram": None, "A": "Hey Berberlin! 💈 Euer Treatwell-Profil zeigt solide Bewertungen – Kunden, die kommen und zufrieden gehen. Aber: Jeder dieser Termine kostet euch Provision. Ihr habt keine eigene Webseite und keine direkte Beziehung zu euren Kunden – alles läuft durch eine Plattform, die täglich wächst und die Preise anpassen kann. 23 Berliner Salons sind bereits unabhängig. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 185, "salon": "BEJTA Beauty Coiffeur", "instagram": None, "A": "Hey BEJTA Beauty Coiffeur! 💄 Haare und Kosmetik unter einem Dach – das ist in Berlin ein echtes Alleinstellungsmerkmal. Aber kein SSL-Zertifikat. Gerade für einen Beauty-Salon ist Vertrauen das Fundament – und wer eure Seite aufruft, sieht als erstes eine Sicherheitswarnung. Das widerspricht allem, wofür ihr steht. 23 Berliner Betriebe haben dieses Problem gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 186, "salon": "Shapes Barbershop", "instagram": "shapes.salon", "A": "Hey Nail von Shapes Barbershop! ✂️ Meistertitel in Köln, Training in Rotterdam, und die Bewertungen zeigen: du erinnerst dich nach über einem Jahr noch an den letzten Cut deines Kunden – weil du Notizen machst. Das ist Handwerk auf Weltklasse-Niveau. Und trotzdem: kein SSL. Kunden, die dich über Empfehlung finden und die URL tippen, sehen sofort eine Browserwarnung. 23 Berliner Salons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 187, "salon": "Anton Friseur und Kosmetik", "instagram": None, "A": "Hey Anton Friseur und Kosmetik! 🌿 Friseur und Kosmetik kombiniert – das ist ein Konzept, das Kunden bindet. Aber ihr seid ausschließlich über Treatwell buchbar: keine eigene Seite, keine eigene Kundendatenbank. Jeder Termin, den ihr verdient habt, läuft durch eine Plattform, die euch dafür berechnet. 23 Berliner Betriebe haben Direktbuchungen aufgebaut. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 188, "salon": "Boulevard Herrenfriseur", "instagram": None, "A": "Hey Boulevard Herrenfriseur! 💈 Als Herrenspezialist in Berlin habt ihr eine klare Nische. Aber ihr seid nur über Treatwell buchbar – keine eigene Website, keine eigene Kundenbasis. Das bedeutet: wenn Treatwell morgen die Konditionen ändert, seid ihr direkt betroffen. 23 Berliner Salons haben ihre Unabhängigkeit zurückgewonnen. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 189, "salon": "BERLIN BARBER LOUNGE", "instagram": None, "A": "Hey BERLIN BARBER LOUNGE! 🛋️ Eine Lounge – das ist mehr als ein Haarschnitt, das ist ein Erlebnis. Aber online ist dieses Erlebnis unsichtbar: keine Webseite, keine Instagram-Präsenz. Wer von euch hört und euch sucht, findet keine sichere Möglichkeit zu buchen. 23 Berliner Betriebe haben das geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 190, "salon": "Maxat Friseur", "instagram": None, "A": "Hey Maxat Friseur! 👋 Eure Google-Bewertungen zeigen persönliche Atmosphäre und faire Beratung – das ist in Berlin selten geworden. Aber kein SSL. Mobile Nutzer sehen beim ersten Klick eine Sicherheitswarnung. Die Mehrheit bricht genau da ab – nicht wegen eurer Arbeit, sondern wegen einer technischen Kleinigkeit. 23 Berliner Salons haben diese Kleinigkeit behoben. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 191, "salon": "Veit Friseure Berlin", "instagram": "@veitfriseure", "A": "Hey Veit Friseure Berlin! ✂️ @veitfriseure zeigt ein LGBTQ+ freundliches Team, das von Modern bis Klassisch alles beherrscht – und das in einem Salon mit echtem Stil. Ich habe aber festgestellt, dass technische Sicherheitsprobleme bei mobilen Nutzern Warnungen auslösen. Euer Ruf und eure Werte verdienen eine Website, die genauso verlässlich ist wie euer Team. 23 Berliner Salons haben diesen Standard. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 192, "salon": "HAIR MÜLLER", "instagram": None, "A": "Hey HAIR MÜLLER! 💇 Professionelle Beratung und hochwertiger Service – das ist das Feedback eurer Kunden über Jahre hinweg. Aber kein SSL-Zertifikat. Browser zeigen Besuchern eine rote Warnung. Wer noch kein Vertrauen zu euch hat, verlässt die Seite sofort. Euer langjähriger Ruf verdient einen besseren ersten Eindruck online. 23 Berliner Salons haben das geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 193, "salon": "Cut 121", "instagram": None, "A": "Hallo Cut 121 Berlin! ✂️ Ein herzliches Team, präzise Schnitte, strahlende Farben – so beschreiben euch eure Kunden auf Treatwell. Aber keine aktive SSL-gesicherte Seite. Neukunden, die euch googeln, finden keine vertrauenswürdige Buchungsmöglichkeit. Eure Qualität verdient eine Online-Präsenz auf gleichem Niveau. 23 Berliner Salons haben diesen Schritt gemacht. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 194, "salon": "Friseur By Hazem", "instagram": None, "A": "Hey Friseur By Hazem! 💇 Stammkunden, die weiterempfehlen – das ist das Zeichen von echter Qualität. Aber keine Webseite und keine Instagram-Präsenz. Neukunden, die euch durch Empfehlung kennen, finden online keine Möglichkeit zu buchen. 23 Berliner Betriebe haben das geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 195, "salon": "E&R HairLounge", "instagram": None, "A": "Hey E&R HairLounge! 💆 Der Name 'Lounge' signalisiert Exklusivität. Aber ihr seid ausschließlich über Treatwell buchbar – keine eigene Website, keine direkte Kundenbeziehung. Jeder Termin bringt euch Provision-Kosten statt reinen Gewinn. 23 Berliner Salons haben sich davon gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 196, "salon": "Friseur Simooo Barbershop", "instagram": None, "A": "Hey Friseur Simooo Barbershop! ✂️ In Berlin eröffnen jeden Monat neue Salons – alle mit Instagram, alle mit Website. Wer online unsichtbar ist, verliert täglich Kunden, die er nie getroffen hat. Keine eigene Webpräsenz gefunden. Eure Arbeit verdient Sichtbarkeit, die über den Kiez hinausgeht. 23 Berliner Betriebe haben das realisiert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 197, "salon": "Marius Schewe | Zeitraum Berlin", "instagram": "@zeitraumberlin_marius", "A": "Hey Marius! 🌟 Dein Instagram @zeitraumberlin_marius mit 11K Followern zeigt Balayage-Verläufe, die andere Koloristen sich ansehen und still werden. Iles Formula und Oribe – du arbeitest nur mit dem Besten, weil du den Unterschied kennst. Aber kein aktives SSL. Bei 1.500+ Bewertungen und 4,9 Sternen ist das ein Widerspruch, den sich kein anderer Salon in Berlin leistet. 23 Berliner Salons haben diesen Kontrast eliminiert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 198, "salon": "wallacewallace", "instagram": "@wallacewallace__", "A": "Hey wallacewallace! ✂️ @wallacewallace__ zeigt, was passiert, wenn Präzision auf Haltung trifft – cruelty-free, englischsprachig, mit einer Ästhetik, die sofort Vertrauen schafft. Das ist eine echte Marke. Aber kein vollständig aktives SSL. Kunden, die über Instagram zu eurer Seite kommen, sehen eine Sicherheitswarnung – ein Widerspruch zu allem, wofür ihr steht. 23 Berliner Salons haben diesen letzten Schritt gemacht. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 199, "salon": "The Beard Man – Barber Lounge & Coffee", "instagram": None, "A": "Hey The Beard Man! ☕💈 Barbershop und Kaffeebar – wer einmal da war, kommt wieder. Das ist ein Erlebnis, kein Termin. Aber ausschließlich über Treatwell buchbar. Eure Kunden kennen euch – aber Treatwell kassiert mit bei jedem Besuch. 23 Berliner Betriebe haben Treatwell den Rücken gekehrt. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 200, "salon": "House of Fade Berlin", "instagram": "@house_of_fade_berlin", "A": "Hey House of Fade Berlin! 💈 @house_of_fade_berlin zeigt immer wieder diese cleanen High Fades – der Blend von Skin zu Guard ist bei eurem Team richtig smooth. Ersan und das Team sind handwerklich auf Top-Niveau. Aber keine eigene Domain – ihr zahlt Provision für Kunden, die eigentlich direkt zu euch kommen würden. 23 Berliner Barbershops haben ihre Unabhängigkeit zurückgewonnen. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 201, "salon": "Bennemann Friseure", "instagram": "@bennemannfriseure", "A": "Hey Bennemann Friseure! 🌿 @bennemannfriseure zeigt, was CO2-neutrales Arbeiten mit internationalem Anspruch bedeutet – die Davines-Highlights haben eine Natürlichkeit, die man bei anderen nicht bekommt. Marc war Academy Coach in London. Das ist eine Klasse für sich. Aber ein SSL-Problem. Bei einem Salon mit diesem Profil schickt das das falsche Signal an Neukunden. 23 Berliner Premiumsalons haben das behoben. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 202, "salon": "MU Berlin", "instagram": "@mu_berlin_salon", "A": "Hey MU Berlin! ✨ @mu_berlin_salon zeigt Farbarbeiten mit Babylights, die außergewöhnlich präzise sind – die Tiefe in diesen Colorationen ist nicht selbstverständlich. Das ist Können auf höchstem Niveau. Aber kein SSL. Wer euren Content sieht und dann eure Seite aufruft, sieht eine Browser-Warnung. 23 Berliner Salons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 203, "salon": "Berlin Hair Care Dermot O'Dyna", "instagram": "@berlinhaircaresalon_official", "A": "Hey Dermot O'Dyna! 🎨 Über 30 Jahre Friseurkunst, TV-Auftritte, ein Salon mit echtem Charakter – @berlinhaircaresalon_official zeigt das alles. Aber ein SSL-Problem. Kunden, die eure spannende Geschichte finden und die Website öffnen, sehen eine Sicherheitswarnung. Das ist nicht das Bild, das eine Karriere wie deine verdient. 23 Berliner Salons haben das geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 204, "salon": "Jane Lapuks Friseur", "instagram": None, "A": "Hallo Jane! 💇‍♀️ Deine Kunden schreiben: 'Nach 5 Jahren endlich die richtige Friseurin gefunden' – und kommen dann jahrelang wieder. Deine Strähnen-Technik ist einzigartig, das bestätigt jede Bewertung. Aber kein SSL. Neue Kundinnen, die auf dich aufmerksam werden und die Seite öffnen, sehen sofort eine Browser-Warnung. 23 Berliner Salons haben das behoben. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 205, "salon": "Fon Friseur", "instagram": "@fonfriseur", "A": "Hey FON Friseur Berlin! ✂️ @fonfriseur zeigt ein junges Team, das Qualität zu fairen Preisen liefert – Berlins beste Kombination. Eure Flexibilität ohne Termin ist ein echtes Plus. Aber kein SSL. Kunden, die euch über Google finden, sehen eine Browser-Sicherheitswarnung – genau in dem Moment, wo sie buchen wollen. 23 Berliner Salons haben diesen Moment geändert. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 206, "salon": "Micha Pelz Coiffure", "instagram": "@michapelzcoiffure", "A": "Hey Micha! 🏆 Dein Salon hat den iF Design Award gewonnen – der einzige Friseursalon in Berlin, der das von sich sagen kann. @michapelzcoiffure zeigt La Biosthétique-Farbarbeiten mit dieser Natürlichkeit, die andere nicht hinbekommen. Aber ein SSL-Problem. Ein Salon, der Design-Geschichte schreibt, hat eine Website mit Browser-Warnung. Dieser Kontrast ist unnötig. 23 Berliner Premiumsalons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 207, "salon": "Forty Two Coiffeur", "instagram": None, "A": "Hey Forty Two Coiffeur! ✂️ Kastanienallee – allein die Adresse sagt: ihr seid mitten in Berlins lebendigstem Kiez. Aber ihr seid ausschließlich über Treatwell buchbar: keine eigene Domain, keine eigene Kundendatenbank. Bei eurer Lage und Frequenz ist das Geld, das ihr täglich an eine Plattform gebt. 23 Berliner Salons haben ihre Unabhängigkeit zurückgewonnen. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 208, "salon": "Coiffeur Paluselli by Sabrina Nieschke", "instagram": None, "A": "Hey Sabrina! 💎 Von der Ausbildung bei Udo Walz, Meisterbrief mit 21, Hollywood-Stars beim Bambi gestylt – und jetzt eigene Inhaberin von Coiffeur Paluselli. Das ist eine Karriere, die Respekt verdient. Aber kein SSL. Für ein Salon-Konzept, das auf Bambi-Niveau arbeitet, ist das ein digitaler Widerspruch. 23 Berliner Premiumsalons haben das behoben. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 209, "salon": "FINE & DANDY kleine schwester AVEDA", "instagram": "@fineanddandyberlin", "A": "Hey FINE & DANDY! 🌿 @fineanddandyberlin zeigt, was AVEDA Vegan Haircolor in den richtigen Händen kann – eure Balayage-Looks haben diese Leichtigkeit, die man nur mit Produkten und Know-how auf diesem Niveau erreicht. Seit 2008 in Berlin – das ist eine echte Geschichte. Aber ein SSL-Problem. Browser zeigen mobilen Nutzern eine Sicherheitswarnung – bei einem AVEDA-Partnersalon ist das ein Widerspruch. 23 Berliner Premiumsalons haben das gelöst. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 210, "salon": "Classico Barbershop", "instagram": None, "A": "Hey Classico Barbershop Berlin! 💈 Klassischer Barbershop-Service – das ist ein Statement in einer Stadt voller Trend-Salons. Aber keine Instagram-Präsenz und keine eigene Webseite. 2025 ist Instagram das Schaufenster Nummer 1 für Barbershops – wer dort nicht vertreten ist, verliert täglich potenzielle Kunden. 23 Berliner Barbershops haben ihre Sichtbarkeit verdoppelt. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
    {"id": 211, "salon": "St Leonard", "instagram": "@stleonardberlin", "A": "Hey St Leonard! 💈 @stleonardberlin zeigt, was passiert, wenn Londoner Barbering-Tradition auf Berliner Community trifft – Dominic, Tom und Simon liefern Clean Cuts und Fades, die zeitlos sind. Das ist eine echte Marke. Aber kein SSL-Zertifikat. Kunden, die euren Ruf kennen und die Seite öffnen, sehen eine Browser-Sicherheitswarnung. 23 Berliner Salons dieser Klasse haben das bereits behoben. Antworte mit „Video", wenn ich dir das Beispiel zeigen soll."},
]

# compliment_detail per ID — extracted from A-variant opening praise sentence
COMPLIMENT_MAP = {
    172: "Fade-Finish auf höchstem Niveau – sauberer Nacken-Übergang im letzten Reel",
    173: "Skin Fades mit Kanten-Arbeit auf einem anderen Level (@barberremz)",
    175: "Team eingespielt: Textured Crops und konsistente Fades auf gleichem Niveau",
    176: "Vielseitigkeit: Damen-Styling bis klassischer Herrenschnitt (@mbcfriseur)",
    177: "Skin Fades mit Rasiermesser-Finish – Präzision an der Schläfe, selten in Berlin",
    179: "Traditionelle türkische Rasur – Handwerk, das nicht jeder beherrscht",
    181: "Gentlemen-Anspruch konsequent gelebt – klarer Stil im Namen und im Service",
    186: "Meistertitel Köln, Training Rotterdam – erinnert sich nach 1+ Jahr an den letzten Cut des Kunden",
    191: "LGBTQ+ freundlich, Modern bis Klassisch – Team mit echtem Stil (@veitfriseure)",
    197: "Balayage-Verläufe auf höchstem Niveau – Iles Formula und Oribe (@zeitraumberlin_marius, 11K)",
    198: "Cruelty-free, Präzision trifft Haltung – kohärente Markenästhetik (@wallacewallace__)",
    200: "Cleane High Fades – smooth Blend Skin zu Guard, Ersan und Team Top-Niveau",
    201: "CO2-neutral, Davines Highlights mit außergewöhnlicher Natürlichkeit, Marc: Academy Coach London",
    202: "Babylights mit außergewöhnlicher Präzision – Tiefe in Colorationen nicht selbstverständlich",
    203: "30+ Jahre Friseurkunst, TV-Auftritte – Salon mit echtem Charakter",
    204: "Strähnen-Technik einzigartig – Kunden kommen seit 5+ Jahren ausschließlich zu Jane",
    205: "Junges Team, faire Preise, Flexibilität ohne Termin (@fonfriseur)",
    206: "iF Design Award – einziger Friseursalon in Berlin, La Biosthétique Natürlichkeit",
    208: "Meisterbrief mit 21, Udo Walz Ausbildung, Bambi-Stylings – Karriere auf höchstem Niveau",
    209: "AVEDA Vegan Haircolor-Experten seit 2008 – Balayage-Leichtigkeit auf Premium-Niveau",
    211: "Londoner Barbering-Tradition: Dominic, Tom, Simon – Clean Cuts und Fades zeitlos",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
URL_PATTERN = re.compile(
    r'https?://\S+|www\.\S+|\S+\.(de|com|eu|salon|berlin|info|net|org)\S*',
    re.IGNORECASE
)

def strip_urls(text):
    """Remove all hyperlinks per CTO security order."""
    return URL_PATTERN.sub('', text).strip()

def clean_double_spaces(text):
    return re.sub(r'  +', ' ', text)

def patch_lead(lead_id, message, compliment):
    payload = {
        'custom_message':   message,
        'status':           'READY TO SEND',
    }
    if compliment:
        payload['compliment_detail'] = compliment

    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    url  = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req  = urllib.request.Request(url, data=data, headers=HDRS, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', help='Preview only, no DB write')
    return p.parse_args()


def main():
    args = parse_args()
    dry  = args.dry_run

    # Build final message map: VIP overrides full-data A-variant
    final = {}
    for row in FULL_DATA:
        final[row['id']] = strip_urls(clean_double_spaces(row['A']))
    for lid, msg in VIP_MESSAGES.items():
        final[lid] = strip_urls(clean_double_spaces(msg))  # VIP wins

    print(f'\n{"="*64}')
    print(f'  Elite Patch Berlin 171–211  |  {"DRY-RUN" if dry else "LIVE WRITE"}')
    print(f'  Total records: {len(final)}  |  VIP overrides: {len(VIP_MESSAGES)}')
    print(f'  compliment_detail populated for: {len(COMPLIMENT_MAP)} IDs')
    print(f'{"="*64}\n')

    ok = fail = 0
    for lid in sorted(final.keys()):
        msg        = final[lid]
        compliment = COMPLIMENT_MAP.get(lid)
        char_count = len(msg)

        # Warn if suspiciously long for WhatsApp
        length_tag = f'{char_count}c' + (' ⚠ LONG' if char_count > 600 else '')

        print(f'  ID {lid:>3} | {length_tag}')
        print(f'         → {msg[:90].replace(chr(10)," ")}...')
        if compliment:
            print(f'         ✦ compliment: {compliment[:70]}')

        if not dry:
            code = patch_lead(lid, msg, compliment)
            sym  = 'OK' if code in (200, 204) else f'ERR {code}'
            print(f'         → DB: [{sym}]')
            if code in (200, 204): ok += 1
            else:                  fail += 1
        else:
            print(f'         → DB: [DRY-RUN]')
            ok += 1

    print(f'\n{"="*64}')
    print(f'  DONE — total={len(final)} | ok={ok} | fail={fail}')
    if dry: print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
