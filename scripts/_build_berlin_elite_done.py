#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
_build_berlin_elite_done.py
Generates data/berlin_elite_done.json — final 10/10 Sie-standard messages for IDs 171-211.

Rules applied:
1. Anrede: „Sie" exclusively — no Hey, no Du, no Ihr
2. No „Heute Nacht" or informal time phrases
3. Instagram-compliment kept where available (specific technique/post reference)
4. No URLs anywhere
5. CTA: „Darf ich Ihnen das Video-Demo dazu schicken?"
6. German quotes „..." throughout
7. Max ~480 chars
"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q  = '„{}“'   # „text"
CTA = 'Darf ich Ihnen das Video-Demo dazu schicken?'
N23 = '23 Berliner Salons haben diesen Schritt bereits gemacht.'

def q(text):
    return '„' + text + '“'

records = [

# ── 171 Friseur Shibaar ── no instagram, no website, reputation-based ──────────
{'id': 171, 'salon': 'Friseur Shibaar', 'instagram': None,
 'msg': (
  'Guten Tag, liebes Shibaar-Team! '
  'Ihr Ruf in Berlin kommt von Ihrer Arbeit – Stammkunden, die seit Jahren kommen und '
  'weiterempfehlen, sind das stärkste Qualitätssignal. '
  'Das Problem: Wer Sie nicht persönlich kennt, findet online keine sichere Buchungsmöglichkeit '
  'und wählt den nächsten Salon. '
  f'{N23} '
  f'{CTA}'
)},

# ── 172 Josh Flagg Barbershop ── instagram, SSL ──────────────────────────────
{'id': 172, 'salon': 'Josh Flagg Barbershop', 'instagram': '@joshflaggbarbershop',
 'msg': (
  'Guten Tag, Josh Flagg Team! '
  'Ihr Fade-Finish auf Instagram ist handwerklich auf einem Level, das in Berlin nur wenige '
  'erreichen – der Übergang am Nacken in Ihrem letzten Reel ist absolut sauber. '
  'Und trotzdem: Ihre Website hat kein SSL. Browser zeigen Neukunden '
  + q('Nicht sicher') +
  ' – bevor sie überhaupt den Buchungsbutton sehen. '
  f'{N23} '
  f'{CTA}'
)},

# ── 173 Barberremz ── instagram, SSL ─────────────────────────────────────────
{'id': 173, 'salon': 'Barberremz', 'instagram': '@barberremz',
 'msg': (
  'Guten Tag! '
  'Die Skin Fades auf @barberremz sind das, wofür Kunden aus ganz Berlin extra fahren – '
  'die Kanten-Arbeit ist auf einem anderen Niveau. '
  'Aber Ihre Website hat kein SSL-Zertifikat: Wer Sie auf Instagram entdeckt und direkt buchen '
  'möchte, sieht eine Browserwarnung statt des Terminformulars. '
  f'{N23} '
  f'{CTA}'
)},

# ── 174 Tommy Shelby Barber ── Treatwell ─────────────────────────────────────
{'id': 174, 'salon': 'Tommy Shelby Barber', 'instagram': None,
 'msg': (
  'Guten Tag, liebes Tommy Shelby Team! '
  'Der Name allein hat Klasse – und wer Peaky-Blinders-Flair in den Barberstuhl bringt, '
  'hat einen klaren Stil. '
  'Das Problem: Jeder Termin läuft über Treatwell – das bedeutet Provision für jeden Kunden, '
  'den Sie selbst aufgebaut haben. Ihre Kunden, fremde Plattform, Ihre Rechnung. '
  f'{N23} '
  f'{CTA}'
)},

# ── 175 Barber Brothers 2 ── instagram, no website ───────────────────────────
{'id': 175, 'salon': 'Barber Brothers 2', 'instagram': '@brothers_barbershop_berlin',
 'msg': (
  'Guten Tag, Barber Brothers Team! '
  'Ihr Instagram zeigt ein Team, das aufeinander eingespielt ist – saubere Textured Crops, '
  'konsistente Fades, jeder Cut auf gleichem Niveau. '
  'Das verdient eine Online-Präsenz, die genauso verlässlich ist. '
  'Ich habe jedoch keine eigene Website gefunden – Neukunden finden keinen Buchungsbutton. '
  f'{N23} '
  f'{CTA}'
)},

# ── 176 MBC Barbershop Berlin ── instagram, SSL ───────────────────────────────
{'id': 176, 'salon': 'MBC Barbershop Berlin', 'instagram': '@mbcfriseur',
 'msg': (
  'Guten Tag, MBC Barbershop Team! '
  '@mbcfriseur zeigt echte Vielseitigkeit – von Damen-Styling bis klassischem Herrenschnitt '
  'beherrscht Ihr Team beides auf hohem Niveau. '
  'Aber Ihre Website hat kein SSL: Neukunden, die Sie entdecken, sehen als Erstes eine '
  'Browserwarnung statt Ihrer Arbeit. '
  f'{N23} '
  f'{CTA}'
)},

# ── 177 Mado Barbershop ── instagram, SSL ────────────────────────────────────
{'id': 177, 'salon': 'Mado Barbershop', 'instagram': '@madobarbershop',
 'msg': (
  'Guten Tag, Mado Barbershop Team! '
  '@madobarbershop zeigt immer wieder Skin Fades mit Rasiermesser-Finish – '
  'die Präzision an der Schläfe ist in Berlin eine Seltenheit. Das ist Handwerk auf höchstem Niveau. '
  'Und trotzdem: Ihre Website hat kein gültiges SSL. Wer Ihren Reel sieht und die Seite öffnet, '
  'sieht eine rote Warnung statt des Buchungsformulars. '
  f'{N23} '
  f'{CTA}'
)},

# ── 178 Al-Kabir Barber Berlin ── Google rep, SSL ────────────────────────────
{'id': 178, 'salon': 'Al-Kabir Barber Berlin', 'instagram': None,
 'msg': (
  'Guten Tag, Al-Kabir Barber Team! '
  'Ihre Google-Bewertungen erzählen von sauberer Arbeit, persönlichem Service und Kunden, '
  'die immer wiederkommen – das ist echter Ruf, aufgebaut durch Können. '
  'Aber Ihre Website hat kein SSL: Neukunden sehen eine technische Warnung statt Ihrer Qualität. '
  f'{N23} '
  f'{CTA}'
)},

# ── 179 Sabri Berber Coiffeur ── traditional craft, no online presence ───────
{'id': 179, 'salon': 'Sabri Berber Coiffeur', 'instagram': None,
 'msg': (
  'Guten Tag, Sabri Berber Coiffeur! '
  'Traditionelle türkische Rasur mitten in Berlin – das ist ein Handwerk, das nicht jeder beherrscht, '
  'und Ihre Stammkunden wissen das. '
  'Aber online findet man Sie kaum: keine Webseite, kein Instagram. Wer Sie durch Empfehlung '
  'kennt und googelt, findet keine Möglichkeit zu buchen. '
  f'{N23} '
  f'{CTA}'
)},

# ── 180 RIDVAN's BARBERSHOP ── no website, SSL ───────────────────────────────
{'id': 180, 'salon': "RIDVAN'S BARBERSHOP", 'instagram': None,
 'msg': (
  "Guten Tag, RIDVAN'S BARBERSHOP Team! "
  'Ihre Kunden kommen wegen persönlicher Betreuung und verlässlicher Qualität – '
  'das zeigen Ihre Bewertungen klar. '
  'Aber Ihre Website hat kein SSL: Wer Sie online sucht, sieht eine Sicherheitswarnung '
  'und klickt sofort weg. Ihr Ruf verdient einen besseren ersten Eindruck. '
  f'{N23} '
  f'{CTA}'
)},

# ── 181 Çetin's GENTLEMEN'S BARBER ── no website, no instagram ───────────────
{'id': 181, 'salon': "Çetin's GENTLEMEN'S BARBER", 'instagram': None,
 'msg': (
  "Guten Tag, Çetin's Gentlemen's Barber Team! "
  'Der Anspruch ist bereits im Namen: Gentlemen-Niveau. '
  'Aber online ist davon nichts zu sehen – keine eigene Website, keine Instagram-Präsenz. '
  'Wer Sie durch Empfehlung findet und googelt, sieht keinen Buchungsbutton '
  'und wählt den nächsten Salon, der online verfügbar ist. '
  f'{N23} '
  f'{CTA}'
)},

# ── 182 Haircut Barbershop Berlin ── SSL ──────────────────────────────────────
{'id': 182, 'salon': 'Haircut Barbershop Berlin', 'instagram': None,
 'msg': (
  'Guten Tag, Haircut Barbershop Berlin Team! '
  'Ihre Google-Bewertungen zeigen einen Salon, dem Stammkunden seit Jahren treu bleiben – '
  'das ist das stärkste Qualitätssignal überhaupt. '
  'Aber Ihre Website hat kein SSL: Mobile Nutzer – also die Mehrheit der Neukunden – '
  'sehen beim ersten Besuch eine Sicherheitswarnung. '
  f'{N23} '
  f'{CTA}'
)},

# ── 183 BERBERIUM ── no website, no instagram ────────────────────────────────
{'id': 183, 'salon': 'BERBERIUM', 'instagram': None,
 'msg': (
  'Guten Tag, BERBERIUM Team! '
  'Der Name klingt wie eine Marke mit Zukunft. '
  'Aber online findet man Sie nicht – keine Website, kein Instagram. '
  'In Berlin eröffnen jeden Monat neue Barbershops, alle aktiv auf Social Media. '
  'Wer heute unsichtbar ist, verliert morgen die Kunden, die er noch nicht kennt. '
  f'{N23} '
  f'{CTA}'
)},

# ── 184 Berberlin ── Treatwell ────────────────────────────────────────────────
{'id': 184, 'salon': 'Berberlin', 'instagram': None,
 'msg': (
  'Guten Tag, Berberlin Team! '
  'Ihr Treatwell-Profil zeigt solide Bewertungen – Kunden, die kommen und zufrieden gehen. '
  'Aber jeder dieser Termine kostet Sie Provision. '
  'Sie haben keine eigene Webseite: alles läuft durch eine Plattform, '
  'die Ihre Kunden als ihre eigenen behandelt. '
  f'{N23} '
  f'{CTA}'
)},

# ── 185 BEJTA Beauty Coiffeur ── SSL, beauty+hair combo ──────────────────────
{'id': 185, 'salon': 'BEJTA Beauty Coiffeur', 'instagram': None,
 'msg': (
  'Guten Tag, BEJTA Beauty Coiffeur Team! '
  'Haare und Kosmetik unter einem Dach – das ist in Berlin ein echtes Alleinstellungsmerkmal. '
  'Aber Ihre Website hat kein SSL-Zertifikat. '
  'Gerade für einen Beauty-Salon ist Vertrauen das Fundament – '
  'und wer Ihre Seite aufruft, sieht als Erstes eine Sicherheitswarnung. '
  f'{N23} '
  f'{CTA}'
)},

# ── 186 Shapes Barbershop ── instagram, SSL, Meister ─────────────────────────
{'id': 186, 'salon': 'Shapes Barbershop', 'instagram': 'shapes.salon',
 'msg': (
  'Guten Tag! '
  'Meistertitel in Köln, Training in Rotterdam – und Ihre Bewertungen zeigen: '
  'Sie erinnern sich nach über einem Jahr noch an den letzten Cut Ihres Kunden, '
  'weil Sie Notizen machen. Das ist Handwerk auf Weltklasse-Niveau. '
  'Und trotzdem: Ihre Website hat kein SSL. Kunden, die Sie über Empfehlung finden, '
  'sehen sofort eine Browserwarnung. Dieser Kontrast ist vermeidbar. '
  f'{N23} '
  f'{CTA}'
)},

# ── 187 Anton Friseur und Kosmetik ── Treatwell ───────────────────────────────
{'id': 187, 'salon': 'Anton Friseur und Kosmetik', 'instagram': None,
 'msg': (
  'Guten Tag, Anton Friseur und Kosmetik Team! '
  'Friseur und Kosmetik kombiniert – das ist ein Konzept, das Kunden bindet. '
  'Aber Sie sind ausschließlich über Treatwell buchbar: keine eigene Seite, '
  'keine eigene Kundendatenbank. '
  'Jeder Termin, den Sie verdient haben, läuft durch eine Plattform, die dafür berechnet. '
  f'{N23} '
  f'{CTA}'
)},

# ── 188 Boulevard Herrenfriseur ── Treatwell ──────────────────────────────────
{'id': 188, 'salon': 'Boulevard Herrenfriseur', 'instagram': None,
 'msg': (
  'Guten Tag, Boulevard Herrenfriseur Team! '
  'Als Herrenspezialist in Berlin haben Sie eine klare Nische. '
  'Aber Sie sind nur über Treatwell buchbar – keine eigene Website, keine eigene Kundenbasis. '
  'Das bedeutet: wenn Treatwell morgen die Konditionen ändert, sind Sie direkt betroffen. '
  f'{N23} '
  f'{CTA}'
)},

# ── 189 BERLIN BARBER LOUNGE ── no website ────────────────────────────────────
{'id': 189, 'salon': 'BERLIN BARBER LOUNGE', 'instagram': None,
 'msg': (
  'Guten Tag, Berlin Barber Lounge Team! '
  'Eine Lounge – das ist mehr als ein Haarschnitt, das ist ein Erlebnis. '
  'Aber online ist dieses Erlebnis unsichtbar: keine Webseite, keine Instagram-Präsenz. '
  'Wer von Ihnen hört und Sie sucht, findet keine sichere Möglichkeit zu buchen. '
  f'{N23} '
  f'{CTA}'
)},

# ── 190 Maxat Friseur ── SSL ───────────────────────────────────────────────────
{'id': 190, 'salon': 'Maxat Friseur', 'instagram': None,
 'msg': (
  'Guten Tag, Maxat Friseur Team! '
  'Ihre Google-Bewertungen zeigen persönliche Atmosphäre und faire Beratung – '
  'das ist in Berlin selten geworden. '
  'Aber Ihre Website hat kein SSL: Mobile Nutzer sehen beim ersten Klick eine Sicherheitswarnung. '
  'Die Mehrheit bricht genau da ab – nicht wegen Ihrer Arbeit, sondern wegen einer Technik-Kleinigkeit. '
  f'{N23} '
  f'{CTA}'
)},

# ── 191 Veit Friseure Berlin ── instagram, SSL, LGBTQ+ ────────────────────────
{'id': 191, 'salon': 'Veit Friseure Berlin', 'instagram': '@veitfriseure',
 'msg': (
  'Guten Tag, Veit Friseure Berlin Team! '
  '@veitfriseure zeigt ein LGBTQ+-freundliches Team, das von Modern bis Klassisch alles beherrscht '
  '– und das in einem Salon mit echtem Stil. '
  'Ich habe jedoch festgestellt: Ihre Website hat ein SSL-Problem, das bei mobilen Nutzern '
  'Sicherheitswarnungen auslöst. Ihr Ruf und Ihre Werte verdienen eine Website, '
  'die genauso verlässlich ist wie Ihr Team. '
  f'{N23} '
  f'{CTA}'
)},

# ── 192 HAIR MÜLLER ── SSL ────────────────────────────────────────────────────
{'id': 192, 'salon': 'HAIR MÜLLER', 'instagram': None,
 'msg': (
  'Guten Tag, Hair Müller Team! '
  'Professionelle Beratung und hochwertiger Service – das ist das Feedback Ihrer Kunden über Jahre hinweg. '
  'Aber Ihre Website hat kein SSL-Zertifikat: Browser zeigen Besuchern eine Warnung. '
  'Wer noch kein Vertrauen zu Ihnen hat, verlässt die Seite sofort – '
  'bevor er Ihre Arbeit sehen kann. '
  f'{N23} '
  f'{CTA}'
)},

# ── 193 Cut 121 ── Treatwell/SSL, multilingual team ──────────────────────────
{'id': 193, 'salon': 'Cut 121', 'instagram': None,
 'msg': (
  'Guten Tag, Cut 121 Berlin Team! '
  'Ein herzliches Team, präzise Schnitte, strahlende Farben – '
  'so beschreiben Sie Ihre Kunden auf Treatwell. '
  'Aber Ihre Website hat keine aktive SSL-Absicherung: '
  'Neukunden, die Sie googeln, finden keine vertrauenswürdige Buchungsmöglichkeit. '
  'Ihre Qualität verdient eine Online-Präsenz auf gleichem Niveau. '
  f'{N23} '
  f'{CTA}'
)},

# ── 194 Friseur By Hazem ── no website, no instagram ─────────────────────────
{'id': 194, 'salon': 'Friseur By Hazem', 'instagram': None,
 'msg': (
  'Guten Tag, Friseur By Hazem Team! '
  'Stammkunden, die weiterempfehlen – das ist das Zeichen von echter Qualität. '
  'Aber Sie haben keine Webseite und keine Instagram-Präsenz. '
  'Neukunden, die Sie durch Empfehlung kennen, finden online keine Möglichkeit zu buchen '
  'und entscheiden sich für den nächsten Salon, der digital verfügbar ist. '
  f'{N23} '
  f'{CTA}'
)},

# ── 195 E&R HairLounge ── Treatwell ───────────────────────────────────────────
{'id': 195, 'salon': 'E&R HairLounge', 'instagram': None,
 'msg': (
  'Guten Tag, E&R HairLounge Team! '
  'Der Name ' + q('Lounge') + ' signalisiert Exklusivität. '
  'Aber Sie sind ausschließlich über Treatwell buchbar – '
  'keine eigene Website, keine direkte Kundenbeziehung. '
  'Jeder Termin bringt Ihnen Provision-Kosten statt reinen Gewinn. '
  f'{N23} '
  f'{CTA}'
)},

# ── 196 Friseur Simooo Barbershop ── no online presence ──────────────────────
{'id': 196, 'salon': 'Friseur Simooo Barbershop', 'instagram': None,
 'msg': (
  'Guten Tag, Friseur Simooo Barbershop Team! '
  'In Berlin eröffnen jeden Monat neue Salons – alle mit Instagram, alle mit Website. '
  'Wer online unsichtbar ist, verliert täglich Kunden, die er nie getroffen hat. '
  'Ich habe keine eigene Webpräsenz für Sie gefunden. '
  'Ihre Arbeit verdient Sichtbarkeit, die über den Kiez hinausgeht. '
  f'{N23} '
  f'{CTA}'
)},

# ── 197 Marius Schewe / Zeitraum Berlin ── instagram 11K, SSL, Balayage ──────
{'id': 197, 'salon': 'Marius Schewe | Zeitraum Berlin', 'instagram': '@zeitraumberlin_marius',
 'msg': (
  'Sehr geehrter Herr Schewe! '
  'Ihr Instagram @zeitraumberlin_marius mit 11.000 Followern zeigt Balayage-Verläufe, '
  'bei denen andere Koloristen genau hinschauen – '
  'Iles Formula und Oribe, weil Sie den Unterschied kennen. '
  'Ich habe Ihre Website getestet: kein aktives SSL. '
  'Bei 1.500+ Bewertungen und 4,9 Sternen ist das ein Widerspruch, den sich kein anderer '
  'Salon in Berlin leistet. '
  f'{N23} '
  f'{CTA}'
)},

# ── 198 wallacewallace ── instagram, SSL, cruelty-free ───────────────────────
{'id': 198, 'salon': 'wallacewallace', 'instagram': '@wallacewallace__',
 'msg': (
  'Guten Tag, wallacewallace Team! '
  '@wallacewallace__ zeigt, was passiert, wenn Präzision auf Haltung trifft – '
  'cruelty-free, englischsprachig, mit einer Ästhetik, die sofort Vertrauen schafft. '
  'Das ist eine echte Marke. '
  'Aber Ihre Website hat kein vollständig aktives SSL – '
  'Kunden, die über Instagram zu Ihnen kommen, sehen eine Sicherheitswarnung. '
  'Ein Widerspruch zu allem, wofür Sie stehen. '
  f'{N23} '
  f'{CTA}'
)},

# ── 199 The Beard Man ── Treatwell, coffee+barber ────────────────────────────
{'id': 199, 'salon': 'The Beard Man – Barber Lounge & Coffee', 'instagram': None,
 'msg': (
  'Guten Tag, The Beard Man Team! '
  'Barbershop und Kaffeebar – wer einmal bei Ihnen war, kommt wieder. Das ist ein Erlebnis, kein Termin. '
  'Aber Sie sind ausschließlich über Treatwell buchbar: '
  'Ihre Kunden kennen Sie – Treatwell kassiert bei jedem Besuch mit. '
  f'{N23} '
  f'{CTA}'
)},

# ── 200 House of Fade Berlin ── instagram, Treatwell, High Fades ─────────────
{'id': 200, 'salon': 'House of Fade Berlin', 'instagram': '@house_of_fade_berlin',
 'msg': (
  'Guten Tag, House of Fade Team! '
  '@house_of_fade_berlin zeigt immer wieder diese cleanen High Fades – '
  'der Blend von Skin zu Guard ist bei Ihrem Team wirklich smooth. Handwerklich Top-Niveau. '
  'Aber Sie haben keine eigene Domain: '
  'Sie zahlen Provision für Kunden, die eigentlich direkt zu Ihnen kommen würden. '
  f'{N23} '
  f'{CTA}'
)},

# ── 201 Bennemann Friseure ── instagram, SSL, CO2-neutral, Marc London ────────
{'id': 201, 'salon': 'Bennemann Friseure', 'instagram': '@bennemannfriseure',
 'msg': (
  'Guten Tag, Bennemann Friseure Team! '
  '@bennemannfriseure zeigt, was CO2-neutrales Arbeiten mit internationalem Anspruch bedeutet – '
  'die Davines-Highlights haben eine Natürlichkeit, die man bei anderen nicht bekommt. '
  'Marc war Academy Coach in London – das ist eine Klasse für sich. '
  'Aber Ihre Website hat ein SSL-Problem, das dieses Niveau nicht widerspiegelt. '
  f'{N23} '
  f'{CTA}'
)},

# ── 202 MU Berlin ── instagram, SSL, Babylights ───────────────────────────────
{'id': 202, 'salon': 'MU Berlin', 'instagram': '@mu_berlin_salon',
 'msg': (
  'Guten Tag, MU Berlin Team! '
  '@mu_berlin_salon zeigt Farbarbeiten mit Babylights, die außergewöhnlich präzise sind – '
  'die Tiefe in diesen Colorationen ist nicht selbstverständlich. '
  'Aber Ihre Website hat kein SSL: Wer Ihren Content sieht und dann die Seite aufruft, '
  'sieht eine Browser-Warnung. Ihr visuelles Niveau verdient einen besseren ersten Eindruck. '
  f'{N23} '
  f'{CTA}'
)},

# ── 203 Berlin Hair Care Dermot O'Dyna ── instagram, 30y career, SSL ─────────
{'id': 203, 'salon': "Berlin Hair Care Dermot O'Dyna", 'instagram': '@berlinhaircaresalon_official',
 'msg': (
  "Guten Tag, Dermot O'Dyna! "
  'Über 30 Jahre Friseurkunst, TV-Auftritte, ein Salon mit echtem Charakter – '
  '@berlinhaircaresalon_official zeigt das alles. '
  'Aber Ihre Website hat ein SSL-Problem: Kunden, die Ihre Geschichte entdecken '
  'und die Seite öffnen, sehen eine Sicherheitswarnung. '
  'Das ist nicht das Bild, das eine Karriere wie Ihre verdient. '
  f'{N23} '
  f'{CTA}'
)},

# ── 204 Jane Lapuks Friseur ── SSL, unique technique, loyal clients ──────────
{'id': 204, 'salon': 'Jane Lapuks Friseur', 'instagram': None,
 'msg': (
  'Guten Tag, Jane! '
  'Ihre Kunden schreiben: ' + q('Nach 5 Jahren endlich die richtige Friseurin gefunden') +
  ' – und kommen dann jahrelang wieder. '
  'Ihre Strähnen-Technik ist einzigartig, das bestätigt jede Bewertung. '
  'Aber Ihre Website hat kein SSL: neue Kundinnen, die auf Sie aufmerksam werden, '
  'sehen sofort eine Browser-Warnung statt Ihrer Arbeit. '
  f'{N23} '
  f'{CTA}'
)},

# ── 205 Fon Friseur ── instagram, SSL, junges Team ────────────────────────────
{'id': 205, 'salon': 'Fon Friseur', 'instagram': '@fonfriseur',
 'msg': (
  'Guten Tag, FON Friseur Team! '
  '@fonfriseur zeigt ein junges Team, das Qualität zu fairen Preisen liefert – '
  'Flexibilität ohne Termin ist ein echtes Plus in Berlin. '
  'Aber Ihre Website hat kein SSL: Kunden, die Sie über Google finden, '
  'sehen eine Sicherheitswarnung genau in dem Moment, wo sie buchen möchten. '
  f'{N23} '
  f'{CTA}'
)},

# ── 206 Micha Pelz Coiffure ── instagram, iF Award, SSL ──────────────────────
{'id': 206, 'salon': 'Micha Pelz Coiffure', 'instagram': '@michapelzcoiffure',
 'msg': (
  'Sehr geehrter Herr Pelz! '
  'Ihr Salon hat den iF Design Award gewonnen – '
  'der einzige Friseursalon in Berlin, der das von sich sagen kann. '
  '@michapelzcoiffure zeigt La Biosthétique-Farbarbeiten mit einer Natürlichkeit, '
  'die andere nicht hinbekommen. '
  'Aber Ihre Website hat aktuell ein SSL-Problem. '
  'Die Sorgfalt, die Sie in jeden Cut stecken, fehlt online. '
  f'{N23} '
  f'{CTA}'
)},

# ── 207 Forty Two Coiffeur ── Treatwell, Kastanienallee ───────────────────────
{'id': 207, 'salon': 'Forty Two Coiffeur', 'instagram': None,
 'msg': (
  'Guten Tag, Forty Two Coiffeur Team! '
  'Kastanienallee – allein die Adresse sagt: Sie sind mitten in Berlins lebendigstem Kiez. '
  'Aber Sie sind ausschließlich über Treatwell buchbar: keine eigene Domain, '
  'keine eigene Kundendatenbank. '
  'Bei Ihrer Lage und Frequenz ist das Geld, das Sie täglich an eine Plattform abgeben. '
  f'{N23} '
  f'{CTA}'
)},

# ── 208 Coiffeur Paluselli by Sabrina Nieschke ── Udo Walz, Bambi, SSL ───────
{'id': 208, 'salon': 'Coiffeur Paluselli by Sabrina Nieschke', 'instagram': None,
 'msg': (
  'Sehr geehrte Frau Nieschke! '
  'Von der Ausbildung bei Udo Walz, Meisterbrief mit 21, Hollywood-Stars beim Bambi gestylt – '
  'und jetzt Inhaberin von Coiffeur Paluselli. Das ist eine Karriere, die Respekt verdient. '
  'Aber Ihre Website hat kein SSL: Browser zeigen Neukunden eine Warnung. '
  'Für ein Konzept auf Ihrem Niveau ist das ein digitaler Widerspruch. '
  f'{N23} '
  f'{CTA}'
)},

# ── 209 FINE & DANDY ── instagram, AVEDA, SSL, seit 2008 ─────────────────────
{'id': 209, 'salon': 'FINE & DANDY kleine schwester AVEDA', 'instagram': '@fineanddandyberlin',
 'msg': (
  'Guten Tag, FINE & DANDY Team! '
  '@fineanddandyberlin zeigt, was AVEDA Vegan Haircolor in den richtigen Händen kann – '
  'Ihre Balayage-Looks haben eine Leichtigkeit, die man nur mit Produkten und Know-how '
  'auf diesem Niveau erreicht. Seit 2008 in Berlin – das ist eine echte Geschichte. '
  'Aber Ihre Website hat ein SSL-Problem: Browser zeigen mobilen Nutzern eine Sicherheitswarnung. '
  f'{N23} '
  f'{CTA}'
)},

# ── 210 Classico Barbershop ── no instagram, no website ──────────────────────
{'id': 210, 'salon': 'Classico Barbershop', 'instagram': None,
 'msg': (
  'Guten Tag, Classico Barbershop Team! '
  'Klassischer Barbershop-Service – das ist ein Statement in einer Stadt voller Trend-Salons. '
  'Aber Sie haben keine Instagram-Präsenz und keine eigene Webseite. '
  '2025 ist Instagram das Schaufenster Nummer 1 für Barbershops – '
  'wer dort nicht vertreten ist, verliert täglich potenzielle Kunden. '
  f'{N23} '
  f'{CTA}'
)},

# ── 211 St Leonard ── instagram, SSL, London tradition ───────────────────────
{'id': 211, 'salon': 'St Leonard', 'instagram': '@stleonardberlin',
 'msg': (
  'Guten Tag, St Leonard Team! '
  '@stleonardberlin zeigt, was passiert, wenn Londoner Barbering-Tradition '
  'auf Berliner Community trifft – Dominic, Tom und Simon liefern Clean Cuts und Fades, '
  'die zeitlos sind. Das ist eine echte Marke. '
  'Aber Ihre Website hat kein SSL-Zertifikat: Kunden, die Ihren Ruf kennen, '
  'sehen beim Öffnen der Seite eine Browser-Warnung. '
  f'{N23} '
  f'{CTA}'
)},
]

