"""Generates a simplified, high-impact 16:9 landscape PDF presentation for HealthKicks Ecosystem
using ReportLab (pure Python, vector graphics, standalone, clickable links).
"""

import os
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


def draw_header(c, category, title, dark=False):
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(TEXT_TEAL if dark else PRIMARY_TEAL)
    c.drawString(50, 495, category.upper())

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(TEXT_LIGHT if dark else TEXT_DARK)
    c.drawString(50, 465, title)


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

    c.setFillColor(PRIMARY_TEAL)
    c.roundRect(50, 480, 100, 6, 3, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 34)
    c.setFillColor(TEXT_LIGHT)
    c.drawString(50, 435, "HealthKicks Ecosystem")

    c.setFont("Helvetica", 16)
    c.setFillColor(TEXT_TEAL)
    c.drawString(50, 405, "Chaussure Intelligente : Podometrie Haute Precision & Detection de Chute Autonome")

    card_w = 265
    card_h = 320
    card_y = 50

    cards_s1 = [
        ("ACTIVITE & SPORT", PRIMARY_TEAL, [
            "Podometre.",
            "Rappel d'inactivite haptique.",
            "Centre sur le mouvement des pieds."
        ]),
        ("SECURITE & PROCHES", ACCENT_AMBER, [
            "Detection de chute.",
            "Alerte par SMS et email."
        ]),
        ("EDGE AI & SOBRIETE", ACCENT_BLUE, [
            "Composants standard grand public (cout relativement faible).",
            "Edge AI."
        ])
    ]

    for idx, (title, color, items) in enumerate(cards_s1):
        x = 50 + idx * 295
        draw_card(c, x, card_y, card_w, card_h, CARD_DARK, color)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(color)
        c.drawString(x + 18, 335, title)

        cur_y = 295
        for b in items:
            lines = wrap_text(b, 30)
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(TEXT_LIGHT)
            c.drawString(x + 18, cur_y, "-")
            c.setFont("Helvetica", 10.5)
            for line in lines:
                c.drawString(x + 30, cur_y, line)
                cur_y -= 16
            cur_y -= 12

    c.showPage()

    # ==========================================
    # SLIDE 2 : Parcours Professionnel & Portfolio QR Code
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Qui suis-je ?", "Parcours Professionnel & Presentation")

    qr_path = "docs/presentation/qr-code.png"
    portfolio_url = "https://daverck.github.io/serck-david-portfolio"

    col_bio_data = [
        ("FORMATION & EXPERTISE", PRIMARY_TEAL, [
            ("Bachelier en Informatique de Gestion", "Formation superieure alliant conception logicielle, gestion de donnees et vision produit."),
            ("Polyvalence Systemes & Logiciels", "Capacite a concevoir une chaine applicative complete : de l'embarque C/C++ jusqu'au Web moderne."),
            ("Frugalite & Securite Zero Trust", "Conception orientee performance, zero fuite memoire et securite de bout en bout.")
        ]),
        ("PARCOURS (3 ENTREPRISES)", ACCENT_BLUE, [
            ("Fiduciaire (Gestion & Finance)", "Rigueur de modelisation, manipulation de donnees critiques et automatisation de processus."),
            ("Operateur Telecom (Reseaux)", "Protocoles de communication, contraintes de connectivite et resilience face aux pannes."),
            ("Entreprise de Services Numeriques (ESN)", "Developpement agile, industrialisation multi-projets, integration continue et delivery rapide.")
        ])
    ]

    # Draw 2 text columns
    for idx, (title, color, items) in enumerate(col_bio_data):
        x = 50 + idx * 290
        draw_card(c, x, 45, 275, 390, CARD_BG, color)
        c.setFont("Helvetica-Bold", 12.5)
        c.setFillColor(color)
        c.drawString(x + 18, 405, title)

        cur_y = 370
        for heading, desc in items:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(TEXT_DARK)
            c.drawString(x + 18, cur_y, "> " + heading)
            cur_y -= 14
            c.setFont("Helvetica", 8.5)
            c.setFillColor(TEXT_MUTED)
            lines = wrap_text(desc, 36)
            for line in lines:
                c.drawString(x + 28, cur_y, line)
                cur_y -= 12
            cur_y -= 8

    # 3rd Column: Competences + QR code & Portfolio Link
    x_qr = 50 + 2 * 290
    draw_card(c, x_qr, 45, 280, 390, CARD_BG, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_qr + 18, 405, "PORTFOLIO & COMPETENCES")

    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_qr + 18, 375, "> Embarque, Mobile, Cloud & Web")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(TEXT_MUTED)
    comp_lines = wrap_text("ESP32-S3, C/C++, TinyML, Flutter/Dart, FastAPI, AWS IoT, PostgreSQL, Angular 22.", 36)
    cur_y = 360
    for line in comp_lines:
        c.drawString(x_qr + 28, cur_y, line)
        cur_y -= 11

    # Draw QR code image
    if os.path.exists(qr_path):
        qr_size = 170
        qr_x = x_qr + (280 - qr_size) / 2
        qr_y = 125
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)
        # Clickable link over the QR code
        c.linkURL(portfolio_url, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), thickness=0)

    # Clickable text link
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(x_qr + 140, 95, "Site Portfolio & CV en ligne :")
    c.setFont("Helvetica", 8)
    c.setFillColor(ACCENT_BLUE)
    link_rect = (x_qr + 15, 65, x_qr + 265, 88)
    c.drawCentredString(x_qr + 140, 75, "daverck.github.io/serck-david-portfolio")
    c.linkURL(portfolio_url, link_rect, thickness=0)

    c.showPage()

    # ==========================================
    # SLIDE 3 : Architecture Système & Schéma
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Vue d'Ensemble", "Architecture Globale : Du Capteur au Cloud")

    # Schéma d'Architecture visuel interactif
    # Ligne 1: 4 Boîtes interconnectées (Flux de données)
    diag_y = 350
    diag_h = 75
    box_w = 175
    gap_x = 45

    diag_boxes = [
        ("CHAUSSURE (Edge)", "ESP32-S3 & MPU-6050", "Inference ML ~12 us\nHaptique PWM 10 kHz", PRIMARY_TEAL),
        ("MOBILE (Gateway)", "Flutter & SQLite", "Odometrie locale\nAuth OAuth2 PKCE", ACCENT_BLUE),
        ("CLOUD (Backend)", "FastAPI & AWS IoT", "Broker STS temporaire\nDynamoDB & Aurora", PRIMARY_TEAL),
        ("DASHBOARD (Web)", "Angular 22 Signals", "Suivi temps reel\nStudio Requalification", ACCENT_AMBER)
    ]

    for i, (title, sub, detail, color) in enumerate(diag_boxes):
        bx = 50 + i * (box_w + gap_x)
        draw_card(c, bx, diag_y, box_w, diag_h, CARD_BG, color, border_width=2)
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(color)
        c.drawCentredString(bx + box_w / 2, diag_y + diag_h - 18, title)
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(bx + box_w / 2, diag_y + diag_h - 32, sub)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(TEXT_MUTED)
        det_lines = detail.split("\n")
        c.drawCentredString(bx + box_w / 2, diag_y + diag_h - 48, det_lines[0])
        c.drawCentredString(bx + box_w / 2, diag_y + diag_h - 60, det_lines[1])

        # Arrow to next box
        if i < len(diag_boxes) - 1:
            ax = bx + box_w + 5
            ay = diag_y + diag_h / 2
            c.setStrokeColor(TEXT_MUTED)
            c.setLineWidth(1.5)
            c.line(ax, ay, ax + gap_x - 10, ay)
            # Arrow head
            p = c.beginPath()
            p.moveTo(ax + gap_x - 10, ay)
            p.lineTo(ax + gap_x - 16, ay + 4)
            p.lineTo(ax + gap_x - 16, ay - 4)
            p.close()
            c.setFillColor(TEXT_MUTED)
            c.drawPath(p, fill=1, stroke=0)

            # Protocol label above arrow
            proto_labels = ["BLE LESC", "MQTT SigV4", "REST / WS"]
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(PRIMARY_TEAL if i == 0 else ACCENT_BLUE)
            c.drawCentredString(ax + (gap_x - 10) / 2, ay + 7, proto_labels[i])

    # 4 Cartes détaillées en dessous
    col_w = 200
    col_h = 280
    col_y = 45

    layers = [
        ("1. CHAUSSURE", "ESP32-S3 & Capteurs", PRIMARY_TEAL, [
            "Centrale IMU 6-axes MPU-6050 (19 Hz).",
            "Inference Edge AI C++ (~12 us).",
            "Vibreur haptique PWM (10 kHz).",
            "Serveur BLE GATT securise (LESC)."
        ]),
        ("2. MOBILE", "Passerelle Flutter / SQLite", ACCENT_BLUE, [
            "Liaison BLE chiffree & appairage 60s.",
            "Odometrie differentielle SQLite.",
            "Auth OAuth2 avec PKCE RFC 7636.",
            "Passerelle MQTT WebSockets SigV4."
        ]),
        ("3. CLOUD", "FastAPI & AWS IoT", PRIMARY_TEAL, [
            "Broker AWS IoT Core (QoS 1).",
            "STS Token Broker : cles 15 min.",
            "Amazon DynamoDB & PostgreSQL 16.",
            "Pipeline d'entrainement MLOps."
        ]),
        ("4. DASHBOARD", "Web Angular 22", ACCENT_AMBER, [
            "Interface reactive Angular Signals.",
            "Visualisation des pas et alertes.",
            "Mode Studio : capture de datasets.",
            "Requalification des modeles."
        ])
    ]

    for idx, (title, sub, accent, items) in enumerate(layers):
        x = 50 + idx * 220
        draw_card(c, x, col_y, col_w, col_h, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 11.5)
        c.setFillColor(accent)
        c.drawString(x + 14, col_y + col_h - 24, title)

        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        c.drawString(x + 14, col_y + col_h - 38, sub)

        cur_y = col_y + col_h - 60
        for it in items:
            lines = wrap_text(it, 25)
            c.setFont("Helvetica-Bold", 8.5)
            c.setFillColor(TEXT_DARK)
            c.drawString(x + 14, cur_y, "-")
            c.setFont("Helvetica", 8.5)
            for line in lines:
                c.drawString(x + 24, cur_y, line)
                cur_y -= 13
            cur_y -= 6

    c.showPage()

    # ==========================================
    # SLIDE 4 : Cœur IoT & Firmware
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Systeme Embarque", "Coeur IoT : Chaussure Instrumentee & ESP32-S3")

    s3_cards = [
        ("ARCHITECTURE MATERIELLE", PRIMARY_TEAL, [
            ("ESP32-S3 (Xtensa 240 MHz)", "Dual-core, 16 MB Flash, 8 MB PSRAM."),
            ("IMU 6-axes MPU-6050", "I2C Fast-Mode (400 kHz) : acc et gyro 3D."),
            ("Actuateur Haptique", "Vibreur PWM 10 kHz (etage MOSFET & diode roue libre)."),
            ("Interfaces", "Bouton appairage GPIO 14 & LED d'etat.")
        ]),
        ("REFERENTIEL BIOMECANIQUE ISB", ACCENT_BLUE, [
            ("Norme ISB (Wu & Cavanagh)", "Repere aligne sur le pied humain."),
            ("Axe Z (Vertical)", "+1.0 g statique au repos sur sol plat."),
            ("Axe X (Antero-posterieur)", "Mesure la propulsion et deceleration."),
            ("Axe Y (Medio-lateral)", "Mesure la stabilite et la pronation.")
        ]),
        ("SECURITE & MAINTENANCE OTA", ACCENT_AMBER, [
            ("Chiffrement BLE LESC", "Appairage securise avec fenetre de 60s."),
            ("Dual-Partition Flash A/B", "Mise a jour sans fil avec validation SHA-256."),
            ("Rollback Automatique", "Probation 15s : retour firmware sain si panne.")
        ])
    ]

    for idx, (title, accent, items) in enumerate(s3_cards):
        x = 50 + idx * 295
        draw_card(c, x, col_y, 275, 390, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(accent)
        c.drawString(x + 15, col_y + 390 - 28, title)

        cur_y = col_y + 390 - 60
        for lbl, desc in items:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(TEXT_DARK)
            c.drawString(x + 15, cur_y, "> " + lbl)
            cur_y -= 14
            c.setFont("Helvetica", 9)
            c.setFillColor(TEXT_MUTED)
            lines = wrap_text(desc, 34)
            for line in lines:
                c.drawString(x + 23, cur_y, line)
                cur_y -= 13
            cur_y -= 10

    c.showPage()

    # ==========================================
    # SLIDE 5 : Edge Machine Learning & Détail des Features
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Intelligence Artificielle Embarquee", "Edge Machine Learning : Classification & Securite")

    s4_cards = [
        ("POURQUOI L'EDGE AI ?", PRIMARY_TEAL, [
            ("Zero Latence Critique", "Reaction immediate lors du choc (< 1 ms) sans delai reseau."),
            ("Autonomie Hors-Reseau", "Fonctionne en zone blanche, sans cloud ni smartphone."),
            ("Confidentialite Totale", "Les signaux cinematiques bruts restent strictement en local.")
        ]),
        ("INDICATEURS BIOMECANIQUES (19 Hz)", ACCENT_BLUE, [
            ("Invariance par Magnitude", "Normes ||a|| et ||w|| : insensibles a l'orientation de la semelle."),
            ("Dispersion & Posture", "Ecarts-types et moyennes axiales (distinction assis vs couche)."),
            ("Directionnalite Temporelle", "Delta ay (fin - debut) et asymetrie d'energie (assis <-> debout)."),
            ("Dynamique & Jerk", "Jerk max d'acceleration (choc de chute vs mouvement amorti).")
        ]),
        ("CLASSIFIEUR & PONDERATION", ACCENT_AMBER, [
            ("Random Forest (40 arbres)", "Ensemble decisionnel rapide converti en code C pur (~12 us)."),
            ("Ponderation Dynamique", "class_weight='balanced' penalise fortement les erreurs sur les chutes rares."),
            ("Cooldown Anti-Rebond", "Debouncing temporel de 5000 ms sans verrou rigide d'impact physique.")
        ])
    ]

    for idx, (title, accent, items) in enumerate(s4_cards):
        x = 50 + idx * 295
        draw_card(c, x, col_y, 275, 390, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 11.5)
        c.setFillColor(accent)
        c.drawString(x + 15, col_y + 390 - 28, title)

        cur_y = col_y + 390 - 58
        for lbl, desc in items:
            c.setFont("Helvetica-Bold", 9.5)
            c.setFillColor(TEXT_DARK)
            c.drawString(x + 15, cur_y, "> " + lbl)
            cur_y -= 13
            c.setFont("Helvetica", 8.5)
            c.setFillColor(TEXT_MUTED)
            lines = wrap_text(desc, 36)
            for line in lines:
                c.drawString(x + 23, cur_y, line)
                cur_y -= 12
            cur_y -= 8

    c.showPage()

    # ==========================================
    # SLIDE 6 : MLOps Pipeline
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Cycle d'Entrainement", "Boucle MLOps : Du Terrain au Code C Embarque")

    steps = [
        ("1. MODE STUDIO HAUTE FREQUENCE", PRIMARY_TEAL,
         "Acquisition brute (54 / 100 Hz) declenchee depuis l'app. Streaming en burst BLE avec controle CRC32 vers DynamoDB pour constituer les jeux de donnees."),
        ("2. STRATIFIED 5-FOLD CROSS VALIDATION", ACCENT_BLUE,
         "Cache local incremental pour reduire les requetes DynamoDB. 5 plis stratifies garantissant la meme proportion de chutes rares. Optimisation sur le Macro F1."),
        ("3. TRANSPILATION C PURE SANS RUNTIME (m2cgen)", PRIMARY_TEAL,
         "Conversion automatique du modele scikit-learn en C standard (activity_model_generated.h). Aucun framework lourd (zero TFLite). Execution en ~12 us."),
        ("4. QUALITY GATE & CONTROLE DU FIRMWARE", ACCENT_AMBER,
         "Quality Gate bloquant : Macro F1-score >= 85% obligatoire. Compilation automatique PlatformIO (pio run) validant les quotas Flash/RAM avant tout commit.")
    ]

    step_h = 88
    for idx, (title, accent, desc) in enumerate(steps):
        y = 350 - idx * 100
        draw_card(c, 50, y, 860, step_h, CARD_BG, accent)

        c.setFillColor(accent)
        c.rect(50, y, 6, step_h, stroke=0, fill=1)

        c.setFont("Helvetica-Bold", 11.5)
        c.setFillColor(accent)
        c.drawString(70, y + step_h - 22, title)

        c.setFont("Helvetica", 9.5)
        c.setFillColor(TEXT_DARK)
        lines = wrap_text(desc, 110)
        cur_y = y + step_h - 40
        for line in lines:
            c.drawString(70, cur_y, line)
            cur_y -= 14

    c.showPage()

    # ==========================================
    # SLIDE 7 : Réseau & Podométrie
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Gestion des Donnees", "Reseau & Podometrie Differentielle Nette")

    # Left: Podométrie
    draw_card(c, 50, col_y, 420, 390, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + 390 - 28, "PODOMETRIE DIFFERENTIELLE (SQLite)")

    podo_items = [
        ("Compteur Materiel Monotone", "L'ESP32 incremente ses pas continuellement sans date ni heure."),
        ("Calcul du Delta Net", "Le mobile compare chaque snapshot : delta = current - previous."),
        ("Resilience aux Redemarrages", "Si current < previous (reboot chaussure), le delta s'adapte sans perte."),
        ("Bascule Propre a Minuit", "Le compteur materiel continue mais le delta est isole pour le nouveau jour."),
        ("Ventilation Horaire Reelle", "Envoi par tranche horaire reelle (hourly_steps) sans heuristique artificielle.")
    ]
    cur_y = col_y + 390 - 55
    for lbl, desc in podo_items:
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

    # Right: MQTT & Cloud
    draw_card(c, 490, col_y, 420, 390, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + 390 - 28, "PASSERELLE TEMPS REEL (AWS IoT Core)")

    mqtt_items = [
        ("WebSockets MQTT Persistant", "Session maintenue ouverte en tache de fond pour latence minimale."),
        ("Authentification SigV4", "Signature cryptographique avec cle temporaire STS (15 min)."),
        ("Alerte de Chute (QoS 1)", "Publication immediate avec accuse de reception vers AWS IoT Core."),
        ("Supervision de Liaison", "Notification de l'etat de connexion Bluetooth et reseau."),
        ("Commandes Haptiques", "Declenchement distant d'une vibration via topic commands/haptic.")
    ]
    cur_y = col_y + 390 - 55
    for lbl, desc in mqtt_items:
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
    # SLIDE 8 : Performances Mesurées & Validation
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Validation & Controle", "Performances Mesurees")

    studio_url = "https://healthkicks.duckdns.org/dashboard/studio/classes"

    # Top KPI cards: temps d'inférence, macro F1, exactitude, rappel chutes
    metric_data = [
        ("~12 us", "TEMPS D'INFERENCE", "Evaluation C sur ESP32 (240 MHz)", PRIMARY_TEAL),
        ("91.3%", "MACRO F1-SCORE", "16 allures motrices classees", PRIMARY_TEAL),
        ("92.2%", "EXACTITUDE GLOBALE", "Robustesse sur tout le dataset", ACCENT_BLUE),
        ("95.5%", "RAPPEL CHUTES", "95.8% F1 sur chute arriere", ACCENT_AMBER)
    ]
    for idx, (val, lbl, sub, accent) in enumerate(metric_data):
        x = 50 + idx * 220
        draw_card(c, x, 360, 200, 85, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(accent)
        c.drawCentredString(x + 100, 415, val)
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(x + 100, 395, lbl)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(TEXT_MUTED)
        c.drawCentredString(x + 100, 375, sub)

    # Left card: Suivi Studio & Benchmark en direct avec lien cliquable
    draw_card(c, 50, 45, 420, 295, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, 310, "SUIVI DES STATISTIQUES ML EN DIRECT")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEXT_DARK)
    c.drawString(68, 280, "> Benchmark & Matrice de Confusion Live")
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT_MUTED)
    intro_lines = wrap_text("Toutes les metriques par classe, precisions, rappels et scores F1 sont consultables en direct sur le Studio Web :", 50)
    cur_y = 265
    for l in intro_lines:
        c.drawString(78, cur_y, l)
        cur_y -= 13

    # Clickable link box
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(ACCENT_BLUE)
    link_y = cur_y - 10
    c.drawString(78, link_y, "healthkicks.duckdns.org/dashboard/studio/classes")
    c.linkURL(studio_url, (78, link_y - 2, 78 + 330, link_y + 12), thickness=0)

    cur_y = link_y - 30
    sub_items = [
        ("Transparence & Auditabilite", "Verification immediate des taux de classification pour chaque classe."),
        ("Requalification Studio", "Visualisation chronologique des echantillons et analyse des derives.")
    ]
    for lbl, desc in sub_items:
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

    # Right card: Rigueur logicielle & tests automatisés
    draw_card(c, 490, 45, 420, 295, CARD_BG, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(508, 310, "RIGUEUR LOGICIELLE & TESTS AUTOMATISES")

    tests_info = [
        ("Approche Contract-Driven", "Tout echange (BLE, REST, MQTT) est regi par des contrats formels sous contracts/."),
        ("324 Tests Backend & 312 Tests Mobile", "Suites completes pytest et Flutter validant odometrie, auth et synchronisation."),
        ("Validation Memoire Firmware", "PlatformIO (pio run) valide 100% des limites de Flash et de RAM statique (0 fuite)."),
        ("Rappel d'Inactivite Haptique", "Seuil reglable de 10 a 120 min avec alerte periodique autonome.")
    ]
    cur_y = 280
    for lbl, desc in tests_info:
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
    # SLIDE 9 : Conclusion & Perspectives
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Synthese & Perspectives d'Avenir", "L'Alliance de l'Intelligence Artificielle et de la Sobriete IoT", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "CE QUE NOUS AVONS DEMONTRE")

    achievements = [
        ("TinyML Frugal & Performant", "Un microcontroleur standard low-cost classifie la demarche en temps reel (~12 us) sans runtime IA lourd."),
        ("Chaine IoT Securisee", "Chiffrement BLE LESC, mise a jour OTA avec rollback, auth OAuth2 PKCE et courtage STS temporaire."),
        ("Podometrie Nette & Verifiable", "Elimination des faux pas et restitution fidele heure par heure pour l'utilisateur."),
        ("Serenite pour les Proches", "Alerte rapide et fiable lors d'un accident par SMS et email sans fausses alarmes repetitives.")
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
    c.drawString(508, 405, "FEUILLE DE ROUTE TECHNOLOGIQUE")

    roadmap = [
        ("Amelioration de la Demarche MLOps", "Versionning systematique des modeles entraines, registre d'artefacts et tracabilite continue des jeux de donnees."),
        ("Adaptation Continue On-Device", "Ajustement fin des seuils a la foulee propre a chaque personne."),
        ("Connectivite Cellulaire NB-IoT", "Option d'autonomie totale en exterieur sans necessiter de smartphone.")
    ]
    cur_y = 370
    for lbl, desc in roadmap:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(508, cur_y, "-> " + lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 48)
        for line in lines:
            c.drawString(522, cur_y, line)
            cur_y -= 13
        cur_y -= 10

    c.showPage()

    # ==========================================
    # SLIDE 10 : Remerciements & Questions / Réponses (Liens Cliquables)
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Echange & Discussion", "Merci pour votre attention ! Questions & Echanges", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "RESSOURCES DU PROJET & DEMO EN LIGNE")

    demo_links = [
        ("Site Portfolio & CV", "https://daverck.github.io/serck-david-portfolio", "daverck.github.io/serck-david-portfolio"),
        ("Plateforme Web Live", "https://healthkicks.duckdns.org", "healthkicks.duckdns.org"),
        ("Studio & Stats du Modele ML", "https://healthkicks.duckdns.org/dashboard/studio/classes", "healthkicks.duckdns.org/dashboard/studio/classes")
    ]

    cur_y = 365
    for lbl, target_url, display_txt in demo_links:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(68, cur_y, "> " + lbl)
        cur_y -= 16

        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_TEAL)
        c.drawString(82, cur_y, display_txt)
        # Clickable hotspot
        c.linkURL(target_url, (82, cur_y - 2, 82 + 320, cur_y + 12), thickness=0)
        cur_y -= 22

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEXT_LIGHT)
    c.drawString(68, cur_y, "> Specifications & Code Source")
    cur_y -= 14
    c.setFont("Helvetica", 8.5)
    c.setFillColor(TEXT_CARD_SUB)
    c.drawString(82, cur_y, "Contrats BLE GATT, protocoles MQTT WebSockets SigV4, CI/CD.")

    # Right Card: Thèmes de discussion proposés (sans Optimisation Embarquée & FreeRTOS)
    draw_card(c, 490, 45, 420, 390, CARD_DARK, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(HexColor("#fbbf24"))
    c.drawString(508, 405, "THEMES DE DISCUSSION PROPOSES")

    discussion_items = [
        ("Algorithmes de Podometrie Nette", "Gestion des bascules temporelles, odometrie differentielle SQLite et resilience aux reboots materiels."),
        ("Securite Zero Trust & Cloud IoT", "Chiffrement BLE LESC, courtage STS de jetons temporaires et MQTT WebSockets SigV4."),
        ("Demarche MLOps & Reentrainement", "De la qualification sous le pied au versioning des modeles et a la transpilation C sans runtime lourd.")
    ]
    cur_y = 365
    for lbl, desc in discussion_items:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(508, cur_y, "> " + lbl)
        cur_y -= 15
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 48)
        for line in lines:
            c.drawString(522, cur_y, line)
            cur_y -= 13
        cur_y -= 12

    c.save()
    print(f"Simplified PDF saved to: {filename}")


if __name__ == "__main__":
    build_pdf()
