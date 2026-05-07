#!/bin/bash
# =============================================================================
# deploy.sh — Vermarkter Sniper Engine | Server Setup Script
# =============================================================================
# Ubuntu 24.04 LTS | DigitalOcean Droplet 46.101.217.35
# Запускати від root: bash deploy.sh
# =============================================================================
SERVER_IP="46.101.217.35"

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }

echo "============================================================"
echo "  Vermarkter Sniper Engine — Server Setup"
echo "  $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "============================================================"

# =============================================================================
# 1. SYSTEM UPDATE + PYTHON
# =============================================================================
info "Оновлення системи..."
apt-get update -qq && apt-get upgrade -y -qq

info "Встановлення Python 3, pip, утиліт..."
apt-get install -y -qq python3 python3-pip python3-venv curl wget git unzip

PYTHON=$(which python3)
info "Python: $($PYTHON --version)"

# =============================================================================
# 2. DIRECTORY STRUCTURE
# =============================================================================
info "Створення структури /opt/vermarkter/..."
mkdir -p /opt/vermarkter/{scripts,batch,data,logs}
chmod 750 /opt/vermarkter
chmod 700 /opt/vermarkter/logs

info "Структура папок:"
echo "  /opt/vermarkter/"
echo "  ├── scripts/   — Python-скрипти"
echo "  ├── batch/     — JSONL файли та batch_id.txt"
echo "  ├── data/      — review JSON, leads"
echo "  └── logs/      — cron output"

# =============================================================================
# 3. PLACEHOLDER CONFIG FILES
# =============================================================================
info "Створення placeholder .env та config.ini..."

cat > /opt/vermarkter/.env << 'ENVEOF'
OPENAI_API_KEY=PASTE_YOUR_OPENAI_KEY_HERE
BREVO_API_KEY=PASTE_YOUR_BREVO_API_KEY_HERE
ENVEOF

cat > /opt/vermarkter/config.ini << 'INIEOF'
[SUPABASE]
url = https://wrvdbvekiteopkdwxuzz.supabase.co
anon_key = PASTE_ANON_KEY_HERE
service_role_key = PASTE_SERVICE_ROLE_KEY_HERE

[GOOGLE]
maps_api_key = PASTE_GOOGLE_MAPS_KEY_HERE

[OPENAI]
api_key = PASTE_OPENAI_API_KEY_HERE
model   = gpt-4o

[SMTP]
host = smtp.zoho.eu
port = 465
user = hello@vermarkter.eu
password = PASTE_ZOHO_APP_PASSWORD_HERE
from = Vermarkter <hello@vermarkter.eu>

[BREVO]
api_key = PASTE_YOUR_BREVO_API_KEY_HERE
from_email = hello@vermarkter.eu
from_name = Vermarkter
daily_limit = 300
INIEOF

chmod 600 /opt/vermarkter/.env
chmod 600 /opt/vermarkter/config.ini
warn "→ ВРУЧНУ відредагуй /opt/vermarkter/.env та /opt/vermarkter/config.ini після завершення скрипту!"

# =============================================================================
# 4. CRON JOBS
# =============================================================================
info "Налаштування cron-завдань..."

CRON_FILE="/etc/cron.d/vermarkter"

cat > "$CRON_FILE" << 'CRONEOF'
# Vermarkter Sniper Engine — автоматичні задачі
# Timezone: Europe/Berlin
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=""

# 09:00 Берлін — генерація повідомлень для нових лідів
0 9 * * * root cd /opt/vermarkter && TZ=Europe/Berlin /usr/bin/python3 scripts/sniper_engine.py --city Berlin --limit 30 >> logs/sniper_engine.log 2>&1

# 03:00 Берлін — пошук нових PLZ (sniper_fetch як harvester)
0 3 * * * root cd /opt/vermarkter && TZ=Europe/Berlin /usr/bin/python3 scripts/sniper_fetch.py >> logs/lead_harvester.log 2>&1

# 10:00 Берлін — Email-розсилка через Brevo (300/день)
0 10 * * * root cd /opt/vermarkter && TZ=Europe/Berlin /usr/bin/python3 scripts/mass_email_sender.py --limit 300 >> logs/mass_email.log 2>&1

