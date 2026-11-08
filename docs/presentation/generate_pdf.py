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
PRIMARY_BLUE = HexColor("#1d5cf5")   # Brand Primary Blue
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
    """Draws a header"""
    c.saveState()

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
        orig_w, orig_h = 700.0, 700.0
        viewbox = root.attrib.get("viewBox", "")
        if viewbox:
            vb_parts = [float(v) for v in viewbox.split()]
            if len(vb_parts) == 4:
                orig_w, orig_h = vb_parts[2], vb_parts[3]

        scale = target_width / orig_w
        target_height = orig_h * scale

        canv.saveState()
        canv.translate(x_offset, y_offset + target_height)
        canv.scale(scale, -scale)

        for elem in root:
            if not elem.tag.endswith("path"):
                continue
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


def draw_arrow(c, x, y, w, color, label_top="", label_bottom="", reverse=False):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.8)
    c.line(x, y, x + w, y)
    p = c.beginPath()
    if not reverse:
        p.moveTo(x + w, y)
        p.lineTo(x + w - 5.5, y + 4)
        p.lineTo(x + w - 5.5, y - 4)
    else:
        p.moveTo(x, y)
        p.lineTo(x + 5.5, y + 4)
        p.lineTo(x + 5.5, y - 4)
    p.close()
    c.setFillColor(color)
    c.drawPath(p, fill=1, stroke=0)
    if label_top:
        c.setFont("Helvetica-Bold", 7.8)
        c.setFillColor(color)
        c.drawCentredString(x + w / 2, y + 7, label_top)
    if label_bottom:
        c.setFont("Helvetica", 6.8)
        c.setFillColor(TEXT_MUTED)
        c.drawCentredString(x + w / 2, y - 11, label_bottom)
    c.restoreState()


def draw_down_arrow(c, x, y_top, y_bottom, color, label=""):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.8)
    c.line(x, y_top, x, y_bottom)
    p = c.beginPath()
    p.moveTo(x, y_bottom)
    p.lineTo(x - 3.8, y_bottom + 5.5)
    p.lineTo(x + 3.8, y_bottom + 5.5)
    p.close()
    c.setFillColor(color)
    c.drawPath(p, fill=1, stroke=0)
    if label:
        c.setFont("Helvetica-Bold", 7.8)
        c.setFillColor(color)
        c.drawString(x + 8, (y_top + y_bottom) / 2 - 2.5, label)
    c.restoreState()


