"""Generates a simplified, high-impact 16:9 landscape PDF presentation for HealthKicks Ecosystem
using ReportLab (pure Python, vector graphics, standalone, clickable links).
"""

import math
import os
from defusedxml.ElementTree import parse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

# Dimensions for 16:9 landscape slide in points (960 x 540)
PAGE_WIDTH = 960.0
PAGE_HEIGHT = 540.0

# Color Palette - Modern Athletic & Clinical Tech
DARK_BG = HexColor("#0b1329")        # Deep Tech Navy (Dark mode slides)
DARK_BG_ACCENT = HexColor("#070c1a") # Extra Deep Navy for subtle gradients/strips
LIGHT_BG = HexColor("#f1f5f9")       # Modern Soft Cool Gray 100
SURFACE_LIGHT = HexColor("#ffffff")  # Pure White Panel
SURFACE_DARK = HexColor("#131d38")   # Deep Tech Blue Panel
BORDER_SUBTLE = HexColor("#e2e8f0")  # Barely visible divider

# Backward compatible color aliases for nested elements
CARD_BG = HexColor("#ffffff")
CARD_DARK = HexColor("#131d38")
BORDER_LIGHT = HexColor("#e2e8f0")

# Vibrant Accent Tones
PRIMARY_BLUE = HexColor("#2563eb")   # Electric HealthKicks Blue
PRIMARY_TEAL = HexColor("#0d9488")   # High-Tech Emerald / Teal 600
TEXT_TEAL = HexColor("#14b8a6")      # Bright Mint
ACCENT_AMBER = HexColor("#d97706")   # Energetic Warm Amber
ACCENT_BLUE = HexColor("#2563eb")    # Bright Azure Blue
ACCENT_PURPLE = HexColor("#7c3aed")  # Rich Violet / AI
ACCENT_ROSE = HexColor("#e11d48")    # Safety Rose / Crimson

# Text Hierarchy
TEXT_DARK = HexColor("#0f172a")      # Slate 900
TEXT_MUTED = HexColor("#64748b")     # Slate 500
TEXT_LIGHT = HexColor("#ffffff")     # Pure White
TEXT_CARD_SUB = HexColor("#94a3b8")  # Slate 400


def draw_slide_background(c, dark=False):
    """Draws a modern subtle gradient/backdrop for the slide with decorative top mesh."""
    c.saveState()
    if dark:
        c.setFillColor(DARK_BG)
        c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
        # Top glowing accent line
        c.setFillColor(PRIMARY_BLUE)
        c.rect(0, PAGE_HEIGHT - 3, PAGE_WIDTH, 3, stroke=0, fill=1)
    else:
        c.setFillColor(LIGHT_BG)
        c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
        # Soft top brand banner strip
        c.setFillColor(HexColor("#ffffff"))
        c.rect(0, PAGE_HEIGHT - 65, PAGE_WIDTH, 65, stroke=0, fill=1)
        c.setFillColor(BORDER_SUBTLE)
        c.rect(0, PAGE_HEIGHT - 65, PAGE_WIDTH, 1, stroke=0, fill=1)
        c.setFillColor(PRIMARY_BLUE)
        c.rect(0, PAGE_HEIGHT - 3, PAGE_WIDTH, 3, stroke=0, fill=1)
    c.restoreState()


def draw_header(c, title, dark=False):
    """Modern header with vertical glowing accent bar."""
    c.saveState()
    # Glowing vertical accent bar
    c.setFillColor(PRIMARY_BLUE)
    c.roundRect(50, 485, 4.5, 22, 2.25, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(TEXT_LIGHT if dark else TEXT_DARK)
    c.drawString(64, 489, title)
    c.restoreState()


def draw_modern_panel(c, x, y, w, h, dark=False, accent_color=None, top_accent=True):
    """Modern surface container: soft flat surface with a glowing top accent line instead of heavy borders."""
    c.saveState()
    bg_col = SURFACE_DARK if dark else SURFACE_LIGHT
    # Base rounded surface
    c.setFillColor(bg_col)
    c.roundRect(x, y, w, h, 8, stroke=0, fill=1)

    # Subtle boundary line (very faint, modern)
    c.setStrokeColor(HexColor("#1e293b") if dark else HexColor("#e2e8f0"))
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 8, stroke=1, fill=0)

    # Glowing top accent line (visual anchor)
    if top_accent and accent_color:
        c.setFillColor(accent_color)
        c.roundRect(x, y + h - 3.5, w, 3.5, 1.75, stroke=0, fill=1)
    c.restoreState()


