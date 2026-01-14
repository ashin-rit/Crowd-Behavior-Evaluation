"""
Test Classifier with Real Scenario Data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_processor import CrowdDataProcessor
from src.classification.zone_classifier import ZoneClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def test_classifier_with_scenario(scenario_name: str, timestamp: int):
    """Test classifier with actual scenario data"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {scenario_name.upper()} - Frame {timestamp}")
    print(f"{'='*60}")
    
    # Load data
    processor = CrowdDataProcessor()
    filepath = f'data/synthetic/{scenario_name}_scenario.csv'
    processor.load_scenario(filepath)
    
    # Get frame
    frame_data = processor.get_frame(timestamp)
    
    # Classify all zones
    classifier = ZoneClassifier()
    classified = classifier.classify_all_zones(frame_data)
    
    # Get summary
    summary = classifier.get_classification_summary(classified)
    
    # Print results
    print(f"\nClassification Results:")
    print(f"  Total Zones: {summary['total_zones']}")
    print(f"  Average Severity: {summary['average_severity']:.2f}/100")
    print(f"Max Severity: {summary['max_severity']:.2f}/100")
    print(f"  Zones Requiring Action: {summary['zones_requiring_action']}")
    print(f"  Elevated Zones: {summary['elevated_zones']}")
    print(f"\nLevel Distribution:")
    for level in ['safe', 'moderate', 'warning', 'critical', 'emergency']:
        count = summary['level_counts'][level]
        pct = summary['level_percentages'][level]
        print(f"  {level.capitalize():12} {count:3} ({pct:5.1f}%)")

    # Get critical zones
    critical = classifier.get_critical_zones(classified)
    if len(critical) > 0:
        print(f"\n⚠️  Critical/Emergency Zones ({len(critical)}):")
        for _, zone in critical.head(5).iterrows():
            print(f"  {zone['zone_id']:12} - {zone['level'].upper():10} "
                f"(Severity: {zone['severity']:.1f})")

    return classified, summary

def visualize_classification(scenario_name: str, timestamp: int):
    """Create visualization of classification results"""
    # Load and classify
    processor = CrowdDataProcessor()
    filepath = f'data/synthetic/{scenario_name}_scenario.csv'
    processor.load_scenario(filepath)

    frame_data = processor.get_frame(timestamp)

    classifier = ZoneClassifier()
    classified = classifier.classify_all_zones(frame_data)

    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # 1. Density heatmap
    density_grid = processor.create_density_grid(timestamp)
    sns.heatmap(
        density_grid,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        vmin=0,
        vmax=8,
        cbar_kws={'label': 'Density (people/m²)'},
        ax=axes[0]
    )
    axes[0].set_title(f'Density Distribution\n{scenario_name.title()} - Frame {timestamp}',
                    fontsize=13, fontweight='bold')

    # 2. Classification heatmap
    # Create classification grid with numeric values
    class_grid = np.zeros((10, 10))
    level_map = {'safe': 0, 'moderate': 1, 'warning': 2, 'critical': 3, 'emergency': 4}

    for _, zone in classified.iterrows():
        x, y = int(zone['x']), int(zone['y'])
        class_grid[x, y] = level_map[zone['level']]

    # Custom colormap
    colors = ['#00FF00', '#7FFF00', '#FFFF00', '#FF8C00', '#FF0000']
    n_bins = 5
    cmap = plt.matplotlib.colors.ListedColormap(colors)

    sns.heatmap(
        class_grid,
        annot=False,
        cmap=cmap,
        vmin=0,
        vmax=4,
        cbar_kws={'label': 'Classification Level',
                'ticks': [0, 1, 2, 3, 4]},
        ax=axes[1]
    )

    # Customize colorbar labels
    colorbar = axes[1].collections[0].colorbar
    colorbar.set_ticklabels(['Safe', 'Moderate', 'Warning', 'Critical', 'Emergency'])

    axes[1].set_title(f'Classification Map\n{scenario_name.title()} - Frame {timestamp}',
                    fontsize=13, fontweight='bold')

    plt.tight_layout()

    # Save
    os.makedirs('results/classification_tests', exist_ok=True)
    output_path = f'results/classification_tests/{scenario_name}_frame_{timestamp}_classification.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualization saved: {output_path}")

    return fig

def run_comprehensive_test():
    """Run comprehensive classification tests"""
    print("=" * 60)
    print("COMPREHENSIVE CLASSIFICATION TEST")
    print("=" * 60)

    test_cases = [
        ('normal', 100),
        ('rush_hour', 100),
        ('emergency', 75),
        ('event_end', 200)
    ]

    for scenario, timestamp in test_cases:
        # Test classification
        classified, summary = test_classifier_with_scenario(scenario, timestamp)
        
        # Create visualization
        visualize_classification(scenario, timestamp)

    print("\n" + "=" * 60)
    print("✅ COMPREHENSIVE TEST COMPLETE")
    print("=" * 60)
    print("\nCheck 'results/classification_tests/' for visualizations")

if __name__ == "__main__":
    run_comprehensive_test()
    plt.show()
