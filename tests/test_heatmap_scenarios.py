"""
Test Heatmap Visualizations Across All Scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_processor import CrowdDataProcessor
from src.classification.zone_classifier import ZoneClassifier
from src.alerts.alert_manager import AlertManager
from src.visualization.heatmap_visualizer import HeatmapVisualizer
import matplotlib.pyplot as plt


def generate_scenario_heatmaps(scenario_name: str, timestamp: int):
    """Generate all heatmap types for a scenario"""
    
    print(f"\n{'='*80}")
    print(f"Generating heatmaps: {scenario_name.upper()} - Frame {timestamp}")
    print(f"{'='*80}")
    
    # Load and process data
    processor = CrowdDataProcessor()
    processor.load_scenario(f'data/synthetic/{scenario_name}_scenario.csv')
    frame_data = processor.get_frame(timestamp)
    
    # Classify
    classifier = ZoneClassifier()
    classified = classifier.classify_all_zones(frame_data)
    
    # Alerts
    alert_mgr = AlertManager()
    alerts = alert_mgr.process_classified_zones(classified)
    active_alerts = alert_mgr.get_active_alerts()
    
    # Density grid
    density_grid = processor.create_density_grid(timestamp)
    
    # Initialize visualizer
    visualizer = HeatmapVisualizer()
    
    # Create output directory
    output_dir = f'results/heatmaps/{scenario_name}'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Density Heatmap
    print("  Creating density heatmap...")
    fig1 = visualizer.create_density_heatmap(
        density_grid,
        title=f"{scenario_name.replace('_', ' ').title()} Scenario\nDensity Distribution (Frame {timestamp})"
    )
    visualizer.save_heatmap(fig1, f'{output_dir}/density_frame_{timestamp}.png')
    plt.close(fig1)
    
    # 2. Classification Heatmap
    print("  Creating classification heatmap...")
    fig2 = visualizer.create_classification_heatmap(
        classified,
        title=f"{scenario_name.replace('_', ' ').title()} Scenario\nClassification Map (Frame {timestamp})"
    )
    visualizer.save_heatmap(fig2, f'{output_dir}/classification_frame_{timestamp}.png')
    plt.close(fig2)
    
    # 3. Dual Heatmap
    print("  Creating dual heatmap...")
    fig3 = visualizer.create_dual_heatmap(
        density_grid,
        classified,
        title=f"{scenario_name.replace('_', ' ').title()} Scenario - Frame {timestamp}"
    )
    visualizer.save_heatmap(fig3, f'{output_dir}/dual_frame_{timestamp}.png')
    plt.close(fig3)
    
    # 4. Annotated Heatmap (if alerts present)
    if active_alerts:
        print("  Creating annotated heatmap...")
        fig4 = visualizer.create_annotated_heatmap(
            density_grid,
            classified,
            active_alerts,
            title=f"{scenario_name.replace('_', ' ').title()} Scenario\nStatus with Alerts (Frame {timestamp})"
        )
        visualizer.save_heatmap(fig4, f'{output_dir}/annotated_frame_{timestamp}.png')
        plt.close(fig4)
    
    print(f"  ✓ All heatmaps generated for {scenario_name}")
    
    return {
        'scenario': scenario_name,
        'timestamp': timestamp,
        'alerts': len(active_alerts),
        'max_density': density_grid.max(),
        'avg_density': density_grid.mean()
    }


def run_all_scenarios():
    """Generate heatmaps for all scenarios"""
    
    print("=" * 80)
    print("HEATMAP GENERATION - ALL SCENARIOS")
    print("=" * 80)
    
    test_cases = [
        ('normal', 100),
        ('rush_hour', 100),
        ('emergency', 75),
        ('event_end', 200)
    ]
    
    results = []
    
    for scenario, timestamp in test_cases:
        result = generate_scenario_heatmaps(scenario, timestamp)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("GENERATION SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Scenario':<15} {'Frame':<8} {'Alerts':<8} {'Max Density':<12} {'Avg Density':<12}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['scenario']:<15} {r['timestamp']:<8} {r['alerts']:<8} "
              f"{r['max_density']:<12.2f} {r['avg_density']:<12.2f}")
    
    print("\n" + "=" * 80)
    print("✅ ALL HEATMAPS GENERATED")
    print("=" * 80)
    print("\nCheck 'results/heatmaps/' for outputs organized by scenario")


if __name__ == '__main__':
    run_all_scenarios()