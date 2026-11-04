"""Generates a professional vector electronic schematic for HealthKicks ESP32-S3 hardware
using schemdraw (pure Python, vector SVG output, converted to high-DPI PNG).
"""

import re
import schemdraw
import schemdraw.elements as elm
import pymupdf


def build_schematic(svg_path="docs/presentation/circuit_esp32.svg",
                    png_path="docs/presentation/circuit_esp32.png"):
    # Dark theme palette matching Slide 3 & Slide 4
    BG_COLOR = "#1e293b"       # Slate 800 (Card background)
    WIRE_PWR_5V = "#ef4444"    # Red (5V)
    WIRE_PWR_3V3 = "#f87171"   # Coral / Salmon (3.3V)
    WIRE_GND = "#64748b"       # Slate 500
    WIRE_I2C_SDA = "#38bdf8"   # Sky Blue
    WIRE_I2C_SCL = "#0ea5e9"   # Ocean Blue
    WIRE_INT = "#fbbf24"       # Amber
    WIRE_PWM = "#c084fc"       # Purple
    WIRE_UI = "#818cf8"        # Indigo
    TEXT_MAIN = "#f8fafc"      # White / Slate 50

    with schemdraw.Drawing(file=svg_path, show=False) as d:
        d.config(
            bgcolor=BG_COLOR,
            color=TEXT_MAIN,
            font="sans-serif",
            fontsize=8.5,
            unit=2.0,
            lw=1.4
        )

        # =========================================================
        # 1. BATTERY & BOOST CONVERTER (Left Section - Perfectly Aligned at Y=6.3)
        # =========================================================
        # Battery LiPo 1S (starts at 4.3, reaches 6.3)
        bat = d.add(elm.BatteryCell().up().at((0.5, 4.3))
                    .label("Batterie LiPo 1S\n3.7V / 500mAh", loc="left", color=TEXT_MAIN))
        d.add(elm.Ground().at(bat.start).color(WIRE_GND))

        # Switch SW1 (Power ON/OFF at Y=6.3)
        sw1 = d.add(elm.Switch().right().at(bat.end)
                    .label("SW1 (Alim)", loc="top", color=TEXT_MAIN))

        # DC/DC Boost 5V (placed so VIN and 5V OUT are at Y=6.3)
        boost = d.add(elm.Ic(
            pins=[
                elm.IcPin(name="GND", side="left", color=WIRE_GND),
                elm.IcPin(name="VIN", side="left", color=WIRE_PWR_5V),
                elm.IcPin(name="GND", side="right", color=WIRE_GND),
                elm.IcPin(name="5V OUT", side="right", color=WIRE_PWR_5V),
            ],
            size=(2.6, 2.6),
            leadlen=0.5
        ).at((4.5, 4.2)).right().label("DC/DC Boost\n(Step-Up 5.0V)", loc="top", color="#38bdf8"))

        # Connect Switch to Boost VIN (straight horizontal)
        d.add(elm.Line().at(sw1.end).to(boost["VIN"]).color(WIRE_PWR_5V))
        # Boost Grounds
        d.add(elm.Ground().at(boost.inL1).color(WIRE_GND))
        d.add(elm.Ground().at(boost.inR1).color(WIRE_GND))

        # =========================================================
        # 2. ESP32-S3 WROOM-1 (Center MCU)
        # =========================================================
        # Left pins:
        #   0: GPIO 13 (UI Statut & Bouton)
        #   1: GND (Masse)
        #   2: 5V (VIN) (Alim Principale - at Y=6.3)
        # Right pins:
        #   0: GND (Masse)
        #   1: GPIO 7 (PWM Vibreur)
        #   2: GPIO 4 (SDA)
        #   3: GPIO 5 (SCL)
        #   4: GPIO 6 (INT WOM)
        #   5: 3.3V OUT (Alim IMU - at Y=6.3)
        esp = d.add(elm.Ic(
            pins=[
                # Left side
                elm.IcPin(name="GPIO 13", side="left", color=WIRE_UI),
                elm.IcPin(name="GND", side="left", color=WIRE_GND),
                elm.IcPin(name="5V (VIN)", side="left", color=WIRE_PWR_5V),
                # Right side
                elm.IcPin(name="GND", side="right", color=WIRE_GND),
                elm.IcPin(name="GPIO 7 (PWM)", side="right", color=WIRE_PWM),
                elm.IcPin(name="GPIO 4 (SDA)", side="right", color=WIRE_I2C_SDA),
                elm.IcPin(name="GPIO 5 (SCL)", side="right", pinlblsize=0, color=WIRE_I2C_SCL),
                elm.IcPin(name="GPIO 6 (INT)", side="right", color=WIRE_INT),
                elm.IcPin(name="3.3V OUT", side="right", color=WIRE_PWR_3V3),
            ],
            size=(4.8, 5.8),
            leadlen=0.6
        ).at((10.0, 1.0)).right().label("ESP32-S3 WROOM-1\n(Dual-Core 240 MHz / BLE 5.0)", loc="top", color="#14b8a6"))

        # Connect Boost 5V OUT straight to ESP32 5V (VIN) (straight horizontal at Y=6.3)
        d.add(elm.Line().at(boost["5V OUT"]).to(esp["5V (VIN)"])
              .color(WIRE_PWR_5V).label("5.0V", loc="top", color=WIRE_PWR_5V))
        # ESP32 Grounds
        d.add(elm.Ground().at(esp.inL2).color(WIRE_GND))
        d.add(elm.Ground().at(esp.inR1).color(WIRE_GND))

        # =========================================================
        # 3. USER INTERFACE: LED & BUTTON (GPIO 13 - Bottom Left)
        # =========================================================
        r_ui = d.add(elm.Resistor().left().at(esp["GPIO 13"])
                     .label("100Ω", loc="top", color=TEXT_MAIN).color(WIRE_UI))
        led_ui = d.add(elm.LED().left().at(r_ui.end)
                       .label("LED Bleue\n(Statut)", loc="bottom", color="#38bdf8").color("#38bdf8"))
        sw2 = d.add(elm.Switch().left().at(led_ui.end)
                    .label("Bouton SW2", loc="top", color=TEXT_MAIN))
        d.add(elm.Ground().at(sw2.end).color(WIRE_GND))

        # =========================================================
        # 4. IMU MPU-6050 (Top Right - VCC Aligned at Y=6.3)
        # =========================================================
        mpu = d.add(elm.Ic(
            pins=[
                elm.IcPin(name="GND + AD0 (0x68)", side="left", color=WIRE_GND),
                elm.IcPin(name="SDA", side="left", color=WIRE_I2C_SDA),
                elm.IcPin(name="SCL", side="left", color=WIRE_I2C_SCL),
                elm.IcPin(name="INT (WOM)", side="left", color=WIRE_INT),
                elm.IcPin(name="VCC (3.3V)", side="left", color=WIRE_PWR_3V3),
            ],
            size=(4.2, 3.4),
            leadlen=0.6
        ).at((18.6, 3.4)).right().label("Module IMU MPU-6050\n(19 Hz / I2C: 0x68)", loc="top", color="#fbbf24"))

        # Straight bus connections to MPU-6050
        # 3.3V is a straight horizontal line at Y=6.3
        d.add(elm.Line().at(esp["3.3V OUT"]).to(mpu["VCC (3.3V)"]).color(WIRE_PWR_3V3))
        d.add(elm.Line().at(esp["GPIO 6 (INT)"]).to(mpu["INT (WOM)"]).color(WIRE_INT))
        d.add(elm.Line().at(esp["GPIO 5 (SCL)"]).to(mpu["SCL"]).color(WIRE_I2C_SCL))
        d.add(elm.Line().at(esp["GPIO 4 (SDA)"]).to(mpu["SDA"]).color(WIRE_I2C_SDA))
        d.add(elm.Ground().at(mpu["GND + AD0 (0x68)"]).color(WIRE_GND))

        # =========================================================
        # 5. HAPTIC VIBRATOR (Bottom Right)
        # =========================================================
        vib = d.add(elm.Ic(
            pins=[
                elm.IcPin(name="GND (Masse)", side="left", color=WIRE_GND),
                elm.IcPin(name="IN / SIG (Gate)", side="left", color=WIRE_PWM),
                elm.IcPin(name="VCC (+3.3V)", side="left", color=WIRE_PWR_3V3),
            ],
            size=(4.2, 2.2),
            leadlen=0.6
        ).at((18.6, 0.6)).right().label("Module Vibreur Haptique\n(LEDC PWM / Driver MOSFET)", loc="top", color="#c084fc"))

        # Straight PWM connection
        d.add(elm.Line().at(esp["GPIO 7 (PWM)"]).to(vib["IN / SIG (Gate)"]).color(WIRE_PWM))
        d.add(elm.Ground().at(vib["GND (Masse)"]).color(WIRE_GND))

        # Tap 3.3V rail from MPU line down to Vibreur VCC
        p_split = (17.4, mpu["VCC (3.3V)"][1])
        p_vib_vcc = (17.4, vib["VCC (+3.3V)"][1])
        d.add(elm.Dot().at(p_split).color(WIRE_PWR_3V3))
        d.add(elm.Line().at(p_split).to(p_vib_vcc).color(WIRE_PWR_3V3))
        d.add(elm.Line().at(p_vib_vcc).to(vib["VCC (+3.3V)"]).color(WIRE_PWR_3V3))

    print(f"Schematic SVG saved to: {svg_path}")

    # Fix SVG background rect for proper rendering in PyMuPDF / browsers
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    m = re.search(r'viewBox="([^"]+)"', svg_content)
    if m:
        vb = m.group(1).split()
        bg_rect = f'\n<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{BG_COLOR}"/>\n'
        idx = svg_content.find(">")
        if idx != -1:
            svg_content = svg_content[:idx+1] + bg_rect + svg_content[idx+1:]
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

    # Convert SVG to High-Resolution PNG for ReportLab PDF insertion
    try:
        doc = pymupdf.open(svg_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=250)
        pix.save(png_path)
        print(f"Schematic high-DPI PNG saved to: {png_path} (width: {pix.width}, height: {pix.height})")
    except Exception as e:
        print(f"Warning: could not render PNG from SVG: {e}")


if __name__ == "__main__":
    build_schematic()
