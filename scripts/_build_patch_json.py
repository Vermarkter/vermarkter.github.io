#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build data/elite_patch_berlin.json from Director's dataset."""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

Q_OPEN  = '„'   # „
Q_CLOSE = '“'   # "
V = Q_OPEN + 'Video' + Q_CLOSE   # „Video"

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

records = [
  {'id': 171, 'compliment': None, 'msg':
   'Hallo Shibaar Team! Euer Ruf kommt von eurer Arbeit – nicht von eurem Internetauftritt. '
   'Das Problem: Genau das kostet euch jeden Monat neue Kunden. Wer euch nicht persönlich kennt, '
   'findet keine sichere Buchungsmöglichkeit. 23 Berliner Betriebe haben diesen Schritt bereits gemacht. '
   f'Antworte mit {V}, wenn ich dir zeigen soll, wie das konkret aussieht.'},

  {'id': 172, 'compliment': 'Fade-Finish auf höchstem Niveau – sauberer Nacken-Übergang im letzten Reel', 'msg':
   'Hey Josh Flagg Team! \U0001f488 Euer Fade-Finish auf Instagram ist handwerklich auf einem Level, '
   'das in Berlin nur wenige erreichen. Und trotzdem: kein SSL. Browser zeigen Neukunden „Nicht sicher“ '
   '– bevor sie überhaupt den Buchungsbutton sehen. 23 Berliner Salons haben genau das geändert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 173, 'compliment': 'Skin Fades mit Kanten-Arbeit auf einem anderen Level (@barberremz)', 'msg':
   'Hey Remz! ✂️ Deine Skin Fades auf @barberremz sind das, wofür Kunden aus ganz Berlin extra fahren. '
   'Aber kein SSL-Zertifikat. Wer dich auf Insta entdeckt, sieht eine Browserwarnung statt deines Terminformulars. '
   f'23 Berliner Salons haben das gelöst. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 174, 'compliment': None, 'msg':
   'Hallo Team von Tommy Shelby Barber! \U0001f488 Der Name allein hat Klasse. Das Problem: Jeder Termin läuft '
   'über Treatwell – das bedeutet Provision für jeden Kunden, den ihr selbst aufgebaut habt. '
   'Eure Kunden, fremde Plattform, eure Rechnung. 23 Berliner Salons sind bereits unabhängig. '
   f'Antworte mit {V}, wenn ich dir zeigen soll, wie du dich befreist.'},

  {'id': 175, 'compliment': 'Team eingespielt: Textured Crops und konsistente Fades auf gleichem Niveau', 'msg':
   'Hey Barber Brothers 2! ✂️ Euer Instagram zeigt ein Team, das aufeinander eingespielt ist – '
   'saubere Textured Crops, konsistente Fades, jeder Cut auf gleichem Niveau. Das verdient eine Online-Präsenz, '
   'die genauso verlässlich ist. Aber keine eigene Website gefunden. 23 Berliner Betriebe haben das gelöst. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 176, 'compliment': 'Vielseitigkeit: Damen-Styling bis klassischer Herrenschnitt (@mbcfriseur)', 'msg':
   'Hey MBC Barbershop! \U0001f44b @mbcfriseur zeigt Vielseitigkeit – von Damen-Styling bis klassischem '
   'Herrenschnitt, das Team beherrscht beides. Aber kein SSL. Neukunden, die euch entdecken, sehen als erstes '
   'eine Browserwarnung statt eurer Arbeit. 23 Berliner Salons haben diesen ersten Eindruck geändert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 177, 'compliment': 'Skin Fades mit Rasiermesser-Finish – Präzision an der Schläfe, selten in Berlin', 'msg':
   'Hey Mado Barbershop! \U0001f488 @madobarbershop zeigt immer wieder diese Skin Fades mit Rasiermesser-Finish – '
   'die Präzision an der Schläfe ist in Berlin eine Seltenheit. Das ist Handwerk auf höchstem Niveau. '
   'Und trotzdem kein gültiges SSL. Wer euren Reel sieht und dann eure Seite öffnet, sieht eine rote Warnung. '
   f'23 Berliner Salons haben das bereits geändert. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 178, 'compliment': None, 'msg':
   'Hey Al-Kabir Barber! \U0001f44b Eure Google-Bewertungen erzählen von sauberer Arbeit, persönlichem Service '
   'und Kunden, die immer wiederkommen. Das ist echter Ruf – aufgebaut durch Können. Aber kein SSL, '
   'keine sichere Webpräsenz. Neukunden sehen eine technische Warnung statt eurer Qualität. '
   f'23 Berliner Salons haben diesen Schritt gemacht. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 179, 'compliment': 'Traditionelle türkische Rasur – Handwerk, das nicht jeder beherrscht', 'msg':
   'Hallo Sabri Berber Coiffeur! \U0001f488 Traditionelle türkische Rasur mitten in Berlin – das ist ein '
   'Handwerk, das nicht jeder beherrscht. Eure Stammkunden wissen das. Aber online findet man euch kaum: '
   'keine Webseite, kein Instagram. 23 Berliner Salons haben diesen Schritt gemacht. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 180, 'compliment': None, 'msg':
   "Hey RIDVAN'S BARBERSHOP! ✂️ Eure Kunden kommen wegen persönlicher Betreuung und "
   'verlässlicher Qualität – das zeigen eure Bewertungen klar. Aber keine eigene Website, kein SSL. '
   'Wer euch online sucht, landet auf einer Seite mit Sicherheitswarnung – und klickt sofort weg. '
   f'23 Berliner Salons haben diesen Standard bereits. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 181, 'compliment': None, 'msg':
   "Hey Çetin's GENTLEMEN'S BARBER! \U0001f3a9 Der Anspruch ist im Namen: Gentlemen-Niveau. Eure Stammkunden "
   'kennen das. Aber keine eigene Website, keine Instagram-Präsenz. Wer euch durch Empfehlung findet '
   'und googelt, sieht keinen Buchungsbutton. '
   f'23 Berliner Betriebe haben diesen Schritt gemacht. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 182, 'compliment': None, 'msg':
   'Hey Haircut Barbershop Berlin! ✂️ Eure Google-Bewertungen zeigen einen Salon, dem Stammkunden '
   'treu bleiben – das ist das stärkste Qualitätssignal. Aber kein SSL. Mobile Nutzer sehen beim '
   'ersten Besuch der Seite eine Sicherheitswarnung. '
   f'23 Berliner Salons haben es behoben. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 183, 'compliment': None, 'msg':
   'Hey BERBERIUM! \U0001f488 Der Name klingt wie eine Marke mit Zukunft. Aber online findet man euch nicht – '
   'keine Website, kein Instagram. In Berlin eröffnen jeden Monat neue Barbershops, die alle auf Social Media '
   'aktiv sind. 23 Berliner Betriebe haben ihre Online-Präsenz aufgebaut. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 184, 'compliment': None, 'msg':
   'Hey Berberlin! \U0001f488 Euer Treatwell-Profil zeigt solide Bewertungen – Kunden, die kommen und '
   'zufrieden gehen. Aber: Jeder dieser Termine kostet euch Provision. Ihr habt keine eigene Webseite – '
   'alles läuft durch eine Plattform, die täglich wächst. 23 Berliner Salons sind bereits unabhängig. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 185, 'compliment': None, 'msg':
   'Hey BEJTA Beauty Coiffeur! \U0001f484 Haare und Kosmetik unter einem Dach – das ist in Berlin ein echtes '
   'Alleinstellungsmerkmal. Aber kein SSL-Zertifikat. Gerade für einen Beauty-Salon ist Vertrauen das Fundament '
   '– und wer eure Seite aufruft, sieht als erstes eine Sicherheitswarnung. Das widerspricht allem, wofür '
   f'ihr steht. 23 Berliner Betriebe haben dieses Problem gelöst. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 186, 'compliment': 'Meistertitel Köln, Training Rotterdam – erinnert sich nach 1+ Jahr an den letzten Cut des Kunden', 'msg':
   'Hey Nail! ✂️ Meistertitel in Köln, Training in Rotterdam – dein Handwerk ist Weltklasse. '
   'Und trotzdem: kein SSL. Kunden, die dich über Empfehlung finden, sehen sofort eine Browserwarnung. '
   f'Dieser Kontrast ist vermeidbar. 23 Berliner Salons haben das gelöst. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 187, 'compliment': None, 'msg':
   'Hey Anton Friseur und Kosmetik! \U0001f33f Friseur und Kosmetik kombiniert – das ist ein Konzept, '
   'das Kunden bindet. Aber ihr seid ausschließlich über Treatwell buchbar: keine eigene Seite, '
   'keine eigene Kundendatenbank. 23 Berliner Betriebe haben Direktbuchungen aufgebaut. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 188, 'compliment': None, 'msg':
   'Hey Boulevard Herrenfriseur! \U0001f488 Als Herrenspezialist in Berlin habt ihr eine klare Nische. '
   'Aber ihr seid nur über Treatwell buchbar – keine eigene Website, keine eigene Kundenbasis. '
   '23 Berliner Salons haben ihre Unabhängigkeit zurückgewonnen. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 189, 'compliment': None, 'msg':
   'Hey BERLIN BARBER LOUNGE! \U0001f6cb️ Eine Lounge – das ist mehr als ein Haarschnitt, das ist ein Erlebnis. '
   'Aber online ist dieses Erlebnis unsichtbar: keine Webseite, keine Instagram-Präsenz. '
   'Wer von euch hört und euch sucht, findet keine sichere Möglichkeit zu buchen. '
   f'23 Berliner Betriebe haben das geändert. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 190, 'compliment': None, 'msg':
   'Hey Maxat Friseur! \U0001f44b Eure Google-Bewertungen zeigen persönliche Atmosphäre und faire Beratung '
   '– das ist in Berlin selten geworden. Aber kein SSL. Mobile Nutzer sehen beim ersten Klick eine '
   'Sicherheitswarnung. 23 Berliner Salons haben diese Kleinigkeit behoben. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 191, 'compliment': 'LGBTQ+ freundlich, Modern bis Klassisch – Team mit echtem Stil (@veitfriseure)', 'msg':
   'Hey Veit Friseure Berlin! ✂️ @veitfriseure zeigt ein LGBTQ+ freundliches Team, das von Modern bis '
   'Klassisch alles beherrscht – und das in einem Salon mit echtem Stil. Aber technische Sicherheitsprobleme '
   'lösen bei mobilen Nutzern Warnungen aus. Euer Ruf verdient eine Website, die genauso verlässlich '
   f'ist wie euer Team. 23 Berliner Salons haben diesen Standard. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 192, 'compliment': None, 'msg':
   'Hey HAIR MÜLLER! \U0001f487 Professionelle Beratung und hochwertiger Service – das ist das Feedback '
   'eurer Kunden über Jahre hinweg. Aber kein SSL-Zertifikat. Browser zeigen Besuchern eine rote Warnung. '
   '23 Berliner Salons haben das geändert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 193, 'compliment': None, 'msg':
   'Hallo Cut 121 Berlin! ✂️ Ein herzliches Team, präzise Schnitte, strahlende Farben – '
   'so beschreiben euch eure Kunden auf Treatwell. Aber keine aktive SSL-gesicherte Seite. '
   'Neukunden finden keine vertrauenswürdige Buchungsmöglichkeit. '
   f'23 Berliner Salons haben diesen Schritt gemacht. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 194, 'compliment': None, 'msg':
   'Hey Friseur By Hazem! \U0001f487 Stammkunden, die weiterempfehlen – das ist das Zeichen von echter '
   'Qualität. Aber keine Webseite und keine Instagram-Präsenz. Neukunden finden online keine '
   'Möglichkeit zu buchen. 23 Berliner Betriebe haben das geändert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 195, 'compliment': None, 'msg':
   'Hey E&R HairLounge! \U0001f486 Der Name „Lounge“ signalisiert Exklusivität. '
   'Aber ihr seid ausschließlich über Treatwell buchbar – keine eigene Website, '
   'keine direkte Kundenbeziehung. 23 Berliner Salons haben sich davon gelöst. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 196, 'compliment': None, 'msg':
   'Hey Friseur Simooo Barbershop! ✂️ In Berlin eröffnen jeden Monat neue Salons – alle mit '
   'Instagram, alle mit Website. Wer online unsichtbar ist, verliert täglich Kunden, die er nie getroffen hat. '
   '23 Berliner Betriebe haben das realisiert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 197, 'compliment': 'Balayage-Verläufe auf höchstem Niveau – Iles Formula und Oribe, 11K Instagram (@zeitraumberlin_marius)', 'msg':
   'Sehr geehrter Herr Schewe, Ihr Instagram mit 11.000 Followern zeigt Balayage-Verläufe auf höchstem '
   'Niveau. Aber ich habe getestet: kein aktives SSL. Bei 1.500+ Bewertungen ist das ein Widerspruch, '
   'den Kunden sofort bemerken. 23 Berliner Top-Salons haben diesen Kontrast bereits eliminiert. '
   f'Antworten Sie mit {V}, wenn ich Ihnen das Beispiel zeigen soll.'},

  {'id': 198, 'compliment': 'Cruelty-free, Präzision trifft Haltung – kohärente Markenaästhetik (@wallacewallace__)', 'msg':
   'Hey wallacewallace! ✂️ @wallacewallace__ zeigt, was passiert, wenn Präzision auf Haltung trifft '
   '– cruelty-free, englischsprachig, mit einer Ästhetik, die sofort Vertrauen schafft. Das ist eine echte '
   'Marke. Aber kein vollständig aktives SSL – Kunden sehen eine Sicherheitswarnung. '
   '23 Berliner Salons haben diesen letzten Schritt gemacht. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 199, 'compliment': None, 'msg':
   'Hey The Beard Man! ☕\U0001f488 Barbershop und Kaffeebar – wer einmal da war, kommt wieder. '
   'Das ist ein Erlebnis, kein Termin. Aber ausschließlich über Treatwell buchbar – '
   'Treatwell kassiert mit bei jedem Besuch. 23 Berliner Betriebe haben Treatwell den Rücken gekehrt. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 200, 'compliment': 'Cleane High Fades – smooth Blend Skin zu Guard, Ersan und Team Top-Niveau', 'msg':
   'Hey House of Fade Berlin! \U0001f488 @house_of_fade_berlin zeigt immer wieder diese cleanen High Fades – '
   'der Blend von Skin zu Guard ist bei eurem Team richtig smooth. Ersan und das Team sind handwerklich auf '
   'Top-Niveau. Aber keine eigene Domain – ihr zahlt Provision für Kunden, die direkt zu euch '
   'kommen würden. 23 Berliner Barbershops haben ihre Unabhängigkeit zurückgewonnen. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 201, 'compliment': 'CO2-neutral, Davines Highlights mit außergewöhnlicher Natürlichkeit, Marc: Academy Coach London', 'msg':
   'Hey Bennemann Friseure! \U0001f33f @bennemannfriseure zeigt, was CO2-neutrales Arbeiten mit internationalem '
   'Anspruch bedeutet – die Davines-Highlights haben eine Natürlichkeit, die man bei anderen nicht bekommt. '
   'Marc war Academy Coach in London. Das ist eine Klasse für sich. Aber ein SSL-Problem sendet das falsche '
   'Signal an Neukunden. 23 Berliner Premiumsalons haben das behoben. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 202, 'compliment': 'Babylights mit außergewöhnlicher Präzision – Tiefe in Colorationen nicht selbstverständlich', 'msg':
   'Hey MU Berlin! ✨ @mu_berlin_salon zeigt Farbarbeiten mit Babylights, die außergewöhnlich präzise '
   'sind – die Tiefe in diesen Colorationen ist nicht selbstverständlich. Aber kein SSL. Wer euren Content '
   'sieht und dann eure Seite aufruft, sieht eine Browser-Warnung. 23 Berliner Salons haben das gelöst. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 203, 'compliment': '30+ Jahre Friseurkunst, TV-Auftritte – Salon mit echtem Charakter', 'msg':
   'Hey Dermot O’Dyna! \U0001f3a8 Über 30 Jahre Friseurkunst, TV-Auftritte, ein Salon mit echtem Charakter. '
   'Aber ein SSL-Problem – Kunden, die eure Geschichte finden und die Website öffnen, sehen eine '
   'Sicherheitswarnung. Das ist nicht das Bild, das eine Karriere wie deine verdient. '
   '23 Berliner Salons haben das geändert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 204, 'compliment': 'Strähnen-Technik einzigartig – Kunden kommen seit 5+ Jahren ausschließlich zu Jane', 'msg':
   'Hallo Jane! \U0001f487‍♀️ Deine Kunden schreiben: „Nach 5 Jahren endlich die richtige '
   'Friseurin gefunden“ – und kommen dann jahrelang wieder. Deine Strähnen-Technik ist einzigartig, '
   'das bestätigt jede Bewertung. Aber kein SSL – neue Kundinnen sehen sofort eine Browser-Warnung. '
   f'23 Berliner Salons haben das behoben. Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 205, 'compliment': 'Junges Team, faire Preise, Flexibilität ohne Termin (@fonfriseur)', 'msg':
   'Hey FON Friseur Berlin! ✂️ @fonfriseur zeigt ein junges Team, das Qualität zu fairen Preisen '
   'liefert. Eure Flexibilität ohne Termin ist ein echtes Plus. Aber kein SSL – Kunden, die euch über '
   'Google finden, sehen eine Browser-Sicherheitswarnung genau in dem Moment, wo sie buchen wollen. '
   '23 Berliner Salons haben diesen Moment geändert. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 206, 'compliment': 'iF Design Award – einziger Friseursalon in Berlin, La Biostétique Natürlichkeit', 'msg':
   'Sehr geehrter Herr Pelz, Ihr Salon hat den iF Design Award gewonnen – das ist einzigartig in Berlin. '
   'Aber aktuell ein SSL-Problem. Die Sorgfalt, die Sie in jeden Cut stecken, fehlt online. '
   '23 Berliner Spitzensalons haben diesen Standard bereits korrigiert. '
   f'Antworten Sie mit {V}, wenn ich Ihnen zeigen darf, wie wir das lösen.'},

  {'id': 207, 'compliment': None, 'msg':
   'Hey Forty Two Coiffeur! ✂️ Kastanienallee – allein die Adresse sagt: ihr seid mitten in Berlins '
   'lebendigstem Kiez. Aber ausschließlich über Treatwell buchbar: keine eigene Domain, keine eigene '
   'Kundendatenbank. Bei eurer Lage ist das Geld, das ihr täglich an eine Plattform gebt. '
   '23 Berliner Salons haben ihre Unabhängigkeit zurückgewonnen. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 208, 'compliment': 'Meisterbrief mit 21, Udo Walz Ausbildung, Bambi-Stylings – Karriere auf höchstem Niveau', 'msg':
   'Sehr geehrte Frau Nieschke, Ihre Karriere von Udo Walz bis zu den Bambi-Stylings verdient höchsten Respekt. '
   'Aber kein SSL. Für ein Konzept auf Ihrem Niveau ist die Browser-Warnung ein kritischer Widerspruch. '
   '23 Berliner Premiumsalons haben das bereits behoben. '
   f'Antworten Sie mit {V}, wenn ich Ihnen die Lösung zeigen darf.'},

  {'id': 209, 'compliment': 'AVEDA Vegan Haircolor-Experten seit 2008 – Balayage-Leichtigkeit auf Premium-Niveau', 'msg':
   'Sehr geehrtes FINE & DANDY Team, eure Balayage-Looks mit AVEDA sind seit 2008 eine Institution in Berlin. '
   'Aber ein SSL-Problem – Browser zeigen eine Sicherheitswarnung. Das passt nicht zu eurem '
   'Qualitätsanspruch. 23 Berliner Premiumsalons haben das gelöst. '
   f'Antworten Sie mit {V}, wenn ich Ihnen das Video-Demo zusenden darf.'},

  {'id': 210, 'compliment': None, 'msg':
   'Hey Classico Barbershop Berlin! \U0001f488 Klassischer Barbershop-Service – das ist ein Statement '
   'in einer Stadt voller Trend-Salons. Aber keine Instagram-Präsenz und keine eigene Webseite. '
   '2025 ist Instagram das Schaufenster Nummer 1 für Barbershops. '
   '23 Berliner Barbershops haben ihre Sichtbarkeit verdoppelt. '
   f'Antworte mit {V}, wenn ich dir das Beispiel zeigen soll.'},

  {'id': 211, 'compliment': 'Londoner Barbering-Tradition: Dominic, Tom, Simon – Clean Cuts und Fades zeitlos', 'msg':
   'Sehr geehrtes St Leonard Team, @stleonardberlin zeigt echte Londoner Barbering-Tradition. '
   'Aber kein SSL-Zertifikat – Kunden, die euren Ruf kennen, sehen beim Öffnen der Seite eine Warnung. '
   '23 Berliner Salons dieser Klasse haben das bereits behoben. '
   f'Antworten Sie mit {V}, wenn ich Ihnen zeigen darf, wie wir eure Unabhängigkeit sichern.'},
]

out = os.path.join(_ROOT, 'data', 'elite_patch_berlin.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f'Saved {len(records)} records to {out}')
with_compliment = sum(1 for r in records if r['compliment'])
print(f'compliment_detail populated: {with_compliment} / {len(records)} IDs')
