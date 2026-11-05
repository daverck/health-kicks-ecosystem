"""Generates a simplified, high-impact 16:9 landscape PDF presentation for HealthKicks Ecosystem
using ReportLab (pure Python, vector graphics, standalone, clickable links).
"""

import os
from defusedxml.ElementTree import parse
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
        tree = parse(svg_path)
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


def draw_arrow(c, x, y, w, color, label_top="", label_bottom=""):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.6)
    c.line(x, y, x + w, y)
    p = c.beginPath()
    p.moveTo(x + w, y)
    p.lineTo(x + w - 5, y + 3.5)
    p.lineTo(x + w - 5, y - 3.5)
    p.close()
    c.setFillColor(color)
    c.drawPath(p, fill=1, stroke=0)
    if label_top:
        c.setFont("Helvetica-Bold", 6.8)
        c.setFillColor(color)
        c.drawCentredString(x + w / 2, y + 6, label_top)
    if label_bottom:
        c.setFont("Helvetica", 5.8)
        c.setFillColor(TEXT_MUTED)
        c.drawCentredString(x + w / 2, y - 10, label_bottom)
    c.restoreState()


def draw_down_arrow(c, x, y_top, y_bottom, color, label=""):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.6)
    c.line(x, y_top, x, y_bottom)
    p = c.beginPath()
    p.moveTo(x, y_bottom)
    p.lineTo(x - 3.5, y_bottom + 5)
    p.lineTo(x + 3.5, y_bottom + 5)
    p.close()
    c.setFillColor(color)
    c.drawPath(p, fill=1, stroke=0)
    if label:
        c.setFont("Helvetica-Bold", 6.8)
        c.setFillColor(color)
        c.drawString(x + 8, (y_top + y_bottom) / 2 - 2.5, label)
    c.restoreState()