def draw_icon_bullet(c, x, y, color):
    """Draws a clean, modern geometric mini-icon bullet instead of basic text dot or broken emojis."""
    c.saveState()
    c.setFillColor(color)
    c.circle(x + 4, y + 3.5, 4, stroke=0, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.circle(x + 4, y + 3.5, 1.8, stroke=0, fill=1)
    c.restoreState()


def draw_vector_icon(c, name, x, y, size=18, color=None, bg_color=None):
    """Draws a clean, modern vector icon in pure ReportLab canvas vector commands."""
    c.saveState()
    primary = color or HexColor("#2563eb")
    secondary = bg_color or HexColor("#eff6ff")

    cx = x + size / 2.0
    cy = y + size / 2.0
    r = size / 2.0

    if name == "bulb":
        # Lightbulb (Slide 1 - Genèse)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        head_r = size * 0.32
        head_cy = y + size * 0.6
        c.circle(cx, head_cy, head_r, stroke=1, fill=1)
        bw, bh = size * 0.32, size * 0.22
        c.setFillColor(primary)
        c.roundRect(cx - bw/2, y + size * 0.16, bw, bh, 1, stroke=1, fill=1)
        c.line(cx - bw*0.25, y + size * 0.1, cx + bw*0.25, y + size * 0.1)
        c.line(cx, head_cy + head_r + 1.5, cx, head_cy + head_r + 3.5)
        c.line(cx - head_r - 1.5, head_cy, cx - head_r - 3.5, head_cy)
        c.line(cx + head_r + 1.5, head_cy, cx + head_r + 3.5, head_cy)

    elif name == "shield":
        # Shield with check (Slide 1 - Sécurité)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        p = c.beginPath()
        p.moveTo(cx, y + size * 0.95)
        p.lineTo(x + size * 0.88, y + size * 0.75)
        p.lineTo(x + size * 0.88, y + size * 0.42)
        p.curveTo(x + size * 0.88, y + size * 0.16, cx + size * 0.15, y + size * 0.05, cx, y + size * 0.02)
        p.curveTo(cx - size * 0.15, y + size * 0.05, x + size * 0.12, y + size * 0.16, x + size * 0.12, y + size * 0.42)
        p.lineTo(x + size * 0.12, y + size * 0.75)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.setStrokeColor(primary)
        c.setLineWidth(1.5)
        p_chk = c.beginPath()
        p_chk.moveTo(x + size * 0.32, y + size * 0.46)
        p_chk.lineTo(x + size * 0.46, y + size * 0.32)
        p_chk.lineTo(x + size * 0.7, y + size * 0.6)
        c.drawPath(p_chk, stroke=1, fill=0)

    elif name == "runner":
        # Runner silhouette (Slide 1 - Foulée)
        c.setFillColor(primary)
        c.circle(cx - size*0.1, y + size*0.78, size*0.14, stroke=0, fill=1)
        c.setStrokeColor(primary)
        c.setLineWidth(1.8)
        c.line(cx - size*0.1, y + size*0.65, cx + size*0.05, y + size*0.4)
        c.line(cx - size*0.05, y + size*0.58, cx - size*0.35, y + size*0.5)
        c.line(cx - size*0.05, y + size*0.58, cx + size*0.25, y + size*0.65)
        c.line(cx + size*0.05, y + size*0.4, cx - size*0.25, y + size*0.25)
        c.line(cx - size*0.25, y + size*0.25, cx - size*0.35, y + size*0.08)
        c.line(cx + size*0.05, y + size*0.4, cx + size*0.28, y + size*0.28)
        c.line(cx + size*0.28, y + size*0.28, cx + size*0.38, y + size*0.1)

    elif name == "chip" or name == "mcu":
        # Microcontroller ESP32 IC with pins (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        body_x, body_y = x + size*0.2, y + size*0.2
        body_w, body_h = size*0.6, size*0.6
        c.roundRect(body_x, body_y, body_w, body_h, 2, stroke=1, fill=1)
        c.setFillColor(primary)
        c.roundRect(body_x + body_w*0.2, body_y + body_h*0.2, body_w*0.6, body_h*0.6, 1, stroke=0, fill=1)
        c.setLineWidth(1.1)
        for i in (0.25, 0.5, 0.75):
            c.line(x + size*0.05, y + size*i, body_x, y + size*i)
            c.line(body_x + body_w, y + size*i, x + size*0.95, y + size*i)
            c.line(x + size*i, y + size*0.05, x + size*i, body_y)
            c.line(x + size*i, body_y + body_h, x + size*i, y + size*0.95)

    elif name == "smartphone":
        # Smartphone (Slide 4, Slide 8)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.3)
        pw, ph = size * 0.52, size * 0.88
        px, py = cx - pw/2, cy - ph/2
        c.roundRect(px, py, pw, ph, 3, stroke=1, fill=1)
        c.setFillColor(HexColor("#ffffff"))
        c.rect(px + 2, py + 4, pw - 4, ph - 9, stroke=0, fill=1)
        c.setLineWidth(1.0)
        c.line(cx - 2.5, py + ph - 2.5, cx + 2.5, py + ph - 2.5)
        c.line(cx - 3, py + 2, cx + 3, py + 2)

    elif name == "cloud_aws":
        # AWS Cloud (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx - size*0.18, cy - size*0.05, size*0.22, stroke=0, fill=1)
        c.circle(cx + size*0.05, cy + size*0.12, size*0.28, stroke=0, fill=1)
        c.circle(cx + size*0.26, cy - size*0.05, size*0.19, stroke=0, fill=1)
        c.roundRect(x + size*0.1, y + size*0.18, size*0.8, size*0.28, 4, stroke=0, fill=1)
        p = c.beginPath()
        p.moveTo(x + size*0.15, y + size*0.22)
        p.curveTo(x + size*0.02, y + size*0.35, x + size*0.05, y + size*0.6, cx - size*0.2, y + size*0.62)
        p.curveTo(cx - size*0.2, y + size*0.85, cx + size*0.25, y + size*0.88, cx + size*0.28, y + size*0.65)
        p.curveTo(x + size*0.88, y + size*0.65, x + size*0.95, y + size*0.35, x + size*0.8, y + size*0.22)
        p.close()
        c.drawPath(p, stroke=1, fill=0)

    elif name == "cloud_ovh":
        # OVH Cloud / Mail Server (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx, cy + size*0.08, size*0.3, stroke=1, fill=1)
        c.circle(cx - size*0.22, cy - size*0.05, size*0.2, stroke=1, fill=1)
        c.circle(cx + size*0.22, cy - size*0.05, size*0.2, stroke=1, fill=1)
        ew, eh = size * 0.42, size * 0.28
        c.setFillColor(primary)
        c.roundRect(cx - ew/2, cy - eh/2 - 2, ew, eh, 1.5, stroke=1, fill=1)
        c.setStrokeColor(HexColor("#ffffff"))
        c.setLineWidth(0.8)
        c.line(cx - ew/2, cy + eh/2 - 2, cx, cy - 1)
        c.line(cx + ew/2, cy + eh/2 - 2, cx, cy - 1)

    elif name == "database":
        # Stacked Cylinders (PostgreSQL) (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        dw = size * 0.68
        dh = size * 0.22
        dx = cx - dw/2
        c.ellipse(dx, y + size*0.14, dx + dw, y + size*0.14 + dh, stroke=1, fill=1)
        c.ellipse(dx, y + size*0.38, dx + dw, y + size*0.38 + dh, stroke=1, fill=1)
        c.ellipse(dx, y + size*0.62, dx + dw, y + size*0.62 + dh, stroke=1, fill=1)
        c.line(dx, y + size*0.25, dx, y + size*0.73)
        c.line(dx + dw, y + size*0.25, dx + dw, y + size*0.73)

    elif name == "database_dynamo":
        # Database + Lightning bolt (Amazon DynamoDB) (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        dw = size * 0.68
        dh = size * 0.25
        dx = cx - dw/2
        c.ellipse(dx, y + size*0.18, dx + dw, y + size*0.18 + dh, stroke=1, fill=1)
        c.ellipse(dx, y + size*0.58, dx + dw, y + size*0.58 + dh, stroke=1, fill=1)
        c.line(dx, y + size*0.3, dx, y + size*0.7)
        c.line(dx + dw, y + size*0.3, dx + dw, y + size*0.7)
        c.setFillColor(primary)
        c.setStrokeColor(primary)
        c.setLineWidth(0.8)
        p = c.beginPath()
        p.moveTo(cx + 1, cy + size*0.35)
        p.lineTo(cx - 3, cy)
        p.lineTo(cx + 1, cy)
        p.lineTo(cx - 1, cy - size*0.35)
        p.lineTo(cx + 4, cy - 2)
        p.lineTo(cx, cy - 2)
        p.close()
        c.drawPath(p, stroke=1, fill=1)

    elif name == "server":
        # Server Rack Chassis (Slide 4, Slide 8)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        sw, sh = size * 0.75, size * 0.65
        sx, sy = cx - sw/2, cy - sh/2
        c.roundRect(sx, sy, sw, sh, 2, stroke=1, fill=1)
        c.line(sx, sy + sh*0.35, sx + sw, sy + sh*0.35)
        c.line(sx, sy + sh*0.68, sx + sw, sy + sh*0.68)
        c.setFillColor(primary)
        c.circle(sx + 3.5, sy + sh*0.84, 1.2, stroke=0, fill=1)
        c.circle(sx + 3.5, sy + sh*0.51, 1.2, stroke=0, fill=1)
        c.circle(sx + 3.5, sy + sh*0.18, 1.2, stroke=0, fill=1)

    elif name == "lambda":
        # Serverless Lambda (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.roundRect(x + 2, y + 2, size - 4, size - 4, 3, stroke=1, fill=1)
        c.setFont("Helvetica-Bold", size * 0.6)
        c.setFillColor(primary)
        c.drawCentredString(cx, cy - size * 0.22, "λ")

    elif name == "iot_core":
        # IoT Core Antenna / Broadcast (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.line(cx, y + size*0.15, cx, y + size*0.65)
        c.circle(cx, y + size*0.7, 2.2, stroke=1, fill=1)
        p_arc1 = c.beginPath()
        p_arc1.arc(cx - size*0.3, y + size*0.4, cx + size*0.3, y + size*1.0, 45, 90)
        c.drawPath(p_arc1, stroke=1, fill=0)

    elif name == "s3_bucket":
        # Amazon S3 Bucket (Slide 4)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        p = c.beginPath()
        p.moveTo(cx - size*0.34, y + size*0.74)
        p.lineTo(cx - size*0.24, y + size*0.18)
        p.lineTo(cx + size*0.24, y + size*0.18)
        p.lineTo(cx + size*0.34, y + size*0.74)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.ellipse(cx - size*0.34, y + size*0.64, cx + size*0.34, y + size*0.84, stroke=1, fill=1)

    elif name == "forest":
        # Random Forest / Decision Trees (Slide 5)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx, y + size*0.82, 2.5, stroke=1, fill=1)
        c.circle(cx - size*0.28, y + size*0.45, 2.2, stroke=1, fill=1)
        c.circle(cx + size*0.28, y + size*0.45, 2.2, stroke=1, fill=1)
        c.circle(cx - size*0.38, y + size*0.15, 1.8, stroke=1, fill=1)
        c.circle(cx - size*0.14, y + size*0.15, 1.8, stroke=1, fill=1)
        c.circle(cx + size*0.14, y + size*0.15, 1.8, stroke=1, fill=1)
        c.circle(cx + size*0.38, y + size*0.15, 1.8, stroke=1, fill=1)
        c.line(cx, y + size*0.82, cx - size*0.28, y + size*0.45)
        c.line(cx, y + size*0.82, cx + size*0.28, y + size*0.45)
        c.line(cx - size*0.28, y + size*0.45, cx - size*0.38, y + size*0.15)
        c.line(cx - size*0.28, y + size*0.45, cx - size*0.14, y + size*0.15)
        c.line(cx + size*0.28, y + size*0.45, cx + size*0.14, y + size*0.15)
        c.line(cx + size*0.28, y + size*0.45, cx + size*0.38, y + size*0.15)

    elif name == "features":
        # Sensor Waveform (Slide 5)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.roundRect(x + 2, y + 2, size - 4, size - 4, 3, stroke=1, fill=1)
        c.setLineWidth(1.5)
        p = c.beginPath()
        p.moveTo(x + 4, cy)
        p.lineTo(x + size*0.35, cy)
        p.lineTo(x + size*0.45, cy + size*0.3)
        p.lineTo(x + size*0.58, cy - size*0.3)
        p.lineTo(x + size*0.68, cy + size*0.15)
        p.lineTo(x + size - 4, cy)
        c.drawPath(p, stroke=1, fill=0)

    elif name == "pipeline":
        # MLOps Pipeline / Stages (Slide 7)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.3)
        sq_s = size * 0.22
        c.roundRect(x + size*0.08, cy - sq_s/2, sq_s, sq_s, 1.5, stroke=1, fill=1)
        c.roundRect(cx - sq_s/2, cy - sq_s/2, sq_s, sq_s, 1.5, stroke=1, fill=1)
        c.roundRect(x + size*0.92 - sq_s, cy - sq_s/2, sq_s, sq_s, 1.5, stroke=1, fill=1)
        c.setLineWidth(1.5)
        c.line(x + size*0.08 + sq_s, cy, cx - sq_s/2, cy)
        c.line(cx + sq_s/2, cy, x + size*0.92 - sq_s, cy)

    elif name == "hitl":
        # Human In The Loop (Slide 7)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx, cy + size*0.15, size*0.15, stroke=1, fill=1)
        p = c.beginPath()
        p.moveTo(cx - size*0.2, cy - size*0.22)
        p.curveTo(cx - size*0.2, cy - size*0.05, cx + size*0.2, cy - size*0.05, cx + size*0.2, cy - size*0.22)
        c.drawPath(p, stroke=1, fill=0)
        c.setLineWidth(1.3)
        p_arc = c.beginPath()
        p_arc.arc(cx - size*0.38, cy - size*0.38, cx + size*0.38, cy + size*0.38, 30, 240)
        c.drawPath(p_arc, stroke=1, fill=0)

    elif name == "play":
        # Action Play Live Demo Badge (Slides 6, 7, 8)
        c.setFillColor(primary)
        c.circle(cx, cy, r, stroke=0, fill=1)
        c.setFillColor(HexColor("#ffffff"))
        p = c.beginPath()
        p.moveTo(cx - size*0.16, cy - size*0.24)
        p.lineTo(cx + size*0.26, cy)
        p.lineTo(cx - size*0.16, cy + size*0.24)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    elif name == "timer":
        # Stopwatch (~12 us) (Slide 6)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.3)
        c.circle(cx, cy - 1, r*0.82, stroke=1, fill=1)
        c.line(cx - 3, cy + r*0.82, cx + 3, cy + r*0.82)
        c.line(cx, cy - 1, cx + 4, cy + 3)

    elif name == "target":
        # Accuracy Bullseye (91.3%) (Slide 6)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx, cy, r*0.88, stroke=1, fill=1)
        c.circle(cx, cy, r*0.5, stroke=1, fill=0)
        c.setFillColor(primary)
        c.circle(cx, cy, r*0.22, stroke=0, fill=1)

    elif name == "impact":
        # Collision / Impact Starburst (Slide 8 - Chute)
        c.setFillColor(primary)
        c.setStrokeColor(HexColor("#ffffff"))
        c.setLineWidth(0.8)
        p = c.beginPath()
        points = 8
        for i in range(points * 2):
            rad = math.pi * i / points
            radius = (size * 0.48) if (i % 2 == 0) else (size * 0.22)
            px = cx + radius * math.cos(rad)
            py = cy + radius * math.sin(rad)
            if i == 0:
                p.moveTo(px, py)
            else:
                p.lineTo(px, py)
        p.close()
        c.drawPath(p, stroke=1, fill=1)

    elif name == "alert":
        # Siren / Alert Warning (Slide 8)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        p = c.beginPath()
        p.moveTo(cx - size*0.3, y + size*0.2)
        p.lineTo(cx + size*0.3, y + size*0.2)
        p.curveTo(cx + size*0.25, y + size*0.6, cx + size*0.15, y + size*0.75, cx, y + size*0.8)
        p.curveTo(cx - size*0.15, y + size*0.75, cx - size*0.25, y + size*0.6, cx - size*0.3, y + size*0.2)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.circle(cx, y + size*0.14, 1.8, stroke=1, fill=1)

    elif name == "phone_alert":
        # Phone with alert (Slide 8)
        draw_vector_icon(c, "smartphone", x, y, size, primary, secondary)
        c.setFillColor(HexColor("#ef4444"))
        c.circle(cx, cy, size*0.16, stroke=0, fill=1)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", size*0.22)
        c.drawCentredString(cx, cy - 2.5, "!")

    elif name == "phone_sms":
        # Phone with SMS (Slide 8)
        draw_vector_icon(c, "smartphone", x, y, size, primary, secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.1)
        c.line(cx + size*0.25, cy + size*0.25, cx + size*0.45, cy + size*0.45)
        c.line(cx + size*0.18, cy + size*0.35, cx + size*0.35, cy + size*0.52)

    elif name == "compass":
        # Compass / Target (Slide 9 - Perspectives)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx, cy, r*0.88, stroke=1, fill=1)
        p = c.beginPath()
        p.moveTo(cx, cy + r*0.75)
        p.lineTo(cx + 2.5, cy)
        p.lineTo(cx, cy - r*0.75)
        p.lineTo(cx - 2.5, cy)
        p.close()
        c.setFillColor(primary)
        c.drawPath(p, stroke=0, fill=1)

    elif name == "github":
        # GitHub Octocat / Branch (Slide 10)
        c.setFillColor(primary)
        c.circle(cx, cy, r*0.9, stroke=0, fill=1)
        c.setFillColor(HexColor("#ffffff"))
        c.setStrokeColor(HexColor("#ffffff"))
        c.setLineWidth(1.0)
        c.circle(cx - 3, cy - 3, 1.5, stroke=1, fill=1)
        c.circle(cx - 3, cy + 3, 1.5, stroke=1, fill=1)
        c.circle(cx + 3, cy + 1, 1.5, stroke=1, fill=1)
        c.line(cx - 3, cy - 3, cx - 3, cy + 3)
        c.line(cx - 3, cy - 1, cx + 3, cy + 1)

    elif name == "globe":
        # Web Globe (Slide 10)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        c.circle(cx, cy, r*0.85, stroke=1, fill=1)
        c.line(cx - r*0.85, cy, cx + r*0.85, cy)
        c.ellipse(cx - r*0.45, cy - r*0.85, cx + r*0.45, cy + r*0.85, stroke=1, fill=0)

    elif name == "chat":
        # Discussion bubbles (Slide 10)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.1)
        c.roundRect(cx - size*0.4, cy - size*0.15, size*0.5, size*0.35, 2, stroke=1, fill=1)
        c.roundRect(cx - size*0.15, cy - size*0.35, size*0.5, size*0.35, 2, stroke=1, fill=1)

    elif name == "footprint":
        # Footprint / Shoe tread (Slide 11 - Podométrie)
        c.setFillColor(primary)
        c.circle(cx, y + size*0.22, size*0.14, stroke=0, fill=1)
        c.ellipse(cx - size*0.18, y + size*0.48, cx + size*0.18, y + size*0.82, stroke=0, fill=1)
        c.circle(cx - size*0.12, y + size*0.9, 1.3, stroke=0, fill=1)
        c.circle(cx, y + size*0.94, 1.5, stroke=0, fill=1)
        c.circle(cx + size*0.12, y + size*0.9, 1.3, stroke=0, fill=1)

    elif name == "money":
        # Euro Coins Stack / Money (Slide 12 - Coûts)
        c.setFillColor(secondary)
        c.setStrokeColor(primary)
        c.setLineWidth(1.2)
        cw, ch = size * 0.65, size * 0.22
        cx_l = cx - cw/2
        c.ellipse(cx_l, y + size*0.16, cx_l + cw, y + size*0.16 + ch, stroke=1, fill=1)
        c.ellipse(cx_l, y + size*0.38, cx_l + cw, y + size*0.38 + ch, stroke=1, fill=1)
        c.ellipse(cx_l, y + size*0.60, cx_l + cw, y + size*0.60 + ch, stroke=1, fill=1)
        c.line(cx_l, y + size*0.27, cx_l, y + size*0.71)
        c.line(cx_l + cw, y + size*0.27, cx_l + cw, y + size*0.71)
        c.setFont("Helvetica-Bold", size*0.32)
        c.setFillColor(primary)
        c.drawCentredString(cx, y + size*0.62, "€")

    elif name == "angular":
        # Angular Shield (Slide 2)
        c.setFillColor(HexColor("#dd0031"))
        c.setStrokeColor(HexColor("#b90024"))
        c.setLineWidth(1.0)
        p = c.beginPath()
        p.moveTo(cx, y + size * 0.98)
        p.lineTo(x + size * 0.92, y + size * 0.8)
        p.lineTo(x + size * 0.82, y + size * 0.28)
        p.lineTo(cx, y + size * 0.02)
        p.lineTo(x + size * 0.18, y + size * 0.28)
        p.lineTo(x + size * 0.08, y + size * 0.8)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        c.setFont("Helvetica-Bold", size * 0.52)
        c.setFillColor(HexColor("#ffffff"))
        c.drawCentredString(cx, y + size * 0.28, "A")

    elif name == "python":
        # Python dual logo (Slide 2)
        c.setFillColor(HexColor("#3776ab"))
        c.setStrokeColor(HexColor("#2b5b84"))
        c.setLineWidth(0.8)
        c.roundRect(cx - size*0.42, cy - size*0.05, size*0.5, size*0.45, 2, stroke=1, fill=1)
        c.setFillColor(HexColor("#ffffff"))
        c.circle(cx - size*0.22, cy + size*0.22, 1.2, stroke=0, fill=1)
        c.setFillColor(HexColor("#ffd438"))
        c.setStrokeColor(HexColor("#e5be26"))
        c.roundRect(cx - size*0.08, cy - size*0.4, size*0.5, size*0.45, 2, stroke=1, fill=1)
        c.setFillColor(HexColor("#ffffff"))
        c.circle(cx + size*0.22, cy - size*0.18, 1.2, stroke=0, fill=1)

    elif name == "java":
        # Java Coffee Cup (Slide 2)
        c.setFillColor(HexColor("#f97316"))
        c.setStrokeColor(HexColor("#c2410c"))
        c.setLineWidth(1.0)
        c.roundRect(cx - size*0.35, y + size*0.15, size*0.55, size*0.42, 2, stroke=1, fill=1)
        # Handle
        c.setStrokeColor(HexColor("#c2410c"))
        c.arc(cx + size*0.15, y + size*0.22, cx + size*0.42, y + size*0.48, 270, 180)
        # Steam curves
        c.setStrokeColor(HexColor("#38bdf8"))
        c.setLineWidth(1.2)
        p1 = c.beginPath()
        p1.moveTo(cx - size*0.15, y + size*0.62)
        p1.curveTo(cx - size*0.22, y + size*0.75, cx - size*0.08, y + size*0.82, cx - size*0.15, y + size*0.92)
        c.drawPath(p1, stroke=1, fill=0)
        p2 = c.beginPath()
        p2.moveTo(cx + size*0.05, y + size*0.62)
        p2.curveTo(cx - size*0.02, y + size*0.75, cx + size*0.12, y + size*0.82, cx + size*0.05, y + size*0.92)
        c.drawPath(p2, stroke=1, fill=0)

    c.restoreState()


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
    # SLIDE 1 : Parcours Professionnel & Portfolio QR Code
    # ==========================================
    draw_slide_background(c, dark=False)

    qr_path = "docs/presentation/qr-code.png"
    portfolio_url = "https://daverck.github.io/serck-david-portfolio"

    card_qr_w = 460
    card_qr_h = 405
    card_qr_x = (PAGE_WIDTH - card_qr_w) / 2
    card_qr_y = 35

    draw_modern_panel(c, card_qr_x, card_qr_y, card_qr_w, card_qr_h, dark=False, accent_color=PRIMARY_BLUE)

    # Nom en grand et centré en haut de la carte
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(card_qr_x + card_qr_w / 2, card_qr_y + card_qr_h - 34, "David Serck")

    # Métier en grand
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_BLUE)
    c.drawCentredString(card_qr_x + card_qr_w / 2, card_qr_y + card_qr_h - 58, "Développeur  Full-Stack : Angular - Python - Java")

    # Micro-icônes officielles des technologies maîtrisées
    tech_y = card_qr_y + card_qr_h - 88
    center_tech_x = card_qr_x + card_qr_w / 2
    if os.path.exists("docs/presentation/angular_dev_color.png"):
        c.drawImage("docs/presentation/angular_dev_color.png", center_tech_x - 52, tech_y, width=22, height=22, preserveAspectRatio=True, mask='auto')
    if os.path.exists("docs/presentation/python_color_official.png"):
        c.drawImage("docs/presentation/python_color_official.png", center_tech_x - 11, tech_y, width=22, height=22, preserveAspectRatio=True, mask='auto')
    if os.path.exists("docs/presentation/java_official_cup.png"):
        c.drawImage("docs/presentation/java_official_cup.png", center_tech_x + 30, tech_y, width=22, height=22, preserveAspectRatio=True, mask='auto')

    if os.path.exists(qr_path):
        qr_size = 250
        qr_x = card_qr_x + (card_qr_w - qr_size) / 2
        qr_y = card_qr_y + 45
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)
        c.linkURL(portfolio_url, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), thickness=0)

    c.showPage()

    # ==========================================
    # SLIDE 2 : Titre & Vision Simplifiée
    # ==========================================
    draw_slide_background(c, dark=True)

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
    c.setFillColor(PRIMARY_BLUE)
    c.drawString(title_x + w_health, title_y, "Kicks")

    # 2 Centered Modern Panels (Activité & Sécurité), positioned below the title
    card_w = 410
    card_h = 165
    card_y = 42

    cards_s1 = [
        ("GENÈSE", ACCENT_AMBER, "bulb", [
            "Amateur de course à pied",
            "Mesure au plus près du pied",
        ]),
        ("FONCTIONNALITÉS & SÉCURITÉ", PRIMARY_TEAL, "shield", [
            # "Clip universel",
            "Détection de types de mouvements",
            "Détection de chute + alertes",
            "Rappel d'inactivité haptique",
            "Podométrie",
        ])
    ]

    for idx, (title, color, icon_name, items) in enumerate(cards_s1):
        x = 50 + idx * 450
        draw_modern_panel(c, x, card_y, card_w, card_h, dark=True, accent_color=color)

        # Subtle watermark runner silhouette for GENÈSE
        if icon_name == "bulb":
            runner_img = "docs/presentation/runner_tabler.png"
            if os.path.exists(runner_img):
                c.drawImage(runner_img, x + card_w - 95, card_y + 14, width=80, height=80, preserveAspectRatio=True, mask='auto')

        draw_vector_icon(c, icon_name, x + 20, card_y + card_h - 32, 20, color=color)

        c.setFont("Helvetica-Bold", 13.5)
        c.setFillColor(color)
        c.drawString(x + 46, card_y + card_h - 26, title)

        cur_y = card_y + card_h - 52
        for b in items:
            lines = wrap_text(b, 46)
            draw_icon_bullet(c, x + 20, cur_y, color)
            c.setFont("Helvetica", 9.5)
            c.setFillColor(TEXT_LIGHT)
            for line in lines:
                c.drawString(x + 36, cur_y, line)
                cur_y -= 14
            cur_y -= 6

    c.showPage()

    # ==========================================
    # SLIDE 3 : Cœur IoT & Biomécanique (Système Embarqué)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "SYSTÈME EMBARQUÉ")

    # Schéma Électronique Global
    schema_y = 205
    schema_h = 245
    draw_modern_panel(c, 50, schema_y, 860, schema_h, dark=True, accent_color=PRIMARY_TEAL)

    # Titre du Schéma Électronique
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEXT_TEAL)
    c.drawString(68, schema_y + schema_h - 18, "SCHÉMA ÉLECTRONIQUE GLOBAL D'INTERCONNEXION MATÉRIELLE (ESP32-S3)")

    schematic_path = "docs/presentation/circuit_esp32.png"
    if os.path.exists(schematic_path):
        c.drawImage(schematic_path, 60, schema_y + 8, width=840, height=210, preserveAspectRatio=True, anchor='c')

    # 2 Cartes en dessous : Biomécanique ISB & Traitement du Signal
    card_b_y = 35
    card_b_h = 160
    card_b_w = 420

    # Carte Gauche : Référentiel ISB
    draw_modern_panel(c, 50, card_b_y, card_b_w, card_b_h, dark=False, accent_color=ACCENT_BLUE)
    ruler_img = "docs/presentation/ruler_tabler.png"
    if os.path.exists(ruler_img):
        c.drawImage(ruler_img, 66, card_b_y + card_b_h - 29, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(88, card_b_y + card_b_h - 24, "RÉFÉRENTIEL BIOMÉCANIQUE ISB")

    # Illustration 3D des axes ISB de la chaussure (agrandie et centrée dans la carte, sans texte redondant)
    axes_img_path = "docs/presentation/shoe_isb_axes.png"
    if os.path.exists(axes_img_path):
        c.drawImage(axes_img_path, 58, card_b_y + 4, width=404, height=126, preserveAspectRatio=True, anchor='c', mask='auto')

    # Carte Droite : Traitement du Signal Embarqué
    draw_modern_panel(c, 490, card_b_y, card_b_w, card_b_h, dark=False, accent_color=ACCENT_AMBER)
    draw_vector_icon(c, "features", 506, card_b_y + card_b_h - 29, 18, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(528, card_b_y + card_b_h - 24, "TRAITEMENT DU SIGNAL")

    dsp_items = [
        ("Fenêtrage Glissant (3.0s)", ""),
        ("Invariance par Rotation", ""),
        ("Calibration du Zéro-G (Biais)", ""),
        ("Filtrage Anti-Rebond Chute", "")
    ]
    cur_y = card_b_y + card_b_h - 48
    for lbl, desc in dsp_items:
        draw_icon_bullet(c, 506, cur_y, ACCENT_AMBER)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(520, cur_y, lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(520, cur_y, line)
            cur_y -= 12
        cur_y -= 5

    c.showPage()

    # ==========================================
    # SLIDE 4 : Architecture Globale Logicielle & Système
    # ==========================================
    draw_slide_background(c, dark=False)
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

    draw_modern_panel(c, x_shoe, y_parent_shoe, w_shoe, h_parent_shoe, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "mcu", x_shoe + 14, y_top - 25, 16, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 36, y_top - 20, "1. EMBARQUÉ (ESP32-S3)")

    # Carte Cœur 0
    draw_card(c, x_shoe + 8, y_core0, w_shoe - 16, h_core0, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)
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
        draw_icon_bullet(c, x_shoe + 14, cur_cy, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 26, cur_cy, t_it)
        cur_cy -= 16

    # Carte Cœur 1
    draw_card(c, x_shoe + 8, y_core1, w_shoe - 16, h_core1, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)
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
        draw_icon_bullet(c, x_shoe + 14, cur_cy, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 26, cur_cy, t_it)
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

    draw_modern_panel(c, x_mob, y_parent_mob, w_mob, h_parent_mob, dark=False, accent_color=ACCENT_BLUE)
    draw_vector_icon(c, "smartphone", x_mob + 14, y_top - 25, 16, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 36, y_top - 20, "2. MOBILE (Flutter / Dart)")

    # Carte Base SQLite
    draw_card(c, x_mob + 8, y_sqlite, w_mob - 16, h_sqlite, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 14, y_sqlite + h_sqlite - 16, "Base Locale SQLite")
    draw_icon_bullet(c, x_mob + 14, y_sqlite + h_sqlite - 34, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_mob + 26, y_sqlite + h_sqlite - 34, "Sandbox OS privée")

    # Carte Sécurité & Keystore
    draw_card(c, x_mob + 8, y_sec, w_mob - 16, h_sec, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)
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
        draw_icon_bullet(c, x_mob + 14, cur_my, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_mob + 26, cur_my, t_it)
        cur_my -= 16

    # Carte Passerelle Hybride Cloud
    draw_card(c, x_mob + 8, y_gw, w_mob - 16, h_gw, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 14, y_gw + h_gw - 16, "Passerelle Hybride Cloud")
    mob_gw_items = [
        "MQTT WSS SigV4",
        "API REST HTTPS"
    ]
    cur_my = y_gw + h_gw - 34
    for t_it in mob_gw_items:
        draw_icon_bullet(c, x_mob + 14, cur_my, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 7.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_mob + 26, cur_my, t_it)
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

    # 3.3 Bas : Bases de données & Stockage S3
    h_db = 128
    y_db = y_ec2 - 10 - h_db          # 230 - 10 - 128 = 92

    # Hauteur parent adaptée au contenu enfant (marge basse 12 pt)
    y_parent_cloud = y_db - 12        # 80
    h_parent_cloud = y_top - y_parent_cloud  # 360 pt

    draw_modern_panel(c, x_cloud, y_parent_cloud, w_cloud, h_parent_cloud, dark=False, accent_color=CLOUD_AWS)
    draw_vector_icon(c, "cloud_aws", x_cloud + 14, y_top - 25, 16, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 36, y_top - 20, "3. CLOUD AWS")

    # Conteneur Ingestion
    draw_card(c, x_cloud + 8, y_ingest, w_cloud - 16, h_ingest, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)

    # Mini-carte gauche : AWS IoT Core (Broker MQTT WSS)
    h_sub_ingest = 62
    draw_card(c, x_cloud + 13, y_ingest + 5, 118, h_sub_ingest, CARD_BG, HexColor("#bae6fd"), border_width=1, radius=4)
    draw_vector_icon(c, "iot_core", x_cloud + 18, y_ingest + 5 + h_sub_ingest - 16, 12, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 34, y_ingest + 5 + h_sub_ingest - 14, "AWS IoT Core")
    draw_icon_bullet(c, x_cloud + 18, y_ingest + 5 + h_sub_ingest - 28, CLOUD_AWS)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 28, y_ingest + 5 + h_sub_ingest - 28, "Broker MQTT WSS")
    draw_icon_bullet(c, x_cloud + 18, y_ingest + 5 + h_sub_ingest - 42, CLOUD_AWS)
    c.drawString(x_cloud + 28, y_ingest + 5 + h_sub_ingest - 42, "Règles IoT SQL")

    # Mini-carte droite : AWS Lambda (Ingestion & Présence)
    draw_card(c, x_cloud + 135, y_ingest + 5, 118, h_sub_ingest, CARD_BG, HexColor("#fde68a"), border_width=1, radius=4)
    draw_vector_icon(c, "lambda", x_cloud + 140, y_ingest + 5 + h_sub_ingest - 16, 12, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 156, y_ingest + 5 + h_sub_ingest - 14, "AWS Lambda")
    draw_icon_bullet(c, x_cloud + 140, y_ingest + 5 + h_sub_ingest - 28, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 150, y_ingest + 5 + h_sub_ingest - 28, "Ingestion télémétrie")
    draw_icon_bullet(c, x_cloud + 140, y_ingest + 5 + h_sub_ingest - 42, ACCENT_AMBER)
    c.drawString(x_cloud + 150, y_ingest + 5 + h_sub_ingest - 42, "Présence & Statut")

    # Conteneur EC2 Docker
    draw_card(c, x_cloud + 8, y_ec2, w_cloud - 16, h_ec2, CARD_BG, HexColor("#cbd5e1"), border_width=1, radius=6)
    draw_vector_icon(c, "server", x_cloud + 14, y_ec2 + h_ec2 - 16, 12, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 30, y_ec2 + h_ec2 - 13, "Serveur EC2")
    c.setFont("Helvetica-Bold", 6.6)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 14, y_ec2 + h_ec2 - 25, "Nginx Reverse Proxy SSL")

    # Backend
    h_sub_ec2 = 58
    draw_card(c, x_cloud + 13, y_ec2 + 5, 118, h_sub_ec2, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 18, y_ec2 + 5 + h_sub_ec2 - 14, "Backend FastAPI")
    draw_icon_bullet(c, x_cloud + 18, y_ec2 + 5 + h_sub_ec2 - 28, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 28, y_ec2 + 5 + h_sub_ec2 - 28, "API REST OpenAPI")
    draw_icon_bullet(c, x_cloud + 18, y_ec2 + 5 + h_sub_ec2 - 42, PRIMARY_TEAL)
    c.drawString(x_cloud + 28, y_ec2 + 5 + h_sub_ec2 - 42, "Courtier STS (15 min)")

    # Frontend
    draw_card(c, x_cloud + 135, y_ec2 + 5, 118, h_sub_ec2, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=4)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 140, y_ec2 + 5 + h_sub_ec2 - 14, "Frontend Angular 22")
    draw_icon_bullet(c, x_cloud + 140, y_ec2 + 5 + h_sub_ec2 - 28, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 150, y_ec2 + 5 + h_sub_ec2 - 28, "Interface Signals")

    # Conteneur Bases de données & Stockage S3
    draw_card(c, x_cloud + 8, y_db, w_cloud - 16, h_db, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)

    # Aurora PG
    h_sub_db = 56
    y_row1_db = y_db + 67
    draw_card(c, x_cloud + 13, y_row1_db, 118, h_sub_db, CARD_BG, HexColor("#a7f3d0"), border_width=1, radius=4)
    draw_vector_icon(c, "database", x_cloud + 18, y_row1_db + h_sub_db - 16, 12, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 34, y_row1_db + h_sub_db - 14, "PostgreSQL 16")
    draw_icon_bullet(c, x_cloud + 18, y_row1_db + h_sub_db - 30, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 28, y_row1_db + h_sub_db - 30, "Migrations Alembic")

    # DynamoDB
    draw_card(c, x_cloud + 135, y_row1_db, 118, h_sub_db, CARD_BG, HexColor("#fde68a"), border_width=1, radius=4)
    draw_vector_icon(c, "database_dynamo", x_cloud + 140, y_row1_db + h_sub_db - 16, 12, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 156, y_row1_db + h_sub_db - 14, "Amazon DynamoDB")
    draw_icon_bullet(c, x_cloud + 140, y_row1_db + h_sub_db - 30, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 150, y_row1_db + h_sub_db - 30, "Séries NoSQL")

    # Amazon S3 (Stockage Firmware OTA)
    y_row2_db = y_db + 5
    draw_card(c, x_cloud + 13, y_row2_db, 240, h_sub_db, CARD_BG, HexColor("#bae6fd"), border_width=1, radius=4)
    draw_vector_icon(c, "s3_bucket", x_cloud + 18, y_row2_db + h_sub_db - 16, 12, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 34, y_row2_db + h_sub_db - 14, "Amazon S3")
    draw_icon_bullet(c, x_cloud + 18, y_row2_db + h_sub_db - 30, CLOUD_AWS)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 28, y_row2_db + h_sub_db - 30, "Stockage des Firmwares OTA (.bin)")

    # FLECHE 3 : Cloud AWS -> Cloud OVH
    draw_arrow(c, 792, 260, 28, ACCENT_AMBER, "SMTP", "TLS 587")

    # -------------------------------------------------------------
    # 4. CLOUD OVH : Serveur Mail Dédié (Hauteur ajustée à son contenu)
    # -------------------------------------------------------------
    w_ovh = 105
    x_ovh = 824
    h_ovh = 72
    y_ovh = 224
    draw_modern_panel(c, x_ovh, y_ovh, w_ovh, h_ovh, dark=False, accent_color=ACCENT_AMBER)
    cloud_img = "docs/presentation/cloud_lucide.png"
    if os.path.exists(cloud_img):
        c.drawImage(cloud_img, x_ovh + 8, y_ovh + h_ovh - 22, width=15, height=15, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_ovh + 26, y_ovh + h_ovh - 17, "4. CLOUD OVH")

    # Card Serveur Mail
    h_mail = 42
    draw_card(c, x_ovh + 8, y_ovh + 6, w_ovh - 16, h_mail, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.8, radius=6)
    mail_img = "docs/presentation/mail_lucide.png"
    if os.path.exists(mail_img):
        c.drawImage(mail_img, x_ovh + 13, y_ovh + 6 + 13, width=15, height=15, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_ovh + 31, y_ovh + 6 + 17, "Serveur Mail")

    c.showPage()

    # ==========================================
    # SLIDE 5 : Edge Machine Learning & Détail des Features
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "INTELLIGENCE ARTIFICIELLE EMBARQUÉE")

    col_y = 45
    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "forest", 68, col_y + 390 - 32, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(92, col_y + 390 - 28, "POURQUOI UN RANDOM FOREST PLUTÔT QU'UN AUTRE ?")

    model_points = [
        ("vs Deep Learning (TFLite Micro)", "100x plus rapide (~12 us vs 15-50 ms)."),
        ("vs Modèles Linéaires & SVM", "Capture nativement les frontières non-linéaires complexes."),
        ("vs Arbre de Décision Unique (CART)", "L'agrégation de 80 arbres (bagging) réduit drastiquement la variance et immunise contre le bruit."),
        ("vs Gradient Boosting (XGBoost)", "Vote probabiliste direct sans interpréteur lourd. class_weight='balanced' préserve un rappel chute >95% sur les classes rares."),
        ("Sélection parmi les modèles m2cgen", "Retenu parmi les algorithmes compatibles pour sa conversion en C pur (arbres if/else), sans runtime ni dépendance.")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in model_points:
        draw_icon_bullet(c, 66, cur_y, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(80, cur_y, lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(80, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
    draw_vector_icon(c, "features", 508, col_y + 390 - 32, 18, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(532, col_y + 390 - 28, "28 FEATURES")

    feat_points = [
        ("1. Intensité Globale (Invariante 3D)", "Normes ||a|| et ||w|| : min, max, moyenne, énergie cinétique."),
        ("2. Rupture & Amplitude Dynamique", "Peak-to-Peak (max - min) et Jerk maximal (choc violent vs allure stable)."),
        ("3. Dispersion & Posture (6 Axes)", "Écarts-types axiaux (ax, ay, az, gx, gy, gz) et moyennes (assis vs couché)."),
        ("4. Directionnalité & Asymétrie", "Delta ay (fin - début) et asymétrie 1ère/2nde moitié (assis <-> debout)."),
        ("5. Stabilité Post-Impact", "Écart-type de queue de fenêtre (détection de l'immobilité au sol).")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in feat_points:
        draw_icon_bullet(c, 506, cur_y, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(520, cur_y, lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(520, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    c.showPage()

    # ==========================================
    # SLIDE 6 : Performances Mesurées & Graphique ML
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "VALIDATION & CONTRÔLE")

    # Badge Démonstration en Direct
    draw_modern_panel(c, 520, 470, 390, 26, dark=False, accent_color=ACCENT_AMBER, top_accent=False)
    draw_vector_icon(c, "play", 528, 474, 16, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawCentredString(720, 478, "DÉMONSTRATION 1 : RECONNAISSANCE D'ALLURE EN DIRECT")

    # Gauche : Graphique des performances ML réel (capture web Studio cliquable)
    ml_img_path = "health-kicks-frontend/public/images/screenshots/web_showcase_ml_confusion_matrix.webp"
    card_l_w = 460
    card_h = 390
    draw_modern_panel(c, 50, col_y, card_l_w, card_h, dark=False, accent_color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(68, col_y + card_h - 26, "BENCHMARK RÉEL STUDIO (MATRICE DE CONFUSION)")

    if os.path.exists(ml_img_path):
        img_w = 424
        img_h = 310
        img_x = 68
        img_y = col_y + 18
        c.drawImage(ml_img_path, 58, col_y + 18, width=444, height=325, preserveAspectRatio=True, anchor='c')
        studio_url = "https://healthkicks.duckdns.org/dashboard/studio/classes"
        c.linkURL(studio_url, (img_x, img_y, img_x + img_w, img_y + img_h), thickness=0)

    # Droite : 2 Grandes Cartes Métriques empilées
    card_r_x = 530
    card_r_w = 380
    card_metric_h = 188

    # Carte 1 (Haut) : Temps d'inférence
    card_1_y = col_y + 202
    draw_modern_panel(c, card_r_x, card_1_y, card_r_w, card_metric_h, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "timer", card_r_x + 36, card_1_y + 104, 34, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(card_r_x + card_r_w / 2 + 15, card_1_y + 115, "~12 us")
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 80, "TEMPS D'INFÉRENCE EMBARQUÉ")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(card_r_x + card_r_w / 2, card_1_y + 55, "Mesure réelle micros() sur Cœur 1 (Xtensa 240 MHz)")

    # Carte 2 (Bas) : Macro F1-Score
    card_2_y = col_y
    draw_modern_panel(c, card_r_x, card_2_y, card_r_w, card_metric_h, dark=False, accent_color=ACCENT_AMBER)
    draw_vector_icon(c, "target", card_r_x + 36, card_2_y + 104, 34, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(ACCENT_AMBER)
    c.drawCentredString(card_r_x + card_r_w / 2 + 15, card_2_y + 115, "91.3%")
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
    draw_slide_background(c, dark=False)
    draw_header(c, "ENTRAÎNEMENT")

    # Badge Démonstration en Direct
    draw_modern_panel(c, 520, 470, 390, 26, dark=False, accent_color=PRIMARY_TEAL, top_accent=False)
    draw_vector_icon(c, "play", 528, 474, 16, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(720, 478, "DÉMONSTRATION 2 : STUDIO WEB & REQUALIFICATION HITL")

    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
    draw_vector_icon(c, "pipeline", 68, col_y + 390 - 32, 18, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(92, col_y + 390 - 28, "MLOps Pipeline")

    steps_mlops = [
        ("1. Capture", ""),
        ("2. Qualification Studio Mobile & Web", ""),
        ("3. Pipeline Python d'Entraînement", ""),
        ("4. Transpilation m2cgen Pure C", ""),
        ("5. Injection Firmware Sans Recompilation", "")
    ]

    cur_y = col_y + 390 - 58
    for lbl, desc in steps_mlops:
        draw_icon_bullet(c, 66, cur_y, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(80, cur_y, lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(80, cur_y, line)
            cur_y -= 13
        cur_y -= 8

    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "hitl", 508, col_y + 390 - 32, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(532, col_y + 390 - 28, "MODE HITL (Human-in-the-Loop)")

    hitl_items = [
        ("Buffer Circulaire Haute Fréquence", ""),
        ("Capture Pré & Post Événement", ""),
        ("Transfert Fast Burst BLE", ""),
        ("Requalification Web Studio", "")
    ]

    cur_y = col_y + 390 - 58
    for lbl, desc in hitl_items:
        draw_icon_bullet(c, 506, cur_y, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(520, cur_y, lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(520, cur_y, line)
            cur_y -= 13
        cur_y -= 8

    c.showPage()

    # ==========================================
    # SLIDE 8 : Détection de Chute & Chaîne d'Urgence
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "DÉTECTION DE CHUTE")

    # Badge Démonstration en Direct
    draw_modern_panel(c, 520, 470, 390, 26, dark=False, accent_color=ACCENT_AMBER, top_accent=False)
    draw_vector_icon(c, "play", 528, 474, 16, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawCentredString(720, 478, "DÉMONSTRATION 3 : SIMULATION D'UNE CHUTE EN DIRECT")

    # Gauche : Points Clés & Illustration Chute
    card_l_x = 45
    card_l_w = 345
    draw_modern_panel(c, card_l_x, col_y, card_l_w, 390, dark=False, accent_color=ACCENT_AMBER)
    draw_vector_icon(c, "shield", card_l_x + 18, col_y + 390 - 32, 16, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(card_l_x + 40, col_y + 390 - 28, "SÉCURITÉ & GESTION DES FAUX-POSITIFS")

    fall_key_points = [
        ("Annulation Automatique par Relèvement", ""),
        ("Période de Cooldown Anti-Rebond (5.0s)", ""),
        ("Délai de Rétractation Utilisateur (60s)", ""),
        ("Orchestration Centralisée Backend", ""),
        ("Repli d'Urgence Appel 112", "")
    ]

    cur_y = col_y + 390 - 54
    for lbl, desc in fall_key_points:
        draw_icon_bullet(c, card_l_x + 16, cur_y, ACCENT_AMBER)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(card_l_x + 30, cur_y, lbl)
        cur_y -= 22

    # Illustration de chute (glissade sur peau de banane avec chaussure connectée)
    fall_img_path = "docs/presentation/fall_illustration.png"
    if os.path.exists(fall_img_path):
        c.drawImage(fall_img_path, card_l_x + 15, col_y + 10, width=315, height=205, preserveAspectRatio=True, anchor='c', mask='auto')

    # Droite : Schéma Graphique Vectoriel de la Chaîne d'Escalade et de Secours
    x_chain = 405
    w_chain = 510
    h_chain = 390
    draw_modern_panel(c, x_chain, col_y, w_chain, h_chain, dark=True, accent_color=PRIMARY_TEAL)
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
    draw_vector_icon(c, "impact", b0_x + 10, b0_y + 4, 16, color=HexColor("#ef4444"))
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#fca5a5"))
    c.drawCentredString(b0_x + b0_w / 2 + 10, b0_y + 7.5, "CHUTE DÉTECTÉ")

    # Flèche 0 -> 1
    draw_down_arrow(c, x_center, 356, 338, HexColor("#ef4444"))

    # 1. Alerte Locale Immédiate (Capteur ESP32-S3)
    b1_y = 286
    b1_h = 52
    draw_card(c, bx_x, b1_y, bx_w, b1_h, HexColor("#0f172a"), HexColor("#14b8a6"), border_width=1.2, radius=6)
    draw_vector_icon(c, "alert", bx_x + 12, b1_y + b1_h - 18, 14, color=HexColor("#14b8a6"))
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#14b8a6"))
    c.drawString(bx_x + 32, b1_y + b1_h - 14, "1. ALERTE LOCALE IMMÉDIATE (CAPTEUR ESP32-S3)")
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
    draw_vector_icon(c, "phone_alert", bx_x + 12, b2_y + b2_h - 18, 14, color=HexColor("#38bdf8"))
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#38bdf8"))
    c.drawString(bx_x + 32, b2_y + b2_h - 14, "2. PASSERELLE MOBILE (FLUTTER / DART)")
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
    draw_vector_icon(c, "server", bx_x + 12, b3_y + b3_h - 18, 14, color=HexColor("#c084fc"))
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#c084fc"))
    c.drawString(bx_x + 32, b3_y + b3_h - 14, "3. BACKEND FASTAPI (ORCHESTRATEUR DE SECOURS)")
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
    draw_vector_icon(c, "phone_sms", bx_x + 12, b4_y + b4_h - 18, 14, color=HexColor("#f59e0b"))
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#f59e0b"))
    c.drawString(bx_x + 32, b4_y + b4_h - 14, "4. RELAIS GSM MOBILE (SmsManager Android)")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(HexColor("#cbd5e1"))
    c.drawString(bx_x + 16, b4_y + 21, "• Émission du SMS natif vers le numéro du proche prioritaire")
    c.drawString(bx_x + 16, b4_y + 8, "• Escalade automatique vers proche suivant si pas d'ACK (3 min)")

    c.showPage()

    # ==========================================
    # SLIDE 9 : Conclusion & Perspectives
    # ==========================================
    draw_slide_background(c, dark=True)
    draw_header(c, "SYNTHÈSE & PERSPECTIVES D'AVENIR", dark=True)

    draw_modern_panel(c, 50, 45, 420, 390, dark=True, accent_color=PRIMARY_TEAL)
    flag_img = "docs/presentation/flag_finish_fa.png"
    if os.path.exists(flag_img):
        c.drawImage(flag_img, 68, 403, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(92, 405, "CE QUE NOUS AVONS DÉMONTRÉ")

    achievements = [
        ("TinyML Performant", ""),
        ("Alerte rapide", ""),
        ("Chaîne IoT Sécurisée", ""),
    ]
    cur_y = 370
    for lbl, desc in achievements:
        draw_icon_bullet(c, 66, cur_y, TEXT_TEAL)
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(80, cur_y, lbl)
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 48)
        for line in lines:
            c.drawString(80, cur_y, line)
            cur_y -= 13
        cur_y -= 10

    draw_modern_panel(c, 490, 45, 420, 390, dark=True, accent_color=ACCENT_AMBER)
    draw_vector_icon(c, "compass", 508, 403, 18, color=HexColor("#fbbf24"))
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(HexColor("#fbbf24"))
    c.drawString(532, 405, "PERSPECTIVES")

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
        draw_icon_bullet(c, 506, cur_y, HexColor("#fbbf24"))
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(520, cur_y, lbl)
        cur_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 54)
        for line in lines:
            c.drawString(520, cur_y, line)
            cur_y -= 11
        cur_y -= 7

    c.showPage()

    # ==========================================
    # SLIDE 9 : Remerciements & Questions / Réponses (Liens Cliquables & Échanges)
    # ==========================================
    draw_slide_background(c, dark=True)
    draw_header(c, "ÉCHANGE & DISCUSSION", dark=True)

    draw_modern_panel(c, 50, 45, 420, 390, dark=True, accent_color=PRIMARY_TEAL)
    link_img = "docs/presentation/link_lucide.png"
    if os.path.exists(link_img):
        c.drawImage(link_img, 68, 403, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(TEXT_TEAL)
    c.drawString(92, 405, "RESSOURCES DU PROJET & DÉMO EN LIGNE")

    demo_links = [
        ("Site Portfolio & CV", "https://daverck.github.io/serck-david-portfolio", "daverck.github.io/serck-david-portfolio", "docs/presentation/globe_lucide.png"),
        ("Plateforme Web Live", "https://healthkicks.duckdns.org", "healthkicks.duckdns.org", "docs/presentation/globe_lucide.png"),
        ("Studio & Stats du Modèle ML", "https://healthkicks.duckdns.org/dashboard/studio/classes", "healthkicks.duckdns.org/dashboard/studio/classes", "docs/presentation/globe_lucide.png"),
        ("Code Source & Spécifications", "https://github.com/daverck/health-kicks-ecosystem", "github.com/daverck/health-kicks-ecosystem", "docs/presentation/github_official.png")
    ]

    cur_y = 365
    for lbl, target_url, display_txt, icon_path in demo_links:
        if os.path.exists(icon_path):
            c.drawImage(icon_path, 64, cur_y - 2, width=12, height=12, preserveAspectRatio=True, mask='auto')
        else:
            draw_icon_bullet(c, 66, cur_y, TEXT_TEAL)
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(82, cur_y, lbl + " :")
        cur_y -= 14
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#38bdf8"))
        c.drawString(82, cur_y, display_txt)
        c.linkURL(target_url, (82, cur_y - 2, 82 + 300, cur_y + 11), thickness=0)
        cur_y -= 14

    draw_modern_panel(c, 490, 45, 420, 390, dark=True, accent_color=ACCENT_AMBER)
    chat_img = "docs/presentation/chat_messages_square.png"
    if os.path.exists(chat_img):
        c.drawImage(chat_img, 508, 403, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(HexColor("#fbbf24"))
    c.drawString(532, 405, "THÈMES TECHNIQUES À APPROFONDIR")

    discussion_items = [
        ("Optimisation FreeRTOS Dual-Core", ""),
        ("Podométrie Nette & Gestion des Reboots", ""),
        ("Boucle MLOps & Mode HITL", ""),
        ("Sécurité Zero Trust & Données de Marche", "")
    ]
    cur_y = 375
    for lbl, desc in discussion_items:
        draw_icon_bullet(c, 506, cur_y, HexColor("#fbbf24"))
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_LIGHT)
        c.drawString(520, cur_y, lbl)
        cur_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_CARD_SUB)
        lines = wrap_text(desc, 54)
        for line in lines:
            c.drawString(520, cur_y, line)
            cur_y -= 11
        cur_y -= 7

    c.showPage()

    # ==========================================
    # SLIDE 10 (ANNEXE / SUPPORT) : Podométrie Différentielle Nette
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "PODOMÉTRIE (SUPPORT / QUESTIONS)")

    # Gauche : Algorithme SQLite & Architecture
    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    footprint_img = "docs/presentation/footprints_lucide.png"
    if os.path.exists(footprint_img):
        c.drawImage(footprint_img, 68, col_y + 390 - 32, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(92, col_y + 390 - 28, "ALGORITHME D'ODOMÉTRIE DIFFÉRENTIELLE")

    podo_items = [
        ("Compteur Monotone Physique", ""),
        ("Calcul Différentiel Mobile", ""),
        ("Résilience aux Redémarrages", ""),
        ("Insensibilité aux Gestes Parasites", ""),
        ("Absence d'horloge RTC matérielle persistante", "")
    ]

    cur_y = col_y + 390 - 55
    for lbl, desc in podo_items:
        draw_icon_bullet(c, 66, cur_y, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(80, cur_y, lbl)
        cur_y -= 13
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(80, cur_y, line)
            cur_y -= 12
        cur_y -= 6

    # Watermark grand format de foulée / trace de pas
    trail_watermark = "docs/presentation/trail_walking_watermark.png"
    if os.path.exists(trail_watermark):
        c.drawImage(trail_watermark, 65, col_y + 20, width=390, height=115, preserveAspectRatio=True, anchor='c', mask='auto')

    # Droite : Graphique Podometre Reel (capture pedometer.png)
    podo_img_path = "health-kicks-frontend/public/images/screenshots/web_showcase_pedometer.webp"
    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
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
    draw_slide_background(c, dark=False)
    draw_header(c, "COÛTS DU PROJET")

    # Gauche : Hardware / Matériel Embarqué
    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "chip", 68, col_y + 390 - 32, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(92, col_y + 390 - 28, "MATÉRIEL EMBARQUÉ & PROTOTYPE")

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
        draw_icon_bullet(c, 66, cur_y, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(80, cur_y, item)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(PRIMARY_TEAL)
        c.drawRightString(450, cur_y, price)
        cur_y -= 13
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 52)
        for line in lines:
            c.drawString(80, cur_y, line)
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
    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
    cloud_img = "docs/presentation/cloud_lucide.png"
    if os.path.exists(cloud_img):
        c.drawImage(cloud_img, 508, col_y + 390 - 32, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(532, col_y + 390 - 28, "INFRASTRUCTURE CLOUD & SERVICES")

    services_costs = [
        ("Cloud AWS (Free Tier & Crédits Gratuits)", "0 EUR / mois", "EC2 t3.micro (750h/m), IoT Core (500k msg), DynamoDB (25 Go), Lambdas STS (1M req/m) entièrement couverts par l'offre gratuite."),
        ("Pipeline CI/CD GitHub Actions", "0 EUR (Free Usage)", ""),
        ("Nom de Domaine Personnalisé Dédié", "~12 EUR / an", "pour l'envoi d'emails"),
        ("Assistance IA & Pair-Programming (Gemini)", "~5.5 EUR / mois", ""),
    ]

    cur_y = col_y + 390 - 75
    for item, price, desc in services_costs:
        draw_icon_bullet(c, 506, cur_y, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(520, cur_y, item)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(ACCENT_BLUE)
        c.drawRightString(890, cur_y, price)
        cur_y -= 14
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_MUTED)
        lines = wrap_text(desc, 50)
        for line in lines:
            c.drawString(520, cur_y, line)
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

    # Illustration pile de pièces de monnaie entre les deux cards (tiers du bas)
    coins_img = "docs/presentation/coins_lucide.png"
    if os.path.exists(coins_img):
        c.drawImage(coins_img, 458, col_y + 55, width=44, height=44, preserveAspectRatio=True, mask='auto')

    c.save()
    print(f"Simplified PDF saved to: {target_filename}")


if __name__ == "__main__":
    build_pdf()