# 09:00 Nice (Europe/Paris = UTC+2) — Каскадна розсилка: Nice→Cannes→Berlin (до 300/день Brevo)
0 7 * * * root cd /opt/vermarkter && TZ=Europe/Paris /usr/bin/python3 scripts/send_email_brevo.py --city Nice --limit 100 >> /opt/vermarkter/logs/email_send.log 2>&1 && /usr/bin/python3 scripts/send_email_brevo.py --city Cannes --limit 100 >> /opt/vermarkter/logs/email_send.log 2>&1 && /usr/bin/python3 scripts/send_email_brevo.py --city Berlin --limit 200 >> /opt/vermarkter/logs/email_send.log 2>&1

# 09:30 Nice — Зведений звіт після розсилки → reports/daily_summary.txt
30 7 * * * root cd /opt/vermarkter && TZ=Europe/Paris /usr/bin/python3 scripts/check_sent_log.py >> /opt/vermarkter/logs/daily_summary.log 2>&1

CRONEOF

chmod 644 "$CRON_FILE"
service cron restart || systemctl restart cron 2>/dev/null || true
info "Cron-завдання встановлено: $CRON_FILE"

# Перевіримо timezone сервера
timedatectl set-timezone Europe/Berlin 2>/dev/null || true
info "Timezone сервера → Europe/Berlin"

# =============================================================================
# 5. BREVO API ПЕРЕВІРКА
# =============================================================================
info "Тест доступності Brevo API (api.brevo.com)..."
python3 - << 'PYEOF'
import urllib.request, json
try:
    req = urllib.request.Request(
        "https://api.brevo.com/v3/account",
        headers={"api-key": "CHECK_AFTER_FILLING_.ENV", "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.loads(r.read())
        print(f"  [BREVO OK] Акаунт: {data.get('email','?')} | Plan: {data.get('plan',[{}])[0].get('type','?')}")
except Exception as e:
    print(f"  [BREVO SKIP] Ключ ще не заповнено (заповни .env і перевір вручну)")
PYEOF

# =============================================================================
# 6. LOG ROTATION
# =============================================================================
info "Налаштування logrotate..."
cat > /etc/logrotate.d/vermarkter << 'LREOF'
/opt/vermarkter/logs/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    copytruncate
}
LREOF

# =============================================================================
# 7. ФІНАЛЬНА ІНСТРУКЦІЯ
# =============================================================================
echo ""
echo "============================================================"
echo "  SETUP ЗАВЕРШЕНО"
echo "============================================================"
echo ""
echo "НАСТУПНІ КРОКИ (виконати вручну):"
echo ""
echo "  1. СКОПІЮВАТИ СКРИПТИ на сервер:"
echo "     (виконати з локальної машини)"
echo ""
echo "     scp -r scripts/ root@46.101.217.35:/opt/vermarkter/"
echo "     scp -r batch/   root@46.101.217.35:/opt/vermarkter/"
echo "     scp -r data/    root@46.101.217.35:/opt/vermarkter/"
echo ""
echo "  2. ЗАПОВНИТИ СЕКРЕТИ (на сервері):"
echo ""
echo "     nano /opt/vermarkter/.env"
echo "       → OPENAI_API_KEY=sk-proj-..."
echo "       → BREVO_API_KEY=xkeysib-..."
echo ""
echo "     nano /opt/vermarkter/config.ini"
echo "       → service_role_key = eyJ..."
echo "       → maps_api_key = AIza..."
echo "       → [BREVO] api_key = xkeysib-..."
echo ""
echo "  3. ТЕСТ ЗАПУСКУ (dry-run):"
echo ""
echo "     cd /opt/vermarkter"
echo "     python3 scripts/sniper_engine.py --city Berlin --limit 5 --dry-run"
echo ""
echo "  4. ПЕРЕВІРИТИ CRON:"
echo ""
echo "     crontab -l -u root"
echo "     cat /etc/cron.d/vermarkter"
echo ""
echo "  5. МОНІТОРИНГ ЛОГІВ:"
echo ""
echo "     tail -f /opt/vermarkter/logs/sniper_engine.log"
echo ""
echo "============================================================"
echo "  Server IP: 46.101.217.35"
echo "  Email Engine: Brevo API | hello@vermarkter.eu"
echo "  Ліміт Brevo Free: 300 листів/день (9000/місяць)"
echo "  Cron Email: щодня о 10:00 Берлін"
echo "============================================================"
