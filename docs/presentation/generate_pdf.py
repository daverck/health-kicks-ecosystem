"""Generates a simplified, high-impact 16:9 landscape PDF presentation for HealthKicks Ecosystem
using ReportLab (pure Python, vector graphics, standalone).
"""

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
    # SLIDE 1 : Titre & Vision
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
            "Podometrie podologique multi-allures (marche, course, escaliers).",
            "Rappel d'inactivite haptique anti-sedentarite sous la semelle.",
            "Zero faux pas : insensibilite aux mouvements parasites des bras."
        ]),
        ("SECURITE & PROCHES", ACCENT_AMBER, [
            "Detection de chute autonome a la source (sur la chaussure).",
            "Garde biomecanique anti-fausses alertes (s'asseoir != tomber).",
            "Alerte immediate envoyee a l'entourage et aux aidants."
        ]),
        ("EDGE AI & SOBRIETE", ACCENT_BLUE, [
            "Intelligence 100% locale sur microcontroleur ESP32-S3.",
            "Zero dependance reseau pour la securite critique.",
            "Inference instantanee en quelques microsecondes (< 15 us)."
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
            lines = wrap_text(b, 32)
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(TEXT_LIGHT)
            c.drawString(x + 18, cur_y, "-")
            c.setFont("Helvetica", 9.5)
            for line in lines:
                c.drawString(x + 30, cur_y, line)
                cur_y -= 14
            cur_y -= 10

    c.showPage()

    # ==========================================
    # SLIDE 2 : Architecture Système
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Vue d'Ensemble", "Architecture Globale : Du Capteur au Cloud")

    col_w = 200
    col_h = 390
    col_y = 45

    layers = [
        ("1. CHAUSSURE", "ESP32-S3 & Capteurs", PRIMARY_TEAL, [
            "Centrale IMU 6-axes MPU-6050.",
            "Inference Edge AI C++ (< 15 us).",
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
            "STS Token Broker : cles ephemeres (15 min).",
            "Amazon DynamoDB & PostgreSQL 16.",
            "Pipeline d'entrainement MLOps."
        ]),
        ("4. DASHBOARD", "Web Angular 22", ACCENT_AMBER, [
            "Interface reactive Angular Signals.",
            "Visualisation des pas et alertes.",
            "Mode Studio : capture de datasets.",
            "Reglage distant des seuils."
        ])
    ]

    for idx, (title, sub, accent, items) in enumerate(layers):
        x = 50 + idx * 220
        draw_card(c, x, col_y, col_w, col_h, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(accent)
        c.drawString(x + 14, col_y + col_h - 26, title)

        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_MUTED)
        c.drawString(x + 14, col_y + col_h - 42, sub)

        cur_y = col_y + col_h - 70
        for it in items:
            lines = wrap_text(it, 25)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(TEXT_DARK)
            c.drawString(x + 14, cur_y, "-")
            c.setFont("Helvetica", 9)
            for line in lines:
                c.drawString(x + 24, cur_y, line)
                cur_y -= 14
            cur_y -= 8

    c.showPage()

    # ==========================================
    # SLIDE 3 : Cœur IoT & Firmware
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Systeme Embarque", "Coeur IoT : Chaussure Instrumentee & ESP32-S3")

    s3_cards = [
        ("ARCHITECTURE MATERIELLE", PRIMARY_TEAL, [
            ("ESP32-S3 (Xtensa 240 MHz)", "Dual-core, 16 MB Flash, 8 MB PSRAM."),
            ("IMU 6-axes MPU-6050", "I2C Fast-Mode (400 kHz) : acc et gyro 3D."),
            ("Actuateur Haptique", "LEDC PWM 10 kHz (MOSFET AO3400)."),
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
        draw_card(c, x, col_y, 275, col_h, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(accent)
        c.drawString(x + 15, col_y + col_h - 28, title)

        cur_y = col_y + col_h - 60
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
    # SLIDE 4 : Edge Machine Learning
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Intelligence Artificielle Embarquee", "Edge Machine Learning : Classification & Securite")

    s4_cards = [
        ("POURQUOI L'EDGE AI ?", PRIMARY_TEAL, [
            ("Zero Latence Critique", "Reaction immediate lors du choc sans delai reseau."),
            ("Autonomie Hors-Reseau", "Fonctionne en zone blanche ou sans smartphone."),
            ("Confidentialite Totale", "Les donnees cinematiques brutes restent en local.")
        ]),
        ("16 INDICATEURS CANONIQUES", ACCENT_BLUE, [
            ("Invariance en Rotation", "Magnitudes euclidiennes ||a|| et ||w|| insensibles a l'orientation."),
            ("Statistiques de Forme", "Min, Max, Moyenne, Ecart-type (Std), Pic-a-pic (P2P)."),
            ("Dispersion & Energie", "Ecarts-types axiaux et puissances moyennes.")
        ]),
        ("CLASSIFIEUR & GARDES HYBRIDES", ACCENT_AMBER, [
            ("ExtraTrees Multiclasse", "Foret d'arbres randomises : robuste face au surapprentissage."),
            ("Detection d'Impact", "Declencheur d'acceleration brutale (> 16.2 m/s2)."),
            ("Garde Post-Chute", "Verification d'assiette et d'immobilite au sol.")
        ])
    ]

    for idx, (title, accent, items) in enumerate(s4_cards):
        x = 50 + idx * 295
        draw_card(c, x, col_y, 275, col_h, CARD_BG, accent)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(accent)
        c.drawString(x + 15, col_y + col_h - 28, title)

        cur_y = col_y + col_h - 60
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
    # SLIDE 5 : MLOps Pipeline
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
    # SLIDE 6 : Réseau & Podométrie
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Gestion des Donnees", "Reseau & Podometrie Differentielle Nette")

    # Left: Podométrie
    draw_card(c, 50, col_y, 420, col_h, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + col_h - 28, "PODOMETRIE DIFFERENTIELLE (SQLite)")

    podo_items = [
        ("Compteur Materiel Monotone", "L'ESP32 incremente ses pas continuellement sans date ni heure."),
        ("Calcul du Delta Net", "Le mobile compare chaque snapshot : delta = current - previous."),
        ("Resilience aux Redemarrages", "Si current < previous (reboot chaussure), le delta s'adapte sans perte."),
        ("Bascule Propre a Minuit", "Le compteur materiel continue mais le delta est isole pour le nouveau jour."),
        ("Ventilation Horaire Reelle", "Envoi par tranche horaire reelle (hourly_steps) sans heuristique artificielle.")
    ]
    cur_y = col_y + col_h - 55
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
    draw_card(c, 490, col_y, 420, col_h, CARD_BG, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + col_h - 28, "PASSERELLE TEMPS REEL (AWS IoT Core)")

    mqtt_items = [
        ("WebSockets MQTT Persistant", "Session maintenue ouverte en tache de fond pour latence minimale."),
        ("Authentification SigV4", "Signature cryptographique avec cle temporaire STS (15 min)."),
        ("Alerte de Chute (QoS 1)", "Publication immediate avec accuse de reception vers AWS IoT Core."),
        ("Supervision de Liaison", "Notification de l'etat de connexion Bluetooth et reseau."),
        ("Commandes Haptiques", "Declenchement distant d'une vibration via topic commands/haptic.")
    ]
    cur_y = col_y + col_h - 55
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
    # SLIDE 7 : Métriques Clés & Paramétrage
    # ==========================================
    c.setFillColor(LIGHT_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Validation & Controle", "Performances Mesurees & Personnalisation")

    metric_data = [
        ("~12 us", "TEMPS D'INFERENCE", "Evaluation C sur ESP32 (240 MHz)", PRIMARY_TEAL),
        ("< 35 ms", "REACTION HAPTIQUE", "Delai impact -> vibration locale", ACCENT_BLUE),
        ("> 88%", "MACRO F1-SCORE", "Separation allures motrices", PRIMARY_TEAL),
        ("> 94%", "SENSIBILITE CHUTE", "Detection fiable avec gardes", ACCENT_AMBER)
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

    draw_card(c, 50, 45, 420, 295, CARD_BG, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(68, 310, "PARAMETRAGE SUR L'APPLICATION MOBILE")

    params = [
        ("Seuil d'Impact Ajustable", "Sensibilite de deceleration reglable (seuil haut pour trail/running, fin pour seniors)."),
        ("Rappel d'Inactivite Configurable", "Intervalle de sedentarite au choix (30, 45, 60 min) avec vibrations plantaires."),
        ("Gestion des Destinataires", "Configuration des contacts prevenus immediatement en cas d'accident.")
    ]
    cur_y = 280
    for lbl, desc in params:
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

    draw_card(c, 490, 45, 420, 295, CARD_BG, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(508, 310, "RIGUEUR LOGICIELLE & TESTS AUTOMATISES")

    tests_info = [
        ("Approche Contract-Driven", "Tout echange (BLE, REST, MQTT) est regi par des contrats formels sous contracts/."),
        ("324 Tests Backend FastAPI", "Suite complete pytest validant authentification, endpoints et persistance."),
        ("210 Tests Application Mobile", "Tests unitaires et de widgets Flutter validant l'odometrie SQLite et la synchronisation."),
        ("Validation Memoire Firmware", "PlatformIO (pio run) valide 100% des limites de Flash et de RAM statique.")
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
    # SLIDE 8 : Conclusion & Perspectives
    # ==========================================
    c.setFillColor(DARK_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_header(c, "Synthese & Perspectives d'Avenir", "L'Alliance de l'Intelligence Artificielle et de la Sobriete IoT", dark=True)

    draw_card(c, 50, 45, 420, 390, CARD_DARK, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, 405, "CE QUE NOUS AVONS DEMONTRE")

    achievements = [
        ("TinyML Frugal & Performant", "Un microcontroleur low-cost peut classifier la demarche en temps reel sans runtime IA lourd."),
        ("Chaine IoT Securisee", "Chiffrement BLE LESC, mise a jour OTA avec rollback, auth OAuth2 PKCE et courtage STS temporaire."),
        ("Podometrie Nette & Verifiable", "Elimination des faux pas et restitution fidele heure par heure pour l'utilisateur."),
        ("Serenite pour les Proches", "Alerte rapide et fiable lors d'un accident sans fausses alarmes repetitives.")
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
        ("Capteurs Piezoresistifs (FSR)", "Mesure de la repartition des pressions plantaires talon / plante."),
        ("Adaptation Continue On-Device", "Ajustement fin des seuils a la foulee propre a chaque personne."),
        ("Connectivite Cellulaire NB-IoT", "Option d'autonomie totale en exterieur sans necessiter de smartphone."),
        ("Integration en Semelle Amovible", "Format glissable dans n'importe quelle chaussure de sport ou de ville.")
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

    c.save()
    print(f"Simplified PDF saved to: {filename}")


if __name__ == "__main__":
    build_pdf()
