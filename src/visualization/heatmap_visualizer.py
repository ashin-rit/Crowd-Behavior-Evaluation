"""
Heatmap Visualizer Module
Creates density and classification heatmaps for crowd monitoring
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import seaborn as sns
import numpy as np
from typing import Optional, Tuple, Dict
import os


class HeatmapVisualizer:
    """
    Creates various heatmap visualizations for crowd data
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (10, 10)):
        """
        Initialize heatmap visualizer
        
        Args:
            grid_size: Tuple of (rows, cols) for venue grid
        """
        self.grid_rows = grid_size[0]
        self.grid_cols = grid_size[1]
        
        # Define color schemes
        self.density_colormap = 'YlOrRd'  # Yellow-Orange-Red
        self.classification_colors = self._define_classification_colors()
        
        # Scale settings
        self.density_vmin = 0
        self.density_vmax = 8
        
    def _define_classification_colors(self) -> Dict:
        """
        Define colors for each classification level
        
        Returns:
            Dictionary mapping levels to colors
        """
        return {
            'safe': '#00FF00',        # Green
            'moderate': '#7FFF00',    # Yellow-Green
            'warning': '#FFFF00',     # Yellow
            'critical': '#FF8C00',    # Orange
            'emergency': '#FF0000'    # Red
        }
    
    def create_density_heatmap(self, 
                              density_grid: np.ndarray,
                              title: str = "Crowd Density Heatmap",
                              show_values: bool = True,
                              figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
        """
        Create density heatmap showing raw density values
        
        Args:
            density_grid: 2D array of density values
            title: Plot title
            show_values: Whether to annotate cells with values
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create heatmap
        im = sns.heatmap(
            density_grid,
            annot=show_values,
            fmt='.1f',
            cmap=self.density_colormap,
            vmin=self.density_vmin,
            vmax=self.density_vmax,
            cbar_kws={'label': 'Density (people/m²)', 'shrink': 0.8},
            linewidths=0.5,
            linecolor='gray',
            square=True,
            ax=ax
        )
        
        # Customize plot
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Zone Column', fontsize=13, fontweight='bold')
        ax.set_ylabel('Zone Row', fontsize=13, fontweight='bold')
        
        # Add tick labels
        ax.set_xticklabels(range(self.grid_cols), fontsize=10)
        ax.set_yticklabels(range(self.grid_rows), fontsize=10)
        
        # Add density threshold lines (optional visual guides)
        self._add_threshold_annotations(ax)
        
        plt.tight_layout()
        
        return fig
    
    def create_classification_heatmap(self,
                                     classified_zones,
                                     title: str = "Zone Classification Map",
                                     show_severity: bool = True,
                                     figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
        """
        Create classification heatmap with discrete color levels
        
        Args:
            classified_zones: DataFrame with classification results
            title: Plot title
            show_severity: Whether to show severity scores in cells
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create classification grid
        class_grid = np.zeros((self.grid_rows, self.grid_cols))
        severity_grid = np.zeros((self.grid_rows, self.grid_cols))
        
        level_map = {
            'safe': 0,
            'moderate': 1,
            'warning': 2,
            'critical': 3,
            'emergency': 4
        }
        
        for _, zone in classified_zones.iterrows():
            x, y = int(zone['x']), int(zone['y'])
            class_grid[x, y] = level_map[zone['level']]
            severity_grid[x, y] = zone['severity']
        
        # Create custom colormap
        colors = [
            self.classification_colors['safe'],
            self.classification_colors['moderate'],
            self.classification_colors['warning'],
            self.classification_colors['critical'],
            self.classification_colors['emergency']
        ]
        cmap = ListedColormap(colors)
        
        # Plot classification
        im = ax.imshow(class_grid, cmap=cmap, vmin=0, vmax=4, 
                      interpolation='nearest', aspect='equal')
        
        # Add grid lines
        for i in range(self.grid_rows + 1):
            ax.axhline(i - 0.5, color='white', linewidth=2)
        for j in range(self.grid_cols + 1):
            ax.axvline(j - 0.5, color='white', linewidth=2)
        
        # Annotate with severity scores
        if show_severity:
            for i in range(self.grid_rows):
                for j in range(self.grid_cols):
                    severity = severity_grid[i, j]
                    level = int(class_grid[i, j])
                    
                    # Choose text color for readability
                    text_color = 'black' if level < 3 else 'white'
                    
                    ax.text(j, i, f'{severity:.0f}', 
                           ha='center', va='center',
                           fontsize=9, fontweight='bold',
                           color=text_color)
        
        # Create legend
        legend_elements = [
            mpatches.Patch(facecolor=self.classification_colors['safe'], 
                          edgecolor='black', label='Safe (0-2 people/m²)'),
            mpatches.Patch(facecolor=self.classification_colors['moderate'], 
                          edgecolor='black', label='Moderate (2-3.5 people/m²)'),
            mpatches.Patch(facecolor=self.classification_colors['warning'], 
                          edgecolor='black', label='Warning (3.5-5 people/m²)'),
            mpatches.Patch(facecolor=self.classification_colors['critical'], 
                          edgecolor='black', label='Critical (5-7 people/m²)'),
            mpatches.Patch(facecolor=self.classification_colors['emergency'], 
                          edgecolor='black', label='Emergency (7+ people/m²)')
        ]
        
        ax.legend(handles=legend_elements, loc='upper left', 
                 bbox_to_anchor=(1.02, 1), fontsize=10,
                 title='Classification Levels', title_fontsize=11)
        
        # Customize plot
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Zone Column', fontsize=13, fontweight='bold')
        ax.set_ylabel('Zone Row', fontsize=13, fontweight='bold')
        
        # Set ticks
        ax.set_xticks(range(self.grid_cols))
        ax.set_yticks(range(self.grid_rows))
        ax.set_xticklabels(range(self.grid_cols), fontsize=10)
        ax.set_yticklabels(range(self.grid_rows), fontsize=10)
        
        plt.tight_layout()
        
        return fig
    
    def create_dual_heatmap(self,
                           density_grid: np.ndarray,
                           classified_zones,
                           title: str = "Crowd Analysis - Density & Classification",
                           figsize: Tuple[int, int] = (20, 9)) -> plt.Figure:
        """
        Create side-by-side density and classification heatmaps
        
        Args:
            density_grid: 2D array of density values
            classified_zones: DataFrame with classification results
            title: Overall title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Left: Density Heatmap
        sns.heatmap(
            density_grid,
            annot=True,
            fmt='.1f',
            cmap=self.density_colormap,
            vmin=self.density_vmin,
            vmax=self.density_vmax,
            cbar_kws={'label': 'Density (people/m²)'},
            linewidths=0.5,
            linecolor='gray',
            square=True,
            ax=ax1
        )
        
        ax1.set_title('Density Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Column', fontsize=11)
        ax1.set_ylabel('Row', fontsize=11)
        
        # Right: Classification Heatmap
        class_grid = np.zeros((self.grid_rows, self.grid_cols))
        level_map = {'safe': 0, 'moderate': 1, 'warning': 2, 'critical': 3, 'emergency': 4}
        
        for _, zone in classified_zones.iterrows():
            x, y = int(zone['x']), int(zone['y'])
            class_grid[x, y] = level_map[zone['level']]
        
        colors = list(self.classification_colors.values())
        cmap = ListedColormap(colors)
        
        im = ax2.imshow(class_grid, cmap=cmap, vmin=0, vmax=4, 
                       interpolation='nearest', aspect='equal')
        
        # Grid lines
        for i in range(self.grid_rows + 1):
            ax2.axhline(i - 0.5, color='white', linewidth=1.5)
        for j in range(self.grid_cols + 1):
            ax2.axvline(j - 0.5, color='white', linewidth=1.5)
        
        ax2.set_title('Classification Map', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Column', fontsize=11)
        ax2.set_ylabel('Row', fontsize=11)
        
        ax2.set_xticks(range(self.grid_cols))
        ax2.set_yticks(range(self.grid_rows))
        
        # Legend for classification
        legend_elements = [
            mpatches.Patch(facecolor=self.classification_colors['safe'], 
                          edgecolor='black', label='Safe'),
            mpatches.Patch(facecolor=self.classification_colors['moderate'], 
                          edgecolor='black', label='Moderate'),
            mpatches.Patch(facecolor=self.classification_colors['warning'], 
                          edgecolor='black', label='Warning'),
            mpatches.Patch(facecolor=self.classification_colors['critical'], 
                          edgecolor='black', label='Critical'),
            mpatches.Patch(facecolor=self.classification_colors['emergency'], 
                          edgecolor='black', label='Emergency')
        ]
        
        ax2.legend(handles=legend_elements, loc='upper left', 
                  bbox_to_anchor=(1.02, 1), fontsize=9)
        
        # Overall title
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        return fig
    
    def create_annotated_heatmap(self,
                                density_grid: np.ndarray,
                                classified_zones,
                                alerts,
                                title: str = "Comprehensive Crowd Status",
                                figsize: Tuple[int, int] = (14, 12)) -> plt.Figure:
        """
        Create annotated heatmap with alerts and instructions
        
        Args:
            density_grid: 2D array of density values
            classified_zones: DataFrame with classification results
            alerts: List of active alerts
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create classification grid
        class_grid = np.zeros((self.grid_rows, self.grid_cols))
        level_map = {'safe': 0, 'moderate': 1, 'warning': 2, 'critical': 3, 'emergency': 4}
        
        for _, zone in classified_zones.iterrows():
            x, y = int(zone['x']), int(zone['y'])
            class_grid[x, y] = level_map[zone['level']]
        
        # Plot
        colors = list(self.classification_colors.values())
        cmap = ListedColormap(colors)
        
        im = ax.imshow(class_grid, cmap=cmap, vmin=0, vmax=4, 
                      interpolation='nearest', aspect='equal')
        
        # Grid lines
        for i in range(self.grid_rows + 1):
            ax.axhline(i - 0.5, color='white', linewidth=2)
        for j in range(self.grid_cols + 1):
            ax.axvline(j - 0.5, color='white', linewidth=2)
        
        # Annotate with density and alert icons
        alert_zones = {alert['zone_id']: alert for alert in alerts}
        
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                zone_id = f"Zone_{i}_{j}"
                density = density_grid[i, j]
                level = int(class_grid[i, j])
                
                # Density value
                text_color = 'black' if level < 3 else 'white'
                ax.text(j, i - 0.2, f'{density:.1f}', 
                       ha='center', va='center',
                       fontsize=8, fontweight='bold',
                       color=text_color)
                
                # Alert icon if present
                if zone_id in alert_zones:
                    alert = alert_zones[zone_id]
                    icon = alert['visual']['icon']
                    ax.text(j, i + 0.2, icon, 
                           ha='center', va='center',
                           fontsize=14)
        
        # Legend
        legend_elements = [
            mpatches.Patch(facecolor=self.classification_colors['safe'], 
                          edgecolor='black', label='Safe'),
            mpatches.Patch(facecolor=self.classification_colors['moderate'], 
                          edgecolor='black', label='Moderate'),
            mpatches.Patch(facecolor=self.classification_colors['warning'], 
                          edgecolor='black', label='Warning'),
            mpatches.Patch(facecolor=self.classification_colors['critical'], 
                          edgecolor='black', label='Critical'),
            mpatches.Patch(facecolor=self.classification_colors['emergency'], 
                          edgecolor='black', label='Emergency')
        ]
        
        ax.legend(handles=legend_elements, loc='upper left', 
                 bbox_to_anchor=(1.02, 1), fontsize=10)
        
        # Title and labels
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Zone Column', fontsize=13, fontweight='bold')
        ax.set_ylabel('Zone Row', fontsize=13, fontweight='bold')
        
        ax.set_xticks(range(self.grid_cols))
        ax.set_yticks(range(self.grid_rows))
        
        # Add alert count in subtitle
        if alerts:
            alert_text = f"{len(alerts)} Active Alert(s)"
            ax.text(0.5, -0.08, alert_text, 
                   transform=ax.transAxes,
                   ha='center', fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        
        return fig
    
    def _add_threshold_annotations(self, ax):
        """Add threshold reference annotations to density heatmap"""
        # Add subtle text annotations for thresholds
        threshold_text = (
            "Thresholds: Safe<2 | Moderate<3.5 | Warning<5 | Critical<7 | Emergency≥7"
        )
        ax.text(0.5, -0.08, threshold_text,
               transform=ax.transAxes,
               ha='center', fontsize=9, style='italic',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    def save_heatmap(self, fig: plt.Figure, filepath: str, dpi: int = 150):
        """
        Save heatmap to file
        
        Args:
            fig: Matplotlib figure
            filepath: Output file path
            dpi: Resolution
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        print(f"✓ Heatmap saved: {filepath}")


# Testing function
def test_heatmap_visualizer():
    """Test heatmap visualizer with sample data"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from src.utils.data_processor import CrowdDataProcessor
    from src.classification.zone_classifier import ZoneClassifier
    from src.alerts.alert_manager import AlertManager
    
    print("=" * 80)
    print("HEATMAP VISUALIZER TEST")
    print("=" * 80)
    
    # Load sample data
    print("\nLoading sample scenario...")
    processor = CrowdDataProcessor()
    processor.load_scenario('data/synthetic/emergency_scenario.csv')
    frame_data = processor.get_frame(75)
    
    # Classify
    print("Classifying zones...")
    classifier = ZoneClassifier()
    classified = classifier.classify_all_zones(frame_data)
    
    # Generate alerts
    print("Generating alerts...")
    alert_mgr = AlertManager()
    alerts = alert_mgr.process_classified_zones(classified)
    active_alerts = alert_mgr.get_active_alerts()
    
    # Create density grid
    print("Creating density grid...")
    density_grid = processor.create_density_grid(75)
    
    # Initialize visualizer
    print("\nInitializing visualizer...")
    visualizer = HeatmapVisualizer()
    
    # Test 1: Density Heatmap
    print("\n1. Creating density heatmap...")
    fig1 = visualizer.create_density_heatmap(
        density_grid,
        title="Emergency Scenario - Density Distribution (Frame 75)"
    )
    visualizer.save_heatmap(fig1, 'results/heatmaps/test_density_heatmap.png')
    
    # Test 2: Classification Heatmap
    print("\n2. Creating classification heatmap...")
    fig2 = visualizer.create_classification_heatmap(
        classified,
        title="Emergency Scenario - Classification Map (Frame 75)"
    )
    visualizer.save_heatmap(fig2, 'results/heatmaps/test_classification_heatmap.png')
    
    # Test 3: Dual Heatmap
    print("\n3. Creating dual heatmap...")
    fig3 = visualizer.create_dual_heatmap(
        density_grid,
        classified,
        title="Emergency Scenario - Comprehensive Analysis (Frame 75)"
    )
    visualizer.save_heatmap(fig3, 'results/heatmaps/test_dual_heatmap.png')
    
    # Test 4: Annotated Heatmap
    print("\n4. Creating annotated heatmap...")
    fig4 = visualizer.create_annotated_heatmap(
        density_grid,
        classified,
        active_alerts,
        title="Emergency Scenario - Status with Alerts (Frame 75)"
    )
    visualizer.save_heatmap(fig4, 'results/heatmaps/test_annotated_heatmap.png')
    
    print("\n" + "=" * 80)
    print("✅ HEATMAP VISUALIZER TEST COMPLETE")
    print("=" * 80)
    print("\nCheck 'results/heatmaps/' for output files")
    
    plt.show()


if __name__ == '__main__':
    test_heatmap_visualizer()