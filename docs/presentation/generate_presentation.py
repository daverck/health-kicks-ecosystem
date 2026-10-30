"""Generates a simplified, high-impact widescreen PowerPoint presentation for HealthKicks Ecosystem.
Focus: Maximum clarity, concise bullet points, prominent metrics, elegant layout.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    DARK_BG = RGBColor(15, 23, 42)        # Slate 900
    LIGHT_BG = RGBColor(248, 250, 252)    # Slate 50
    CARD_BG = RGBColor(255, 255, 255)     # White
    DARK_CARD_BG = RGBColor(30, 41, 59)   # Slate 800
    
    PRIMARY_TEAL = RGBColor(13, 148, 136) # Teal 600
    ACCENT_AMBER = RGBColor(217, 119, 6)  # Amber 600
    ACCENT_BLUE = RGBColor(37, 99, 235)   # Blue 600
    
    TEXT_DARK = RGBColor(15, 23, 42)       # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139)  # Slate 500
    TEXT_LIGHT = RGBColor(248, 250, 252)  # Slate 50
    TEXT_TEAL = RGBColor(20, 184, 166)    # Teal 500

    def add_header(slide, title_text, category_text, dark=False):
        # Category Badge
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = PRIMARY_TEAL if not dark else TEXT_TEAL
        p_cat.font.name = "Segoe UI"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(25)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_DARK if not dark else TEXT_LIGHT
        p_title.font.name = "Segoe UI"

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    # ==========================================
    # SLIDE 1 : Titre & Vision
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, DARK_BG)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(1.5), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY_TEAL
    bar.line.fill.background()

    # Title & Subtitle
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(1.8))
    tf = t_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "HealthKicks Ecosystem"
    p.font.size = Pt(42)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p.font.name = "Segoe UI"
    
    p2 = tf.add_paragraph()
    p2.text = "Chaussure Intelligente : Podométrie Haute Précision & Détection de Chute Autonome"
    p2.font.size = Pt(19)
    p2.font.color.rgb = TEXT_TEAL
    p2.font.name = "Segoe UI"
    p2.space_before = Pt(8)

    # 3 Simplified Cards
    card_w = Inches(3.72)
    card_h = Inches(3.4)
    top_pos = Inches(3.4)

    cards_s1 = [
        ("🏃  ACTIVITÉ & SPORT", PRIMARY_TEAL, [
            "Podométrie podologique multi-allures (marche, course, escaliers).",
            "Rappel d'inactivité haptique anti-sédentarité sous la semelle.",
            "Zéro faux pas : insensibilité aux mouvements parasites des bras."
        ]),
        ("🛡️  SÉCURITÉ & PROCHES", ACCENT_AMBER, [
            "Détection de chute autonome à la source (sur la chaussure).",
            "Garde biomécanique anti-fausses alertes (s'asseoir ≠ tomber).",
            "Alerte immédiate envoyée à l'entourage et aux aidants."
        ]),
        ("⚡  EDGE AI & SOBRIÉTÉ", ACCENT_BLUE, [
            "Intelligence 100% locale sur microcontrôleur ESP32-S3.",
            "Zéro dépendance réseau pour la sécurité critique.",
            "Inférence instantanée en quelques microsecondes."
        ])
    ]

    for idx, (title, color, items) in enumerate(cards_s1):
        left = Inches(0.8 + idx * 4.0)
        box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top_pos, card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = DARK_CARD_BG
        box.line.color.rgb = color
        box.line.width = Pt(1.5)
        
        tf_c = box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = Inches(0.3)
        tf_c.margin_right = Inches(0.3)
        tf_c.margin_top = Inches(0.35)
        
        p = tf_c.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color
        p.font.name = "Segoe UI"
        p.space_after = Pt(12)

        for b in items:
            pb = tf_c.add_paragraph()
            pb.text = "• " + b
            pb.font.size = Pt(12)
            pb.font.color.rgb = TEXT_LIGHT
            pb.font.name = "Segoe UI"
            pb.space_before = Pt(8)

    s1.notes_slide.notes_text_frame.text = (
        "[00:00 - 01:00]\n"
        "Bonjour à tous. Je vous présente HealthKicks, une chaussure intelligente d'analyse du mouvement et de sécurité.\n\n"
        "Contrairement aux montres connectées qui comptent des faux pas à cause des gestes de bras, la chaussure capture la mécanique réelle de la marche et propose un rappel d'inactivité sous la semelle.\n\n"
        "Elle intègre aussi une détection de chute autonome qui alerte instantanément les proches, sans dépendre du cloud pour la décision d'urgence."
    )

    # ==========================================
    # SLIDE 2 : Architecture Système
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, LIGHT_BG)
    add_header(s2, "Architecture Globale : Du Capteur au Cloud", "Vue d'Ensemble")

    col_w = Inches(2.78)
    col_h = Inches(5.3)
    c_top = Inches(1.6)

    layers = [
        ("1. CHAUSSURE", "ESP32-S3 & Capteurs", PRIMARY_TEAL, [
            "Centrale IMU 6-axes MPU-6050",
            "Inférence Edge AI C++ (< 15 µs)",
            "Vibreur haptique PWM (10 kHz)",
            "Serveur BLE GATT sécurisé (LESC)"
        ]),
        ("2. MOBILE", "Passerelle Flutter / SQLite", ACCENT_BLUE, [
            "Liaison BLE chiffrée & appairage 60s",
            "Odométrie différentielle SQLite",
            "Auth OAuth2 avec PKCE RFC 7636",
            "Passerelle MQTT WebSockets SigV4"
        ]),
        ("3. CLOUD", "FastAPI & AWS IoT", PRIMARY_TEAL, [
            "Broker AWS IoT Core (QoS 1)",
            "STS Token Broker : clés éphémères (15 min)",
            "Amazon DynamoDB & PostgreSQL 16",
            "Pipeline d'entraînement MLOps"
        ]),
        ("4. DASHBOARD", "Web Angular 22", ACCENT_AMBER, [
            "Interface réactive Angular Signals",
            "Visualisation des pas et alertes",
            "Mode Studio : capture de datasets",
            "Réglage distant des seuils"
        ])
    ]

    for idx, (title, subtitle, accent, items) in enumerate(layers):
        left = Inches(0.8 + idx * 2.95)
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, c_top, col_w, col_h)
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = accent
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.3)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = accent
        p.font.name = "Segoe UI"
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.font.name = "Segoe UI"
        p_sub.space_after = Pt(16)

        for it in items:
            pi = tf.add_paragraph()
            pi.text = "• " + it
            pi.font.size = Pt(11.5)
            pi.font.color.rgb = TEXT_DARK
            pi.font.name = "Segoe UI"
            pi.space_before = Pt(8)

    s2.notes_slide.notes_text_frame.text = (
        "[01:00 - 02:30]\n"
        "L'architecture sépare clairement les responsabilités :\n"
        "1. La chaussure (ESP32-S3) traite le signal et réagit localement.\n"
        "2. Le smartphone sert de passerelle en BLE chiffré et stocke hors-ligne en SQLite.\n"
        "3. Le Cloud AWS & FastAPI : le mobile s'authentifie via OAuth2 PKCE. FastAPI joue le rôle de STS Token Broker en générant des clés AWS temporaires de 15 minutes restreintes au topic de la chaussure. La communication temps réel est assurée par MQTT WebSockets signé en SigV4.\n"
        "4. Le tableau de bord web permet de suivre l'activité et d'enregistrer des sessions Studio."
    )

    # ==========================================
    # SLIDE 3 : Cœur IoT & Firmware
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, LIGHT_BG)
    add_header(s3, "Cœur IoT : Chaussure Instrumentée & ESP32-S3", "Système Embarqué")

    c_w = Inches(3.72)
    c_h = Inches(5.3)

    sections_s3 = [
        ("ARCHITECTURE MATÉRIELLE", PRIMARY_TEAL, [
            ("ESP32-S3 (Xtensa 240 MHz)", "Dual-core, 16 MB Flash, 8 MB PSRAM."),
            ("IMU 6-axes MPU-6050", "I2C Fast-Mode (400 kHz) : accélération et gyro 3D."),
            ("Actuateur Haptique", "LEDC PWM 10 kHz (MOSFET AO3400 + diode de roue libre)."),
            ("Interfaces", "Bouton d'appairage GPIO 14 & LED de statut d'état.")
        ]),
        ("RÉFÉRENTIEL BIOMÉCANIQUE ISB", ACCENT_BLUE, [
            ("Norme ISB (Wu & Cavanagh)", "Repère aligné sur l'anatomie du pied humain."),
            ("Axe Z (Vertical)", "+1.0 g statique au repos sur sol plat."),
            ("Axe X (Antéro-postérieur)", "Mesure la propulsion et la décélération de la foulée."),
            ("Axe Y (Médio-latéral)", "Mesure la stabilité latérale et la pronation.")
        ]),
        ("SÉCURITÉ & MAINTENANCE OTA", ACCENT_AMBER, [
            ("Chiffrement BLE LESC", "Appairage sécurisé avec fenêtre physique de 60s."),
            ("Dual-Partition Flash A/B", "Mise à jour sans fil avec validation SHA-256 (32 octets)."),
            ("Rollback Automatique", "Probation de 15s : retour instantané à l'ancienne version si l'IMU ne répond pas.")
        ])
    ]

    for idx, (title, accent, items) in enumerate(sections_s3):
        left = Inches(0.8 + idx * 4.0)
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, c_top, c_w, c_h)
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = accent
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = accent
        p.font.name = "Segoe UI"
        p.space_after = Pt(14)

        for label, desc in items:
            pl = tf.add_paragraph()
            pl.text = "▸ " + label
            pl.font.size = Pt(11.5)
            pl.font.bold = True
            pl.font.color.rgb = TEXT_DARK
            pl.font.name = "Segoe UI"
            pl.space_before = Pt(8)

            pd = tf.add_paragraph()
            pd.text = desc
            pd.font.size = Pt(10.5)
            pd.font.color.rgb = TEXT_MUTED
            pd.font.name = "Segoe UI"
            pd.space_before = Pt(2)

    s3.notes_slide.notes_text_frame.text = (
        "[02:30 - 05:00]\n"
        "Sur la chaussure, l'ESP32-S3 communique avec l'IMU en I2C à 400 kHz.\n"
        "L'alignement suit le standard biomécanique ISB : l'axe Z vertical mesure la gravité (+1g statique), X la propulsion et Y la stabilité. Le vibreur haptique est piloté en PWM à 10 kHz pour des alertes discrètes ou franches.\n"
        "Comme la semelle est hermétique, les mises à jour se font par BLE OTA. Le binaire est vérifié par SHA-256, et un rollback automatique restaure l'ancien firmware si le capteur ne répond pas dans les 15 secondes."
    )

    # ==========================================
    # SLIDE 4 : Edge AI & Machine Learning
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, LIGHT_BG)
    add_header(s4, "Edge Machine Learning : Classification & Sécurité", "Intelligence Artificielle Embarquée")

    s4_blocks = [
        ("POURQUOI L'EDGE AI ?", PRIMARY_TEAL, [
            ("Zéro Latence Critique", "Réaction immédiate lors du choc sans délai de transmission réseau."),
            ("Autonomie Hors-Réseau", "Fonctionne en forêt, en montagne ou si le téléphone est déchargé."),
            ("Confidentialité Totale", "Les données cinématiques brutes restent sur la chaussure.")
        ]),
        ("16 INDICATEURS CANONIQUES", ACCENT_BLUE, [
            ("Invariance en Rotation", "Magnitudes euclidiennes ||a|| et ||ω|| insensibles à la pose du pied."),
            ("Statistiques de Forme", "Min, Max, Moyenne, Écart-type (Std), Pic-à-pic (P2P)."),
            ("Dispersion & Énergie", "Écarts-types axiaux et puissances moyennes de mouvement.")
        ]),
        ("CLASSIFIEUR & GARDES HYBRIDES", ACCENT_AMBER, [
            ("ExtraTrees Multiclasse", "Forêt d'arbres randomisés : robuste face au surapprentissage."),
            ("Détection d'Impact", "Déclencheur d'accélération brutale (> 16.2 m/s²)."),
            ("Garde Post-Chute", "Vérification d'assiette et d'immobilité (isUprightFlatFootStillness).")
        ])
    ]

    for idx, (title, accent, items) in enumerate(s4_blocks):
        left = Inches(0.8 + idx * 4.0)
        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, c_top, c_w, c_h)
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = accent
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = accent
        p.font.name = "Segoe UI"
        p.space_after = Pt(14)

        for label, desc in items:
            pl = tf.add_paragraph()
            pl.text = "▸ " + label
            pl.font.size = Pt(11.5)
            pl.font.bold = True
            pl.font.color.rgb = TEXT_DARK
            pl.font.name = "Segoe UI"
            pl.space_before = Pt(8)

            pd = tf.add_paragraph()
            pd.text = desc
            pd.font.size = Pt(10.5)
            pd.font.color.rgb = TEXT_MUTED
            pd.font.name = "Segoe UI"
            pd.space_before = Pt(2)

    s4.notes_slide.notes_text_frame.text = (
        "[05:00 - 08:00]\n"
        "L'IA embarquée traite le signal à 19 Hz sur une fenêtre glissante de 2 secondes.\n"
        "Au lieu de traiter les signaux bruts qui dépendent de l'orientation exacte du pied, nous extrayons 16 indicateurs canoniques basés sur les magnitudes euclidiennes (invariantes en rotation) et l'énergie du mouvement.\n"
        "Le modèle champion est un ExtraTrees multiclasse (forêt d'arbres décisionnels avec seuils randomisés), particulièrement résistant au surapprentissage.\n"
        "Pour éviter les fausses alertes (ex: s'asseoir vivement dans un fauteuil), nous combinons l'IA avec une garde biomécanique : détection de choc > 16.2 m/s² suivie d'une vérification de l'immobilité anormale au sol."
    )

    # ==========================================
    # SLIDE 5 : MLOps Pipeline
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, LIGHT_BG)
    add_header(s5, "Boucle MLOps : Du Terrain au Code C Embarqué", "Cycle d'Entraînement")

    step_w = Inches(11.73)
    step_h = Inches(1.15)
    
    steps_data = [
        ("1. MODE STUDIO HAUTE FRÉQUENCE", PRIMARY_TEAL,
         "Acquisition brute (54 / 100 Hz) déclenchée depuis l'application. Streaming en burst BLE avec contrôle CRC32 vers DynamoDB pour constituer les jeux de données."),
        
        ("2. STRATIFIED 5-FOLD CROSS VALIDATION", ACCENT_BLUE,
         "Cache incrémental local pour minimiser les coûts AWS. 5 plis stratifiés garantissant la même proportion de chutes rares. Optimisation sur le Macro F1-score."),
        
        ("3. TRANSPILATION C PURE SANS RUNTIME (m2cgen)", PRIMARY_TEAL,
         "Conversion automatique du modèle scikit-learn en C standard (activity_model_generated.h). Aucun framework lourd (zéro TFLite). Exécution en ~12 µs."),
        
        ("4. QUALITY GATE & CONTRÔLE DU FIRMWARE", ACCENT_AMBER,
         "Quality Gate bloquant : Macro F1-score ≥ 85% obligatoire. Compilation automatique PlatformIO (pio run) validant les quotas Flash/RAM avant tout déploiement.")
    ]

    for idx, (title, accent, desc) in enumerate(steps_data):
        top = Inches(1.6 + idx * 1.35)
        box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top, step_w, step_h)
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = accent
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = accent
        p.font.name = "Segoe UI"

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_DARK
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(4)

    s5.notes_slide.notes_text_frame.text = (
        "[08:00 - 10:30]\n"
        "L'entraînement est automatisé par notre script update_edge_model.py :\n"
        "1. Le mode Studio permet d'enregistrer des sessions réelles à 54 ou 100 Hz, envoyées en BLE burst vers DynamoDB.\n"
        "2. L'évaluation utilise une validation croisée stratifiée en 5 plis (Stratified 5-Fold) pour répartir équitablement les chutes rares et optimiser le Macro F1-score.\n"
        "3. Le modèle champion est transpilé en C pur via m2cgen. Il s'exécute en seulement 12 microsecondes sans aucun framework externe.\n"
        "4. Un Quality Gate bloque la mise à jour si le F1-score est inférieur à 85%, et PlatformIO valide la compilation du firmware."
    )

    # ==========================================
    # SLIDE 6 : Réseau & Podométrie
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, LIGHT_BG)
    add_header(s6, "Réseau & Podométrie Différentielle Nette", "Gestion des Données")

    box_w = Inches(5.7)
    box_h = Inches(5.3)

    # Left: Podométrie
    b_left = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), c_top, box_w, box_h)
    b_left.fill.solid()
    b_left.fill.fore_color.rgb = CARD_BG
    b_left.line.color.rgb = PRIMARY_TEAL
    b_left.line.width = Pt(1.5)

    tf_l = b_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.3)
    tf_l.margin_right = Inches(0.3)
    tf_l.margin_top = Inches(0.3)

    p = tf_l.paragraphs[0]
    p.text = "PODOMÉTRIE DIFFÉRENTIELLE (SQLite)"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_TEAL
    p.font.name = "Segoe UI"
    p.space_after = Pt(12)

    podo_items = [
        ("Compteur Matériel Monotone", "L'ESP32 incrémente ses pas continuellement sans notion de date ni d'heure."),
        ("Calcul du Delta Net", "Le mobile compare chaque snapshot reçu : delta = current - previous."),
        ("Résilience aux Redémarrages", "Si current < previous (reboot chaussure), le delta s'adapte sans perte."),
        ("Bascule Propre à Minuit", "Le compteur matériel continue mais le delta est isolé pour le nouveau jour."),
        ("Ventilation Horaire Réelle", "Envoi par tranche horaire réelle (hourly_steps) sans heuristique artificielle.")
    ]
    for lbl, desc in podo_items:
        pl = tf_l.add_paragraph()
        pl.text = "▸ " + lbl
        pl.font.size = Pt(11.5)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_DARK
        pl.font.name = "Segoe UI"
        pl.space_before = Pt(8)

        pd = tf_l.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(2)

    # Right: MQTT & Cloud
    b_right = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), c_top, box_w, box_h)
    b_right.fill.solid()
    b_right.fill.fore_color.rgb = CARD_BG
    b_right.line.color.rgb = ACCENT_BLUE
    b_right.line.width = Pt(1.5)

    tf_r = b_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.3)
    tf_r.margin_right = Inches(0.3)
    tf_r.margin_top = Inches(0.3)

    p = tf_r.paragraphs[0]
    p.text = "PASSERELLE TEMPS RÉEL (AWS IoT Core)"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Segoe UI"
    p.space_after = Pt(12)

    mqtt_items = [
        ("WebSockets MQTT Persistant", "Session maintenue ouverte en tâche de fond pour une latence minimale."),
        ("Authentification SigV4", "Signature cryptographique de chaque trame avec clé temporaire STS."),
        ("Alerte de Chute (QoS 1)", "Publication immédiate avec accusé de réception vers AWS IoT Core."),
        ("Supervision de Liaison", "Notification de l'état de connexion Bluetooth et réseau."),
        ("Commandes Haptiques", "Déclenchement distant d'une vibration via topic commands/haptic.")
    ]
    for lbl, desc in mqtt_items:
        pl = tf_r.add_paragraph()
        pl.text = "▸ " + lbl
        pl.font.size = Pt(11.5)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_DARK
        pl.font.name = "Segoe UI"
        pl.space_before = Pt(8)

        pd = tf_r.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(2)

    s6.notes_slide.notes_text_frame.text = (
        "[10:30 - 12:30]\n"
        "Pour la podométrie, l'ESP32 possède un compteur monotone physique qui ne connaît pas les jours. Notre application mobile implémente une odométrie différentielle SQLite : elle calcule le delta net de pas, gère les redémarrages de chaussure et ventile les pas heure par heure de manière 100% réelle.\n"
        "Pour les alertes, le mobile maintient une connexion WebSockets MQTT signée en SigV4 vers AWS IoT Core, ce qui permet d'envoyer l'alerte de chute en quelques dizaines de millisecondes aux proches."
    )

    # ==========================================
    # SLIDE 7 : Métriques Clés & Paramétrage
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, LIGHT_BG)
    add_header(s7, "Performances Mesurées & Personnalisation", "Validation & Contrôle")

    metric_w = Inches(2.78)
    metric_h = Inches(1.5)
    
    metrics = [
        ("~12 µs", "TEMPS D'INFÉRENCE", "Évaluation C sur ESP32 (240 MHz)", PRIMARY_TEAL),
        ("< 35 ms", "RÉACTION HAPTIQUE", "Délai impact ➔ vibration locale", ACCENT_BLUE),
        ("> 88%", "MACRO F1-SCORE", "Séparation des allures motrices", PRIMARY_TEAL),
        ("> 94%", "SENSIBILITÉ CHUTE", "Détection fiable avec gardes", ACCENT_AMBER)
    ]

    for idx, (val, label, sub, accent) in enumerate(metrics):
        left = Inches(0.8 + idx * 2.95)
        m_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.6), metric_w, metric_h)
        m_box.fill.solid()
        m_box.fill.fore_color.rgb = CARD_BG
        m_box.line.color.rgb = accent
        m_box.line.width = Pt(1.5)

        tf = m_box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        tf.margin_right = Inches(0.15)
        tf.margin_top = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = accent
        p.font.name = "Segoe UI"
        p.alignment = PP_ALIGN.CENTER

        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.font.size = Pt(10)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = TEXT_DARK
        p_lbl.font.name = "Segoe UI"
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.space_before = Pt(2)

        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.font.name = "Segoe UI"
        p_sub.alignment = PP_ALIGN.CENTER

    top_b = Inches(3.5)
    b_bottom_w = Inches(5.7)
    b_bottom_h = Inches(3.4)

    # Left: Paramétrage Mobile
    b_p = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_b, b_bottom_w, b_bottom_h)
    b_p.fill.solid()
    b_p.fill.fore_color.rgb = CARD_BG
    b_p.line.color.rgb = ACCENT_AMBER
    b_p.line.width = Pt(1.5)

    tf_p = b_p.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = Inches(0.3)
    tf_p.margin_right = Inches(0.3)
    tf_p.margin_top = Inches(0.25)

    p = tf_p.paragraphs[0]
    p.text = "PARAMÉTRAGE SUR L'APPLICATION MOBILE"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.font.name = "Segoe UI"
    p.space_after = Pt(8)

    param_items = [
        ("Seuil d'Impact Ajustable", "Sensibilité de décélération réglable selon le profil (seuil élevé pour le trail/running, fin pour seniors)."),
        ("Rappel d'Inactivité Personnalisable", "Intervalle de sédentarité au choix (30, 45, 60 minutes) avec vibrations plantaires."),
        ("Gestion des Destinataires", "Configuration des contacts prévenus immédiatement en cas d'accident.")
    ]
    for lbl, desc in param_items:
        pl = tf_p.add_paragraph()
        pl.text = "▸ " + lbl
        pl.font.size = Pt(11)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_DARK
        pl.font.name = "Segoe UI"
        pl.space_before = Pt(6)

        pd = tf_p.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MUTED
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(2)

    # Right: Rigueur Logicielle
    b_q = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), top_b, b_bottom_w, b_bottom_h)
    b_q.fill.solid()
    b_q.fill.fore_color.rgb = CARD_BG
    b_q.line.color.rgb = PRIMARY_TEAL
    b_q.line.width = Pt(1.5)

    tf_q = b_q.text_frame
    tf_q.word_wrap = True
    tf_q.margin_left = Inches(0.3)
    tf_q.margin_right = Inches(0.3)
    tf_q.margin_top = Inches(0.25)

    p = tf_q.paragraphs[0]
    p.text = "RIGUEUR LOGICIELLE & TESTS AUTOMATISÉS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_TEAL
    p.font.name = "Segoe UI"
    p.space_after = Pt(8)

    qual_items = [
        ("Approche Contract-Driven", "Tout échange (BLE, REST, MQTT) est régi par des contrats formels sous contracts/."),
        ("324 Tests Backend FastAPI", "Suite complète pytest validant l'authentification, les endpoints et la persistance."),
        ("210 Tests Application Mobile", "Tests unitaires et de widgets Flutter validant l'odométrie SQLite et la synchronisation."),
        ("Validation Mémoire Firmware", "PlatformIO (pio run) valide 100% des limites de Flash et de RAM statique.")
    ]
    for lbl, desc in qual_items:
        pl = tf_q.add_paragraph()
        pl.text = "▸ " + lbl
        pl.font.size = Pt(11)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_DARK
        pl.font.name = "Segoe UI"
        pl.space_before = Pt(6)

        pd = tf_q.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MUTED
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(2)

    s7.notes_slide.notes_text_frame.text = (
        "[12:30 - 14:00]\n"
        "Côté résultats : l'inférence C prend moins de 15 microsecondes avec 0 Ko d'allocation dynamique.\n"
        "Le modèle atteint un Macro F1-score > 88% et plus de 94% de sensibilité sur les chutes.\n"
        "Sur l'application mobile, l'utilisateur peut personnaliser la sensibilité du seuil d'impact ainsi que l'intervalle de rappel d'inactivité.\n"
        "Le projet est fiabilisé par plus de 530 tests automatisés au vert sur le mobile et le backend."
    )

    # ==========================================
    # SLIDE 8 : Conclusion & Perspectives
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, DARK_BG)

    cat_b = s8.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
    p = cat_b.text_frame.paragraphs[0]
    p.text = "SYNTHÈSE & PERSPECTIVES D'AVENIR".upper()
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_TEAL
    p.font.name = "Segoe UI"

    t_box = s8.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.8))
    p = t_box.text_frame.paragraphs[0]
    p.text = "L'Alliance de l'Intelligence Artificielle et de la Sobriété IoT"
    p.font.size = Pt(25)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p.font.name = "Segoe UI"

    card_w8 = Inches(5.7)
    card_h8 = Inches(5.0)

    # Left: Ce que nous avons démontré
    c_l8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), card_w8, card_h8)
    c_l8.fill.solid()
    c_l8.fill.fore_color.rgb = DARK_CARD_BG
    c_l8.line.color.rgb = PRIMARY_TEAL
    c_l8.line.width = Pt(1.5)

    tf_l8 = c_l8.text_frame
    tf_l8.word_wrap = True
    tf_l8.margin_left = Inches(0.3)
    tf_l8.margin_right = Inches(0.3)
    tf_l8.margin_top = Inches(0.3)

    p = tf_l8.paragraphs[0]
    p.text = "CE QUE NOUS AVONS DÉMONTRÉ"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_TEAL
    p.font.name = "Segoe UI"
    p.space_after = Pt(14)

    achievements = [
        ("TinyML Frugal & Performant", "Un microcontrôleur low-cost peut classifier la démarche humaine en temps réel sans runtime IA lourd."),
        ("Chaîne IoT Sécurisée", "Chiffrement BLE LESC, mise à jour OTA avec rollback, auth OAuth2 PKCE et jetons temporaires AWS STS."),
        ("Podométrie Nette & Vérifiable", "Élimination des faux pas et restitution fidèle heure par heure pour l'utilisateur."),
        ("Sérénité pour les Proches", "Alerte rapide et fiable lors d'un accident sans fausses alarmes répétitives.")
    ]
    for lbl, desc in achievements:
        pl = tf_l8.add_paragraph()
        pl.text = "✔ " + lbl
        pl.font.size = Pt(11.5)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_LIGHT
        pl.font.name = "Segoe UI"
        pl.space_before = Pt(8)

        pd = tf_l8.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = RGBColor(148, 163, 184)
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(2)

    # Right: Perspectives
    c_r8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), Inches(1.8), card_w8, card_h8)
    c_r8.fill.solid()
    c_r8.fill.fore_color.rgb = DARK_CARD_BG
    c_r8.line.color.rgb = ACCENT_AMBER
    c_r8.line.width = Pt(1.5)

    tf_r8 = c_r8.text_frame
    tf_r8.word_wrap = True
    tf_r8.margin_left = Inches(0.3)
    tf_r8.margin_right = Inches(0.3)
    tf_r8.margin_top = Inches(0.3)

    p = tf_r8.paragraphs[0]
    p.text = "FEUILLE DE ROUTE TECHNOLOGIQUE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(251, 191, 36)
    p.font.name = "Segoe UI"
    p.space_after = Pt(14)

    roadmap = [
        ("Capteurs Piézorésistifs (FSR)", "Mesure de la répartition des pressions plantaires talon / plante."),
        ("Adaptation Continue On-Device", "Ajustement fin des seuils à la foulée propre à chaque personne."),
        ("Connectivité Cellulaire NB-IoT", "Option d'autonomie totale en extérieur sans smartphone à proximité."),
        ("Intégration en Semelle Amovible", "Format glissable dans n'importe quelle chaussure de sport ou de ville.")
    ]
    for lbl, desc in roadmap:
        pl = tf_r8.add_paragraph()
        pl.text = "➔ " + lbl
        pl.font.size = Pt(11.5)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_LIGHT
        pl.font.name = "Segoe UI"
        pl.space_before = Pt(8)

        pd = tf_r8.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = RGBColor(148, 163, 184)
        pd.font.name = "Segoe UI"
        pd.space_before = Pt(2)

    s8.notes_slide.notes_text_frame.text = (
        "[14:00 - 15:00]\n"
        "En conclusion, HealthKicks prouve qu'on peut concilier l'Intelligence Artificielle et la frugalité IoT dans un objet du quotidien.\n\n"
        "Nous qualifions le mouvement à la source pour encourager le sport, prévenir la sédentarité et alerter l'entourage en cas d'accident.\n\n"
        "Je vous remercie pour votre attention et je réponds avec grand plaisir à vos questions."
    )

    output_path = "docs/presentation/presentation_healthkicks.pptx"
    prs.save(output_path)
    print(f"Simplified presentation saved to: {output_path}")

if __name__ == "__main__":
    create_presentation()