def build_pdf(filename="docs/presentation/presentation_healthkicks.pdf"):
    target_filename = filename
    if os.path.exists(filename):
        try:
            with open(filename, "ab"):
                pass
        except PermissionError:
            target_filename = "docs/presentation/presentation_healthkicks_preview.pdf"
            print(f"Warning: {filename} is currently open in an external PDF reader. Generating {target_filename} instead.")

    c = canvas.Canvas(target_filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # ==========================================
    # SLIDE 1 : Titre & Vision Simplifiée
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)

    # Big vector logo, enlarged and centered horizontally on the slide
    logo_svg_path = "health-kicks-frontend/public/images/logos/concept_a_vector.svg"
    logo_w = 320
    logo_h = 440.0 * (logo_w / 660.0)  # ~213.3 pt
    logo_x = (PAGE_WIDTH - logo_w) / 2  # 320.0
    logo_y = 280
    draw_svg_paths(c, logo_svg_path, logo_x, logo_y, logo_w)

    # Large Styled Title matching the web app: Health (white) + Kicks (primary-600 / #1d5cf5)
    title_font_size = 46
    c.setFont("Helvetica-Bold", title_font_size)
    w_health = c.stringWidth("Health", "Helvetica-Bold", title_font_size)
    w_kicks = c.stringWidth("Kicks", "Helvetica-Bold", title_font_size)
    total_title_w = w_health + w_kicks
    title_x = (PAGE_WIDTH - total_title_w) / 2
    title_y = 236

    c.setFillColor(TEXT_LIGHT)
    c.drawString(title_x, title_y, "Health")
    c.setFillColor(HexColor("#1d5cf5"))  # Tailwind primary-600
    c.drawString(title_x + w_health, title_y, "Kicks")

    # 2 Centered Cards (Activité & Sécurité), positioned below the title
    card_w = 410
    card_h = 165
    card_y = 42

    cards_s1 = [
        ("GENÈSE", ACCENT_AMBER, [
            "Amateur de course à pied",
            "Mesure au plus près du pied",
        ]),
        ("FONCTIONNALITÉS & SÉCURITÉ", PRIMARY_TEAL, [
            # "Clip universel",
            "Détection de types de mouvements",
            "Détection de chute + alertes",
            "Rappel d'inactivité haptique",
            "Podométrie",
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
            c.drawString(x + 18, cur_y, "•")
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
    # SLIDE 3 : Cœur IoT & Biomécanique (Système Embarqué)
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "SYSTÈME EMBARQUÉ")

    # Schéma Électronique Global
    schema_y = 205
    schema_h = 245
    draw_card(c, 50, schema_y, 860, schema_h, CARD_DARK, PRIMARY_TEAL, border_width=1.5, radius=8)

    # Titre du Schéma Électronique
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, schema_y + schema_h - 16, "SCHÉMA ÉLECTRONIQUE GLOBAL D'INTERCONNEXION MATÉRIELLE (ESP32-S3)")

    schematic_path = "docs/presentation/circuit_esp32.png"
    if os.path.exists(schematic_path):
        c.drawImage(schematic_path, 60, schema_y + 8, width=840, height=210, preserveAspectRatio=True, anchor='c')

    # 2 Cartes en dessous : Biomécanique ISB & Traitement du Signal
    card_b_y = 35
    card_b_h = 160
    card_b_w = 420

    # Carte Gauche : Référentiel ISB
    draw_card(c, 50, card_b_y, card_b_w, card_b_h, CARD_BG, ACCENT_BLUE, border_width=1.5, radius=8)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(68, card_b_y + card_b_h - 24, "RÉFÉRENTIEL BIOMÉCANIQUE ISB")

    isb_items = [
        ("Axe Z (Vertical)", "+1.0 g au repos"),
        ("Axe X (Antéro-postérieur)", ""),
        ("Axe Y (Médio-latéral)", "")
    ]
    cur_y = card_b_y + card_b_h - 48
    for lbl, desc in isb_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "• " + lbl)
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
        ("Fenêtrage Glissant (3.0s)", ""),
        ("Invariance par Rotation", ""),
        ("Calibration du Zéro-G (Biais)", ""),
        ("Filtrage Anti-Rebond Chute", "")
    ]
    cur_y = card_b_y + card_b_h - 48
    for lbl, desc in dsp_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "• " + lbl)
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
    # SLIDE 4 : Architecture Globale Logicielle & Système
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Architecture Globale")

    diag_y = 45
    diag_h = 395
    CLOUD_AWS = HexColor("#0284c7")

    # -------------------------------------------------------------
    # 1. EMBARQUÉ : ESP32-S3 (Dual-Core FreeRTOS)
    # -------------------------------------------------------------
    w_shoe = 215
    x_shoe = 38
    y_top = 440

    # Cœur 0 : Réseau & Système (3 items)
    h_core0 = 82
    y_core0 = y_top - 32 - h_core0  # 440 - 32 - 82 = 326

    # Cœur 1 : Temps Réel & Métier (5 items, calibré sans blanc résiduel)
    h_core1 = 114
    y_core1 = y_core0 - 10 - h_core1  # 326 - 10 - 114 = 202

    # Hauteur parent adaptée au contenu enfant (marge basse 12 pt)
    y_parent_shoe = y_core1 - 12      # 190
    h_parent_shoe = y_top - y_parent_shoe  # 250 pt

    draw_card(c, x_shoe, y_parent_shoe, w_shoe, h_parent_shoe, CARD_BG, PRIMARY_TEAL, border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 12, y_top - 20, "1. EMBARQUÉ (ESP32-S3)")

    # Carte Cœur 0
    draw_card(c, x_shoe + 8, y_core0, w_shoe - 16, h_core0, LIGHT_BG, PRIMARY_TEAL, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 14, y_core0 + h_core0 - 16, "Cœur 0 : Réseau & Système")
    core0_items = [
        "Pile NimBLE GATT",
        "OTA Streaming Service",
        "Power Manager"
    ]
    cur_cy = y_core0 + h_core0 - 34
    for t_it in core0_items:
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 14, cur_cy, "• " + t_it)
        cur_cy -= 16

    # Carte Cœur 1
    draw_card(c, x_shoe + 8, y_core1, w_shoe - 16, h_core1, LIGHT_BG, PRIMARY_TEAL, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 14, y_core1 + h_core1 - 16, "Cœur 1 : Temps Réel & Métier")

    core1_all_items = [
        "Bus I2C pour capteurs inertiels",
        "Inférence TinyML C pur",
        "Task Watchdog (TWDT 5s)",
        "Pilote Haptique PWM",
        "Buffer Circulaire HITL"
    ]
    cur_cy = y_core1 + h_core1 - 34
    for t_it in core1_all_items:
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 14, cur_cy, "• " + t_it)
        cur_cy -= 16

    # FLECHE 1 : ESP32-S3 -> Mobile
    draw_arrow(c, 256, 280, 36, PRIMARY_TEAL, "BLE GATT", "LESC Chiffré")

    # -------------------------------------------------------------
    # 2. PASSERELLE MOBILE : Flutter / SQLite
    # -------------------------------------------------------------
    w_mob = 176
    x_mob = 296

    # 2.1 Base Locale SQLite (1 item)
    h_sqlite = 50
    y_sqlite = y_top - 32 - h_sqlite  # 440 - 32 - 50 = 358

    # 2.2 Sécurité & Keystore (3 items)
    h_sec = 82
    y_sec = y_sqlite - 10 - h_sec      # 358 - 10 - 82 = 266

    # 2.3 Passerelle Hybride Cloud (2 items)
    h_gw = 66
    y_gw = y_sec - 10 - h_gw          # 266 - 10 - 66 = 190

    # Hauteur parent adaptée au contenu enfant (marge basse 12 pt)
    y_parent_mob = y_gw - 12          # 178
    h_parent_mob = y_top - y_parent_mob   # 262 pt

    draw_card(c, x_mob, y_parent_mob, w_mob, h_parent_mob, CARD_BG, ACCENT_BLUE, border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 12, y_top - 20, "2. MOBILE (Flutter / Dart)")

    # Carte Base SQLite
    draw_card(c, x_mob + 8, y_sqlite, w_mob - 16, h_sqlite, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 14, y_sqlite + h_sqlite - 16, "Base Locale SQLite")
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_mob + 14, y_sqlite + h_sqlite - 34, "• Sandbox OS privée")

    # Carte Sécurité & Keystore
    draw_card(c, x_mob + 8, y_sec, w_mob - 16, h_sec, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 14, y_sec + h_sec - 16, "Sécurité & Keystore")
    mob_sec_items = [
        "Hardware Keystore",
        "Tokens OAuth2 PKCE",
        "Courtier AWS STS"
    ]
    cur_my = y_sec + h_sec - 34
    for t_it in mob_sec_items:
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_mob + 14, cur_my, "• " + t_it)
        cur_my -= 16

    # Carte Passerelle Hybride Cloud
    draw_card(c, x_mob + 8, y_gw, w_mob - 16, h_gw, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 14, y_gw + h_gw - 16, "Passerelle Hybride Cloud")
    mob_gw_items = [
        "MQTT WSS SigV4",
        "API REST HTTPS"
    ]
    cur_my = y_gw + h_gw - 34
    for t_it in mob_gw_items:
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_mob + 14, cur_my, "• " + t_it)
        cur_my -= 16

    # FLECHE 2 : Mobile -> Cloud AWS
    draw_arrow(c, 475, 280, 42, ACCENT_BLUE, "MQTT WSS / REST", "SigV4 + HTTPS")

    # -------------------------------------------------------------
    # 3. CLOUD AWS : Ingestion, EC2 & Bases
    # -------------------------------------------------------------
    w_cloud = 266
    x_cloud = 522

    # 3.1 Haut : Ingestion IoT Core + AWS Lambda
    h_ingest = 72
    y_ingest = y_top - 32 - h_ingest  # 440 - 32 - 72 = 336

    # 3.2 Milieu : Serveur EC2 Docker
    h_ec2 = 96
    y_ec2 = y_ingest - 10 - h_ec2     # 336 - 10 - 96 = 230

    # 3.3 Bas : Bases de données
    h_db = 68
    y_db = y_ec2 - 10 - h_db          # 230 - 10 - 68 = 152

    # Hauteur parent adaptée au contenu enfant (marge basse 12 pt)
    y_parent_cloud = y_db - 12        # 140
    h_parent_cloud = y_top - y_parent_cloud  # 300 pt

    draw_card(c, x_cloud, y_parent_cloud, w_cloud, h_parent_cloud, CARD_BG, CLOUD_AWS, border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 12, y_top - 20, "3. CLOUD AWS")

    # Conteneur Ingestion
    draw_card(c, x_cloud + 8, y_ingest, w_cloud - 16, h_ingest, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)

    # Mini-carte gauche : AWS IoT Core (Broker MQTT WSS)
    h_sub_ingest = 62
    draw_card(c, x_cloud + 13, y_ingest + 5, 118, h_sub_ingest, CARD_BG, CLOUD_AWS, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 18, y_ingest + 5 + h_sub_ingest - 14, "AWS IoT Core")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 18, y_ingest + 5 + h_sub_ingest - 28, "• Broker MQTT WSS")
    c.drawString(x_cloud + 18, y_ingest + 5 + h_sub_ingest - 42, "• Règles IoT SQL")

    # Mini-carte droite : AWS Lambda (Ingestion & Présence)
    draw_card(c, x_cloud + 135, y_ingest + 5, 118, h_sub_ingest, CARD_BG, ACCENT_AMBER, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 140, y_ingest + 5 + h_sub_ingest - 14, "AWS Lambda")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 140, y_ingest + 5 + h_sub_ingest - 28, "• Ingestion télémétrie")
    c.drawString(x_cloud + 140, y_ingest + 5 + h_sub_ingest - 42, "• Présence & Statut")

    # Conteneur EC2 Docker
    draw_card(c, x_cloud + 8, y_ec2, w_cloud - 16, h_ec2, CARD_BG, CLOUD_AWS, border_width=1.2, radius=6)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 14, y_ec2 + h_ec2 - 13, "Serveur EC2")
    c.setFont("Helvetica-Bold", 6.6)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 14, y_ec2 + h_ec2 - 25, "Nginx Reverse Proxy SSL")

    # Backend
    h_sub_ec2 = 58
    draw_card(c, x_cloud + 13, y_ec2 + 5, 118, h_sub_ec2, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 18, y_ec2 + 5 + h_sub_ec2 - 14, "Backend FastAPI")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 18, y_ec2 + 5 + h_sub_ec2 - 28, "• API REST OpenAPI")
    c.drawString(x_cloud + 18, y_ec2 + 5 + h_sub_ec2 - 42, "• Courtier STS (15 min)")

    # Frontend
    draw_card(c, x_cloud + 135, y_ec2 + 5, 118, h_sub_ec2, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 140, y_ec2 + 5 + h_sub_ec2 - 14, "Frontend Angular 22")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 140, y_ec2 + 5 + h_sub_ec2 - 28, "• Interface Signals")

    # Conteneur Bases de données
    draw_card(c, x_cloud + 8, y_db, w_cloud - 16, h_db, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)

    # Aurora PG
    h_sub_db = 58
    draw_card(c, x_cloud + 13, y_db + 5, 118, h_sub_db, CARD_BG, PRIMARY_TEAL, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 18, y_db + 5 + h_sub_db - 14, "• PostgreSQL 16")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 18, y_db + 5 + h_sub_db - 30, "• Migrations Alembic")

    # DynamoDB
    draw_card(c, x_cloud + 135, y_db + 5, 118, h_sub_db, CARD_BG, ACCENT_AMBER, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 140, y_db + 5 + h_sub_db - 14, "• Amazon DynamoDB")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 140, y_db + 5 + h_sub_db - 30, "• Séries NoSQL")

    # FLECHE 3 : Cloud AWS -> Cloud OVH
    draw_arrow(c, 792, 260, 28, ACCENT_AMBER, "SMTP", "TLS 587")

    # -------------------------------------------------------------
    # 4. CLOUD OVH : Serveur Mail Dédié (Hauteur ajustée à son contenu)
    # -------------------------------------------------------------
    w_ovh = 105
    x_ovh = 824
    h_ovh = 72
    y_ovh = 224
    draw_card(c, x_ovh, y_ovh, w_ovh, h_ovh, CARD_BG, ACCENT_AMBER, border_width=2, radius=10)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_ovh + 10, y_ovh + h_ovh - 18, "4. CLOUD OVH")

    # Card Serveur Mail
    h_mail = 42
    draw_card(c, x_ovh + 8, y_ovh + 6, w_ovh - 16, h_mail, LIGHT_BG, BORDER_LIGHT, border_width=1, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_AMBER)
    c.drawCentredString(x_ovh + w_ovh / 2, y_ovh + 6 + 17, "Serveur Mail")

    c.showPage()

    # ==========================================
    # SLIDE 5 : Edge Machine Learning & Détail des Features
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "INTELLIGENCE ARTIFICIELLE EMBARQUÉE")

    col_y = 45
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "POURQUOI UN RANDOM FOREST PLUTÔT QU'UN AUTRE ?")

    model_points = [
        ("vs Deep Learning (TFLite Micro)", "100x plus rapide (~12 us vs 15-50 ms)."),
        ("vs Modèles Linéaires & SVM", "Capture nativement les frontières non-linéaires complexes."),
        ("vs Arbre de Décision Unique (CART)", "L'agrégation de 80 arbres (bagging) réduit drastiquement la variance et immunise contre le bruit."),
        ("vs Gradient Boosting (XGBoost)", "Vote probabiliste direct sans interpréteur lourd. class_weight='balanced' préserve un rappel chute >95% sur les classes rares."),
        ("Sélection parmi les modèles m2cgen", "Retenu parmi les algorithmes compatibles pour sa conversion en C pur (arbres if/else), sans runtime ni dépendance.")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in model_points:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "• " + lbl)
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
        ("1. Intensité Globale (Invariante 3D)", "Normes ||a|| et ||w|| : min, max, moyenne, énergie cinétique."),
        ("2. Rupture & Amplitude Dynamique", "Peak-to-Peak (max - min) et Jerk maximal (choc violent vs allure stable)."),
        ("3. Dispersion & Posture (6 Axes)", "Écarts-types axiaux (ax, ay, az, gx, gy, gz) et moyennes (assis vs couché)."),
        ("4. Directionnalité & Asymétrie", "Delta ay (fin - début) et asymétrie 1ère/2nde moitié (assis <-> debout)."),
        ("5. Stabilité Post-Impact", "Écart-type de queue de fenêtre (détection de l'immobilité au sol).")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in feat_points:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "• " + lbl)
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
    draw_header(c, "VALIDATION & CONTRÔLE")

    # Badge Démonstration en Direct
    draw_card(c, 520, 470, 390, 26, ACCENT_AMBER, ACCENT_AMBER, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(TEXT_LIGHT)
    c.drawCentredString(715, 478, "DÉMONSTRATION 1 : RECONNAISSANCE D'ALLURE EN DIRECT")

    # Gauche : Graphique des performances ML réel (capture web Studio cliquable)
    ml_img_path = "health-kicks-frontend/public/images/screenshots/web_showcase_ml_stats.avif"
    card_l_w = 460
    card_h = 390
    draw_card(c, 50, col_y, card_l_w, card_h, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + card_h - 26, "BENCHMARK RÉEL STUDIO (F1-SCORE & DISTRIBUTION)")

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
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 80, "TEMPS D'INFÉRENCE EMBARQUÉ")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 55, "Mesure réelle micros() sur Cœur 1 (Xtensa 240 MHz)")

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
    c.drawCentredString(card_r_x + card_r_w / 2, card_2_y + 55, "Classification multiclasse temps réel sur 16 états moteurs")

    c.showPage()

    # ==========================================
    # SLIDE 7 : MLOps Pipeline & Mode HITL
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "ENTRAÎNEMENT")

    # Badge Démonstration en Direct
    draw_card(c, 520, 470, 390, 26, PRIMARY_TEAL, PRIMARY_TEAL, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(TEXT_LIGHT)
    c.drawCentredString(715, 478, "DÉMONSTRATION 2 : STUDIO WEB & REQUALIFICATION HITL")

    draw_card(c, 50, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(68, col_y + 390 - 28, "MLOps Pipeline")

    steps_mlops = [
        ("1. Capture", ""),
        ("2. Qualification Studio Mobile & Web", ""),
        ("3. Pipeline Python d'Entraînement", ""),
        ("4. Transpilation m2cgen Pure C", ""),
        ("5. Injection Firmware Sans Recompilation", "")
    ]

    cur_y = col_y + 390 - 58
    for lbl, desc in steps_mlops:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "• " + lbl)
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
        ("Buffer Circulaire Haute Fréquence", ""),
        ("Capture Pré & Post Événement", ""),
        ("Transfert Fast Burst BLE", ""),
        ("Requalification Web Studio", "")
    ]

    cur_y = col_y + 390 - 58
    for lbl, desc in hitl_items:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "• " + lbl)
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
    # SLIDE 8 : Détection de Chute & Chaîne d'Urgence
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "DÉTECTION DE CHUTE")

    # Badge Démonstration en Direct
    draw_card(c, 520, 470, 390, 26, ACCENT_AMBER, ACCENT_AMBER, border_width=1, radius=4)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(TEXT_LIGHT)
    c.drawCentredString(715, 478, "DÉMONSTRATION 3 : SIMULATION D'UNE CHUTE EN DIRECT")

    # Gauche : Points Clés (Annulation Automatique & Cooldown)
    card_l_x = 45
    card_l_w = 345
    draw_card(c, card_l_x, col_y, card_l_w, 390, CARD_BG, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(card_l_x + 18, col_y + 390 - 28, "SÉCURITÉ & GESTION DES FAUX-POSITIFS")

    fall_key_points = [
        ("Annulation Automatique par Relèvement", ""),
        ("Période de Cooldown Anti-Rebond (5.0s)", ""),
        ("Délai de Rétractation Utilisateur (60s)", ""),
        ("Orchestration Centralisée Backend", ""),
        ("Repli d'Urgence Appel 112", "")
    ]

    cur_y = col_y + 390 - 75
    for lbl, desc in fall_key_points:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(card_l_x + 18, cur_y, "• " + lbl)
        cur_y -= 48

    # Droite : Schéma Graphique Vectoriel de la Chaîne d'Escalade et de Secours
    x_chain = 405
    w_chain = 510
    h_chain = 390
    draw_card(c, x_chain, col_y, w_chain, h_chain, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(TEXT_TEAL)
    c.drawString(x_chain + 18, col_y + h_chain - 26, "CHAÎNE D'ESCALADE & SECOURS")

    bx_x = x_chain + 16
    bx_w = w_chain - 32
    x_center = x_chain + w_chain / 2

    # 0. Événement Déclencheur Choc & Immobilité
    b0_w = 340
    b0_h = 24
    b0_x = x_chain + (w_chain - b0_w) / 2
    b0_y = 356
    draw_card(c, b0_x, b0_y, b0_w, b0_h, HexColor("#450a0a"), HexColor("#ef4444"), border_width=1.2, radius=5)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#fca5a5"))
    c.drawCentredString(b0_x + b0_w / 2, b0_y + 7.5, "CHUTE DÉTECTÉ")

    # Flèche 0 -> 1
    draw_down_arrow(c, x_center, 356, 338, HexColor("#ef4444"))

    # 1. Alerte Locale Immédiate (Capteur ESP32-S3)
    b1_y = 286
    b1_h = 52
    draw_card(c, bx_x, b1_y, bx_w, b1_h, HexColor("#0f172a"), HexColor("#14b8a6"), border_width=1.2, radius=6)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#14b8a6"))
    c.drawString(bx_x + 12, b1_y + b1_h - 14, "1. ALERTE LOCALE IMMÉDIATE (CAPTEUR ESP32-S3)")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(HexColor("#cbd5e1"))
    c.drawString(bx_x + 16, b1_y + 24, "• Vibreur actif & Cooldown 5s anti-rebond")
    c.drawString(bx_x + 16, b1_y + 10, "• Émission trame BLE GATT prioritaire")

    # Flèche 1 -> 2
    draw_down_arrow(c, x_center, 286, 268, HexColor("#38bdf8"), "BLE GATT")

    # 2. Passerelle Mobile (Flutter)
    b2_y = 202
    b2_h = 66
    draw_card(c, bx_x, b2_y, bx_w, b2_h, HexColor("#0f172a"), HexColor("#38bdf8"), border_width=1.2, radius=6)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#38bdf8"))
    c.drawString(bx_x + 12, b2_y + b2_h - 14, "2. PASSERELLE MOBILE (FLUTTER / DART)")
    c.setFont("Helvetica-Bold", 7.8)
    c.setFillColor(HexColor("#34d399"))
    c.drawString(bx_x + 16, b2_y + 37, "• Si Relèvement ou clic 'Je vais bien' :")
    c.drawString(bx_x + 26, b2_y + 25, "==> ANNULATION IMMÉDIATE (Aucun message émis au Cloud)")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(HexColor("#cbd5e1"))
    c.drawString(bx_x + 16, b2_y + 10, "• Alerte sonore stridente & écran rouge (délai 60s) + Coordonnées GPS")

    # Flèche 2 -> 3
    draw_down_arrow(c, x_center, 202, 184, HexColor("#c084fc"), "60s écoulées sans annulation")

    # 3. Backend FastAPI (Orchestrateur de Secours)
    b3_y = 118
    b3_h = 66
    draw_card(c, bx_x, b3_y, bx_w, b3_h, HexColor("#0f172a"), HexColor("#c084fc"), border_width=1.2, radius=6)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#c084fc"))
    c.drawString(bx_x + 12, b3_y + b3_h - 14, "3. BACKEND FASTAPI (ORCHESTRATEUR DE SECOURS)")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(HexColor("#cbd5e1"))
    c.drawString(bx_x + 16, b3_y + 36, "• Récupération ordonnée des contacts d'urgence (Priorités 1 à 5)")
    c.drawString(bx_x + 16, b3_y + 22, "• Envoi direct de l'email d'urgence avec lien d'acquittement (ACK)")
    c.drawString(bx_x + 16, b3_y + 9, "• Ordre MQTT Downlink 'SEND_SMS' envoyé au mobile")

    # Flèche 3 -> 4
    draw_down_arrow(c, x_center, 118, 100, HexColor("#f59e0b"), "MQTT Downlink")

    # 4. Relais GSM Mobile (SmsManager Android)
    b4_y = 52
    b4_h = 48
    draw_card(c, bx_x, b4_y, bx_w, b4_h, HexColor("#0f172a"), HexColor("#f59e0b"), border_width=1.2, radius=6)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#f59e0b"))
    c.drawString(bx_x + 12, b4_y + b4_h - 14, "4. RELAIS GSM MOBILE (SmsManager Android)")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(HexColor("#cbd5e1"))
    c.drawString(bx_x + 16, b4_y + 21, "• Émission du SMS natif vers le numéro du proche prioritaire")
    c.drawString(bx_x + 16, b4_y + 8, "• Escalade automatique vers proche suivant si pas d'ACK (3 min)")

    c.showPage()

    # ==========================================
    # SLIDE 9 : Conclusion & Perspectives
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "SYNTHÈSE & PERSPECTIVES D'AVENIR", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "CE QUE NOUS AVONS DÉMONTRÉ")

    achievements = [
        ("TinyML Performant", ""),
        ("Alerte rapide", ""),
        ("Chaîne IoT Sécurisée", ""),
    ]
    cur_y = 370
    for lbl, desc in achievements:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(68, cur_y, "• " + lbl)
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
    c.drawString(508, 405, "PERSPECTIVES")

    roadmap = [
        ("MLOps Continu & Adaptation On-Device", ""),
        ("Redondance", ""),
        ("Escalade Avancée des Alertes", ""),
        ("Dispositif Jumeau (Twin Devices)", ""),
        ("Séances d'exercices ou chorégraphie", ""),
        ("Éléments de Confort", ""),
        ("Connectivité Cellulaire NB-IoT", "")
    ]
    cur_y = 375
    for lbl, desc in roadmap:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(508, cur_y, "• " + lbl)
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
    draw_header(c, "ÉCHANGE & DISCUSSION", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "RESSOURCES DU PROJET & DÉMO EN LIGNE")

    demo_links = [
        ("Site Portfolio & CV", "https://daverck.github.io/serck-david-portfolio", "daverck.github.io/serck-david-portfolio"),
        ("Plateforme Web Live", "https://healthkicks.duckdns.org", "healthkicks.duckdns.org"),
        ("Studio & Stats du Modèle ML", "https://healthkicks.duckdns.org/dashboard/studio/classes", "healthkicks.duckdns.org/dashboard/studio/classes"),
        ("Code Source & Spécifications", "https://github.com/daverck/health-kicks-ecosystem", "github.com/daverck/health-kicks-ecosystem")
    ]

    cur_y = 365
    for lbl, target_url, display_txt in demo_links:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(68, cur_y, "• " + lbl + " :")
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(ACCENT_BLUE)
        c.drawString(82, cur_y, display_txt)
        c.linkURL(target_url, (82, cur_y - 2, 82 + 300, cur_y + 11), thickness=0)
        cur_y -= 14

    draw_card(c, 490, 45, 420, 390, CARD_DARK, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(HexColor("#fbbf24"))
    c.drawString(508, 405, "THÈMES TECHNIQUES À APPROFONDIR")

    discussion_items = [
        ("Optimisation FreeRTOS Dual-Core", ""),
        ("Podométrie Nette & Gestion des Reboots", ""),
        ("Boucle MLOps & Mode HITL", ""),
        ("Sécurité Zero Trust & Données de Marche", "")
    ]
    cur_y = 375
    for lbl, desc in discussion_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(508, cur_y, "• " + lbl)
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
    draw_header(c, "PODOMÉTRIE (SUPPORT / QUESTIONS)")

    # Gauche : Algorithme SQLite & Architecture
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "ALGORITHME DE PODOMÉTRIE NETTE (SQLite)")

    podo_items = [
        ("Compteur Monotone Physique", ""),
        ("Calcul Différentiel Mobile", ""),
        ("Résilience aux Redémarrages", ""),
        # ("Bascule Nette a Minuit", ""),
        # ("Ventilation Horaire Reelle", "Chaque pas est assigne a son heure exacte d'accumulation (aucune extrapolation theorique)."),
        ("Insensibilité aux Gestes Parasites", "")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in podo_items:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "• " + lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(78, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    # Droite : Graphique Podometre Reel (capture pedometer.png)
    podo_img_path = "health-kicks-frontend/public/images/screenshots/web_showcase_pedometer.avif"
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
    draw_header(c, "COÛTS DU PROJET")

    # Gauche : Hardware / Matériel Embarqué
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "MATÉRIEL EMBARQUÉ & PROTOTYPE")

    hw_costs = [
        ("Microcontrôleur ESP32-S3 WROOM-1", "~15.00 EUR", "Dual-Core 240 MHz, 8 Mo Flash, 512 Ko SRAM, BLE 5.0, WiFi"),
        ("Module IMU 6 axes (MPU-6050)", "~3.00 EUR", "Accéléromètre 3D + Gyroscope 3D I2C"),
        ("Vibreur Haptique", "~3.00 EUR", "Contrôle par signal PWM"),
        ("Batterie LiPo 1S Rechargeable (500 mAh)", "~4.50 EUR", ""),
        ("Convertisseur DC/DC & Régulateur LDO", "~2.00 EUR", ""),
        ("Support Perfboard & composants électroniques divers", "~5.00 EUR", "Circuit d'intégration, connectique, résistances, interrupteur")
    ]

    cur_y = col_y + 390 - 75
    for item, price, desc in hw_costs:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(68, cur_y, "• " + item)
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
    c.drawString(68, col_y + 20, "TOTAL")
    c.setFillColor(PRIMARY_TEAL)
    c.drawRightString(450, col_y + 20, "32.50 EUR")

    # Droite : Cloud, Nom de Domaine & Outils
    draw_card(c, 490, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + 390 - 28, "INFRASTRUCTURE CLOUD & SERVICES")

    services_costs = [
        ("Cloud AWS (Free Tier & Crédits Gratuits)", "0 EUR / mois", "EC2 t3.micro (750h/m), IoT Core (500k msg), DynamoDB (25 Go), Lambdas STS (1M req/m) entièrement couverts par l'offre gratuite."),
        ("Pipeline CI/CD GitHub Actions", "0 EUR (Free Usage)", ""),
        ("Nom de Domaine Personnalisé Dédié", "~12 EUR / an", "pour l'envoi d'emails"),
        ("Assistance IA & Pair-Programming (Gemini)", "~5.5 EUR / mois", ""),
    ]

    cur_y = col_y + 390 - 75
    for item, price, desc in services_costs:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(508, cur_y, "• " + item)
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
    c.drawString(508, col_y + 20, "TOTAL")
    c.setFillColor(ACCENT_BLUE)
    c.drawRightString(890, col_y + 20, "~6.50 EUR / mois (12 EUR / an + 5.50/m)")

    c.save()
    print(f"Simplified PDF saved to: {target_filename}")


if __name__ == "__main__":
    build_pdf()
