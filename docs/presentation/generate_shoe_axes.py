"""Generates a high-resolution 3D biomechanical reference illustration for HealthKicks
showing a realistic athletic running shoe with its attached IMU sensor and ISB coordinate system (+X, +Y, +Z).
Conforms strictly to shoe-3d-scene.service.ts ISB definitions.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image


def generate_shoe_isb_axes(
    output_path="docs/presentation/shoe_isb_axes.png",
    base_shoe_path="docs/presentation/realistic_sneaker_base.png",
):
    fig, ax = plt.subplots(figsize=(8.6, 3.4), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.set_aspect('equal')

    if os.path.exists(base_shoe_path):
        img = Image.open(base_shoe_path).convert("RGBA")
        arr = np.array(img)
        # Render the realistic sneaker in true 2:1 athletic proportions
        ax.imshow(arr, extent=[-2.20, 2.30, -0.45, 1.65], zorder=2)

    # Coordinate Frame Origin on the Instep Laces (IMU Sensor Mounting Point)
    ox, oy = 0.28, 0.88

    # Subtle IMU Sensor Clip Module on the laces
    imu_box = patches.FancyBboxPatch(
        (ox - 0.14, oy - 0.09), 0.28, 0.18,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor='#0f172a', edgecolor='#14b8a6', linewidth=2.2, zorder=8
    )
    ax.add_patch(imu_box)

    # 1. Axe Z : Longitudinal / Vertical / Haut (BLEU #2563eb / #1d4ed8)
    dz = 1.42
    ax.annotate("", xy=(ox, oy + dz), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color='#2563eb', lw=4.8, mutation_scale=28),
                zorder=10)
    ax.text(ox + 0.16, oy + dz - 0.16, "+Z (Vertical / Haut)\n+1.0 g au repos",
            color='#1d4ed8', fontsize=19.5, fontweight='bold', va='center',
            bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='none', alpha=0.92),
            zorder=11)

    # 2. Axe X : Antéro-postérieur / Avant (ROUGE #ef4444 / #b91c1c)
    dx, dy_x = 1.95, -0.32
    ax.annotate("", xy=(ox + dx, oy + dy_x), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color='#ef4444', lw=4.8, mutation_scale=28),
                zorder=10)
    ax.text(ox + dx + 0.08, oy + dy_x + 0.12, "+X (Antéro-postérieur)\nDirection de marche",
            color='#b91c1c', fontsize=19.5, fontweight='bold', va='top',
            bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='none', alpha=0.92),
            zorder=11)

    # 3. Axe Y : Médio-latéral / Droite (VERT #10b981 / #047857)
    dy_lat_x, dy_lat_y = -1.35, -0.66
    ax.annotate("", xy=(ox + dy_lat_x, oy + dy_lat_y), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color='#10b981', lw=4.8, mutation_scale=28),
                zorder=10)
    ax.text(ox + dy_lat_x - 0.06, oy + dy_lat_y + 0.02, "+Y (Médio-latéral)\nCôté latéral pied",
            color='#047857', fontsize=19.5, fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='none', alpha=0.92),
            zorder=11)

    # Origin dot on IMU sensor
    ax.scatter([ox], [oy], color='#ffffff', s=85, edgecolors='#14b8a6', lw=3.0, zorder=12)

    ax.set_xlim(-3.85, 4.95)
    ax.set_ylim(-0.62, 2.55)
    ax.axis('off')

    plt.tight_layout(pad=0.01)
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.02, facecolor='#ffffff', transparent=False, dpi=300)
    plt.close()
    print(f"ISB axes illustration successfully saved to: {output_path}")


if __name__ == "__main__":
    generate_shoe_isb_axes()