# Validate
print(f'Total records: {len(records)}')
issues = []
for r in records:
    m = r['msg']
    if 'Heute Nacht' in m:
        issues.append(f"ID {r['id']}: contains 'Heute Nacht'")
    import re as _re
    # Check for informal Du/ihr forms — NOT Ihr/Ihre/Ihnen (Sie-form)
    if _re.search(r'\b(du|dein|deine|dich|dir|euer|eure|euch)\b', m, _re.IGNORECASE):
        issues.append(f"ID {r['id']}: informal Du/ihr address found")
    # Check for lowercase 'ihr' (possessive informal) but not 'Ihr/Ihre/Ihnen'
    if _re.search(r'\b(ihr|eure|euch)\b', m):
        issues.append(f"ID {r['id']}: lowercase informal 'ihr/eure/euch'")
    if 'http' in m or 'www.' in m or '.de/' in m or '.com/' in m:
        issues.append(f"ID {r['id']}: URL found")
    if 'Video-Demo' not in m:
        issues.append(f"ID {r['id']}: missing CTA keyword")
    chars = len(m)
    if chars > 600:
        issues.append(f"ID {r['id']}: {chars}c — TOO LONG (>600)")

if issues:
    print('\nVALIDATION ISSUES:')
    for i in issues: print(' ', i)
else:
    print('Validation: ALL OK')

out = os.path.join(_ROOT, 'data', 'berlin_elite_done.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
print(f'\nSaved -> {out}')
for r in records:
    print(f"  ID {r['id']:>3} | {len(r['msg'])}c | {'✦ instagram' if r['instagram'] else '—'}")
