#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, sys, os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

leads = [
  {"id":4691,"name":"L'atelier de Marie : salon de coiffure : coiffeur libanais : hairdresser","website":"https://www.planity.com/atelier-de-marie-06000-nice","phone":"+33 9 88 54 66 55"},
  {"id":4692,"name":"Coiffure Hair Nice","website":"https://www.hair-nice.fr/","phone":"+33 4 93 88 04 73"},
  {"id":4693,"name":"GM coiffure by Pauline","website":None,"phone":"+33 4 93 85 70 07"},
  {"id":4694,"name":"Salon Carré d'Or : Coiffeur à Nice","website":"http://coiffeur-carredor.fr/","phone":"+33 4 93 16 22 07"},
  {"id":4695,"name":"Unik","website":"https://www.instagram.com/unikcoiffure/","phone":"+33 4 93 62 03 22"},
  {"id":4696,"name":"MARINE - COIFFURE & ESTHÉTIQUE","website":"https://www.planity.com/marine-coiffure-esthetique-06000-nice","phone":"+33 7 67 60 06 66"},
  {"id":4697,"name":"Cynthia & Co","website":"https://www.cynthiaandco.fr/","phone":"+33 4 93 85 91 31"},
  {"id":4698,"name":"LE FIL DE L'ÂME","website":"http://www.fildelame.fr/","phone":"+33 4 93 87 45 73"},
  {"id":4699,"name":"Salon Gaspard","website":"https://www.instagram.com/gaspard_coiffure","phone":"+33 4 93 85 06 37"},
  {"id":4700,"name":"Nice Cut mp Coiffure","website":None,"phone":"+33 4 93 92 45 15"},
  {"id":4701,"name":"Identity Hair Design","website":"http://www.identityhairdesign.fr/","phone":"+33 4 93 81 95 33"},
  {"id":4702,"name":"Xena Coiffure","website":"https://m.facebook.com/XENA-Coiffure-525805560897839/","phone":"+33 6 09 07 48 45"},
  {"id":4703,"name":"Le Salon Michel Barbera Coiffure","website":"https://www.planity.com/michel-barbera-06000-nice","phone":"+33 4 93 88 81 11"},
  {"id":4704,"name":"Alias","website":"http://www.aliascoiffure.fr/","phone":"+33 4 93 53 97 33"},
  {"id":4705,"name":"MYSOKO - Salon de coiffure visagiste & Lissage Nice","website":"http://www.mysoko.fr/","phone":"+33 7 67 37 89 13"},
  {"id":4706,"name":"KRISTEL HAIR CONCEPT - Coiffure & Onglerie","website":None,"phone":"+33 6 59 43 08 22"},
  {"id":4707,"name":"Jade & Co.","website":"https://www.planity.com/jade-co-06000-nice","phone":"+33 4 93 91 82 73"},
  {"id":4708,"name":"Hair bar - Nice","website":"https://nail.beauty.ivof.com/hair-bar-nice/","phone":"+33 9 67 47 95 48"},
  {"id":4709,"name":"THIERRY ANTOINE COIFFURE ESTHETIQUE","website":"http://www.thierry-antoine.fr/","phone":"+33 4 93 16 04 77"},
  {"id":4710,"name":"Max Gauthier Coiffure","website":"https://www.instagram.com/maxgauthiercoiffure/","phone":"+33 4 93 37 94 34"},
  {"id":4711,"name":"SOUTH SIDE BARBER NICE","website":"https://www.southsidebarber.fr/","phone":"+33 4 89 00 35 41"},
  {"id":4712,"name":"Seven Barbershop - Nice","website":"https://www.planity.com/seven-barbershop-06000-nice","phone":"+33 7 45 14 37 01"},
  {"id":4713,"name":"West Barber Shop","website":"https://www.planity.com/west-barber-06000-nice","phone":"+33 4 83 39 88 31"},
  {"id":4714,"name":"Le barbier de nice","website":None,"phone":"+33 9 87 56 05 13"},
  {"id":4715,"name":"Barber House Port","website":None,"phone":"+33 7 61 73 84 72"},
  {"id":4716,"name":"MY BARBER SHOP ( Avec / Sans RDV)","website":None,"phone":None},
  {"id":4717,"name":"Le local_barbershop","website":None,"phone":"+33 9 52 08 41 96"},
  {"id":4718,"name":"Best Barber","website":"https://frmaps.xyz/business/best-barber-KBfcL5Hg","phone":"+33 7 44 59 14 99"},
  {"id":4719,"name":"Man To Man barbershop","website":"https://frmapsy.com/business/man-to-man-barbershop-axG2KStc","phone":"+33 6 66 56 07 46"},
  {"id":4720,"name":"BLACKBOX Nice","website":"https://blackboxparis.com/place/blackbox-nice/","phone":"+33 9 65 24 00 45"},
  {"id":4721,"name":"Estika Barber","website":"http://www.planity.com/estika-barber-06300-nice-jro","phone":"+33 6 50 65 57 01"},
  {"id":4722,"name":"My Barberhood","website":None,"phone":"+33 6 88 44 60 24"},
  {"id":4723,"name":"KDH Barber Nice","website":"https://www.planity.com/kdh-barber-06000-nice","phone":"+33 9 87 02 96 27"},
  {"id":4724,"name":"One Love origin","website":None,"phone":"+33 4 93 88 80 12"},
  {"id":4725,"name":"SALON4MEN","website":"http://www.salon4men.fr/","phone":"+33 4 93 56 76 96"},
  {"id":4726,"name":"SOUTH SIDE BARBER STUDIO","website":"https://www.southsidebarber.fr/","phone":"+33 9 55 50 10 50"},
  {"id":4727,"name":"Barber Style - Barber shop Nice","website":None,"phone":"+33 7 68 52 61 02"},
  {"id":4728,"name":"Comptoir des Barbiers","website":None,"phone":"+33 6 16 77 68 99"},
  {"id":4729,"name":"Barber Chic Nice","website":None,"phone":"+33 6 74 98 16 69"},
  {"id":4730,"name":"YU Barber","website":"https://www.planity.com/yu-barber-06000-nice","phone":"+33 9 56 22 64 03"},
]

