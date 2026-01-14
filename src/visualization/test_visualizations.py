"""
Test Visualizations
Creates sample plots to verify data quality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import CrowdDataProcessor
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_single_frame_heatmap(processor: CrowdDataProcessor, timestamp: int, scenario_name: str):
    """Plot density heatmap for a single frame"""
    
    # Get density grid
    density_grid = processor.create_density_grid(timestamp)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # Create heatmap
    sns.heatmap(
        density_grid,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Density (people/m²)'},
        vmin=0,
        vmax=8,
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title(f'{scenario_name.title()} Scenario - Frame {timestamp}\nCrowd Density Heatmap', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Zone Column', fontsize=11)
    ax.set_ylabel('Zone Row', fontsize=11)
    
    plt.tight_layout()
    
    # Save
    os.makedirs('results/test_visualizations', exist_ok=True)
    output_path = f'results/test_visualizations/{scenario_name}_frame_{timestamp}_heatmap.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    
    return fig


def plot_temporal_evolution(processor: CrowdDataProcessor, x: int, y: int, scenario_name: str):
    """Plot how a specific zone evolves over time"""
    
    # Get temporal profile
    temporal_data = processor.get_temporal_profile(x, y)
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot density over time
    axes[0].plot(temporal_data['timestamp'], temporal_data['density'], 
                linewidth=2, color='darkred')
    axes[0].fill_between(temporal_data['timestamp'], temporal_data['density'], 
                         alpha=0.3, color='red')
    axes[0].axhline(y=2, color='green', linestyle='--', alpha=0.5, label='Safe threshold')
    axes[0].axhline(y=5, color='orange', linestyle='--', alpha=0.5, label='Warning threshold')
    axes[0].axhline(y=7, color='red', linestyle='--', alpha=0.5, label='Critical threshold')
    axes[0].set_ylabel('Density (people/m²)', fontsize=11)
    axes[0].set_title(f'Zone ({x},{y}) Temporal Evolution - {scenario_name.title()}', 
                     fontsize=13, fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Plot movement speed over time
    axes[1].plot(temporal_data['timestamp'], temporal_data['movement_speed'], 
                linewidth=2, color='darkblue')
    axes[1].fill_between(temporal_data['timestamp'], temporal_data['movement_speed'], 
                         alpha=0.3, color='blue')
    axes[1].set_ylabel('Speed (m/s)', fontsize=11)
    axes[1].grid(alpha=0.3)
    
    # Plot direction variance over time
    axes[2].plot(temporal_data['timestamp'], temporal_data['direction_variance'], 
                linewidth=2, color='darkgreen')
    axes[2].fill_between(temporal_data['timestamp'], temporal_data['direction_variance'], 
                         alpha=0.3, color='green')
    axes[2].set_ylabel('Direction Variance (°)', fontsize=11)
    axes[2].set_xlabel('Timestamp', fontsize=11)
    axes[2].grid(alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_path = f'results/test_visualizations/{scenario_name}_zone_{x}_{y}_temporal.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    
    return fig


def plot_comparison_frames(processor: CrowdDataProcessor, timestamps: list, scenario_name: str):
    """Plot multiple frames side by side"""
    
    n_frames = len(timestamps)
    fig, axes = plt.subplots(1, n_frames, figsize=(6*n_frames, 5))
    
    if n_frames == 1:
        axes = [axes]
    
    for idx, ts in enumerate(timestamps):
        density_grid = processor.create_density_grid(ts)
        
        sns.heatmap(
            density_grid,
            annot=False,
            cmap='YlOrRd',
            vmin=0,
            vmax=8,
            cbar=True if idx == n_frames-1 else False,
            cbar_kws={'label': 'Density (people/m²)'},
            ax=axes[idx]
        )
        
        axes[idx].set_title(f'Frame {ts}', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Column')
        axes[idx].set_ylabel('Row')
    
    fig.suptitle(f'{scenario_name.title()} Scenario - Temporal Comparison', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Save
    output_path = f'results/test_visualizations/{scenario_name}_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    
    return fig


def plot_spatial_statistics(processor: CrowdDataProcessor, timestamp: int, scenario_name: str):
    """Plot spatial statistics for a given timestamp"""
    
    frame = processor.get_frame(timestamp)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Density histogram
    axes[0, 0].hist(frame['density'], bins=30, color='skyblue', edgecolor='black')
    axes[0, 0].axvline(frame['density'].mean(), color='red', linestyle='--', 
                      linewidth=2, label=f'Mean: {frame["density"].mean():.2f}')
    axes[0, 0].set_xlabel('Density (people/m²)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Density Distribution')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # Speed histogram
    axes[0, 1].hist(frame['movement_speed'], bins=30, color='lightgreen', edgecolor='black')
    axes[0, 1].axvline(frame['movement_speed'].mean(), color='red', linestyle='--', 
                      linewidth=2, label=f'Mean: {frame["movement_speed"].mean():.2f}')
    axes[0, 1].set_xlabel('Movement Speed (m/s)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Speed Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    
    # Density vs Speed scatter
    axes[1, 0].scatter(frame['density'], frame['movement_speed'], 
                      alpha=0.6, c=frame['density'], cmap='YlOrRd')
    axes[1, 0].set_xlabel('Density (people/m²)')
    axes[1, 0].set_ylabel('Movement Speed (m/s)')
    axes[1, 0].set_title('Density vs Speed Relationship')
    axes[1, 0].grid(alpha=0.3)
    
    # Direction variance histogram
    axes[1, 1].hist(frame['direction_variance'], bins=30, color='lightcoral', edgecolor='black')
    axes[1, 1].axvline(frame['direction_variance'].mean(), color='red', linestyle='--', 
                      linewidth=2, label=f'Mean: {frame["direction_variance"].mean():.1f}')
    axes[1, 1].set_xlabel('Direction Variance (°)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Direction Variance Distribution')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)
    
    fig.suptitle(f'{scenario_name.title()} Scenario - Frame {timestamp} Statistics', 
                fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save
    output_path = f'results/test_visualizations/{scenario_name}_frame_{timestamp}_statistics.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    
    return fig


def run_all_visualizations():
    """Generate all test visualizations"""
    print("=" * 60)
    print("GENERATING TEST VISUALIZATIONS")
    print("=" * 60)
    
    processor = CrowdDataProcessor()
    
    scenarios = [
        ('normal', [0, 100, 199]),
        ('rush_hour', [0, 100, 199]),
        ('emergency', [0, 50, 149]),
        ('event_end', [0, 125, 249])
    ]
    
    for scenario_name, key_frames in scenarios:
        print(f"\n--- Processing: {scenario_name.upper()} ---")
        
        filepath = f'data/synthetic/{scenario_name}_scenario.csv'
        processor.load_scenario(filepath)
        
        # 1. Single frame heatmap (middle frame)
        mid_frame = key_frames[1]
        print(f"Creating heatmap for frame {mid_frame}...")
        plot_single_frame_heatmap(processor, mid_frame, scenario_name)
        
        # 2. Temporal evolution (center zone)
        print(f"Creating temporal evolution plot...")
        plot_temporal_evolution(processor, 5, 5, scenario_name)
        
        # 3. Frame comparison
        print(f"Creating frame comparison...")
        plot_comparison_frames(processor, key_frames, scenario_name)
        
        # 4. Spatial statistics
        print(f"Creating spatial statistics...")
        plot_spatial_statistics(processor, mid_frame, scenario_name)
        
        print(f"✅ {scenario_name.upper()} visualizations complete\n")
    
    print("=" * 60)
    print("✅ ALL VISUALIZATIONS GENERATED")
    print("=" * 60)
    print("\nCheck 'results/test_visualizations/' folder for outputs")


if __name__ == '__main__':
    run_all_visualizations()
    plt.show()