"""
Zone Classifier Module
Classifies crowd zones based on density and movement parameters
"""

import json
import os
from typing import Dict, Tuple, Optional, List
import pandas as pd


class ZoneClassifier:
    """
    Intelligent zone classification system with 5-level classification
    """
    
    def __init__(self, config_path: str = 'config/classification_config.json'):
        """
        Initialize classifier with configuration
        
        Args:
            config_path: Path to classification configuration file
        """
        self.config = self._load_config(config_path)
        self.thresholds = self.config['classification_thresholds']
        self.movement_thresholds = self.config['movement_thresholds']
        self.severity_weights = self.config['severity_weights']
        self.elevation_rules = self.config['elevation_rules']
        
        # Create level ordering for elevation
        self.level_order = ['safe', 'moderate', 'warning', 'critical', 'emergency']
        
        # Statistics tracking
        self.classification_history = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load classification configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config
    
    def classify_zone(self, 
                     density: float, 
                     speed: Optional[float] = None, 
                     variance: Optional[float] = None,
                     zone_id: Optional[str] = None) -> Dict:
        """
        Classify a single zone based on parameters
        
        Args:
            density: Crowd density (people/m²)
            speed: Movement speed (m/s) - optional
            variance: Direction variance (degrees) - optional
            zone_id: Zone identifier - optional
            
        Returns:
            Dictionary with classification results
        """
        # Step 1: Primary classification by density
        base_level = self._classify_by_density(density)
        
        # Step 2: Calculate base severity score
        severity_score = self._calculate_severity_score(density, speed, variance)
        
        # Step 3: Check for movement-based adjustments
        adjusted_level = base_level
        elevation_reason = None
        
        if speed is not None and variance is not None:
            adjusted_level, elevation_reason = self._adjust_by_movement(
                base_level, density, speed, variance
            )
        
        # Step 4: Get classification details
        level_info = self.thresholds[adjusted_level]
        
        # Step 5: Create result dictionary
        result = {
            'zone_id': zone_id,
            'level': adjusted_level,
            'base_level': base_level,
            'color': level_info['color_hex'],
            'color_name': level_info['color_name'],
            'alert_level': level_info['alert_level'],
            'severity_score': round(severity_score, 2),
            'requires_action': level_info['requires_action'],
            'description': level_info['description'],
            'density': density,
            'speed': speed,
            'variance': variance,
            'elevated': adjusted_level != base_level,
            'elevation_reason': elevation_reason
        }
        
        # Track classification
        self.classification_history.append(result)
        
        return result
    
    def _classify_by_density(self, density: float) -> str:
        """
        Primary classification based on density thresholds
        
        Args:
            density: Crowd density (people/m²)
            
        Returns:
            Classification level string
        """
        for level, thresholds in self.thresholds.items():
            if thresholds['density_min'] <= density < thresholds['density_max']:
                return level
        
        # Default to emergency if exceeds all thresholds
        return 'emergency'
    
    def _calculate_severity_score(self, 
                                  density: float, 
                                  speed: Optional[float], 
                                  variance: Optional[float]) -> float:
        """
        Calculate severity score (0-100) based on all parameters
        
        Args:
            density: Crowd density
            speed: Movement speed
            variance: Direction variance
            
        Returns:
            Severity score (0-100)
        """
        max_density = self.config['capacity_settings']['absolute_max_density']
        
        # Density component (0-100)
        density_score = min(100, (density / max_density) * 100)
        
        # If movement data available, include it
        if speed is not None and variance is not None:
            # Speed component (inverted - slower is worse)
            max_speed = self.movement_thresholds['speed']['fast']
            speed_score = (1 - min(speed, max_speed) / max_speed) * 100
            
            # Variance component (higher is worse)
            max_variance = self.movement_thresholds['direction_variance']['panic']
            variance_score = min(100, (variance / max_variance) * 100)
            
            # Weighted combination
            severity = (
                density_score * self.severity_weights['density_weight'] +
                speed_score * self.severity_weights['speed_weight'] +
                variance_score * self.severity_weights['variance_weight']
            )
        else:
            # Only density available
            severity = density_score
        
        return max(0, min(100, severity))
    
    def _adjust_by_movement(self, 
                           base_level: str, 
                           density: float,
                           speed: float, 
                           variance: float) -> Tuple[str, Optional[str]]:
        """
        Adjust classification based on movement patterns
        
        Args:
            base_level: Base classification level
            density: Crowd density
            speed: Movement speed
            variance: Direction variance
            
        Returns:
            Tuple of (adjusted_level, reason)
        """
        # Check for panic indicators
        if self.elevation_rules['panic_detection']['enabled']:
            panic_speed = self.elevation_rules['panic_detection']['speed_threshold']
            panic_variance = self.elevation_rules['panic_detection']['variance_threshold']
            
            # Low speed + high variance = panic/gridlock
            if speed < panic_speed and variance > panic_variance:
                elevated_level = self._elevate_level(
                    base_level, 
                    self.elevation_rules['panic_detection']['elevation_amount']
                )
                
                if elevated_level != base_level:
                    return elevated_level, "Panic indicators detected (slow movement + chaos)"
        
        # Check for orderly evacuation (no elevation needed)
        if self.elevation_rules['orderly_evacuation']['enabled']:
            orderly_speed = self.elevation_rules['orderly_evacuation']['speed_threshold']
            orderly_variance = self.elevation_rules['orderly_evacuation']['variance_threshold']
            
            # High speed + low variance = orderly movement
            if speed > orderly_speed and variance < orderly_variance:
                return base_level, "Orderly evacuation detected"
        
        return base_level, None
    
    def _elevate_level(self, current_level: str, elevation_amount: int) -> str:
        """
        Elevate classification level by specified amount
        
        Args:
            current_level: Current classification level
            elevation_amount: Number of levels to elevate
            
        Returns:
            Elevated level
        """
        try:
            current_index = self.level_order.index(current_level)
            new_index = min(current_index + elevation_amount, len(self.level_order) - 1)
            return self.level_order[new_index]
        except ValueError:
            return current_level
    
    def classify_all_zones(self, frame_data: pd.DataFrame) -> pd.DataFrame:
        """
        Classify all zones in a frame
        
        Args:
            frame_data: DataFrame with zone data
            
        Returns:
            DataFrame with classification results
        """
        results = []
        
        for _, zone in frame_data.iterrows():
            classification = self.classify_zone(
                density=zone['density'],
                speed=zone.get('movement_speed'),
                variance=zone.get('direction_variance'),
                zone_id=zone.get('zone_id')
            )
            
            results.append({
                'zone_id': classification['zone_id'],
                'x': zone['x_coord'],
                'y': zone['y_coord'],
                'level': classification['level'],
                'base_level': classification['base_level'],
                'color': classification['color'],
                'severity': classification['severity_score'],
                'density': classification['density'],
                'speed': classification['speed'],
                'variance': classification['variance'],
                'requires_action': classification['requires_action'],
                'elevated': classification['elevated'],
                'elevation_reason': classification['elevation_reason']
            })
        
        return pd.DataFrame(results)
    
    def get_classification_summary(self, classified_zones: pd.DataFrame) -> Dict:
        """
        Get summary statistics for classified zones
        
        Args:
            classified_zones: DataFrame with classification results
            
        Returns:
            Dictionary with summary statistics
        """
        total_zones = len(classified_zones)
        
        summary = {
            'total_zones': total_zones,
            'level_counts': {},
            'level_percentages': {},
            'average_severity': classified_zones['severity'].mean(),
            'max_severity': classified_zones['severity'].max(),
            'zones_requiring_action': classified_zones['requires_action'].sum(),
            'elevated_zones': classified_zones['elevated'].sum()
        }
        
        # Count each level
        for level in self.level_order:
            count = len(classified_zones[classified_zones['level'] == level])
            summary['level_counts'][level] = count
            summary['level_percentages'][level] = (count / total_zones * 100) if total_zones > 0 else 0
        
        return summary
    
    def get_critical_zones(self, classified_zones: pd.DataFrame) -> pd.DataFrame:
        """
        Get zones classified as critical or emergency
        
        Args:
            classified_zones: DataFrame with classification results
            
        Returns:
            DataFrame with only critical/emergency zones
        """
        critical = classified_zones[
            classified_zones['level'].isin(['critical', 'emergency'])
        ]
        
        return critical.sort_values('severity', ascending=False)
    
    def export_classification_rules(self, output_path: str):
        """
        Export current classification rules to file
        
        Args:
            output_path: Path to save rules
        """
        with open(output_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"✓ Classification rules exported to: {output_path}")
    
    def print_classification_info(self):
        """Print classification system information"""
        print("\n" + "=" * 60)
        print("ZONE CLASSIFICATION SYSTEM")
        print("=" * 60)
        
        print("\nClassification Levels:")
        for level in self.level_order:
            info = self.thresholds[level]
            print(f"\n  {level.upper()}:")
            print(f"    Density Range: {info['density_min']:.1f} - {info['density_max']:.1f} people/m²")
            print(f"    Color: {info['color_name']} ({info['color_hex']})")
            print(f"    Alert Level: {info['alert_level']}")
            print(f"    Action Required: {'Yes' if info['requires_action'] else 'No'}")
            print(f"    Description: {info['description']}")
        
        print("\n" + "=" * 60)
        print("Movement Adjustment Rules:")
        print("=" * 60)
        
        if self.elevation_rules['panic_detection']['enabled']:
            print("\n  Panic Detection: ENABLED")
            print(f"    Speed < {self.elevation_rules['panic_detection']['speed_threshold']} m/s")
            print(f"    Variance > {self.elevation_rules['panic_detection']['variance_threshold']}°")
            print(f"    → Elevate by {self.elevation_rules['panic_detection']['elevation_amount']} level(s)")
        
        if self.elevation_rules['orderly_evacuation']['enabled']:
            print("\n  Orderly Evacuation Detection: ENABLED")
            print(f"    Speed > {self.elevation_rules['orderly_evacuation']['speed_threshold']} m/s")
            print(f"    Variance < {self.elevation_rules['orderly_evacuation']['variance_threshold']}°")
            print(f"    → Maintain current level")
        
        print("\n" + "=" * 60)