AR_SIGNALS = ['libanais','arabic','arab','orient','halal','marokk','nour','noor','alhambra','morocc','maroc']
UA_SIGNALS = ['ukraine','ukrainien','ukrainienne','oleksandr','iryna','kateryna','olena','dmytro','oksana','svitlana','kovalchuk','petrenko','shevchenko']

def channel(phone):
    if not phone:
        return 'Email'
    p = phone.replace(' ', '')
    if p.startswith('+336') or p.startswith('+337'):
        return 'WA'
    return 'Email'

def pain(website):
    if not website:
        return 'NoWeb'
    if 'planity.com' in website:
        return 'Planity'
    return 'OwnSite'

def lang(name, website):
    combined = ((name or '') + ' ' + (website or '')).lower()
    for sig in AR_SIGNALS:
        if sig in combined:
            return 'AR'
    for sig in UA_SIGNALS:
        if sig in combined:
            return 'UA'
    return 'FR'

result = []
for l in leads:
    result.append({
        'id': l['id'],
        'name': l['name'],
        'website': l['website'],
        'phone': l['phone'],
        'channel': channel(l['phone']),
        'pain': pain(l['website']),
        'lang': lang(l['name'], l['website']),
    })

os.makedirs('data', exist_ok=True)
with open('data/nice_routing_40.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('SAVED — data/nice_routing_40.json')
print()
print(f"{'ID':<6} {'Назва':<46} {'Канал':<7} {'Біль':<9} Мова")
print('-' * 80)
for r in result:
    print(f"{r['id']:<6} {r['name'][:45]:<46} {r['channel']:<7} {r['pain']:<9} {r['lang']}")

wa  = sum(1 for r in result if r['channel'] == 'WA')
em  = sum(1 for r in result if r['channel'] == 'Email')
pl  = sum(1 for r in result if r['pain'] == 'Planity')
nw  = sum(1 for r in result if r['pain'] == 'NoWeb')
own = sum(1 for r in result if r['pain'] == 'OwnSite')
ar  = sum(1 for r in result if r['lang'] == 'AR')
ua  = sum(1 for r in result if r['lang'] == 'UA')
fr  = sum(1 for r in result if r['lang'] == 'FR')
print()
print(f"Канал   — WA: {wa}  |  Email: {em}")
print(f"Біль    — Planity: {pl}  |  NoWeb: {nw}  |  OwnSite: {own}")
print(f"Мова    — FR: {fr}  |  AR: {ar}  |  UA: {ua}")
