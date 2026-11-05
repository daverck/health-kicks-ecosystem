"""Generates an intuitive, high-impact fall detection illustration for HealthKicks Slide 8
depicting a slip/fall dynamic (glissade, perte d'équilibre, choc d'impact).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def generate_fall_illustration(output_path="docs/presentation/fall_illustration.png"):
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Ground line with impact wave
    ax.plot([-2.5, 2.5], [-1.0, -1.0], color='#cbd5e1', lw=2.5, zorder=1)

    # 1. SLIP HAZARD : Classic stylized yellow banana peel 🍌 under foot
    bx = 0.5
    by = -1.0
    # Banana peel curve
    peel_x = [bx - 0.25, bx - 0.1, bx + 0.1, bx + 0.35, bx + 0.45, bx + 0.25, bx + 0.05, bx - 0.15, bx - 0.25]
    peel_y = [by + 0.05, by + 0.22, by + 0.26, by + 0.15, by + 0.02, by + 0.08, by + 0.14, by + 0.08, by + 0.05]
    ax.fill(peel_x, peel_y, color='#facc15', ec='#ca8a04', lw=1.5, zorder=5)
    # Slip lines on ground under banana
    ax.plot([bx - 0.5, bx + 0.7], [by - 0.06, by - 0.06], color='#eab308', lw=2, linestyle='--', zorder=4)

    # 2. FALLING RUNNER (Dynamic slip silhouette tilted back at ~45 deg)
    # Hip / Pelvis at (-0.2, -0.2)
    hip_x, hip_y = -0.2, -0.25

    # Torso (angled backward to left)
    neck_x, neck_y = -0.9, 0.45
    ax.plot([hip_x, neck_x], [hip_y, neck_y], color='#1e293b', lw=6, solid_capstyle='round', zorder=6)

    # Head (circle tilted back)
    head_x, head_y = -1.15, 0.75
    head = plt.Circle((head_x, head_y), 0.22, fc='#1e293b', ec='#0f172a', lw=1.5, zorder=7)
    ax.add_patch(head)

    # Shock exclamation marks above head
    ax.text(head_x - 0.25, head_y + 0.35, "!", color='#ef4444', fontsize=18, fontweight='black', zorder=8)
    ax.text(head_x, head_y + 0.45, "!", color='#f59e0b', fontsize=14, fontweight='black', zorder=8)

    # Left Arm (flailing backward/up for balance)
    ax.plot([neck_x, -1.45, -1.7], [neck_y, 0.55, 0.9], color='#1e293b', lw=4.5, solid_capstyle='round', zorder=6)

    # Right Arm (reaching forward/up)
    ax.plot([neck_x, -0.4, -0.1], [neck_y, 0.8, 1.1], color='#1e293b', lw=4.5, solid_capstyle='round', zorder=6)

    # Left Leg (flying forward/up in the air)
    knee_l_x, knee_l_y = 0.3, 0.3
    foot_l_x, foot_l_y = 0.8, 0.75
    ax.plot([hip_x, knee_l_x, foot_l_x], [hip_y, knee_l_y, foot_l_y], color='#1e293b', lw=5.5, solid_capstyle='round', zorder=6)
    # Left shoe (red accent)
    ax.plot([foot_l_x, foot_l_x + 0.2], [foot_l_y, foot_l_y + 0.05], color='#ef4444', lw=7, solid_capstyle='round', zorder=7)

    # Right Leg (slipping forward on the ground / banana peel)
    knee_r_x, knee_r_y = 0.2, -0.6
    foot_r_x, foot_r_y = 0.55, -0.92
    ax.plot([hip_x, knee_r_x, foot_r_x], [hip_y, knee_r_y, foot_r_y], color='#1e293b', lw=5.5, solid_capstyle='round', zorder=6)
    # Right shoe (with sensor clip on banana peel)
    ax.plot([foot_r_x - 0.05, foot_r_x + 0.25], [foot_r_y, foot_r_y + 0.08], color='#ef4444', lw=7, solid_capstyle='round', zorder=7)

    # Sensor clip blue dot on shoe
    ax.scatter([foot_r_x + 0.08], [foot_r_y + 0.08], color='#38bdf8', s=45, edgecolors='#0f172a', lw=1.5, zorder=8)

    # 3. IMPACT / ACCELERATION BURST
    # Kinetic motion arcs behind the back
    arc1 = patches.Arc((-0.2, -0.2), 2.2, 1.8, angle=0, theta1=110, theta2=160, color='#ef4444', lw=2.5, linestyle=':')
    arc2 = patches.Arc((-0.2, -0.2), 2.6, 2.2, angle=0, theta1=115, theta2=165, color='#f97316', lw=2, linestyle='--')
    ax.add_patch(arc1)
    ax.add_patch(arc2)

    # Impact starburst at the foot slip point
    star_x, star_y = 0.9, -0.85
    burst = patches.RegularPolygon((star_x, star_y), numVertices=8, radius=0.28,
                                   orientation=np.pi/8, fc='#fef08a', ec='#eab308', lw=1.5, zorder=4)
    ax.add_patch(burst)

    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-1.3, 1.25)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', transparent=True, dpi=300)
    plt.close()
    print(f"Fall illustration successfully saved to: {output_path}")


if __name__ == "__main__":
    generate_fall_illustration()
