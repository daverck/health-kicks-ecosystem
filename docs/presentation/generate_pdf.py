"""Generates a simplified, high-impact 16:9 landscape PDF presentation for HealthKicks Ecosystem
using ReportLab (pure Python, vector graphics, standalone, clickable links).
"""

import os
import xml.etree.ElementTree as ET
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

# Dimensions for 16:9 landscape slide in points (960 x 540)
PAGE_WIDTH = 960.0
PAGE_HEIGHT = 540.0

# Color Palette
DARK_BG = HexColor("#0f172a")        # Slate 900
LIGHT_BG = HexColor("#f8fafc")       # Slate 50
CARD_BG = HexColor("#ffffff")        # White
CARD_DARK = HexColor("#1e293b")      # Slate 800
BORDER_LIGHT = HexColor("#e2e8f0")   # Slate 200

PRIMARY_TEAL = HexColor("#0d9488")   # Teal 600
TEXT_TEAL = HexColor("#14b8a6")      # Teal 500
ACCENT_AMBER = HexColor("#d97706")   # Amber 600
ACCENT_BLUE = HexColor("#2563eb")    # Blue 600

TEXT_DARK = HexColor("#0f172a")      # Slate 900
TEXT_MUTED = HexColor("#64748b")     # Slate 500
TEXT_LIGHT = HexColor("#f8fafc")     # Slate 50
TEXT_CARD_SUB = HexColor("#94a3b8")  # Slate 400


def draw_header(c, title, dark=False):
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(TEXT_LIGHT if dark else TEXT_DARK)
    c.drawString(50, 480, title)


def draw_svg_paths(canv, svg_path, x_offset, y_offset, target_width):
    """Renders pure SVG path vector commands directly onto ReportLab canvas."""
    if not os.path.exists(svg_path):
        return
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        orig_w, orig_h = 660.0, 440.0
        scale = target_width / orig_w
        target_height = orig_h * scale

        canv.saveState()
        canv.translate(x_offset, y_offset + target_height)
        canv.scale(scale, -scale)

        for elem in root:
            d = elem.attrib.get("d", "")
            fill = elem.attrib.get("fill", "#0EA871")
            canv.setFillColor(HexColor(fill))

            tokens = d.split()
            if not tokens:
                continue
            p = canv.beginPath()
            idx = 0
            while idx < len(tokens):
                cmd = tokens[idx]
                if cmd == "M":
                    p.moveTo(float(tokens[idx + 1]), float(tokens[idx + 2]))
                    idx += 3
                elif cmd == "L":
                    p.lineTo(float(tokens[idx + 1]), float(tokens[idx + 2]))
                    idx += 3
                elif cmd == "Z":
                    p.close()
                    idx += 1
                else:
                    idx += 1
            canv.drawPath(p, fill=1, stroke=0)
        canv.restoreState()
    except Exception as e:
        print(f"Warning: could not render SVG {svg_path}: {e}")