def draw_demo_badge(c, text, accent_color=ACCENT_AMBER):
    """Draws an appealing, high-visibility demonstration pill badge in the slide header."""
    c.saveState()
    bx = 490
    by = 468
    bw = 420
    bh = 30
    radius = 15

    # Soft outer glow halo
    c.setFillColor(accent_color)
    c.setFillAlpha(0.18)
    c.roundRect(bx - 3, by - 3, bw + 6, bh + 6, radius + 3, fill=1, stroke=0)

    # Rich dark-slate pill body with vibrant colored border
    c.setFillAlpha(1.0)
    c.setFillColor(HexColor("#0f172a"))
    c.setStrokeColor(accent_color)
    c.setLineWidth(2.0)
    c.roundRect(bx, by, bw, bh, radius, fill=1, stroke=1)

    # Solid vibrant play circle on the left
    cx = bx + 18
    cy = by + bh / 2
    c.setFillColor(accent_color)
    c.circle(cx, cy, 10, fill=1, stroke=0)

    # Crisp white play triangle inside circle
    p = c.beginPath()
    p.moveTo(cx - 3.0, cy + 4.8)
    p.lineTo(cx - 3.0, cy - 4.8)
    p.lineTo(cx + 5.2, cy)
    p.close()
    c.setFillColor(HexColor("#ffffff"))
    c.drawPath(p, fill=1, stroke=0)

    # High-contrast bold label
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(HexColor("#ffffff"))
    c.drawCentredString(bx + 15 + bw / 2, by + 10.5, text)
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

    # Consistent bullet typography scale across all slides
    BULLET_TITLE_SIZE = 12.5      # Standalone bullet lists (Slides 3, 4, 8, 10, 11, 12)
    BULLET_DETAIL_TITLE = 11.5    # Detailed bullet lists with sub-text (Slide 6)
    BULLET_DETAIL_SUB = 9.8       # Sub-text for detailed bullet lists (Slide 6)

    # ==========================================
    # SLIDE 1 (COUVERTURE) : Logo & Nom du Projet
    # ==========================================
    draw_slide_background(c, dark=True)

    logo_svg_path = "health-kicks-frontend/public/favicon.svg"
    logo_w = 400
    logo_x = (PAGE_WIDTH - logo_w) / 2
    logo_y = 155
    draw_svg_paths(c, logo_svg_path, logo_x, logo_y, logo_w)

    title_font_size = 56
    c.setFont("Helvetica-Bold", title_font_size)
    w_health = c.stringWidth("Health", "Helvetica-Bold", title_font_size)
    w_kicks = c.stringWidth("Kicks", "Helvetica-Bold", title_font_size)
    total_title_w = w_health + w_kicks
    title_x = (PAGE_WIDTH - total_title_w) / 2
    title_y = 140

    c.setFillColor(TEXT_LIGHT)
    c.drawString(title_x, title_y, "Health")
    c.setFillColor(PRIMARY_BLUE)
    c.drawString(title_x + w_health, title_y, "Kicks")

    c.showPage()

    # ==========================================
    # SLIDE 2 : Parcours Professionnel & Portfolio QR Code
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
    # SLIDE 3 : Genèse & Fonctionnalités (Concept)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "CONCEPT")

    # Badge Démonstration en Direct (Haute Visibilité)
    draw_demo_badge(c, "DÉMONSTRATION 1 : RECONNAISSANCE D'ALLURE EN DIRECT", accent_color=ACCENT_AMBER)

    card_w = 420
    card_h = 260
    card_y = 140

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
        x = 50 + idx * 440
        draw_modern_panel(c, x, card_y, card_w, card_h, dark=False, accent_color=color)

        # Illustration du coureur connecté avec onde télémétrique pour GENÈSE
        if icon_name == "bulb":
            runner_img = "docs/presentation/connected_runner.png"
            if os.path.exists(runner_img):
                c.drawImage(runner_img, x + 16, card_y + 8, width=388, height=142, preserveAspectRatio=True, anchor='c')

        draw_vector_icon(c, icon_name, x + 22, card_y + card_h - 36, 22, color=color)

        c.setFont("Helvetica-Bold", 14.5)
        c.setFillColor(color)
        c.drawString(x + 50, card_y + card_h - 30, title)

        cur_y = card_y + card_h - 70
        for b in items:
            draw_icon_bullet(c, x + 22, cur_y + 1, color)
            c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
            c.setFillColor(TEXT_DARK)
            c.drawString(x + 38, cur_y, b)
            cur_y -= 32

    c.showPage()

    # ==========================================
    # SLIDE 4 : Cœur IoT & Biomécanique (Système Embarqué)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "SCHÉMA ÉLECTRONIQUE")

    # Schéma Électronique Global (Plein écran centré)
    schema_y = 40
    schema_h = 405
    draw_modern_panel(c, 50, schema_y, 860, schema_h, dark=False, accent_color=PRIMARY_TEAL)

    schematic_path = "docs/presentation/circuit_esp32.png"
    if os.path.exists(schematic_path):
        c.drawImage(schematic_path, 60, schema_y + 12, width=840, height=350, preserveAspectRatio=True, anchor='c')

    c.showPage()

    # ==========================================
    # SLIDE 5 : Architecture Globale Logicielle & Système (Agrandie, 4. CLOUD OVH sous 2. MOBILE)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "ARCHITECTURE GLOBALE")

    CLOUD_AWS = HexColor("#0284c7")
    y_top = 445

    # -------------------------------------------------------------
    # 1. EMBARQUÉ : ESP32-S3 (Dual-Core FreeRTOS) - Largeur agrandie à 248 pt
    # -------------------------------------------------------------
    w_shoe = 242
    x_shoe = 34

    # Cœur 0 : Réseau & Système (3 items)
    h_core0 = 104
    y_core0 = y_top - 38 - h_core0  # 303

    # Cœur 1 : Temps Réel & Métier (5 items)
    h_core1 = 152
    y_core1 = y_core0 - 12 - h_core1  # 139

    y_parent_shoe = y_core1 - 12      # 127
    h_parent_shoe = y_top - y_parent_shoe  # 318 pt

    draw_modern_panel(c, x_shoe, y_parent_shoe, w_shoe, h_parent_shoe, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "mcu", x_shoe + 14, y_top - 28, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 38, y_top - 22, "1. EMBARQUÉ (ESP32-S3)")

    # Carte Cœur 0
    draw_card(c, x_shoe + 10, y_core0, w_shoe - 20, h_core0, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 18, y_core0 + h_core0 - 19, "Cœur 0 : Réseau & Système")
    core0_items = [
        "Pile NimBLE GATT",
        "OTA Streaming Service",
        "Power Manager"
    ]
    cur_cy = y_core0 + h_core0 - 42
    for t_it in core0_items:
        draw_icon_bullet(c, x_shoe + 18, cur_cy + 0.5, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 9.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 32, cur_cy, t_it)
        cur_cy -= 22

    # Carte Cœur 1
    draw_card(c, x_shoe + 10, y_core1, w_shoe - 20, h_core1, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_shoe + 18, y_core1 + h_core1 - 19, "Cœur 1 : Temps Réel & Métier")

    core1_all_items = [
        "Bus I2C pour capteurs inertiels",
        "Pilote Haptique PWM",
        "Buffer Circulaire HITL",
        "Inférence TinyML",
        "Task Watchdog (5s)",

    ]
    cur_cy = y_core1 + h_core1 - 42
    for t_it in core1_all_items:
        draw_icon_bullet(c, x_shoe + 18, cur_cy + 0.5, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 9.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_shoe + 32, cur_cy, t_it)
        cur_cy -= 22

    # FLECHE 1 : ESP32-S3 -> Mobile
    draw_arrow(c, 279, 305, 52, PRIMARY_TEAL, "BLE GATT", "LESC Chiffré")

    # -------------------------------------------------------------
    # 2. PASSERELLE MOBILE : Flutter / SQLite (Haut Colonne 2, largeur 216 pt)
    # -------------------------------------------------------------
    w_mob = 214
    x_mob = 334

    # 2.1 Base Locale SQLite (1 item)
    h_sqlite = 56
    y_sqlite = y_top - 36 - h_sqlite  # 353

    # 2.2 Sécurité & Keystore (3 items)
    h_sec = 96
    y_sec = y_sqlite - 8 - h_sec      # 249

    # 2.3 Passerelle Hybride Cloud (2 items)
    h_gw = 76
    y_gw = y_sec - 8 - h_gw          # 165

    y_parent_mob = y_gw - 10          # 155
    h_parent_mob = y_top - y_parent_mob   # 290 pt

    draw_modern_panel(c, x_mob, y_parent_mob, w_mob, h_parent_mob, dark=False, accent_color=ACCENT_BLUE)
    draw_vector_icon(c, "smartphone", x_mob + 14, y_top - 28, 18, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 36, y_top - 22, "2. MOBILE (Flutter / Dart)")

    # Carte Base SQLite
    draw_card(c, x_mob + 10, y_sqlite, w_mob - 20, h_sqlite, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)
    c.setFont("Helvetica-Bold", 9.8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 18, y_sqlite + h_sqlite - 18, "Base Locale SQLite")
    draw_icon_bullet(c, x_mob + 18, y_sqlite + h_sqlite - 39.5, ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 9.2)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_mob + 32, y_sqlite + h_sqlite - 40, "Sandbox OS privée")

    # Carte Sécurité & Keystore
    draw_card(c, x_mob + 10, y_sec, w_mob - 20, h_sec, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)
    c.setFont("Helvetica-Bold", 9.8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 18, y_sec + h_sec - 18, "Sécurité & Keystore")
    mob_sec_items = [
        "Hardware Keystore",
        "Tokens OAuth2 PKCE",
        "Courtier STS"
    ]
    cur_my = y_sec + h_sec - 40
    for t_it in mob_sec_items:
        draw_icon_bullet(c, x_mob + 18, cur_my + 0.5, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 9.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_mob + 32, cur_my, t_it)
        cur_my -= 20

    # Carte Passerelle Hybride Cloud
    draw_card(c, x_mob + 10, y_gw, w_mob - 20, h_gw, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)
    c.setFont("Helvetica-Bold", 9.8)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(x_mob + 18, y_gw + h_gw - 18, "Passerelle Hybride Cloud")
    mob_gw_items = [
        "MQTT WSS SigV4",
        "API REST HTTPS"
    ]
    cur_my = y_gw + h_gw - 40
    for t_it in mob_gw_items:
        draw_icon_bullet(c, x_mob + 18, cur_my + 0.5, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 9.2)
        c.setFillColor(TEXT_DARK)
        c.drawString(x_mob + 32, cur_my, t_it)
        cur_my -= 20

    # -------------------------------------------------------------
    # 4. CLOUD OVH : Serveur Mail Dédié (Positionné sous 2. MOBILE)
    # -------------------------------------------------------------
    w_ovh = 214
    x_ovh = 334
    y_ovh = 42
    h_ovh = 96
    draw_modern_panel(c, x_ovh, y_ovh, w_ovh, h_ovh, dark=False, accent_color=ACCENT_AMBER)
    cloud_img = "docs/presentation/cloud_lucide.png"
    if os.path.exists(cloud_img):
        c.drawImage(cloud_img, x_ovh + 14, y_ovh + h_ovh - 26, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_ovh + 36, y_ovh + h_ovh - 21, "4. CLOUD OVH")

    # Card Serveur Mail
    h_mail = 52
    draw_card(c, x_ovh + 10, y_ovh + 10, w_ovh - 20, h_mail, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)
    mail_img = "docs/presentation/mail_lucide.png"
    if os.path.exists(mail_img):
        c.drawImage(mail_img, x_ovh + 18, y_ovh + 10 + 17, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_ovh + 42, y_ovh + 10 + 21, "Serveur Mail")

    # FLECHE 2 : Mobile -> Cloud AWS
    draw_arrow(c, 551, 305, 68, ACCENT_BLUE, "MQTT WSS / REST", "SigV4 + HTTPS")

    # FLECHE 3 : Cloud AWS -> Cloud OVH (vers la gauche en bas)
    draw_arrow(c, 551, 90, 68, ACCENT_AMBER, "SMTP", "TLS 587", reverse=True)

    # -------------------------------------------------------------
    # 3. CLOUD AWS : Ingestion, EC2 & Bases (Largeur agrandie à 300 pt)
    # -------------------------------------------------------------
    w_cloud = 300
    x_cloud = 622
    w_sub = 134

    # 3.1 Haut : Ingestion IoT Core + AWS Lambda
    h_ingest = 86
    y_ingest = y_top - 36 - h_ingest  # 323

    # 3.2 Milieu : Serveur EC2 Docker
    h_ec2 = 112
    y_ec2 = y_ingest - 10 - h_ec2     # 201

    # 3.3 Bas : Bases de données & Stockage S3
    h_db = 139
    y_db = y_ec2 - 10 - h_db          # 52

    y_parent_cloud = 42
    h_parent_cloud = y_top - y_parent_cloud  # 403 pt

    draw_modern_panel(c, x_cloud, y_parent_cloud, w_cloud, h_parent_cloud, dark=False, accent_color=CLOUD_AWS)
    draw_vector_icon(c, "cloud_aws", x_cloud + 14, y_top - 28, 18, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 38, y_top - 22, "3. CLOUD AWS")

    # Conteneur Ingestion
    draw_card(c, x_cloud + 8, y_ingest, w_cloud - 16, h_ingest, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)

    # Mini-carte gauche : AWS IoT Core (Broker MQTT WSS)
    h_sub_ingest = 74
    draw_card(c, x_cloud + 13, y_ingest + 6, w_sub, h_sub_ingest, CARD_BG, HexColor("#bae6fd"), border_width=1, radius=5)
    draw_vector_icon(c, "iot_core", x_cloud + 18, y_ingest + 6 + h_sub_ingest - 18, 13, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 35, y_ingest + 6 + h_sub_ingest - 15, "AWS IoT Core")
    draw_icon_bullet(c, x_cloud + 18, y_ingest + 6 + h_sub_ingest - 34, CLOUD_AWS)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 30, y_ingest + 6 + h_sub_ingest - 34, "Broker MQTT WSS")
    draw_icon_bullet(c, x_cloud + 18, y_ingest + 6 + h_sub_ingest - 52, CLOUD_AWS)
    c.drawString(x_cloud + 30, y_ingest + 6 + h_sub_ingest - 52, "Règles IoT SQL")

    # Mini-carte droite : AWS Lambda (Ingestion & Présence)
    draw_card(c, x_cloud + 153, y_ingest + 6, w_sub, h_sub_ingest, CARD_BG, HexColor("#fde68a"), border_width=1, radius=5)
    draw_vector_icon(c, "lambda", x_cloud + 158, y_ingest + 6 + h_sub_ingest - 18, 13, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 175, y_ingest + 6 + h_sub_ingest - 15, "AWS Lambda")
    draw_icon_bullet(c, x_cloud + 158, y_ingest + 6 + h_sub_ingest - 34, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 170, y_ingest + 6 + h_sub_ingest - 34, "Ingestion télémétrie")
    draw_icon_bullet(c, x_cloud + 158, y_ingest + 6 + h_sub_ingest - 52, ACCENT_AMBER)
    c.drawString(x_cloud + 170, y_ingest + 6 + h_sub_ingest - 52, "Présence & Statut")

    # Conteneur EC2 Docker
    draw_card(c, x_cloud + 8, y_ec2, w_cloud - 16, h_ec2, CARD_BG, HexColor("#cbd5e1"), border_width=1, radius=6)
    draw_vector_icon(c, "server", x_cloud + 14, y_ec2 + h_ec2 - 18, 13, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 9.2)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 32, y_ec2 + h_ec2 - 15, "Serveur EC2")
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 14, y_ec2 + h_ec2 - 29, "Nginx Reverse Proxy SSL")

    # Backend
    h_sub_ec2 = 70
    draw_card(c, x_cloud + 13, y_ec2 + 6, w_sub, h_sub_ec2, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=5)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 18, y_ec2 + 6 + h_sub_ec2 - 16, "Backend FastAPI")
    draw_icon_bullet(c, x_cloud + 18, y_ec2 + 6 + h_sub_ec2 - 34, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 30, y_ec2 + 6 + h_sub_ec2 - 34, "API REST OpenAPI")
    draw_icon_bullet(c, x_cloud + 18, y_ec2 + 6 + h_sub_ec2 - 52, PRIMARY_TEAL)
    c.drawString(x_cloud + 30, y_ec2 + 6 + h_sub_ec2 - 52, "Courtier STS (15 min)")

    # Frontend
    draw_card(c, x_cloud + 153, y_ec2 + 6, w_sub, h_sub_ec2, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=5)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 158, y_ec2 + 6 + h_sub_ec2 - 16, "Frontend Angular 22")
    draw_icon_bullet(c, x_cloud + 158, y_ec2 + 6 + h_sub_ec2 - 34, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 170, y_ec2 + 6 + h_sub_ec2 - 34, "Interface Signals")

    # Conteneur Bases de données & Stockage S3
    draw_card(c, x_cloud + 8, y_db, w_cloud - 16, h_db, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=0.9, radius=6)

    # Aurora PG
    h_sub_db = 60
    y_row1_db = y_db + 72
    draw_card(c, x_cloud + 13, y_row1_db, w_sub, h_sub_db, CARD_BG, HexColor("#a7f3d0"), border_width=1, radius=5)
    draw_vector_icon(c, "database", x_cloud + 18, y_row1_db + h_sub_db - 18, 13, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(x_cloud + 35, y_row1_db + h_sub_db - 15, "PostgreSQL 16")
    draw_icon_bullet(c, x_cloud + 18, y_row1_db + h_sub_db - 36, PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 30, y_row1_db + h_sub_db - 36, "Migrations Alembic")

    # DynamoDB
    draw_card(c, x_cloud + 153, y_row1_db, w_sub, h_sub_db, CARD_BG, HexColor("#fde68a"), border_width=1, radius=5)
    draw_vector_icon(c, "database_dynamo", x_cloud + 158, y_row1_db + h_sub_db - 18, 13, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(x_cloud + 174, y_row1_db + h_sub_db - 15, "Amazon DynamoDB")
    draw_icon_bullet(c, x_cloud + 158, y_row1_db + h_sub_db - 36, ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 170, y_row1_db + h_sub_db - 36, "Séries NoSQL + Rate limiting")

    # Amazon S3 (Stockage Firmware OTA - half width w_sub matching other sub-cards)
    y_row2_db = y_db + 6
    draw_card(c, x_cloud + 13, y_row2_db, w_sub, h_sub_db, CARD_BG, HexColor("#bae6fd"), border_width=1, radius=5)
    draw_vector_icon(c, "s3_bucket", x_cloud + 18, y_row2_db + h_sub_db - 18, 13, color=CLOUD_AWS)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(CLOUD_AWS)
    c.drawString(x_cloud + 35, y_row2_db + h_sub_db - 15, "Amazon S3")
    draw_icon_bullet(c, x_cloud + 18, y_row2_db + h_sub_db - 36, CLOUD_AWS)
    c.setFont("Helvetica-Bold", 8.0)
    c.setFillColor(TEXT_DARK)
    c.drawString(x_cloud + 30, y_row2_db + h_sub_db - 36, "Firmwares OTA (.bin)")

    c.showPage()

    # ==========================================
    # SLIDE 6 : Edge Machine Learning & Détail des Features (Grille 2x2)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "INTELLIGENCE ARTIFICIELLE EMBARQUÉE")

    card_w = 420
    row_top_y = 248
    row_top_h = 194
    row_bot_y = 40
    row_bot_h = 194

    # 1. Haut-Gauche : RÉFÉRENTIEL BIOMÉCANIQUE ISB
    draw_modern_panel(c, 50, row_top_y, card_w, row_top_h, dark=False, accent_color=ACCENT_BLUE)
    ruler_img = "docs/presentation/ruler_tabler.png"
    if os.path.exists(ruler_img):
        c.drawImage(ruler_img, 66, row_top_y + row_top_h - 29, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(88, row_top_y + row_top_h - 24, "RÉFÉRENTIEL BIOMÉCANIQUE ISB")

    axes_img_path = "docs/presentation/shoe_isb_axes.png"
    if os.path.exists(axes_img_path):
        c.drawImage(axes_img_path, 56, row_top_y + 6, width=408, height=154, preserveAspectRatio=True, anchor='c')

    # 2. Haut-Droite : TRAITEMENT DU SIGNAL
    draw_modern_panel(c, 490, row_top_y, card_w, row_top_h, dark=False, accent_color=ACCENT_AMBER)
    draw_vector_icon(c, "features", 506, row_top_y + row_top_h - 29, 18, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(528, row_top_y + row_top_h - 24, "TRAITEMENT DU SIGNAL")

    dsp_items = [
        "Invariance par Rotation",
        "Calibration du Zéro-G",
        "Fenêtrage Glissant de 3.0s"
    ]
    cur_y = row_top_y + row_top_h - 58
    for lbl in dsp_items:
        draw_icon_bullet(c, 506, cur_y + 1, ACCENT_AMBER)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(522, cur_y, lbl)
        cur_y -= 32

    # 3. Bas-Gauche : 28 FEATURES
    draw_modern_panel(c, 50, row_bot_y, card_w, row_bot_h, dark=False, accent_color=ACCENT_BLUE)
    draw_vector_icon(c, "features", 66, row_bot_y + row_bot_h - 29, 18, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(88, row_bot_y + row_bot_h - 24, "28 FEATURES")

    feat_points = [
        "1. Intensité Globale (Invariante 3D)",
        "2. Rupture & Amplitude Dynamique",
        "3. Dispersion & Posture (6 Axes)",
        "4. Directionnalité & Asymétrie",
        "5. Stabilité Post-Impact"
    ]

    cur_y = row_bot_y + row_bot_h - 56
    for lbl in feat_points:
        draw_icon_bullet(c, 66, cur_y + 1, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(82, cur_y, lbl)
        cur_y -= 28

    # 4. Bas-Droite : CHOIX DU MODÈLE D'INFÉRENCE
    draw_modern_panel(c, 490, row_bot_y, card_w, row_bot_h, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "forest", 506, row_bot_y + row_bot_h - 29, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(528, row_bot_y + row_bot_h - 24, "CHOIX DU MODÈLE D'INFÉRENCE")

    model_points = [
        "Sélection parmi les modèles m2cgen",
        "Random Forest (80 arbres)",
        "vs Deep Learning"
    ]

    cur_y = row_bot_y + row_bot_h - 56
    for lbl in model_points:
        draw_icon_bullet(c, 506, cur_y + 1, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(522, cur_y, lbl)
        cur_y -= 28

    c.showPage()

    # ==========================================
    # SLIDE 7 : Performances Mesurées & Graphique ML
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "VALIDATION & CONTRÔLE")

    # Gauche : Graphique des performances ML réel (capture web Studio cliquable)
    col_y = 45
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
    # SLIDE 8 : MLOps Pipeline (Schéma) & Mode HITL
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "ENTRAÎNEMENT")

    # Badge Démonstration en Direct (Haute Visibilité)
    draw_demo_badge(c, "DÉMONSTRATION 2 : STUDIO WEB & REQUALIFICATION HITL", accent_color=PRIMARY_TEAL)

    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
    draw_vector_icon(c, "pipeline", 68, col_y + 390 - 32, 18, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(92, col_y + 390 - 28, "MLOps")

    # Schéma Visuel du Pipeline MLOps (5 étapes connectées)
    mlops_schema_steps = [
        ("1. Capture Inertielle (ESP32-S3)", "Flux IMU 6 axes (50 Hz) transmis via BLE GATT", "mcu", PRIMARY_TEAL, HexColor("#f0fdfa"), HexColor("#99f6e4")),
        ("2. Qualification Studio (Mobile & Web)", "Labellisation terrain & validation visuelle des séries", "smartphone", ACCENT_BLUE, HexColor("#eff6ff"), HexColor("#bfdbfe")),
        ("3. Script Python d'Entraînement", "Extraction des 28 features & Random Forest (Scikit-Learn)", "forest", HexColor("#7c3aed"), HexColor("#f5f3ff"), HexColor("#ddd6fe")),
        ("4. Transpilation C Pur (m2cgen)", "Génération d'arbres statiques C++ sans runtime", "chip", ACCENT_AMBER, HexColor("#fffbeb"), HexColor("#fde68a")),
        ("5. Injection Firmware Sans Recompilation", "Déploiement OTA du modèle sur le capteur", "cloud_aws", HexColor("#0284c7"), HexColor("#f0f9ff"), HexColor("#bae6fd")),
    ]

    step_x = 68
    step_w = 384
    step_h = 48
    step_gap = 18
    cur_step_y = col_y + 390 - 52 - step_h

    for idx, (st_title, st_sub, st_icon, st_col, st_bg, st_border) in enumerate(mlops_schema_steps):
        draw_card(c, step_x, cur_step_y, step_w, step_h, st_bg, st_border, border_width=1.2, radius=6)
        # Icon badge on the left
        draw_card(c, step_x + 10, cur_step_y + 8, 32, 32, HexColor("#ffffff"), st_border, border_width=1.0, radius=6)
        draw_vector_icon(c, st_icon, step_x + 17, cur_step_y + 15, 18, color=st_col)

        c.setFont("Helvetica-Bold", 10.2)
        c.setFillColor(st_col)
        c.drawString(step_x + 50, cur_step_y + 28, st_title)

        c.setFont("Helvetica", 9.0)
        c.setFillColor(TEXT_DARK)
        c.drawString(step_x + 50, cur_step_y + 12, st_sub)

        if idx < len(mlops_schema_steps) - 1:
            arrow_top = cur_step_y
            arrow_bot = cur_step_y - step_gap
            draw_down_arrow(c, step_x + step_w / 2, arrow_top, arrow_bot, st_col)

        cur_step_y -= (step_h + step_gap)

    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "hitl", 508, col_y + 390 - 32, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(532, col_y + 390 - 28, "MODE HITL (Human-in-the-Loop)")

    hitl_items = [
        ("Buffer Circulaire", ""),
        ("Requalification/Confirmation", "")
    ]

    cur_y = col_y + 390 - 65
    for lbl, desc in hitl_items:
        draw_icon_bullet(c, 506, cur_y + 1, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(522, cur_y, lbl)
        cur_y -= 32

    # Schéma Visuel de la Fenêtre Temporelle du Buffer Circulaire (Moitié inférieure de la carte HITL)
    c.saveState()
    # Conteneur interne doux
    draw_card(c, 506, 60, 388, 255, HexColor("#f8fafc"), HexColor("#cbd5e1"), border_width=1.0, radius=8)
    c.setFont("Helvetica-Bold", 9.8)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(700, 297, "FENÊTRE TEMPORELLE DU BUFFER CIRCULAIRE (3.0 s)")

    # 1. Anneau du Buffer Circulaire RAM (Gauche)
    ring_cx = 595
    ring_cy = 205
    ring_r_out = 54
    ring_r_in = 34

    # Fond de l'anneau (segments mémoire en rotation continue)
    c.setStrokeColor(HexColor("#cbd5e1"))
    c.setLineWidth(16)
    c.circle(ring_cx, ring_cy, (ring_r_out + ring_r_in) / 2, stroke=1, fill=0)

    # Arc Pré-Événement (Bleu : T - 1.5s à T)
    p_pre = c.beginPath()
    p_pre.arc(ring_cx - 44, ring_cy - 44, ring_cx + 44, ring_cy + 44, startAng=100, extent=110)
    c.setStrokeColor(ACCENT_BLUE)
    c.setLineWidth(16)
    c.drawPath(p_pre, stroke=1, fill=0)

    # Arc Instant T / Impact (Ambre/Rouge : Pic d'événement)
    p_imp = c.beginPath()
    p_imp.arc(ring_cx - 44, ring_cy - 44, ring_cx + 44, ring_cy + 44, startAng=55, extent=45)
    c.setStrokeColor(ACCENT_AMBER)
    c.setLineWidth(18)
    c.drawPath(p_imp, stroke=1, fill=0)

    # Arc Post-Événement (Teal : T à T + 1.5s)
    p_post = c.beginPath()
    p_post.arc(ring_cx - 44, ring_cy - 44, ring_cx + 44, ring_cy + 44, startAng=-55, extent=110)
    c.setStrokeColor(PRIMARY_TEAL)
    c.setLineWidth(16)
    c.drawPath(p_post, stroke=1, fill=0)

    # Séparateurs de cellules mémoire sur l'anneau
    c.setStrokeColor(HexColor("#ffffff"))
    c.setLineWidth(1.2)
    for deg in range(0, 360, 20):
        rad = math.radians(deg)
        x1 = ring_cx + ring_r_in * math.cos(rad)
        y1 = ring_cy + ring_r_in * math.sin(rad)
        x2 = ring_cx + ring_r_out * math.cos(rad)
        y2 = ring_cy + ring_r_out * math.sin(rad)
        c.line(x1, y1, x2, y2)

    # Centre de l'anneau
    c.setFillColor(HexColor("#ffffff"))
    c.setStrokeColor(HexColor("#cbd5e1"))
    c.setLineWidth(1.0)
    c.circle(ring_cx, ring_cy, ring_r_in - 1, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(ring_cx, ring_cy + 6, "RAM PSRAM")
    c.setFont("Helvetica-Bold", 7.8)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(ring_cx, ring_cy - 6, "FIFO 19 Hz")
    c.setFont("Helvetica", 7.2)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(ring_cx, ring_cy - 17, "57 échant.")

    # Légende sous l'anneau (Pré / Instant T / Post)
    leg_y = 132
    # Pré-événement
    c.setFillColor(ACCENT_BLUE)
    c.roundRect(516, leg_y, 8, 8, 2, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 7.8)
    c.setFillColor(TEXT_DARK)
    c.drawString(528, leg_y + 1, "Pré-événement (-1.5s)")

    # Instant T
    c.setFillColor(ACCENT_AMBER)
    c.roundRect(516, leg_y - 15, 8, 8, 2, stroke=0, fill=1)
    c.drawString(528, leg_y - 14, "Instant T (Mouvement / Choc)")

    # Post-événement
    c.setFillColor(PRIMARY_TEAL)
    c.roundRect(516, leg_y - 30, 8, 8, 2, stroke=0, fill=1)
    c.drawString(528, leg_y - 29, "Post-événement (+1.5s)")

    # 2. Flèche Fast Burst BLE vers Smartphone / Studio (Droite)
    draw_arrow(c, 656, 205, 62, PRIMARY_TEAL, "Fast Burst", "BLE GATT")

    # 3. Carte Réception Smartphone & Studio (Droite)
    rx_x = 724
    rx_y = 152
    rx_w = 156
    rx_h = 106
    draw_card(c, rx_x, rx_y, rx_w, rx_h, HexColor("#ffffff"), HexColor("#99f6e4"), border_width=1.2, radius=6)
    draw_card(c, rx_x + 10, rx_y + rx_h - 36, 26, 26, HexColor("#f0fdfa"), HexColor("#99f6e4"), border_width=1.0, radius=5)
    draw_vector_icon(c, "smartphone", rx_x + 15, rx_y + rx_h - 31, 16, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 9.0)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(rx_x + 42, rx_y + rx_h - 21, "Mobile & Studio")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(TEXT_MUTED)
    c.drawString(rx_x + 42, rx_y + rx_h - 32, "Trame 6 axes complète")

    # Mini-graphe d'onde capturée dans la carte Mobile & Studio
    wave_box_x = rx_x + 10
    wave_box_y = rx_y + 10
    wave_box_w = rx_w - 20
    wave_box_h = 54
    draw_card(c, wave_box_x, wave_box_y, wave_box_w, wave_box_h, HexColor("#f8fafc"), HexColor("#e2e8f0"), border_width=0.8, radius=4)

    # Zones colorées Pré / Choc / Post dans le mini-graphe
    w_third = wave_box_w / 3.0
    # Zone T (Choc au milieu)
    c.setFillColor(HexColor("#fef3c7"))
    c.rect(wave_box_x + w_third, wave_box_y + 2, w_third, wave_box_h - 4, stroke=0, fill=1)

    # Courbe de signal IMU synthétique (Pré calme -> Pic T -> Post stabilisation)
    pts_wave = [
        (wave_box_x + 6, wave_box_y + 24),
        (wave_box_x + 18, wave_box_y + 27),
        (wave_box_x + 30, wave_box_y + 22),
        (wave_box_x + 44, wave_box_y + 25),
        (wave_box_x + 54, wave_box_y + 12),
        (wave_box_x + 64, wave_box_y + 48),
        (wave_box_x + 74, wave_box_y + 8),
        (wave_box_x + 84, wave_box_y + 38),
        (wave_box_x + 94, wave_box_y + 20),
        (wave_box_x + 108, wave_box_y + 22),
        (wave_box_x + 120, wave_box_y + 21),
        (wave_box_x + 130, wave_box_y + 22),
    ]
    p_w = c.beginPath()
    p_w.moveTo(pts_wave[0][0], pts_wave[0][1])
    for px, py in pts_wave[1:]:
        p_w.lineTo(px, py)
    c.setStrokeColor(PRIMARY_TEAL)
    c.setLineWidth(1.6)
    c.drawPath(p_w, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 6.8)
    c.setFillColor(ACCENT_BLUE)
    c.drawCentredString(wave_box_x + w_third / 2, wave_box_y + 4, "Pré")
    c.setFillColor(ACCENT_AMBER)
    c.drawCentredString(wave_box_x + w_third * 1.5, wave_box_y + 4, "Instant T")
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(wave_box_x + w_third * 2.5, wave_box_y + 4, "Post")

    # Bandeau bas : Action de requalification
    draw_card(c, 668, 72, 212, 24, HexColor("#f0fdfa"), HexColor("#99f6e4"), border_width=0.9, radius=5)
    c.setFont("Helvetica-Bold", 8.2)
    c.setFillColor(PRIMARY_TEAL)
    c.drawCentredString(774, 81, "✓ Validation ou Requalification 1-clic")
    c.restoreState()

    c.showPage()

    # ==========================================
    # SLIDE 9 : Détection de Chute & Chaîne d'Urgence
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "DÉTECTION DE CHUTE")

    # Badge Démonstration en Direct (Haute Visibilité)
    draw_demo_badge(c, "DÉMONSTRATION 3 : SIMULATION D'UNE CHUTE EN DIRECT", accent_color=ACCENT_AMBER)

    card_l_x = 45
    card_l_w = 345

    # Illustration de chute moderne centrée verticalement avec la carte de droite (centre Y = 240)
    fall_img_path = "docs/presentation/fall_illustration.png"
    if os.path.exists(fall_img_path):
        c.drawImage(fall_img_path, 42, 110, width=350, height=260, preserveAspectRatio=True, anchor='c', mask='auto')

    # Droite : Schéma Graphique Vectoriel aligné sur le style du MLOps Pipeline (Slide 8), sans titre
    x_chain = 405
    w_chain = 510
    h_chain = 390
    draw_modern_panel(c, x_chain, col_y, w_chain, h_chain, dark=False, accent_color=PRIMARY_TEAL)

    bx_x = x_chain + 18
    bx_w = w_chain - 36
    x_center = x_chain + w_chain / 2

    # 0. Événement Déclencheur Choc & Immobilité
    b0_w = 340
    b0_h = 38
    b0_x = x_chain + (w_chain - b0_w) / 2
    b0_y = 382
    draw_card(c, b0_x, b0_y, b0_w, b0_h, HexColor("#fef2f2"), HexColor("#fca5a5"), border_width=1.2, radius=6)
    draw_card(c, b0_x + 10, b0_y + 5, 28, 28, HexColor("#ffffff"), HexColor("#fca5a5"), border_width=1.0, radius=6)
    draw_vector_icon(c, "impact", b0_x + 16, b0_y + 11, 16, color=HexColor("#dc2626"))
    c.setFont("Helvetica-Bold", 10.2)
    c.setFillColor(HexColor("#dc2626"))
    c.drawCentredString(b0_x + b0_w / 2 + 12, b0_y + 14, "CHUTE DÉTECTÉE")

    # Flèche 0 -> 1
    draw_down_arrow(c, x_center, 382, 364, HexColor("#dc2626"))

    # 1. Alerte Locale Immédiate (Capteur ESP32-S3)
    b1_y = 308
    b1_h = 56
    draw_card(c, bx_x, b1_y, bx_w, b1_h, HexColor("#f0fdfa"), HexColor("#99f6e4"), border_width=1.2, radius=6)
    draw_card(c, bx_x + 10, b1_y + 12, 32, 32, HexColor("#ffffff"), HexColor("#99f6e4"), border_width=1.0, radius=6)
    draw_vector_icon(c, "alert", bx_x + 17, b1_y + 19, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 10.0)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(bx_x + 50, b1_y + 39, "1. ALERTE LOCALE IMMÉDIATE (CAPTEUR ESP32-S3)")
    c.setFont("Helvetica", 8.8)
    c.setFillColor(TEXT_DARK)
    c.drawString(bx_x + 50, b1_y + 24, "• Vibreur actif & Cooldown anti-rebond")
    c.drawString(bx_x + 50, b1_y + 10, "• Émission trame BLE GATT prioritaire")

    # Flèche 1 -> 2
    draw_down_arrow(c, x_center, 308, 290, PRIMARY_TEAL, "BLE GATT")

    # 2. Passerelle Mobile (Flutter)
    b2_y = 222
    b2_h = 68
    draw_card(c, bx_x, b2_y, bx_w, b2_h, HexColor("#eff6ff"), HexColor("#bfdbfe"), border_width=1.2, radius=6)
    draw_card(c, bx_x + 10, b2_y + 18, 32, 32, HexColor("#ffffff"), HexColor("#bfdbfe"), border_width=1.0, radius=6)
    draw_vector_icon(c, "phone_alert", bx_x + 17, b2_y + 25, 18, color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 10.0)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(bx_x + 50, b2_y + 51, "2. PASSERELLE MOBILE (FLUTTER / DART)")
    c.setFont("Helvetica-Bold", 8.6)
    c.setFillColor(HexColor("#047857"))
    c.drawString(bx_x + 50, b2_y + 37, "• Si Relèvement ou clic 'Je vais bien' :")
    c.drawString(bx_x + 60, b2_y + 24, "==> ANNULATION IMMÉDIATE (Aucun message émis au Cloud)")
    c.setFont("Helvetica", 8.6)
    c.setFillColor(TEXT_DARK)
    c.drawString(bx_x + 50, b2_y + 9, "• Alerte sonore stridente & écran rouge (délai 60s) + Coordonnées GPS")

    # Flèche 2 -> 3
    draw_down_arrow(c, x_center, 222, 204, ACCENT_BLUE, "60s écoulées sans annulation")

    # 3. Backend FastAPI (Orchestrateur de Secours)
    b3_y = 136
    b3_h = 68
    draw_card(c, bx_x, b3_y, bx_w, b3_h, HexColor("#f5f3ff"), HexColor("#ddd6fe"), border_width=1.2, radius=6)
    draw_card(c, bx_x + 10, b3_y + 18, 32, 32, HexColor("#ffffff"), HexColor("#ddd6fe"), border_width=1.0, radius=6)
    draw_vector_icon(c, "server", bx_x + 17, b3_y + 25, 18, color=HexColor("#7c3aed"))
    c.setFont("Helvetica-Bold", 10.0)
    c.setFillColor(HexColor("#7c3aed"))
    c.drawString(bx_x + 50, b3_y + 51, "3. BACKEND FASTAPI (ORCHESTRATEUR DE SECOURS)")
    c.setFont("Helvetica", 8.8)
    c.setFillColor(TEXT_DARK)
    c.drawString(bx_x + 50, b3_y + 37, "• Récupération ordonnée des contacts d'urgence (Priorités 1 à 5)")
    c.drawString(bx_x + 50, b3_y + 23, "• Envoi direct de l'email d'urgence avec lien d'acquittement (ACK)")
    c.drawString(bx_x + 50, b3_y + 9, "• Ordre MQTT Downlink 'SEND_SMS' envoyé au mobile")

    # Flèche 3 -> 4
    draw_down_arrow(c, x_center, 136, 118, HexColor("#7c3aed"), "MQTT Downlink")

    # 4. Relais GSM Mobile (SmsManager Android)
    b4_y = 62
    b4_h = 56
    draw_card(c, bx_x, b4_y, bx_w, b4_h, HexColor("#fffbeb"), HexColor("#fde68a"), border_width=1.2, radius=6)
    draw_card(c, bx_x + 10, b4_y + 12, 32, 32, HexColor("#ffffff"), HexColor("#fde68a"), border_width=1.0, radius=6)
    draw_vector_icon(c, "phone_sms", bx_x + 17, b4_y + 19, 18, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 10.0)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(bx_x + 50, b4_y + 39, "4. RELAIS GSM MOBILE (SmsManager Android)")
    c.setFont("Helvetica", 8.8)
    c.setFillColor(TEXT_DARK)
    c.drawString(bx_x + 50, b4_y + 24, "• Émission du SMS natif vers le numéro du proche prioritaire")
    c.drawString(bx_x + 50, b4_y + 10, "• Escalade automatique vers proche suivant si pas d'ACK (3 min)")

    c.showPage()

    # ==========================================
    # SLIDE 10 : Conclusion & Perspectives (Fond Clair)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "SYNTHÈSE & PERSPECTIVES D'AVENIR", dark=False)

    draw_modern_panel(c, 50, 45, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    flag_img = "docs/presentation/flag_finish_fa.png"
    if os.path.exists(flag_img):
        c.drawImage(flag_img, 68, 403, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(92, 405, "CE QUE NOUS AVONS DÉMONTRÉ")

    achievements = [
        ("TinyML Performant", ""),
        ("Alerte rapide", ""),
        ("Chaîne IoT Sécurisée", ""),
    ]
    cur_y = 370
    for lbl, desc in achievements:
        draw_icon_bullet(c, 66, cur_y + 1, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(82, cur_y, lbl)
        cur_y -= 32

    # Illustration du chemin sinueux vers l'horizon (Moitié inférieure de la carte gauche)
    horizon_img = "docs/presentation/horizon_pathway.png"
    if os.path.exists(horizon_img):
        c.drawImage(horizon_img, 58, 52, width=404, height=235, preserveAspectRatio=True, anchor='c')

        # Pastilles des jalons le long du chemin (du premier plan vers l'horizon)
        milestones = [
            (366, 86, "TinyML", PRIMARY_TEAL, HexColor("#f0fdfa")),
            (148, 152, "Alerte", ACCENT_BLUE, HexColor("#eff6ff")),
            (390, 198, "Sécurité", ACCENT_BLUE, HexColor("#eff6ff")),
            (178, 222, "NB-IoT & Twin", ACCENT_AMBER, HexColor("#fffbeb")),
        ]
        for mx, my, mlbl, mcol, mbg in milestones:
            c.setFont("Helvetica-Bold", 8.2)
            tw = c.stringWidth(mlbl, "Helvetica-Bold", 8.2)
            pw = tw + 14
            ph = 15
            c.saveState()
            c.setFillColor(mbg)
            c.setStrokeColor(mcol)
            c.setLineWidth(1.0)
            c.roundRect(mx - pw / 2, my - ph / 2, pw, ph, 7.5, stroke=1, fill=1)
            c.setFillColor(mcol)
            c.drawCentredString(mx, my - 2.8, mlbl)
            c.restoreState()

    draw_modern_panel(c, 490, 45, 420, 390, dark=False, accent_color=ACCENT_AMBER)
    draw_vector_icon(c, "compass", 508, 403, 18, color=ACCENT_AMBER)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_AMBER)
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
    cur_y = 370
    for lbl, desc in roadmap:
        draw_icon_bullet(c, 506, cur_y + 1, ACCENT_AMBER)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(522, cur_y, lbl)
        cur_y -= 32

    c.showPage()

    # ==========================================
    # SLIDE 11 : Remerciements & Questions / Réponses (Fond Clair)
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "ÉCHANGE & DISCUSSION", dark=False)

    draw_modern_panel(c, 50, 45, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    link_img = "docs/presentation/link_lucide.png"
    if os.path.exists(link_img):
        c.drawImage(link_img, 68, 403, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(92, 405, "RESSOURCES DU PROJET & DÉMO EN LIGNE")

    demo_links = [
        ("Site Portfolio & CV", "https://daverck.github.io/serck-david-portfolio", "daverck.github.io/serck-david-portfolio", "docs/presentation/globe_lucide.png"),
        ("Plateforme Web Live", "https://healthkicks.duckdns.org", "healthkicks.duckdns.org", "docs/presentation/globe_lucide.png"),
        ("Code Source & Spécifications", "https://github.com/daverck/health-kicks-ecosystem", "github.com/daverck/health-kicks-ecosystem", "docs/presentation/github_official.png")
    ]

    cur_y = 365
    for lbl, target_url, display_txt, icon_path in demo_links:
        if os.path.exists(icon_path):
            c.drawImage(icon_path, 64, cur_y - 1, width=14, height=14, preserveAspectRatio=True, mask='auto')
        else:
            draw_icon_bullet(c, 66, cur_y + 1, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(84, cur_y, lbl + " :")
        cur_y -= 17
        c.setFont("Helvetica", 10.5)
        c.setFillColor(ACCENT_BLUE)
        c.drawString(84, cur_y, display_txt)
        c.linkURL(target_url, (84, cur_y - 2, 84 + 320, cur_y + 12), thickness=0)
        cur_y -= 20

    draw_modern_panel(c, 490, 45, 420, 390, dark=False, accent_color=ACCENT_AMBER)
    chat_img = "docs/presentation/chat_messages_square.png"
    if os.path.exists(chat_img):
        c.drawImage(chat_img, 508, 403, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_AMBER)
    c.drawString(532, 405, "THÈMES TECHNIQUES À APPROFONDIR")

    discussion_items = [
        ("Podométrie Nette & Gestion des Reboots", ""),
        ("Sécurité Zero Trust & Données de Marche", ""),
        ("Coûts du projet", ""),
    ]
    cur_y = 370
    for lbl, desc in discussion_items:
        draw_icon_bullet(c, 506, cur_y + 1, ACCENT_AMBER)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(522, cur_y, lbl)
        cur_y -= 32

    # Illustration vectorielle Échange & Questions-Réponses Tech (Bas de la carte de droite)
    qa_img = "docs/presentation/qa_discussion.png"
    if os.path.exists(qa_img):
        c.drawImage(qa_img, 502, 52, width=396, height=235, preserveAspectRatio=True, anchor='c')

    c.showPage()

    # ==========================================
    # SLIDE 12 (ANNEXE / SUPPORT) : Podométrie Différentielle Nette
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "PODOMÉTRIE (SUPPORT / QUESTIONS)")

    # Gauche : Algorithme SQLite & Architecture
    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    footprint_img = "docs/presentation/footprints_lucide.png"
    if os.path.exists(footprint_img):
        c.drawImage(footprint_img, 68, col_y + 390 - 32, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(PRIMARY_TEAL)
    c.drawString(92, col_y + 390 - 28, "ALGORITHME D'ODOMÉTRIE DIFFÉRENTIELLE")

    podo_items = [
        ("Compteur Monotone Physique", ""),
        ("Calcul Différentiel Mobile", ""),
        ("Résilience aux Redémarrages", ""),
        ("Insensibilité aux Gestes Parasites", ""),
        ("Absence d'horloge RTC matérielle persistante", "")
    ]

    cur_y = col_y + 390 - 62
    for lbl, desc in podo_items:
        draw_icon_bullet(c, 66, cur_y + 1, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", BULLET_TITLE_SIZE)
        c.setFillColor(TEXT_DARK)
        c.drawString(82, cur_y, lbl)
        cur_y -= 32

    # Watermark grand format de foulée / trace de pas
    trail_watermark = "docs/presentation/trail_walking_watermark.png"
    if os.path.exists(trail_watermark):
        c.drawImage(trail_watermark, 65, col_y + 20, width=390, height=115, preserveAspectRatio=True, anchor='c', mask='auto')

    # Droite : Graphique Podometre Reel (capture pedometer.png)
    podo_img_path = "health-kicks-frontend/public/images/screenshots/web_showcase_pedometer.webp"
    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(508, col_y + 390 - 28, "RESTITUTION CLINIQUE DES PAS PAR HEURE")

    if os.path.exists(podo_img_path):
        c.drawImage(podo_img_path, 508, 110, width=384, height=230, preserveAspectRatio=True)
        steps_url = "https://healthkicks.duckdns.org/dashboard/steps"
        c.linkURL(steps_url, (508, 110, 508 + 384, 110 + 230), thickness=0)

    c.showPage()

    # ==========================================
    # SLIDE 13 (ANNEXE / SUPPORT) : Coûts du Projet & Frugalité
    # ==========================================
    draw_slide_background(c, dark=False)
    draw_header(c, "COÛTS DU PROJET")

    # Gauche : Hardware / Matériel Embarqué
    draw_modern_panel(c, 50, col_y, 420, 390, dark=False, accent_color=PRIMARY_TEAL)
    draw_vector_icon(c, "chip", 68, col_y + 390 - 32, 18, color=PRIMARY_TEAL)
    c.setFont("Helvetica-Bold", 13.5)
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

    cur_y = col_y + 390 - 65
    for item, price, desc in hw_costs:
        draw_icon_bullet(c, 66, cur_y + 1, PRIMARY_TEAL)
        c.setFont("Helvetica-Bold", 10.8)
        c.setFillColor(TEXT_DARK)
        c.drawString(82, cur_y, item)
        c.setFont("Helvetica-Bold", 10.8)
        c.setFillColor(PRIMARY_TEAL)
        c.drawRightString(452, cur_y, price)
        cur_y -= 15
        if desc:
            c.setFont("Helvetica", 9.2)
            c.setFillColor(TEXT_MUTED)
            lines = wrap_text(desc, 48)
            for line in lines:
                c.drawString(82, cur_y, line)
                cur_y -= 13
        cur_y -= 8

    # Ligne de TOTAL Matériel
    c.setStrokeColor(PRIMARY_TEAL)
    c.setLineWidth(1)
    c.line(68, col_y + 36, 452, col_y + 36)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(68, col_y + 18, "TOTAL")
    c.setFillColor(PRIMARY_TEAL)
    c.drawRightString(452, col_y + 18, "32.50 EUR")

    # Droite : Cloud, Nom de Domaine & Outils
    draw_modern_panel(c, 490, col_y, 420, 390, dark=False, accent_color=ACCENT_BLUE)
    cloud_img = "docs/presentation/cloud_lucide.png"
    if os.path.exists(cloud_img):
        c.drawImage(cloud_img, 508, col_y + 390 - 32, width=18, height=18, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(ACCENT_BLUE)
    c.drawString(532, col_y + 390 - 28, "INFRASTRUCTURE CLOUD & SERVICES")

    services_costs = [
        ("Cloud AWS (Free Tier & Crédits Gratuits)", "0 EUR / mois", "EC2 t3.micro (750h/m), IoT Core (500k msg), DynamoDB (25 Go), Lambdas STS (1M req/m) entièrement couverts par l'offre gratuite."),
        ("Pipeline CI/CD GitHub Actions", "0 EUR (Free Usage)", ""),
        ("Nom de Domaine Personnalisé Dédié", "~12 EUR / an", "pour l'envoi d'emails"),
        ("Assistance IA & Pair-Programming (Gemini)", "~5.5 EUR / mois", ""),
    ]

    cur_y = col_y + 390 - 65
    for item, price, desc in services_costs:
        draw_icon_bullet(c, 506, cur_y + 1, ACCENT_BLUE)
        c.setFont("Helvetica-Bold", 10.8)
        c.setFillColor(TEXT_DARK)
        c.drawString(522, cur_y, item)
        c.setFont("Helvetica-Bold", 10.8)
        c.setFillColor(ACCENT_BLUE)
        c.drawRightString(892, cur_y, price)
        cur_y -= 15
        if desc:
            c.setFont("Helvetica", 9.2)
            c.setFillColor(TEXT_MUTED)
            lines = wrap_text(desc, 46)
            for line in lines:
                c.drawString(522, cur_y, line)
                cur_y -= 13
        cur_y -= 12

    # Ligne de TOTAL Cloud & Services
    c.setStrokeColor(ACCENT_BLUE)
    c.setLineWidth(1)
    c.line(508, col_y + 36, 892, col_y + 36)
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(508, col_y + 18, "TOTAL")
    c.setFillColor(ACCENT_BLUE)
    c.drawRightString(892, col_y + 18, "~6.50 EUR / mois (12 EUR / an + 5.50/m)")

    # Illustration pile de pièces de monnaie entre les deux cards (tiers du bas)
    coins_img = "docs/presentation/coins_lucide.png"
    if os.path.exists(coins_img):
        c.drawImage(coins_img, 458, col_y + 55, width=44, height=44, preserveAspectRatio=True, mask='auto')

    c.save()
    print(f"Simplified PDF saved to: {target_filename}")


if __name__ == "__main__":
    build_pdf()
