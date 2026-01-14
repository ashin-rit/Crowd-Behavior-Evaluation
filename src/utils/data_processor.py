"""
Data Processor Module
Handles loading, validation, and preprocessing of crowd data
"""

import pandas as pd
import numpy as np
import os
from typing import Tuple, Optional, Dict, List


class CrowdDataProcessor:
    """
    Processes and validates crowd behavior data
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (10, 10), zone_area: float = 10.0):
        """
        Initialize data processor
        
        Args:
            grid_size: Tuple of (rows, cols) for venue grid
            zone_area: Area of each zone in square meters
        """
        self.grid_rows = grid_size[0]
        self.grid_cols = grid_size[1]
        self.zone_area = zone_area
        self.total_zones = self.grid_rows * self.grid_cols
        
        self.current_scenario = None
        self.scenario_name = None
        self.scenario_stats = {}
        
    def load_scenario(self, filepath: str) -> pd.DataFrame:
        """
        Load scenario data from CSV file
        
        Args:
            filepath: Path to scenario CSV file
            
        Returns:
            DataFrame with scenario data
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Scenario file not found: {filepath}")
        
        print(f"Loading scenario from: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Store scenario info
            self.current_scenario = df
            self.scenario_name = os.path.basename(filepath).replace('_scenario.csv', '')
            
            # Validate loaded data
            self._validate_data(df)
            
            # Calculate statistics
            self._calculate_statistics(df)
            
            print(f"✓ Loaded {len(df):,} records")
            print(f"✓ Timestamps: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"✓ Zones: {df['zone_id'].nunique()}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading scenario: {str(e)}")
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data integrity and quality
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes
        """
        errors = []
        warnings = []
        
        # Check required columns
        required_columns = [
            'timestamp', 'zone_id', 'x_coord', 'y_coord', 
            'density', 'people_count', 'movement_speed', 'direction_variance'
        ]
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check for missing values
        null_counts = df.isnull().sum()
        if null_counts.any():
            errors.append(f"Missing values found: {null_counts[null_counts > 0].to_dict()}")
        
        # Check for negative densities
        negative_density = (df['density'] < 0).sum()
        if negative_density > 0:
            errors.append(f"Negative density values: {negative_density} records")
        
        # Check for unrealistic speeds (>3 m/s is running)
        high_speed = (df['movement_speed'] > 3.0).sum()
        if high_speed > 0:
            warnings.append(f"Unusually high speeds (>3 m/s): {high_speed} records")
        
        # Check timestamp continuity
        timestamps = sorted(df['timestamp'].unique())
        expected_timestamps = list(range(min(timestamps), max(timestamps) + 1))
        if timestamps != expected_timestamps:
            errors.append("Non-continuous timestamps detected")
        
        # Check zone completeness per timestamp
        zones_per_ts = df.groupby('timestamp').size()
        if not all(zones_per_ts == self.total_zones):
            errors.append("Some timestamps missing zone data")
        
        # Check coordinate ranges
        if df['x_coord'].max() >= self.grid_rows or df['x_coord'].min() < 0:
            errors.append(f"Invalid x_coord values (must be 0-{self.grid_rows-1})")
        
        if df['y_coord'].max() >= self.grid_cols or df['y_coord'].min() < 0:
            errors.append(f"Invalid y_coord values (must be 0-{self.grid_cols-1})")
        
        # Report results
        if errors:
            print("\n❌ VALIDATION FAILED:")
            for error in errors:
                print(f"   ERROR: {error}")
            raise ValueError("Data validation failed")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
        
        print("✓ Data validation passed")
        return True
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate scenario statistics
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_records': len(df),
            'total_timestamps': df['timestamp'].nunique(),
            'total_zones': df['zone_id'].nunique(),
            'density': {
                'min': df['density'].min(),
                'max': df['density'].max(),
                'mean': df['density'].mean(),
                'median': df['density'].median(),
                'std': df['density'].std()
            },
            'speed': {
                'min': df['movement_speed'].min(),
                'max': df['movement_speed'].max(),
                'mean': df['movement_speed'].mean(),
                'std': df['movement_speed'].std()
            },
            'direction_variance': {
                'min': df['direction_variance'].min(),
                'max': df['direction_variance'].max(),
                'mean': df['direction_variance'].mean(),
                'std': df['direction_variance'].std()
            }
        }
        
        # Classification distribution
        stats['classification'] = {
            'safe': len(df[df['density'] < 2]),
            'moderate': len(df[(df['density'] >= 2) & (df['density'] < 3.5)]),
            'warning': len(df[(df['density'] >= 3.5) & (df['density'] < 5)]),
            'critical': len(df[(df['density'] >= 5) & (df['density'] < 7)]),
            'emergency': len(df[df['density'] >= 7])
        }
        
        self.scenario_stats = stats
        return stats
    
    def get_frame(self, timestamp: int) -> pd.DataFrame:
        """
        Get data for a specific timestamp
        
        Args:
            timestamp: Time step to retrieve
            
        Returns:
            DataFrame with all zones at that timestamp
        """
        if self.current_scenario is None:
            raise ValueError("No scenario loaded. Call load_scenario() first.")
        
        frame = self.current_scenario[self.current_scenario['timestamp'] == timestamp]
        
        if len(frame) == 0:
            raise ValueError(f"No data found for timestamp {timestamp}")
        
        return frame.copy()
    
    def get_zone(self, zone_id: str) -> pd.DataFrame:
        """
        Get temporal data for a specific zone
        
        Args:
            zone_id: Zone identifier (e.g., 'Zone_5_3')
            
        Returns:
            DataFrame with all timestamps for that zone
        """
        if self.current_scenario is None:
            raise ValueError("No scenario loaded. Call load_scenario() first.")
        
        zone_data = self.current_scenario[self.current_scenario['zone_id'] == zone_id]
        
        if len(zone_data) == 0:
            raise ValueError(f"No data found for zone {zone_id}")
        
        return zone_data.copy()
    
    def get_zone_by_coords(self, x: int, y: int, timestamp: Optional[int] = None) -> pd.DataFrame:
        """
        Get zone data by coordinates
        
        Args:
            x: Row coordinate
            y: Column coordinate
            timestamp: Optional specific timestamp
            
        Returns:
            DataFrame with zone data
        """
        if self.current_scenario is None:
            raise ValueError("No scenario loaded. Call load_scenario() first.")
        
        mask = (self.current_scenario['x_coord'] == x) & (self.current_scenario['y_coord'] == y)
        
        if timestamp is not None:
            mask = mask & (self.current_scenario['timestamp'] == timestamp)
        
        zone_data = self.current_scenario[mask]
        
        if len(zone_data) == 0:
            raise ValueError(f"No data found for coordinates ({x}, {y})")
        
        return zone_data.copy()
    
    def create_density_grid(self, timestamp: int) -> np.ndarray:
        """
        Create 2D density grid for a specific timestamp
        
        Args:
            timestamp: Time step
            
        Returns:
            2D numpy array of densities
        """
        frame = self.get_frame(timestamp)
        
        # Initialize grid
        grid = np.zeros((self.grid_rows, self.grid_cols))
        
        # Fill grid with density values
        for _, row in frame.iterrows():
            x, y = int(row['x_coord']), int(row['y_coord'])
            grid[x, y] = row['density']
        
        return grid
    
    def create_speed_grid(self, timestamp: int) -> np.ndarray:
        """
        Create 2D movement speed grid
        
        Args:
            timestamp: Time step
            
        Returns:
            2D numpy array of speeds
        """
        frame = self.get_frame(timestamp)
        
        grid = np.zeros((self.grid_rows, self.grid_cols))
        
        for _, row in frame.iterrows():
            x, y = int(row['x_coord']), int(row['y_coord'])
            grid[x, y] = row['movement_speed']
        
        return grid
    
    def create_variance_grid(self, timestamp: int) -> np.ndarray:
        """
        Create 2D direction variance grid
        
        Args:
            timestamp: Time step
            
        Returns:
            2D numpy array of direction variances
        """
        frame = self.get_frame(timestamp)
        
        grid = np.zeros((self.grid_rows, self.grid_cols))
        
        for _, row in frame.iterrows():
            x, y = int(row['x_coord']), int(row['y_coord'])
            grid[x, y] = row['direction_variance']
        
        return grid
    
    def get_temporal_profile(self, x: int, y: int) -> pd.DataFrame:
        """
        Get temporal profile of a zone (how it changes over time)
        
        Args:
            x: Row coordinate
            y: Column coordinate
            
        Returns:
            DataFrame with temporal data
        """
        zone_data = self.get_zone_by_coords(x, y)
        
        # Sort by timestamp
        zone_data = zone_data.sort_values('timestamp')
        
        return zone_data[['timestamp', 'density', 'movement_speed', 'direction_variance']]
    
    def get_spatial_profile(self, timestamp: int) -> pd.DataFrame:
        """
        Get spatial profile at a specific time
        
        Args:
            timestamp: Time step
            
        Returns:
            DataFrame with spatial data
        """
        frame = self.get_frame(timestamp)
        
        return frame[['x_coord', 'y_coord', 'zone_id', 'density', 
                     'movement_speed', 'direction_variance']]
    
    def calculate_zone_metrics(self, zone_data: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive metrics for a zone
        
        Args:
            zone_data: DataFrame with zone information
            
        Returns:
            Dictionary of calculated metrics
        """
        if len(zone_data) == 0:
            return {}
        
        # Get first row (assuming single timestamp)
        row = zone_data.iloc[0]
        
        metrics = {
            'zone_id': row['zone_id'],
            'x_coord': int(row['x_coord']),
            'y_coord': int(row['y_coord']),
            'density': float(row['density']),
            'people_count': int(row['people_count']),
            'movement_speed': float(row['movement_speed']),
            'direction_variance': float(row['direction_variance']),
            'area': self.zone_area,
            'capacity_utilization': (row['density'] / 8.0) * 100,  # Assume max 8 people/m²
            'flow_rate': row['density'] * row['movement_speed']  # people passing per second
        }
        
        return metrics
    
    def get_statistics_summary(self) -> Dict:
        """
        Get summary statistics for current scenario
        
        Returns:
            Dictionary of statistics
        """
        if not self.scenario_stats:
            raise ValueError("No statistics available. Load a scenario first.")
        
        return self.scenario_stats.copy()
    
    def print_statistics(self):
        """Print formatted statistics"""
        if not self.scenario_stats:
            print("No statistics available")
            return
        
        stats = self.scenario_stats
        
        print("\n" + "=" * 60)
        print(f"SCENARIO STATISTICS: {self.scenario_name.upper()}")
        print("=" * 60)
        
        print(f"\nDataset Overview:")
        print(f"  Total Records:  {stats['total_records']:,}")
        print(f"  Timestamps:     {stats['total_timestamps']}")
        print(f"  Zones:          {stats['total_zones']}")
        
        print(f"\nDensity Metrics:")
        print(f"  Min:     {stats['density']['min']:6.2f} people/m²")
        print(f"  Max:     {stats['density']['max']:6.2f} people/m²")
        print(f"  Mean:    {stats['density']['mean']:6.2f} people/m²")
        print(f"  Median:  {stats['density']['median']:6.2f} people/m²")
        print(f"  Std Dev: {stats['density']['std']:6.2f}")
        
        print(f"\nMovement Speed:")
        print(f"  Min:     {stats['speed']['min']:6.2f} m/s")
        print(f"  Max:     {stats['speed']['max']:6.2f} m/s")
        print(f"  Mean:    {stats['speed']['mean']:6.2f} m/s")
        
        print(f"\nDirection Variance:")
        print(f"  Min:     {stats['direction_variance']['min']:6.1f}°")
        print(f"  Max:     {stats['direction_variance']['max']:6.1f}°")
        print(f"  Mean:    {stats['direction_variance']['mean']:6.1f}°")
        
        print(f"\nClassification Distribution:")
        total = stats['total_records']
        for level, count in stats['classification'].items():
            percentage = (count / total) * 100
            print(f"  {level.capitalize():12} {count:6,} ({percentage:5.1f}%)")
        
        print("=" * 60)
    
    def export_frame_to_csv(self, timestamp: int, output_path: str):
        """
        Export a single frame to CSV
        
        Args:
            timestamp: Time step to export
            output_path: Output file path
        """
        frame = self.get_frame(timestamp)
        frame.to_csv(output_path, index=False)
        print(f"✓ Frame {timestamp} exported to: {output_path}")
    
    def get_time_range(self) -> Tuple[int, int]:
        """
        Get the time range of current scenario
        
        Returns:
            Tuple of (min_timestamp, max_timestamp)
        """
        if self.current_scenario is None:
            raise ValueError("No scenario loaded")
        
        return (
            self.current_scenario['timestamp'].min(),
            self.current_scenario['timestamp'].max()
        )
    
    def get_high_density_zones(self, timestamp: int, threshold: float = 5.0) -> pd.DataFrame:
        """
        Get zones exceeding density threshold at a specific time
        
        Args:
            timestamp: Time step
            threshold: Density threshold
            
        Returns:
            DataFrame with high-density zones
        """
        frame = self.get_frame(timestamp)
        high_density = frame[frame['density'] >= threshold]
        
        return high_density.sort_values('density', ascending=False)


# Testing function
def test_data_processor():
    """Test the data processor with all scenarios"""
    print("=" * 60)
    print("DATA PROCESSOR TEST")
    print("=" * 60)
    
    processor = CrowdDataProcessor()
    scenarios = ['normal', 'rush_hour', 'emergency', 'event_end']
    
    for scenario_name in scenarios:
        print(f"\n{'='*60}")
        print(f"Testing: {scenario_name.upper()}")
        print(f"{'='*60}")
        
        filepath = f'data/synthetic/{scenario_name}_scenario.csv'
        
        try:
            # Load scenario
            df = processor.load_scenario(filepath)
            
            # Print statistics
            processor.print_statistics()
            
            # Test frame extraction
            print(f"\n--- Testing Frame Extraction ---")
            frame_0 = processor.get_frame(0)
            print(f"✓ Frame 0: {len(frame_0)} zones")
            
            # Test density grid
            print(f"\n--- Testing Grid Creation ---")
            density_grid = processor.create_density_grid(0)
            print(f"✓ Density grid shape: {density_grid.shape}")
            print(f"  Grid min: {density_grid.min():.2f}")
            print(f"  Grid max: {density_grid.max():.2f}")
            
            # Test zone extraction
            print(f"\n--- Testing Zone Extraction ---")
            zone_data = processor.get_zone_by_coords(5, 5, timestamp=0)
            print(f"✓ Zone (5,5) at t=0:")
            print(f"  Density: {zone_data['density'].values[0]:.2f}")
            print(f"  Speed: {zone_data['movement_speed'].values[0]:.2f}")
            
            # Test high density zones
            print(f"\n--- Testing High Density Detection ---")
            min_ts, max_ts = processor.get_time_range()
            mid_ts = (min_ts + max_ts) // 2
            high_density = processor.get_high_density_zones(mid_ts, threshold=5.0)
            print(f"✓ High density zones at t={mid_ts}: {len(high_density)}")
            
            if len(high_density) > 0:
                print(f"  Top zone: {high_density.iloc[0]['zone_id']} "
                      f"with density {high_density.iloc[0]['density']:.2f}")
            
            print(f"\n✅ {scenario_name.upper()} - ALL TESTS PASSED")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
    
    print(f"\n{'='*60}")
    print("DATA PROCESSOR TEST COMPLETE")
    print(f"{'='*60}")


if __name__ == '__main__':
    test_data_processor()