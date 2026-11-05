"""Generates a high-resolution 3D biomechanical reference illustration for HealthKicks
showing the sneaker with its attached IMU sensor and ISB coordinate system (+X, +Y, +Z).
Conforms strictly to shoe-3d-scene.service.ts ISB definitions.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def generate_shoe_isb_axes(output_path="docs/presentation/shoe_isb_axes.png"):
    fig, ax = plt.subplots(figsize=(6.8, 4.4), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Draw Ground Shadow under sneaker
    shadow_x = np.linspace(-1.7, 2.9, 100)
    shadow_y = -0.32 + 0.05 * np.sin((shadow_x + 1.7) / 4.6 * np.pi)
    ax.fill_between(shadow_x, -0.42, shadow_y, color='#f1f5f9', alpha=0.8, zorder=1)

    # Stylized Athletic Sneaker Profile in Light Blue
    # Sole (cushion midsole + rubber outsole)
    sole_x = [-1.6, -1.5, -0.7, 0.2, 1.3, 2.3, 2.85, 2.7, 2.0, 1.1, 0.1, -0.9, -1.6]
    sole_y = [-0.02, -0.28, -0.28, -0.2, -0.25, -0.2, 0.18, 0.45, 0.2, 0.1, 0.1, 0.18, -0.02]
    ax.fill(sole_x, sole_y, color='#bae6fd', alpha=0.5, zorder=2)
    ax.plot(sole_x, sole_y, color='#38bdf8', lw=2.0, zorder=3)

    # Upper Body of Sneaker (light blue mesh + heel counter)
    upper_x = [-1.5, -1.62, -1.4, -0.9, -0.25, 0.45, 1.35, 2.15, 2.7, 2.1, 1.1, 0.4, -0.3, -0.8, -1.3, -1.5]
    upper_y = [0.18, 0.8, 1.38, 1.3, 0.9, 0.72, 0.55, 0.4, 0.48, 0.7, 1.08, 1.48, 1.68, 1.58, 0.98, 0.18]
    ax.fill(upper_x, upper_y, color='#e0f2fe', alpha=0.6, zorder=2)
    ax.plot(upper_x, upper_y, color='#0ea5e9', lw=2.2, zorder=3)

    # Dynamic Sport Swish Wave on Sneaker Body (sky blue)
    swish_x = [-0.8, -0.1, 0.8, 1.8, 1.2, 0.3, -0.5, -0.8]
    swish_y = [0.65, 0.45, 0.35, 0.42, 0.52, 0.6, 0.75, 0.65]
    ax.fill(swish_x, swish_y, color='#7dd3fc', alpha=0.5, zorder=3)
    ax.plot(swish_x, swish_y, color='#0284c7', lw=1.2, alpha=0.6, zorder=3)

    # Laces Eyelets and Lacing System in clean sky blue
    laces_x = [-0.12, 0.25, 0.62, 1.0]
    laces_y = [1.38, 1.18, 0.98, 0.78]
    ax.plot(laces_x, laces_y, color='#0284c7', lw=2.2, marker='o', markersize=4.5,
            markerfacecolor='#ffffff', markeredgecolor='#0284c7', markeredgewidth=1.6, zorder=4)

    # Coordinate Frame Origin (Center of IMU sensing point on laces)
    ox, oy = 0.45, 1.08

    # 1. Axe Z : Longitudinal / Vertical / Haut (BLEU #2563eb / #1d4ed8)
    # At rest on the ground, the normal force from floor points UP -> accelerometer reads +1.0 g
    dz = 1.45
    ax.annotate("", xy=(ox, oy + dz), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color='#2563eb', lw=3.2, mutation_scale=18),
                zorder=10)
    ax.text(ox + 0.12, oy + dz, "+Z (Vertical / Haut)\n+1.0 g au repos",
            color='#1d4ed8', fontsize=8.8, fontweight='bold', va='center', zorder=11)

    # 2. Axe X : Antéro-postérieur / Avant (ROUGE #ef4444 / #b91c1c)
    # Forward direction of running/walking along shoe long axis
    dx, dy_x = 2.0, -0.3
    ax.annotate("", xy=(ox + dx, oy + dy_x), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color='#ef4444', lw=3.2, mutation_scale=18),
                zorder=10)
    ax.text(ox + dx + 0.08, oy + dy_x - 0.02, "+X (Antéro-postérieur / Avant)\nDirection de la marche",
            color='#b91c1c', fontsize=8.8, fontweight='bold', va='top', zorder=11)

    # 3. Axe Y : Médio-latéral / Droite (VERT #10b981 / #047857)
    # Lateral perspective arrow pointing towards the outer right of foot
    dy_lat_x, dy_lat_y = -1.3, -0.68
    ax.annotate("", xy=(ox + dy_lat_x, oy + dy_lat_y), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color='#10b981', lw=3.2, mutation_scale=18),
                zorder=10)
    ax.text(ox + dy_lat_x - 0.08, oy + dy_lat_y - 0.06, "+Y (Médio-latéral / Droite)\nCôté latéral pied",
            color='#047857', fontsize=8.8, fontweight='bold', ha='right', va='top', zorder=11)

    # Origin point (clean subtle white dot with blue ring)
    ax.scatter([ox], [oy], color='#ffffff', s=45, edgecolors='#0284c7', lw=2.2, zorder=12)

    ax.set_xlim(-2.3, 3.8)
    ax.set_ylim(-1.1, 2.9)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', transparent=True, dpi=300)
    plt.close()
    print(f"ISB axes illustration successfully saved to: {output_path}")


if __name__ == "__main__":
    generate_shoe_isb_axes()