def draw_card(c, x, y, w, h, bg_color, border_color, border_width=1.5, radius=8):
    c.saveState()
    c.setFillColor(bg_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(border_width)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    c.restoreState()


def wrap_text(text, max_chars):
    words = text.split()
    lines = []
    current_line = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def build_pdf(filename="docs/presentation/presentation_healthkicks.pdf"):
    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # ==========================================
    # SLIDE 1 : Titre & Vision Simplifiée
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(TEXT_LIGHT)
    c.drawString(50, 440, "HealthKicks")

    # Big vector logo, enlarged and centered horizontally on the slide
    logo_svg_path = "health-kicks-frontend/public/images/logos/concept_a_vector.svg"
    logo_w = 260
    logo_x = (PAGE_WIDTH - logo_w) / 2  # 350
    draw_svg_paths(c, logo_svg_path, logo_x, 335, logo_w)

    # 2 Centered Cards (Activité & Sécurité), smaller height, pushed down
    card_w = 410
    card_h = 190
    card_y = 50

    cards_s1 = [
        ("GENÈSE", ACCENT_AMBER, [
            "Amateur de course à pied",
            "Mesure au plus près du pied",
        ]),
        ("FONCTIONALITÉS & SECURITÉ", PRIMARY_TEAL, [
            # "Clip universel",
            "Détection de type de mouvements",
            "Detection de chute + alertes",
            "Rappel d'inactivite haptique",
            "Podometrie",
        ])
    ]

    for idx, (title, color, items) in enumerate(cards_s1):
        x = 50 + idx * 450
        draw_card(c, x, card_y, card_w, card_h, CARD_DARK, color, border_width=2)

        c.setFont("Helvetica-Bold", 13.5)
        c.setFillColor(color)
        c.drawString(x + 18, card_y + card_h - 26, title)

        cur_y = card_y + card_h - 52
        for b in items:
            lines = wrap_text(b, 46)
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(TEXT_LIGHT)
            c.drawString(x + 18, cur_y, "-")
            c.setFont("Helvetica", 9.5)
            for line in lines:
                c.drawString(x + 30, cur_y, line)
                cur_y -= 14
            cur_y -= 6

    c.showPage()

    # ==========================================
    # SLIDE 2 : Parcours Professionnel & Portfolio QR Code
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Qui suis-je ?")

    qr_path = "docs/presentation/qr-code.png"
    portfolio_url = "https://daverck.github.io/serck-david-portfolio"

    card_qr_w = 460
    card_qr_h = 405
    card_qr_x = (PAGE_WIDTH - card_qr_w) / 2
    card_qr_y = 35

    draw_card(c, card_qr_x, card_qr_y, card_qr_w, card_qr_h, CARD_BG, PRIMARY_TEAL, border_width=2, radius=12)

    # Nom en grand et centré en haut de la carte
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(card_qr_x + card_qr_w / 2, card_qr_y + card_qr_h - 34, "David Serck")

    # Métier en grand
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(card_qr_x + card_qr_w / 2, card_qr_y + card_qr_h - 58, "Développeur Full-Stack : Angular - Python - Java")

    if os.path.exists(qr_path):
        qr_size = 250
        qr_x = card_qr_x + (card_qr_w - qr_size) / 2
        qr_y = card_qr_y + 45
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)
        c.linkURL(portfolio_url, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), thickness=0)

    c.showPage()

    # ==========================================
    # SLIDE 3 : Architecture Globale Logicielle & Système
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Architecture Global")

    diag_y = 45
    diag_h = 395

    # 1. EMBARQUE : ESP32-S3 (Dual-Core FreeRTOS)
    w_shoe = 260
    x_shoe = 50
    draw_card(c, x_shoe, diag_y, w_shoe, diag_h, CARD_BG, PRIMARY_TEAL, border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 14, diag_y + diag_h - 22, "1. EMBARQUE (ESP32-S3 / FreeRTOS)")
    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_shoe + 14, diag_y + diag_h - 36, "Repartition symetrique sur 2 coeurs Xtensa 240 MHz")

    # Coeur 0
    draw_card(c, x_shoe + 10, diag_y + diag_h - 170, w_shoe - 20, 124, LIGHT_BG, PRIMARY_TEAL, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 18, diag_y + diag_h - 60, "Coeur 0 : Reseau & Systeme")
    core0_items = [
        ("Pile NimBLE GATT", "Serveur BLE, pairage securise LESC 60s."),
        ("OTA Streaming Service", "Reception du binaire Flash sans coupure."),
        ("Power Manager", "Veille legere & deep sleep anti-decharge.")
    ]
    cur_cy = diag_y + diag_h - 78
    for t_it, d_it in core0_items:
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 18, cur_cy, "> " + t_it)
        cur_cy -= 11
        c.setFont("Helvetica", 6.8)
        c.setFillColor(TEXT_MUTED)
        c.drawString(x_shoe + 24, cur_cy, d_it)
        cur_cy -= 15

    # Coeur 1
    draw_card(c, x_shoe + 10, diag_y + 14, w_shoe - 20, 200, LIGHT_BG, ACCENT_BLUE, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_shoe + 18, diag_y + 198, "Coeur 1 : Temps Reel & Metier")
    core1_items = [
        ("Bus I2C Fast-Mode (400 kHz)", "Acquisition non-bloquante a 19 Hz (53 ms)."),
        ("Inference TinyML C pur", "Random Forest compile (~12 us, pile pure)."),
        ("Task Watchdog (TWDT 5s)", "Protection contre tout blocage I2C / CPU."),
        ("Pilote Haptique PWM (10 kHz)", "Vibrations anti-sedentarite et alarmes."),
        ("Buffer Circulaire HITL (76 trames)", "Historique 4.0s pour requalification Studio.")
    ]
    cur_cy = diag_y + 182
    for t_it, d_it in core1_items:
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 18, cur_cy, "> " + t_it)
        cur_cy -= 11
        c.setFont("Helvetica", 6.8)
        c.setFillColor(TEXT_MUTED)
        c.drawString(x_shoe + 24, cur_cy, d_it)
        cur_cy -= 14

    # FLECHE 1 : BLE LESC
    arr1_x = x_shoe + w_shoe + 3
    arr1_y = diag_y + diag_h / 2 + 10
    arr1_w = 40
    c.setStrokeColor(PRIMARY_TEAL)
    c.setLineWidth(1.8)
    c.line(arr1_x, arr1_y, arr1_x + arr1_w, arr1_y)
    p = c.beginPath()
    p.moveTo(arr1_x + arr1_w, arr1_y)
    p.lineTo(arr1_x + arr1_w - 6, arr1_y + 4)
    p.lineTo(arr1_x + arr1_w - 6, arr1_y - 4)
    p.close()
    c.setFillColor(PRIMARY_TEAL)
    c.drawPath(p, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(arr1_x + arr1_w / 2, arr1_y + 8, "BLE GATT")
    c.setFont("Helvetica", 6.8)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(arr1_x + arr1_w / 2, arr1_y - 12, "LESC Chiffre")

    # 2. PASSERELLE MOBILE : Flutter / SQLite
    w_mob = 210
    x_mob = arr1_x + arr1_w + 5
    draw_card(c, x_mob, diag_y, w_mob, diag_h, CARD_BG, ACCENT_BLUE, border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 14, diag_y + diag_h - 22, "2. MOBILE (Flutter / Dart)")
    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_mob + 14, diag_y + diag_h - 36, "Passerelle de terrain & persistance locale")

    mob_cards = [
        ("Base Locale SQLite", "Stockage hors-ligne sans perte\\nConsolidation des donnees de marche"),
        ("Securite & Auth OAuth2", "Echange tickets PKCE RFC 7636\\nRecuperation jetons AWS STS temporaires"),
        ("Passerelle MQTT SigV4", "WebSockets vers AWS IoT Core (QoS 1)\\nSignature cryptographique des requetes"),
    ]
    cur_my = diag_y + diag_h - 52
    for m_t, m_d in mob_cards:
        draw_card(c, x_mob + 10, cur_my - 68, w_mob - 20, 68, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(ACCENT_BLUE)
        c.drawString(x_mob + 18, cur_my - 16, m_t)
        c.setFont("Helvetica", 6.8)
        c.setFillColor(TEXT_MUTED)
        for line_idx, line in enumerate(m_d.split("\\n")):
            c.drawString(x_mob + 18, cur_my - 30 - (line_idx * 11), line)
        cur_my -= 82

    # FLECHE 2 : MQTT SigV4
    arr2_x = x_mob + w_mob + 3
    arr2_y = diag_y + diag_h / 2 + 10
    arr2_w = 40
    c.setStrokeColor(ACCENT_BLUE)
    c.setLineWidth(1.8)
    c.line(arr2_x, arr2_y, arr2_x + arr2_w, arr2_y)
    p = c.beginPath()
    p.moveTo(arr2_x + arr2_w, arr2_y)
    p.lineTo(arr2_x + arr2_w - 6, arr2_y + 4)
    p.lineTo(arr2_x + arr2_w - 6, arr2_y - 4)
    p.close()
    c.setFillColor(ACCENT_BLUE)
    c.drawPath(p, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawCentredString(arr2_x + arr2_w / 2, arr2_y + 8, "MQTT SigV4")
    c.setFont("Helvetica", 6.8)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(arr2_x + arr2_w / 2, arr2_y - 12, "WebSockets")

    # 3. CLOUD AWS & SERVEUR DEDIE
    w_cloud = 330
    x_cloud = arr2_x + arr2_w + 5
    draw_card(c, x_cloud, diag_y, w_cloud, diag_h, CARD_BG, HexColor("#0284c7"), border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(HexColor("#0284c7"))
    c.drawString(x_cloud + 14, diag_y + diag_h - 22, "3. CLOUD AWS & SERVEUR HEALTHKICKS")
    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 14, diag_y + diag_h - 36, "Ingestion sans serveur, bases distribuees & conteneurs Docker")

    # 3.1 Haut : Ingestion IoT Core + Lambdas
    y_ingest = diag_y + diag_h - 120
    h_ingest = 74
    draw_card(c, x_cloud + 10, y_ingest, w_cloud - 20, h_ingest, LIGHT_BG, HexColor("#38bdf8"), border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor("#0284c7"))
    c.drawString(x_cloud + 18, y_ingest + h_ingest - 14, "AWS IoT Core (Broker MQTT QoS 1) & Fonctions Lambdas")

    draw_card(c, x_cloud + 16, y_ingest + 8, 140, 46, CARD_BG, BORDER_LIGHT, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 22, y_ingest + 40, "Lambda Ingest (Chutes/Telemetrie)")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 22, y_ingest + 27, "Ecriture directe sans serveur")
    c.drawString(x_cloud + 22, y_ingest + 15, "-> DynamoDB Time-Series")

    draw_card(c, x_cloud + 164, y_ingest + 8, 140, 46, CARD_BG, BORDER_LIGHT, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 170, y_ingest + 40, "Lambda Presence (Statuts)")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 170, y_ingest + 27, "Notification online / offline")
    c.drawString(x_cloud + 170, y_ingest + 15, "-> API FastAPI Internal")

    # 3.2 Milieu : Serveur EC2 Docker & Domaine
    y_ec2 = diag_y + 105
    h_ec2 = 130
    draw_card(c, x_cloud + 10, y_ec2, w_cloud - 20, h_ec2, CARD_BG, PRIMARY_TEAL, border_width=1.5, radius=8)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 18, y_ec2 + h_ec2 - 14, "Serveur EC2 (AWS t3.micro)")

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 145, y_ec2 + h_ec2 - 14, "eu-north-1b | 2 vCPU x86_64 | 1 Go RAM | 8 Go SSD gp3")

    c.setFont("Helvetica", 6.2)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 18, y_ec2 + h_ec2 - 25, "OS: Ubuntu 26.04 LTS Server | Nginx Reverse Proxy (SSL Let's Encrypt / DNS domaine)")

    # Backend
    draw_card(c, x_cloud + 16, y_ec2 + 6, 140, 92, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=5)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 22, y_ec2 + 82, "Docker Backend FastAPI")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 22, y_ec2 + 70, "- API REST OpenAPI / Python")
    c.drawString(x_cloud + 22, y_ec2 + 58, "- Courtier jetons STS (15 min)")
    c.drawString(x_cloud + 22, y_ec2 + 46, "- Routage Email avec SPF/DKIM")
    c.drawString(x_cloud + 22, y_ec2 + 34, "- Gestion sessions Studio / HITL")
    c.drawString(x_cloud + 22, y_ec2 + 22, "- Relais d'alertes & audit")
    c.drawString(x_cloud + 22, y_ec2 + 10, "- Reverse proxy Nginx en amont")

    # Frontend
    draw_card(c, x_cloud + 164, y_ec2 + 6, 140, 92, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=5)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 170, y_ec2 + 82, "Docker Frontend Angular 22")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 170, y_ec2 + 70, "- Interface reactive Signals")
    c.drawString(x_cloud + 170, y_ec2 + 58, "- SPA Standalone Components")
    c.drawString(x_cloud + 170, y_ec2 + 46, "- Suivi podometrie patient")
    c.drawString(x_cloud + 170, y_ec2 + 34, "- Studio Requalification ML")
    c.drawString(x_cloud + 170, y_ec2 + 22, "- Echanges 100% REST HTTPS")
    c.drawString(x_cloud + 170, y_ec2 + 10, "- Reverse proxy Nginx en amont")

    # 3.3 Bas : Bases de donnees
    y_db = diag_y + 8
    h_db = 90
    draw_card(c, x_cloud + 10, y_db, w_cloud - 20, h_db, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 18, y_db + h_db - 14, "Double Persistance Relationnelle & NoSQL")

    draw_card(c, x_cloud + 16, y_db + 8, 140, 64, CARD_BG, PRIMARY_TEAL, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 22, y_db + 56, "PostgreSQL 16 (Aurora)")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 22, y_db + 43, "Verite relationnelle & metier :")
    c.drawString(x_cloud + 22, y_db + 31, "comptes, profils, podometrie nette")
    c.drawString(x_cloud + 22, y_db + 19, "et sessions Studio (Alembic)")

    draw_card(c, x_cloud + 164, y_db + 8, 140, 64, CARD_BG, ACCENT_AMBER, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 170, y_db + 56, "Amazon DynamoDB")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(x_cloud + 170, y_db + 43, "Series temporelles brutes :")
    c.drawString(x_cloud + 170, y_db + 31, "evenements chutes, telemetrie")
    c.drawString(x_cloud + 170, y_db + 19, "et paquets Studio Burst (NoSQL)")

    c.showPage()

    # ==========================================
    # SLIDE 4 : Cœur IoT & Biomécanique
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "SYSTEME EMBARQUE")

    # Schéma Électronique Global en ASCII Art
    schema_y = 205
    schema_h = 245
    draw_card(c, 50, schema_y, 860, schema_h, CARD_DARK, PRIMARY_TEAL, border_width=1.5, radius=8)

    # Titre du Schéma Électronique
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, schema_y + schema_h - 16, "SCHEMA ELECTRONIQUE GLOBAL D'INTERCONNEXION MATERIELLE (ESP32-S3)")

    ascii_circuit = [
        "+-------------------+       +----------------+   +---------------------------------------+   +-----------------------+",
        "|  Batterie LiPo 1S |       | DC/DC Boost 5V |   |           ESP32-S3 WROOM-1            |   |  Module IMU MPU-6050  |",
        "|  (3.7V / 500mAh)  |       |                |   |                                       |   |                       |",
        "|       [VBAT 3.7V] |--[/]->| [VIN]    [VOUT]|==>| [VIN 5V]                   [3.3V OUT] |---+--> [VCC 3.3V]         |",
        "|                   |  SW1  |                |   |                                       |   |                       |",
        "|             [GND] |------>| [GND]    [GND] |-->| [GND]                           [GND] |---+--> [GND & AD0] (0x68) |",
        "+-------------------+       +----------------+   |                                       |   |                       |",
        "                                                 | [GPIO 4]  (I2C SDA Donnees) ----------|---+--> [SDA]              |",
        "                                                 | [GPIO 5]  (I2C SCL Horloge) ----------|---+--> [SCL]              |",
        "                                                 | [GPIO 6] <----------------------------|---+--- [INT] (WOM Reveil) |",
        "                                                 |                                       |   +-----------------------+",
        "                                                 |                                       |                            ",
        "                                                 |                                       |   +-----------------------+",
        "                                                 |                                       |   | Module Vibreur        |",
        "                                                 | [3.3V OUT] ---------------------------|---+--> [VCC +3.3V]        |",
        "                                                 | [GPIO 7]   (PWM LEDC) ----------------|---+--> [IN / SIG] (Gate)  |",
        "                                                 | [GND] --------------------------------|---+--> [GND Masse]        |",
        "                                                 |                                       |   +-----------------------+",
        "                                                 |                                       |                            ",
        "                                                 | [GPIO 13] (Statut & Bouton) ----------|--> [R:100R]--[>|]--[/]--+  ",
        "                                                 |                                       |    LED Bleue   Bouton   |  ",
        "                                                 | [GND] <-------------------------------|-------------------------+  ",
        "                                                 +---------------------------------------+                            "
    ]

    c.setFont("Courier-Bold", 6.8)
    c.setFillColor(TEXT_LIGHT)
    line_y = schema_y + schema_h - 30
    for line in ascii_circuit:
        c.drawString(60, line_y, line)
        line_y -= 9.0

    # 2 Cartes en dessous : Biomécanique ISB & Traitement du Signal
    card_b_y = 35
    card_b_h = 160
    card_b_w = 420

    # Carte Gauche : Référentiel ISB
    draw_card(c, 50, card_b_y, card_b_w, card_b_h, CARD_BG, ACCENT_BLUE, border_width=1.5, radius=8)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(68, card_b_y + card_b_h - 24, "REFERENTIEL BIOMECANIQUE ISB")

    isb_items = [
        ("Axe Z (Vertical)", "+1.0 g au repos"),
        ("Axe X (Antero-posterieur)", ""),
        ("Axe Y (Medio-lateral)", "")
    ]
    cur_y = card_b_y + card_b_h - 48
    for lbl, desc in isb_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "> " + lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(78, cur_y, line)
            cur_y -= 12
        cur_y -= 5

    # Carte Droite : Traitement du Signal Embarqué
    draw_card(c, 490, card_b_y, card_b_w, card_b_h, CARD_BG, ACCENT_AMBER, border_width=1.5, radius=8)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(508, card_b_y + card_b_h - 24, "TRAITEMENT DU SIGNAL")

    dsp_items = [
        ("Fenetrage Glissant (3.0s)", ""),
        ("Invariance par Rotation", ""),
        ("Calibration du Zero-G (Biais)", ""),
        ("Filtrage Anti-Rebond Chute", "")
    ]
    cur_y = card_b_y + card_b_h - 48
    for lbl, desc in dsp_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "> " + lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(518, cur_y, line)
            cur_y -= 12
        cur_y -= 5

    c.showPage()

    # ==========================================
    # SLIDE 5 : Edge Machine Learning & Détail des Features
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "INTELLIGENCE ARTIFICIELLE EMBARQUEE")

    col_y = 45
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "POURQUOI UN RANDOM FOREST PLUTOT QU'UN AUTRE ?")

    model_points = [
        ("vs Deep Learning (TFLite Micro)", "100x plus rapide (~12 us vs 15-50 ms)."),
        ("vs Modeles Lineaires & SVM", "Capture nativement les frontieres non-lineaires complexes "),
        ("vs Arbre de Decision Unique (CART)", "L'agregation de 80 arbres (bagging) reduit drastiquement la variance et immunise contre le bruit"),
        ("vs Gradient Boosting (XGBoost)", "Vote probabiliste direct sans interpreteur lourd. class_weight='balanced' preserve un rappel chute >95% sur les classes rares."),
        ("Transpilation C Pur (m2cgen)", "")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in model_points:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "> " + lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(78, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    draw_card(c, 490, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + 390 - 28, "28 FEATURES")

    feat_points = [
        ("Magnitudes axiales", "min, max, mean, std, peak-to-peak"),
        ("Magnitudes Angulaire", ""),
        ("Dispersion par Axe", "std"),
        ("jerk maximal", "Derivee temporelle de l'acceleration"),
        ("Immobilite Post-Chute", "Ecart-type sur la derniere moitie de fenetre"),
        ("Dynamique Temporelle", "peak-to-peak premiere moitie")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in feat_points:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "> " + lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(518, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    c.showPage()

    # ==========================================
    # SLIDE 6 : Performances Mesurées & Graphique ML
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "VALIDATION & CONTROLE")

    # Badge Démonstration en Direct
    draw_card(c, 520, 470, 390, 26, ACCENT_AMBER, ACCENT_AMBER, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(TEXT_LIGHT)
    c.drawCentredString(715, 478, "DEMONSTRATION 1 : DETECTION DE CHUTE EN DIRECT")

    # Gauche : Graphique des performances ML réel (capture web Studio cliquable)
    ml_img_path = "health-kicks-frontend/public/images/screenshots/ml_stats.png"
    card_l_w = 460
    card_h = 390
    draw_card(c, 50, col_y, card_l_w, card_h, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + card_h - 26, "BENCHMARK REEL STUDIO (F1-SCORE & DISTRIBUTION)")

    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_MUTED)
    c.drawString(68, col_y + card_h - 40, "Matrice de confusion et métriques par classe (cliquer sur l'image pour ouvrir en direct)")

    if os.path.exists(ml_img_path):
        img_w = 424
        img_h = 310
        img_x = 68
        img_y = col_y + 18
        c.drawImage(ml_img_path, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True)
        studio_url = "https://healthkicks.duckdns.org/dashboard/studio/classes"
        c.linkURL(studio_url, (img_x, img_y, img_x + img_w, img_y + img_h), thickness=0)

    # Droite : 2 Grandes Cartes Métriques empilées
    card_r_x = 530
    card_r_w = 380
    card_metric_h = 188

    # Carte 1 (Haut) : Temps d'inférence
    card_1_y = col_y + 202
    draw_card(c, card_r_x, card_1_y, card_r_w, card_metric_h, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 115, "~12 us")
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 80, "TEMPS D'INFERENCE EMBARQUE")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 55, "Mesure reelle micros() sur Coeur 1 (Xtensa 240 MHz)")
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 38, "Transpilation C pur : zero allocation dynamique (0 Ko RAM)")
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 21, "100x plus rapide qu'un runtime de reseaux de neurones")

    # Carte 2 (Bas) : Macro F1-Score
    card_2_y = col_y
    draw_card(c, card_r_x, card_2_y, card_r_w, card_metric_h, CARD_BG, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(ACCENT_AMBER)
    c.drawCentredString(card_r_x + card_r_w / 2, card_2_y + 115, "91.3%")
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(card_r_x + card_r_w / 2, card_2_y + 80, "MACRO F1-SCORE GLOBAL")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(card_r_x + card_r_w / 2, card_2_y + 55, "Classification multiclasse temps reel sur 16 etats moteurs")
    c.drawCentredString(card_r_x + card_r_w / 2, card_2_y + 38, "Rappel chutes critiques : > 95% (ponderation balanced)")
    c.drawCentredString(card_r_x + card_r_w / 2, card_2_y + 21, "Robustesse aux faux positifs du quotidien (marche, repos, assis)")

    c.showPage()

    # ==========================================
    # SLIDE 7 : MLOps Pipeline & Mode HITL
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "CYCLE D'ENTRAINEMENT CONTINU")

    # Badge Démonstration en Direct
    draw_card(c, 520, 470, 390, 26, PRIMARY_TEAL, PRIMARY_TEAL, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(TEXT_LIGHT)
    c.drawCentredString(715, 478, "DEMONSTRATION 2 : STUDIO WEB & REQUALIFICATION HITL")

    draw_card(c, 50, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(68, col_y + 390 - 28, "MLOps Pipeline")

    steps_mlops = [
        ("1. Capture", ""),
        ("2. Qualification Studio Mobile & Web", ""),
        ("3. Pipeline Python d'Entrainement", ""),
        ("4. Transpilation m2cgen Pure C", ""),
        ("5. Injection Firmware Sans Recompilation", "")
    ]

    cur_y = col_y + 390 - 58
    for lbl, desc in steps_mlops:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "> " + lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(78, cur_y, line)
            cur_y -= 13
        cur_y -= 8

    draw_card(c, 490, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(508, col_y + 390 - 28, "MODE HITL (Human-in-the-Loop)")

    hitl_items = [
        ("Buffer Circulaire Haute Frequence", ""),
        ("Capture Pre & Post Evenement", ""),
        ("Transfert Fast Burst BLE", ""),
        ("Requalification Web Studio", "")
    ]

    cur_y = col_y + 390 - 58
    for lbl, desc in hitl_items:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "> " + lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(518, cur_y, line)
            cur_y -= 13
        cur_y -= 8

    c.showPage()

    # ==========================================
    # SLIDE 8 : Conclusion & Perspectives
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "SYNTHESE & PERSPECTIVES D'AVENIR", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "CE QUE NOUS AVONS DEMONTRE")

    achievements = [
        ("TinyML Performant", ""),
        ("Chaine IoT Securisee", ""),
        ("Alerte rapide", "")
    ]
    cur_y = 370
    for lbl, desc in achievements:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(68, cur_y, "[x] " + lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 48)
        for line in lines:
            c.drawString(82, cur_y, line)
            cur_y -= 13
        cur_y -= 10

    draw_card(c, 490, 45, 420, 390, CARD_DARK, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(HexColor("#fbbf24"))
    c.drawString(508, 405, "FEUILLE DE ROUTE")

    roadmap = [
        ("Dispositif Jumeau (Twin Devices)", ""),
        ("Elements de Confort", ""),
        ("Escalade Avancee des Alertes", ""),
        ("Redondance", ""),
        ("MLOps Continu & Adaptation On-Device", ""),
        ("Séances d'exercices ou choégraphie", ""),
        ("Connectivite Cellulaire NB-IoT", "")
    ]
    cur_y = 375
    for lbl, desc in roadmap:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(508, cur_y, "-> " + lbl)
        cur_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 54)
        for line in lines:
            c.drawString(522, cur_y, line)
            cur_y -= 11
        cur_y -= 7

    c.showPage()

    # ==========================================
    # SLIDE 9 : Remerciements & Questions / Réponses (Liens Cliquables & Échanges)
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "ECHANGE & DISCUSSION", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "RESSOURCES DU PROJET & DEMO EN LIGNE")

    demo_links = [
        ("Site Portfolio & CV", "https://daverck.github.io/serck-david-portfolio", "daverck.github.io/serck-david-portfolio"),
        ("Plateforme Web Live", "https://healthkicks.duckdns.org", "healthkicks.duckdns.org"),
        ("Studio & Stats du Modele ML", "https://healthkicks.duckdns.org/dashboard/studio/classes", "healthkicks.duckdns.org/dashboard/studio/classes"),
        ("SCode Source & Specifications", "https://github.com/daverck/health-kicks-ecosystem", "github.com/daverck/health-kicks-ecosystem")
    ]

    cur_y = 365
    for lbl, target_url, display_txt in demo_links:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(68, cur_y, "> " + lbl + " :")
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(ACCENT_BLUE)
        c.drawString(82, cur_y, display_txt)
        c.linkURL(target_url, (82, cur_y - 2, 82 + 300, cur_y + 11), thickness=0)
        cur_y -= 14

    draw_card(c, 490, 45, 420, 390, CARD_DARK, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(HexColor("#fbbf24"))
    c.drawString(508, 405, "THEMES TECHNIQUES A APPROFONDIR")

    discussion_items = [
        ("Optimisation FreeRTOS Dual-Core", ""),
        ("Podométrie Nette & Gestion des Reboots", ""),
        ("Boucle MLOps & Mode HITL", ""),
        ("Securite Zero Trust & Donnees de Marche", "")
    ]
    cur_y = 375
    for lbl, desc in discussion_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(508, cur_y, "> " + lbl)
        cur_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 54)
        for line in lines:
            c.drawString(522, cur_y, line)
            cur_y -= 11
        cur_y -= 7

    c.showPage()

    # ==========================================
    # SLIDE 10 (ANNEXE / SUPPORT) : Podométrie Différentielle Nette
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "PODOMETRIE (SUPPORT / QUESTIONS)")

    # Gauche : Algorithme SQLite & Architecture
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "ALGORITHME D'ODOMETRIE NETTE (SQLite)")

    podo_items = [
        ("Compteur Monotone Physique", ""),
        ("Calcul Differentiel Mobile", ""),
        ("Resilience aux Redemarrages", ""),
        ("Bascule Nette a Minuit", ""),
        # ("Ventilation Horaire Reelle", "Chaque pas est assigne a son heure exacte d'accumulation (aucune extrapolation theorique)."),
        ("Insensibilite aux Gestes Parasites", "")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in podo_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "> " + lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(78, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    # Droite : Graphique Podometre Reel (capture pedometer.png)
    podo_img_path = "health-kicks-frontend/public/images/screenshots/pedometer.png"
    draw_card(c, 490, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + 390 - 28, "RESTITUTION CLINIQUE DES PAS PAR HEURE")

    if os.path.exists(podo_img_path):
        c.drawImage(podo_img_path, 508, 110, width=384, height=230, preserveAspectRatio=True)
        steps_url = "https://healthkicks.duckdns.org/dashboard/steps"
        c.linkURL(steps_url, (508, 110, 508 + 384, 110 + 230), thickness=0)

    c.showPage()

    # ==========================================
    # SLIDE 11 (ANNEXE / SUPPORT) : Coûts du Projet & Frugalité
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "COUTS DU PROJET & FRUGALITE (SUPPORT)")

    # Gauche : Hardware / Matériel Embarqué
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "MATERIEL EMBARQUE & PROTOTYPE")

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(TEXT_DARK)
    c.drawString(68, col_y + 390 - 50, "Cout unitaire prototype : ~32.50 EUR (Industrialisation : < 15 EUR)")

    hw_costs = [
        ("Microcontroleur ESP32-S3 WROOM-1", "~15.00 EUR", "Dual-Core 240 MHz, 8 Mo Flash, 512 Ko SRAM, BLE 5.0, WiFi"),
        ("Module IMU 6 axes (MPU-6050)", "~3.00 EUR", "Accelerometre 3D + Gyroscope 3D I2C (echantillonnage 19 Hz)"),
        ("Vibreur Haptique Miniaturise", "~3.00 EUR", "Moteur vibrant DC controle par signal PWM LEDC"),
        ("Batterie LiPo 1S Rechargeable (500 mAh)", "~4.50 EUR", "Alimentation nomade autonome, compacite maximale pour clip"),
        ("Convertisseur DC/DC & Regulateur LDO", "~2.00 EUR", "Abaisseur haute efficacite avec protection decharge profonde"),
        ("Support Perfboard & composant électronique divers", "~5.00 EUR", "Circuit d'integration, connectique, resistances, interrupteur")
    ]

    cur_y = col_y + 390 - 75
    for item, price, desc in hw_costs:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "> " + item)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(PRIMARY_TEAL)
        c.drawRightString(450, cur_y, price)
        cur_y -= 13
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 52)
        for line in lines:
            c.drawString(78, cur_y, line)
            cur_y -= 11
        cur_y -= 5

    # Ligne de TOTAL Matériel
    c.setStrokeColor(PRIMARY_TEAL)
    c.setLineWidth(1)
    c.line(68, col_y + 36, 450, col_y + 36)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(68, col_y + 20, "TOTAL MATERIEL PROTOTYPE")
    c.setFillColor(PRIMARY_TEAL)
    c.drawRightString(450, col_y + 20, "32.50 EUR")

    # Droite : Cloud, Nom de Domaine & Outils
    draw_card(c, 490, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + 390 - 28, "INFRASTRUCTURE CLOUD & SERVICES")

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(TEXT_DARK)
    c.drawString(508, col_y + 390 - 50, "Cout Cloud mensuel : ~0 EUR (Free Tier)")

    services_costs = [
        ("Cloud AWS (Free Tier & Credits Gratuits)", "0 EUR / mois", "EC2 t3.micro (750h/m), IoT Core (500k msg), DynamoDB (25 Go), Lambdas STS (1M req/m) entierement couverts par l'offre gratuite."),
        ("Pipeline CI/CD GitHub Actions", "0 EUR (Free Usage)", "Builds multi-plateformes, execution des suites de tests unitaires et validation automatique a chaque commit."),
        ("Nom de Domaine Personnalise Dedie", "~12 EUR / an", "Achat d'un domaine pour la production : securisation SSL HTTPS, configuration SPF / DKIM / DMARC pour l'envoi garanti d'emails d'alerte sans spam."),
        ("Assistance IA & Pair-Programming (Gemini)", "~5.5 EUR / mois", "Utilisation de Gemini pour l'orchestration multi-agents, le developpement fullstack, le refactoring TinyML et les tests automatisés."),
    ]

    cur_y = col_y + 390 - 75
    for item, price, desc in services_costs:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "> " + item)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(ACCENT_BLUE)
        c.drawRightString(890, cur_y, price)
        cur_y -= 14
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(518, cur_y, line)
            cur_y -= 12
        cur_y -= 8

    # Ligne de TOTAL Cloud & Services
    c.setStrokeColor(ACCENT_BLUE)
    c.setLineWidth(1)
    c.line(508, col_y + 36, 890, col_y + 36)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(508, col_y + 20, "TOTAL SERVICES RECURRENTS")
    c.setFillColor(ACCENT_BLUE)
    c.drawRightString(890, col_y + 20, "~6.50 EUR / mois (12 EUR / an + 5.50/m)")

    c.save()
    print(f"Simplified PDF saved to: {filename}")


if __name__ == "__main__":
    build_pdf()
