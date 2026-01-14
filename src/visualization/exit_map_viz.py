"""
Exit Map Visualization
Visualize exit regions and zone assignments
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.alerts.instruction_generator import InstructionGenerator
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def visualize_exit_regions():
    """Visualize exit region assignments"""
    
    generator = InstructionGenerator()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 11))
    
    # Create grid
    grid = np.zeros((10, 10))
    
    # Color mapping
    region_colors = {
        'North': 1,
        'South': 2,
        'East': 3,
        'West': 4,
        'Central': 5
    }
    
    colors_hex = {
        'North': '#FFB6C1',    # Light pink
        'South': '#ADD8E6',    # Light blue
        'East': '#90EE90',     # Light green
        'West': '#FFD700',     # Gold
        'Central': '#DDA0DD'   # Plum
    }
    
    # Fill grid with region colors
    for region, zones in generator.exit_map.items():
        for (x, y) in zones:
            grid[x, y] = region_colors[region]
    
    # Create custom colormap
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap([
        colors_hex['North'],
        colors_hex['South'],
        colors_hex['East'],
        colors_hex['West'],
        colors_hex['Central']
    ])
    
    # Plot
    im = ax.imshow(grid, cmap=cmap, vmin=1, vmax=5, interpolation='nearest')
    
    # Add grid lines
    for i in range(11):
        ax.axhline(i - 0.5, color='white', linewidth=2)
        ax.axvline(i - 0.5, color='white', linewidth=2)
    
    # Add zone labels
    for i in range(10):
        for j in range(10):
            region = generator.get_zone_region(i, j)
            exits = generator.get_nearest_exits(i, j, max_exits=1)
            
            # Zone ID
            ax.text(j, i, f'({i},{j})', 
                   ha='center', va='center', fontsize=7, fontweight='bold')
            
            # Nearest exit
            ax.text(j, i + 0.3, exits[0], 
                   ha='center', va='center', fontsize=6, style='italic', color='darkblue')
    
    # Add exit markers
    exit_positions = {
        'North': (0, 5),
        'South': (9, 5),
        'East': (5, 9),
        'West': (5, 0)
    }
    
    for exit_name, (ex, ey) in exit_positions.items():
        ax.plot(ey, ex, marker='*', markersize=20, color='red', 
               markeredgecolor='black', markeredgewidth=2)
        ax.text(ey, ex - 0.6, f'{exit_name}\nExit', 
               ha='center', va='top', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', linewidth=2))
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=colors_hex['North'], edgecolor='black', label='North Exit Region'),
        mpatches.Patch(facecolor=colors_hex['South'], edgecolor='black', label='South Exit Region'),
        mpatches.Patch(facecolor=colors_hex['East'], edgecolor='black', label='East Exit Region'),
        mpatches.Patch(facecolor=colors_hex['West'], edgecolor='black', label='West Exit Region'),
        mpatches.Patch(facecolor=colors_hex['Central'], edgecolor='black', label='Central Region (Multiple Exits)'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='red', markersize=15, 
                  markeredgecolor='black', label='Exit Location')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), 
             fontsize=10, frameon=True, fancybox=True, shadow=True)
    
    # Labels
    ax.set_xlabel('Column', fontsize=12, fontweight='bold')
    ax.set_ylabel('Row', fontsize=12, fontweight='bold')
    ax.set_title('Exit Region Map - Zone-to-Exit Assignments\n10×10 Grid Venue Layout', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Ticks
    ax.set_xticks(range(10))
    ax.set_yticks(range(10))
    
    plt.tight_layout()
    
    # Save
    os.makedirs('results/exit_maps', exist_ok=True)
    output_path = 'results/exit_maps/exit_region_map.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Exit map saved: {output_path}")
    
    return fig


def visualize_instruction_example():
    """Visualize example instruction scenario"""
    
    generator = InstructionGenerator()
    
    # Create example scenario
    example_zones = [
        {'zone_id': 'Zone_2_3', 'x': 2, 'y': 3, 'level': 'safe', 'severity': 18.5},
        {'zone_id': 'Zone_5_8', 'x': 5, 'y': 8, 'level': 'warning', 'severity': 52.3},
        {'zone_id': 'Zone_8_5', 'x': 8, 'y': 5, 'level': 'critical', 'severity': 71.8},
        {'zone_id': 'Zone_1_1', 'x': 1, 'y': 1, 'level': 'emergency', 'severity': 88.2},
    ]
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Create base grid (all safe)
    grid = np.zeros((10, 10))
    
    # Level to number mapping
    level_map = {
        'safe': 0,
        'moderate': 1,
        'warning': 2,
        'critical': 3,
        'emergency': 4
    }
    
    # Fill example zones
    for zone in example_zones:
        grid[zone['x'], zone['y']] = level_map[zone['level']]
    
    # Color map
    colors = ['#00FF00', '#7FFF00', '#FFFF00', '#FF8C00', '#FF0000']
    cmap = plt.matplotlib.colors.ListedColormap(colors)
    
    # Plot
    im = ax.imshow(grid, cmap=cmap, vmin=0, vmax=4, interpolation='nearest')
    
    # Grid lines
    for i in range(11):
        ax.axhline(i - 0.5, color='gray', linewidth=1, alpha=0.5)
        ax.axvline(i - 0.5, color='gray', linewidth=1, alpha=0.5)
    
    # Add zone labels and instructions
    for zone in example_zones:
        x, y = zone['x'], zone['y']
        
        # Generate instruction
        instruction = generator.generate_instruction(
            zone_id=zone['zone_id'],
            x=x,
            y=y,
            level=zone['level'],
            severity=zone['severity']
        )
        
        # Zone marker
        ax.plot(y, x, 'o', markersize=25, markerfacecolor='white', 
               markeredgecolor='black', markeredgewidth=2)
        
        # Zone ID
        ax.text(y, x, zone['zone_id'], ha='center', va='center', 
               fontsize=7, fontweight='bold')
        
        # Arrow to instruction box
        if x < 5:
            text_y = y + 2
            arrow_props = dict(arrowstyle='->', lw=2, color='black')
        else:
            text_y = y - 2
            arrow_props = dict(arrowstyle='->', lw=2, color='black')
        
        # Instruction text (truncated)
        inst_short = instruction['instruction_text'][:80] + "..."
        
        ax.annotate(
            f"{instruction['icon']} {zone['level'].upper()}\n{inst_short}",
            xy=(y, x),
            xytext=(text_y, x),
            fontsize=7,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                     edgecolor=colors[level_map[zone['level']]], linewidth=2),
            arrowprops=arrow_props
        )
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3, 4])
    cbar.set_ticklabels(['Safe', 'Moderate', 'Warning', 'Critical', 'Emergency'])
    cbar.set_label('Classification Level', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Column', fontsize=12, fontweight='bold')
    ax.set_ylabel('Row', fontsize=12, fontweight='bold')
    ax.set_title('Instruction Generation Example\nZone-Specific Evacuation Guidance', 
                fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(range(10))
    ax.set_yticks(range(10))
    
    plt.tight_layout()
    
    # Save
    output_path = 'results/exit_maps/instruction_example.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Instruction example saved: {output_path}")
    
    return fig


if __name__ == '__main__':
    print("=" * 80)
    print("GENERATING EXIT MAP VISUALIZATIONS")
    print("=" * 80)
    
    print("\nCreating exit region map...")
    visualize_exit_regions()
    
    print("\nCreating instruction example...")
    visualize_instruction_example()
    
    print("\n" + "=" * 80)
    print("✅ VISUALIZATIONS COMPLETE")
    print("=" * 80)
    
    plt.show()