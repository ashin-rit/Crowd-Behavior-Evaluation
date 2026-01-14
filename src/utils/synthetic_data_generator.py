"""
Synthetic Crowd Data Generator
Generates realistic crowd behavior scenarios for testing
"""

import numpy as np
import pandas as pd
import os


class SyntheticCrowdGenerator:
    """
    Generates synthetic crowd behavior data for different scenarios
    """
    
    def __init__(self, grid_size=(10, 10), zone_area=10):
        """
        Initialize generator
        
        Args:
            grid_size: Tuple (rows, cols) for venue grid
            zone_area: Area of each zone in square meters
        """
        self.grid_rows = grid_size[0]
        self.grid_cols = grid_size[1]
        self.zone_area = zone_area
        self.total_zones = self.grid_rows * self.grid_cols
        
    def generate_normal_scenario(self, duration=200, seed=42):
        """
        Generate normal crowd behavior scenario
        Low to moderate density, regular movement
        """
        print("Generating Normal Scenario...")
        np.random.seed(seed)
        
        data = []
        
        for t in range(duration):
            for i in range(self.grid_rows):
                for j in range(self.grid_cols):
                    # Base density: low to moderate
                    base_density = np.random.uniform(0.5, 2.5)
                    
                    # Add spatial correlation (nearby zones similar)
                    spatial_noise = np.random.normal(0, 0.2)
                    
                    # Add temporal continuity (smooth changes)
                    temporal_factor = 1.0 + 0.1 * np.sin(t / 20)
                    
                    # Final density
                    density = max(0, base_density + spatial_noise) * temporal_factor
                    
                    # Movement parameters (normal behavior)
                    speed = np.random.uniform(0.8, 1.5)  # Normal walking
                    direction_variance = np.random.uniform(20, 60)  # Some variation
                    
                    # Calculate people count
                    people_count = int(density * self.zone_area)
                    
                    # Create record
                    data.append({
                        'timestamp': t,
                        'zone_id': f'Zone_{i}_{j}',
                        'x_coord': i,
                        'y_coord': j,
                        'density': round(density, 2),
                        'people_count': people_count,
                        'movement_speed': round(speed, 2),
                        'direction_variance': round(direction_variance, 1)
                    })
        
        df = pd.DataFrame(data)
        print(f"✓ Normal Scenario: {len(df)} records generated")
        return df
    
    def generate_rush_hour_scenario(self, duration=200, seed=43):
        """
        Generate rush hour scenario
        Moderate to high density, some warning zones
        """
        print("Generating Rush Hour Scenario...")
        np.random.seed(seed)
        
        data = []
        
        # Define high-traffic zones (entrance, popular areas)
        high_traffic_zones = [
            (0, 4), (0, 5),  # Top entrance
            (5, 5), (5, 6),  # Center (popular area)
            (9, 4), (9, 5)   # Bottom entrance
        ]
        
        for t in range(duration):
            for i in range(self.grid_rows):
                for j in range(self.grid_cols):
                    # Check if high-traffic zone
                    is_high_traffic = (i, j) in high_traffic_zones
                    
                    if is_high_traffic:
                        # Higher density in traffic zones
                        base_density = np.random.uniform(3.0, 5.0)
                        speed = np.random.uniform(0.5, 1.0)  # Slower due to crowding
                        direction_variance = np.random.uniform(60, 100)  # More chaotic
                    else:
                        # Normal density elsewhere
                        base_density = np.random.uniform(2.0, 3.5)
                        speed = np.random.uniform(0.8, 1.3)
                        direction_variance = np.random.uniform(40, 70)
                    
                    # Spatial correlation
                    if i > 0:
                        # Influence from row above
                        spatial_noise = np.random.normal(0, 0.3)
                        base_density += spatial_noise
                    
                    # Temporal variation (rush builds and subsides)
                    rush_factor = 1.0 + 0.3 * np.sin(t / 30)
                    density = max(0, base_density * rush_factor)
                    
                    people_count = int(density * self.zone_area)
                    
                    data.append({
                        'timestamp': t,
                        'zone_id': f'Zone_{i}_{j}',
                        'x_coord': i,
                        'y_coord': j,
                        'density': round(density, 2),
                        'people_count': people_count,
                        'movement_speed': round(speed, 2),
                        'direction_variance': round(direction_variance, 1)
                    })
        
        df = pd.DataFrame(data)
        print(f"✓ Rush Hour Scenario: {len(df)} records generated")
        return df
    
    def generate_emergency_scenario(self, duration=150, seed=44):
        """
        Generate emergency/panic scenario
        High density, erratic movement, critical zones
        """
        print("Generating Emergency Scenario...")
        np.random.seed(seed)
        
        data = []
        
        # Emergency starts at timestamp 30
        emergency_start = 30
        
        for t in range(duration):
            for i in range(self.grid_rows):
                for j in range(self.grid_cols):
                    # Calculate distance from exits (bottom rows are exits)
                    dist_from_exit = abs(i - 9) + abs(j - 5)
                    
                    if t < emergency_start:
                        # Normal conditions before emergency
                        base_density = np.random.uniform(2.0, 4.0)
                        speed = np.random.uniform(0.8, 1.4)
                        direction_variance = np.random.uniform(30, 60)
                    else:
                        # Emergency conditions
                        # Higher density near exits (everyone rushing there)
                        exit_factor = 1.0 + (10 - dist_from_exit) / 10
                        
                        # Panic builds over time
                        panic_factor = 1.0 + (t - emergency_start) / 100
                        
                        base_density = np.random.uniform(4.0, 7.5) * exit_factor
                        
                        # Panic movement: very slow due to crowding
                        speed = np.random.uniform(0.2, 0.8)
                        
                        # High direction variance (chaotic)
                        direction_variance = np.random.uniform(100, 180) * panic_factor
                    
                    # Spatial correlation (panic spreads)
                    spatial_noise = np.random.normal(0, 0.4)
                    density = max(0, min(10, base_density + spatial_noise))  # Cap at 10
                    
                    people_count = int(density * self.zone_area)
                    
                    data.append({
                        'timestamp': t,
                        'zone_id': f'Zone_{i}_{j}',
                        'x_coord': i,
                        'y_coord': j,
                        'density': round(density, 2),
                        'people_count': people_count,
                        'movement_speed': round(speed, 2),
                        'direction_variance': round(direction_variance, 1)
                    })
        
        df = pd.DataFrame(data)
        print(f"✓ Emergency Scenario: {len(df)} records generated")
        return df
    
    def generate_event_end_scenario(self, duration=250, seed=45):
        """
        Generate event ending scenario
        Gradually increasing density as people leave
        """
        print("Generating Event End Scenario...")
        np.random.seed(seed)
        
        data = []
        
        # Exit locations (people move toward these)
        exit_zones = [
            (9, 2), (9, 3),  # West exit
            (9, 7), (9, 8),  # East exit
            (0, 4), (0, 5)   # North exit
        ]
        
        for t in range(duration):
            # Density gradually increases as event ends
            time_factor = t / duration  # 0 to 1
            
            for i in range(self.grid_rows):
                for j in range(self.grid_cols):
                    # Calculate distance to nearest exit
                    min_dist = min(
                        abs(i - ex) + abs(j - ey) 
                        for ex, ey in exit_zones
                    )
                    
                    # Density higher near exits as time progresses
                    base_density = 1.0 + 5.0 * time_factor
                    
                    # Exit proximity factor (more crowded near exits)
                    exit_proximity = 1.0 + (10 - min_dist) / 15
                    
                    density = base_density * exit_proximity
                    
                    # Movement speed depends on density
                    if density < 3:
                        speed = np.random.uniform(1.0, 1.5)  # Fast
                    elif density < 5:
                        speed = np.random.uniform(0.6, 1.0)  # Moderate
                    else:
                        speed = np.random.uniform(0.3, 0.6)  # Slow
                    
                    # Direction variance increases with density
                    direction_variance = 30 + min(100, density * 15)
                    
                    # Add randomness
                    density += np.random.normal(0, 0.3)
                    density = max(0, min(8, density))  # Clamp between 0-8
                    
                    people_count = int(density * self.zone_area)
                    
                    data.append({
                        'timestamp': t,
                        'zone_id': f'Zone_{i}_{j}',
                        'x_coord': i,
                        'y_coord': j,
                        'density': round(density, 2),
                        'people_count': people_count,
                        'movement_speed': round(speed, 2),
                        'direction_variance': round(direction_variance, 1)
                    })
        
        df = pd.DataFrame(data)
        print(f"✓ Event End Scenario: {len(df)} records generated")
        return df
    
    def save_scenario(self, df, scenario_name, output_dir='data/synthetic'):
        """
        Save scenario to CSV file
        """
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = f'{scenario_name.lower().replace(" ", "_")}_scenario.csv'
        filepath = os.path.join(output_dir, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to: {filepath}")
        
        return filepath
    
    def generate_all_scenarios(self):
        """
        Generate all 4 scenarios and save them
        """
        print("=" * 60)
        print("SYNTHETIC CROWD DATA GENERATION")
        print("=" * 60)
        print()
        
        scenarios = []
        
        # 1. Normal Scenario
        df_normal = self.generate_normal_scenario(duration=200)
        path_normal = self.save_scenario(df_normal, 'normal')
        scenarios.append(('Normal', df_normal, path_normal))
        print()
        
        # 2. Rush Hour Scenario
        df_rush = self.generate_rush_hour_scenario(duration=200)
        path_rush = self.save_scenario(df_rush, 'rush_hour')
        scenarios.append(('Rush Hour', df_rush, path_rush))
        print()
        
        # 3. Emergency Scenario
        df_emergency = self.generate_emergency_scenario(duration=150)
        path_emergency = self.save_scenario(df_emergency, 'emergency')
        scenarios.append(('Emergency', df_emergency, path_emergency))
        print()
        
        # 4. Event End Scenario
        df_event = self.generate_event_end_scenario(duration=250)
        path_event = self.save_scenario(df_event, 'event_end')
        scenarios.append(('Event End', df_event, path_event))
        print()
        
        print("=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        
        # Print summary
        print("\nSummary:")
        for name, df, path in scenarios:
            print(f"  {name:15} - {len(df):6} records - {path}")
        
        return scenarios


# Main execution
if __name__ == '__main__':
    # Create generator
    generator = SyntheticCrowdGenerator(grid_size=(10, 10), zone_area=10)
    
    # Generate all scenarios
    scenarios = generator.generate_all_scenarios()
    
    print("\n✅ All scenarios generated successfully!")
    print("\nNext step: Verify the data quality")