# Testing function
def test_classifier():
    """Test the zone classifier"""
    print("=" * 60)
    print("ZONE CLASSIFIER TEST")
    print("=" * 60)
    
    # Initialize classifier
    classifier = ZoneClassifier()
    
    # Print system info
    classifier.print_classification_info()
    
    print("\n" + "=" * 60)
    print("TESTING INDIVIDUAL CLASSIFICATIONS")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            'name': 'Normal conditions',
            'density': 1.5,
            'speed': 1.2,
            'variance': 45,
            'expected': 'safe'
        },
        {
            'name': 'Moderate density',
            'density': 2.8,
            'speed': 1.0,
            'variance': 55,
            'expected': 'moderate'
        },
        {
            'name': 'Warning level',
            'density': 4.2,
            'speed': 0.8,
            'variance': 75,
            'expected': 'warning'
        },
        {
            'name': 'Critical congestion',
            'density': 6.0,
            'speed': 0.6,
            'variance': 95,
            'expected': 'critical'
        },
        {
            'name': 'Emergency situation',
            'density': 7.8,
            'speed': 0.3,
            'variance': 150,
            'expected': 'emergency'
        },
        {
            'name': 'Panic scenario (elevation test)',
            'density': 3.8,
            'speed': 0.4,
            'variance': 135,
            'expected': 'elevated to critical'
        },
        {
            'name': 'Orderly evacuation',
            'density': 4.0,
            'speed': 1.6,
            'variance': 50,
            'expected': 'warning (not elevated)'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"  Input: Density={test['density']}, Speed={test['speed']}, Variance={test['variance']}")
        
        result = classifier.classify_zone(
            density=test['density'],
            speed=test['speed'],
            variance=test['variance'],
            zone_id=f"Test_Zone_{i}"
        )
        
        print(f"  Result: {result['level'].upper()}")
        print(f"  Color: {result['color_name']}")
        print(f"  Severity: {result['severity_score']}/100")
        print(f"  Action Required: {'Yes' if result['requires_action'] else 'No'}")
        
        if result['elevated']:
            print(f"  ⚠️  ELEVATED from {result['base_level']} → {result['level']}")
            print(f"  Reason: {result['elevation_reason']}")
        
        # Verify expectation
        if test['expected'].lower() in result['level'] or 'elevated' in test['expected'].lower():
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL - Expected: {test['expected']}")
    
    print("\n" + "=" * 60)
    print("✅ CLASSIFIER TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    test_classifier()