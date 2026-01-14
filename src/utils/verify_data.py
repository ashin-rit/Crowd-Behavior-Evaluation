"""
Data Verification Script
Checks quality and characteristics of generated data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


class DataVerifier:
    """
    Verifies quality of synthetic crowd data
    """
    
    def __init__(self, data_dir='data/synthetic'):
        self.data_dir = data_dir
        
    def load_scenario(self, scenario_name):
        """Load scenario CSV file"""
        filename = f'{scenario_name}_scenario.csv'
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"✗ File not found: {filepath}")
            return None
        
        df = pd.read_csv(filepath)
        print(f"✓ Loaded {scenario_name}: {len(df)} records")
        return df
    
    def print_basic_stats(self, df, scenario_name):
        """Print basic statistics"""
        print(f"\n{'=' * 60}")
        print(f"{scenario_name.upper()} SCENARIO - STATISTICS")
        print(f"{'=' * 60}")
        
        print(f"\nDataset Info:")
        print(f"  Total records: {len(df):,}")
        print(f"  Timestamps: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"  Unique zones: {df['zone_id'].nunique()}")
        
        print(f"\nDensity Statistics:")
        print(f"  Min:  {df['density'].min():.2f} people/m²")
        print(f"  Max:  {df['density'].max():.2f} people/m²")
        print(f"  Mean: {df['density'].mean():.2f} people/m²")
        print(f"  Std:  {df['density'].std():.2f} people/m²")
        
        print(f"\nSpeed Statistics:")
        print(f"  Min:  {df['movement_speed'].min():.2f} m/s")
        print(f"  Max:  {df['movement_speed'].max():.2f} m/s")
        print(f"  Mean: {df['movement_speed'].mean():.2f} m/s")
        
        print(f"\nDirection Variance:")
        print(f"  Min:  {df['direction_variance'].min():.1f}°")
        print(f"  Max:  {df['direction_variance'].max():.1f}°")
        print(f"  Mean: {df['direction_variance'].mean():.1f}°")
        
        # Classify zones by density levels
        safe = len(df[df['density'] < 2])
        moderate = len(df[(df['density'] >= 2) & (df['density'] < 3.5)])
        warning = len(df[(df['density'] >= 3.5) & (df['density'] < 5)])
        critical = len(df[(df['density'] >= 5) & (df['density'] < 7)])
        emergency = len(df[df['density'] >= 7])
        
        total = len(df)
        print(f"\nZone Classification Distribution:")
        print(f"  Safe (0-2):        {safe:6} ({safe/total*100:5.1f}%)")
        print(f"  Moderate (2-3.5):  {moderate:6} ({moderate/total*100:5.1f}%)")
        print(f"  Warning (3.5-5):   {warning:6} ({warning/total*100:5.1f}%)")
        print(f"  Critical (5-7):    {critical:6} ({critical/total*100:5.1f}%)")
        print(f"  Emergency (7+):    {emergency:6} ({emergency/total*100:5.1f}%)")
    
    def verify_data_quality(self, df, scenario_name):
        """Check for data quality issues"""
        print(f"\n{'=' * 60}")
        print(f"DATA QUALITY CHECKS - {scenario_name.upper()}")
        print(f"{'=' * 60}")
        
        issues = []
        
        # Check for missing values
        missing = df.isnull().sum().sum()
        if missing > 0:
            issues.append(f"Missing values: {missing}")
        else:
            print("✓ No missing values")
        
        # Check for negative values
        negative_density = len(df[df['density'] < 0])
        if negative_density > 0:
            issues.append(f"Negative density values: {negative_density}")
        else:
            print("✓ No negative density values")
        
        # Check for unrealistic speeds
        unrealistic_speed = len(df[df['movement_speed'] > 3.0])
        if unrealistic_speed > 0:
            issues.append(f"Unrealistic speeds (>3 m/s): {unrealistic_speed}")
        else:
            print("✓ All speeds realistic (<3 m/s)")
        
        # Check timestamp continuity
        timestamps = sorted(df['timestamp'].unique())
        expected = list(range(min(timestamps), max(timestamps) + 1))
        if timestamps != expected:
            issues.append("Timestamp gaps detected")
        else:
            print("✓ Continuous timestamps")
        
        # Check zone completeness
        zones_per_timestamp = df.groupby('timestamp')['zone_id'].count()
        if not all(zones_per_timestamp == 100):  # 10x10 grid
            issues.append("Missing zones in some timestamps")
        else:
            print("✓ All zones present in every timestamp")
        
        if issues:
            print("\n⚠️  Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Data quality: EXCELLENT")
        
        return len(issues) == 0
    
    def plot_density_distribution(self, scenarios_data):
        """Plot density distributions for all scenarios"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for idx, (name, df) in enumerate(scenarios_data):
            ax = axes[idx]
            
            # Histogram
            ax.hist(df['density'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
            ax.axvline(df['density'].mean(), color='red', linestyle='--', 
                      linewidth=2, label=f'Mean: {df["density"].mean():.2f}')
            
            # Threshold lines
            ax.axvline(2, color='green', linestyle=':', alpha=0.5, label='Safe')
            ax.axvline(3.5, color='yellow', linestyle=':', alpha=0.5, label='Moderate')
            ax.axvline(5, color='orange', linestyle=':', alpha=0.5, label='Warning')
            ax.axvline(7, color='red', linestyle=':', alpha=0.5, label='Critical')
            
            ax.set_xlabel('Density (people/m²)', fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            ax.set_title(f'{name} Scenario - Density Distribution', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        os.makedirs('results/data_verification', exist_ok=True)
        plt.savefig('results/data_verification/density_distributions.png', dpi=150)
        print("\n✓ Density distribution plot saved to: results/data_verification/density_distributions.png")
        
        plt.show()
    
    def plot_temporal_patterns(self, scenarios_data):
        """Plot how density changes over time"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for idx, (name, df) in enumerate(scenarios_data):
            ax = axes[idx]
            
            # Calculate average density per timestamp
            temporal = df.groupby('timestamp')['density'].agg(['mean', 'max', 'min'])
            
            ax.plot(temporal.index, temporal['mean'], label='Average', linewidth=2)
            ax.fill_between(temporal.index, temporal['min'], temporal['max'], 
                           alpha=0.3, label='Min-Max Range')
            
            # Threshold lines
            ax.axhline(2, color='green', linestyle='--', alpha=0.5, label='Safe threshold')
            ax.axhline(5, color='orange', linestyle='--', alpha=0.5, label='Warning threshold')
            ax.axhline(7, color='red', linestyle='--', alpha=0.5, label='Critical threshold')
            
            ax.set_xlabel('Time Step', fontsize=11)
            ax.set_ylabel('Density (people/m²)', fontsize=11)
            ax.set_title(f'{name} Scenario - Temporal Pattern', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        plt.savefig('results/data_verification/temporal_patterns.png', dpi=150)
        print("✓ Temporal patterns plot saved to: results/data_verification/temporal_patterns.png")
        
        plt.show()
    
    def verify_all_scenarios(self):
        """Main verification function"""
        print("=" * 60)
        print("DATA VERIFICATION PROCESS")
        print("=" * 60)
        
        scenarios = ['normal', 'rush_hour', 'emergency', 'event_end']
        scenarios_data = []
        all_passed = True
        
        for scenario in scenarios:
            df = self.load_scenario(scenario)
            if df is not None:
                scenarios_data.append((scenario.replace('_', ' ').title(), df))
                self.print_basic_stats(df, scenario)
                passed = self.verify_data_quality(df, scenario)
                all_passed = all_passed and passed
                print()
        
        if scenarios_data:
            print("\nGenerating visualizations...")
            self.plot_density_distribution(scenarios_data)
            self.plot_temporal_patterns(scenarios_data)
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ ALL SCENARIOS PASSED QUALITY CHECKS")
        else:
            print("⚠️  SOME SCENARIOS HAVE QUALITY ISSUES")
        print("=" * 60)


if __name__ == '__main__':
    verifier = DataVerifier()
    verifier.verify_all_scenarios()