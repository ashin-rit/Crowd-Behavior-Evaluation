"""
Alert Manager Module
Manages visual and audio alerts for crowd safety monitoring
"""

import time
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict


class AlertManager:
    """
    Manages multi-level alert system with visual and audio components
    """
    
    def __init__(self, cooldown_seconds: float = 2.5):
        """
        Initialize alert manager
        
        Args:
            cooldown_seconds: Minimum time between same alert types
        """
        self.cooldown_seconds = cooldown_seconds
        
        # Alert configuration
        self.alert_config = self._initialize_alert_config()
        
        # Tracking
        self.last_alert_time = defaultdict(float)
        self.active_alerts = []
        self.alert_history = []
        
        # Statistics
        self.total_alerts_triggered = 0
        self.alerts_by_level = defaultdict(int)
        
    def _initialize_alert_config(self) -> Dict:
        """
        Initialize alert configuration for each level
        
        Returns:
            Dictionary with alert specifications
        """
        config = {
            'safe': {
                'priority': 0,
                'visual': {
                    'color': '#00FF00',
                    'flash': False,
                    'flash_rate': 0,
                    'icon': '✓',
                    'message': 'Normal Operations'
                },
                'audio': {
                    'enabled': False,
                    'frequency': 0,
                    'duration': 0,
                    'beeps': 0,
                    'pattern': []
                }
            },
            'moderate': {
                'priority': 1,
                'visual': {
                    'color': '#7FFF00',
                    'flash': False,
                    'flash_rate': 0,
                    'icon': '⚠',
                    'message': 'Increased Density - Monitor'
                },
                'audio': {
                    'enabled': False,
                    'frequency': 0,
                    'duration': 0,
                    'beeps': 0,
                    'pattern': []
                }
            },
            'warning': {
                'priority': 2,
                'visual': {
                    'color': '#FFFF00',
                    'flash': True,
                    'flash_rate': 1.0,  # Hz
                    'icon': '⚠️',
                    'message': 'HIGH DENSITY WARNING'
                },
                'audio': {
                    'enabled': True,
                    'frequency': 800,  # Hz
                    'duration': 0.3,   # seconds
                    'beeps': 1,
                    'pattern': [('beep', 0.3)]
                }
            },
            'critical': {
                'priority': 3,
                'visual': {
                    'color': '#FF8C00',
                    'flash': True,
                    'flash_rate': 2.0,  # Hz (faster)
                    'icon': '🔴',
                    'message': 'CRITICAL CONGESTION'
                },
                'audio': {
                    'enabled': True,
                    'frequency': 1000,  # Hz
                    'duration': 0.5,    # seconds
                    'beeps': 2,
                    'pattern': [('beep', 0.5), ('pause', 0.2), ('beep', 0.5)]
                }
            },
            'emergency': {
                'priority': 4,
                'visual': {
                    'color': '#FF0000',
                    'flash': True,
                    'flash_rate': 3.0,  # Hz (fastest)
                    'icon': '🚨',
                    'message': 'EMERGENCY - EVACUATE NOW'
                },
                'audio': {
                    'enabled': True,
                    'frequency': 1200,  # Hz
                    'duration': 0.7,    # seconds
                    'beeps': 3,
                    'pattern': [
                        ('beep', 0.7), 
                        ('pause', 0.2), 
                        ('beep', 0.7), 
                        ('pause', 0.2), 
                        ('beep', 0.7)
                    ]
                }
            }
        }
        
        return config
    
    def check_cooldown(self, alert_key: str) -> bool:
        """
        Check if alert is outside cooldown period
        
        Args:
            alert_key: Unique identifier for alert type
            
        Returns:
            True if alert can be triggered
        """
        current_time = time.time()
        last_time = self.last_alert_time.get(alert_key, 0)
        
        if current_time - last_time >= self.cooldown_seconds:
            return True
        
        return False
    
    def trigger_alert(self, level: str, zone_id: str, severity: float) -> Optional[Dict]:
        """
        Trigger an alert for a specific zone and level
        
        Args:
            level: Classification level
            zone_id: Zone identifier
            severity: Severity score (0-100)
            
        Returns:
            Alert information if triggered, None if in cooldown
        """
        # Check if alert should be triggered
        if level not in ['warning', 'critical', 'emergency']:
            return None
        
        # Create alert key
        alert_key = f"{level}_{zone_id}"
        
        # Check cooldown
        if not self.check_cooldown(alert_key):
            return None
        
        # Get alert configuration
        config = self.alert_config[level]
        
        # Create alert object
        alert = {
            'timestamp': time.time(),
            'level': level,
            'zone_id': zone_id,
            'severity': severity,
            'priority': config['priority'],
            'visual': config['visual'].copy(),
            'audio': config['audio'].copy(),
            'alert_key': alert_key
        }
        
        # Update tracking
        self.last_alert_time[alert_key] = time.time()
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        # Update statistics
        self.total_alerts_triggered += 1
        self.alerts_by_level[level] += 1
        
        return alert
    
    def process_classified_zones(self, classified_zones) -> List[Dict]:
        """
        Process all classified zones and trigger appropriate alerts
        
        Args:
            classified_zones: DataFrame with classification results
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        for _, zone in classified_zones.iterrows():
            alert = self.trigger_alert(
                level=zone['level'],
                zone_id=zone['zone_id'],
                severity=zone['severity']
            )
            
            if alert:
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def get_active_alerts(self, max_age_seconds: float = 10.0) -> List[Dict]:
        """
        Get currently active alerts (within time window)
        
        Args:
            max_age_seconds: Maximum age for alert to be considered active
            
        Returns:
            List of active alerts
        """
        current_time = time.time()
        
        active = [
            alert for alert in self.active_alerts
            if current_time - alert['timestamp'] <= max_age_seconds
        ]
        
        # Sort by priority (highest first)
        active.sort(key=lambda x: x['priority'], reverse=True)
        
        return active
    
    def get_priority_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """
        Filter and sort alerts by priority
        
        Args:
            alerts: List of alerts
            
        Returns:
            Sorted list with highest priority first
        """
        # Priority order: emergency > critical > warning
        priority_order = {'emergency': 0, 'critical': 1, 'warning': 2}
        
        sorted_alerts = sorted(
            alerts,
            key=lambda x: (priority_order.get(x['level'], 99), -x['severity'])
        )
        
        return sorted_alerts
    
    def generate_visual_alert(self, alert: Dict) -> Dict:
        """
        Generate visual alert parameters
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Visual alert specifications
        """
        visual = alert['visual']
        
        # Calculate flash state if flashing enabled
        flash_on = True
        if visual['flash']:
            # Calculate current flash state based on time
            elapsed = time.time() - alert['timestamp']
            flash_cycle = 1.0 / visual['flash_rate']
            flash_on = (elapsed % flash_cycle) < (flash_cycle / 2)
        
        return {
            'color': visual['color'] if flash_on or not visual['flash'] else '#FFFFFF',
            'flash': visual['flash'],
            'flash_on': flash_on,
            'icon': visual['icon'],
            'message': visual['message'],
            'level': alert['level'],
            'zone_id': alert['zone_id'],
            'severity': alert['severity']
        }
    
    def generate_audio_alert(self, alert: Dict) -> Dict:
        """
        Generate audio alert parameters
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Audio alert specifications
        """
        audio = alert['audio']
        
        if not audio['enabled']:
            return None
        
        return {
            'frequency': audio['frequency'],
            'duration': audio['duration'],
            'beeps': audio['beeps'],
            'pattern': audio['pattern'],
            'level': alert['level']
        }
    
    def create_alert_banner(self, alerts: List[Dict]) -> str:
        """
        Create formatted alert banner text
        
        Args:
            alerts: List of active alerts
            
        Returns:
            Formatted banner string
        """
        if not alerts:
            return "✓ All zones normal - No alerts"
        
        # Get highest priority alert
        top_alert = alerts[0]
        
        banner = f"{top_alert['visual']['icon']} {top_alert['visual']['message']}"
        
        if len(alerts) > 1:
            banner += f" | +{len(alerts)-1} more alert(s)"
        
        return banner
    
    def get_severity_indicator(self, severity: float) -> Dict:
        """
        Generate severity indicator parameters
        
        Args:
            severity: Severity score (0-100)
            
        Returns:
            Indicator specifications
        """
        # Determine color based on severity
        if severity < 20:
            color = '#00FF00'  # Green
            level_text = 'LOW'
        elif severity < 40:
            color = '#7FFF00'  # Yellow-green
            level_text = 'MODERATE'
        elif severity < 60:
            color = '#FFFF00'  # Yellow
            level_text = 'ELEVATED'
        elif severity < 80:
            color = '#FF8C00'  # Orange
            level_text = 'HIGH'
        else:
            color = '#FF0000'  # Red
            level_text = 'CRITICAL'
        
        return {
            'severity': severity,
            'percentage': severity,
            'color': color,
            'level_text': level_text,
            'bar_filled': int((severity / 100) * 50)  # For ASCII bar
        }
    
    def generate_alert_summary(self, alerts: List[Dict]) -> Dict:
        """
        Generate summary of current alert situation
        
        Args:
            alerts: List of alerts
            
        Returns:
            Summary statistics
        """
        summary = {
            'total_alerts': len(alerts),
            'by_level': {
                'emergency': 0,
                'critical': 0,
                'warning': 0
            },
            'highest_priority': None,
            'highest_severity': 0,
            'zones_affected': set()
        }
        
        for alert in alerts:
            level = alert['level']
            if level in summary['by_level']:
                summary['by_level'][level] += 1
            
            summary['zones_affected'].add(alert['zone_id'])
            
            if alert['severity'] > summary['highest_severity']:
                summary['highest_severity'] = alert['severity']
                summary['highest_priority'] = alert
        
        summary['zones_affected'] = len(summary['zones_affected'])
        
        return summary
    
    def clear_old_alerts(self, max_age_seconds: float = 60.0):
        """
        Remove old alerts from active list
        
        Args:
            max_age_seconds: Maximum age to keep alerts
        """
        current_time = time.time()
        
        self.active_alerts = [
            alert for alert in self.active_alerts
            if current_time - alert['timestamp'] <= max_age_seconds
        ]
    
    def reset_alerts(self):
        """Reset all active alerts and cooldowns"""
        self.active_alerts = []
        self.last_alert_time = defaultdict(float)
    
    def get_statistics(self) -> Dict:
        """
        Get alert system statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_alerts_triggered': self.total_alerts_triggered,
            'alerts_by_level': dict(self.alerts_by_level),
            'active_alerts_count': len(self.active_alerts),
            'cooldown_seconds': self.cooldown_seconds
        }
    
    def print_alert_config(self):
        """Print alert configuration"""
        print("\n" + "=" * 80)
        print("ALERT SYSTEM CONFIGURATION")
        print("=" * 80)
        
        print(f"\nCooldown Period: {self.cooldown_seconds} seconds")
        
        for level in ['safe', 'moderate', 'warning', 'critical', 'emergency']:
            config = self.alert_config[level]
            
            print(f"\n{level.upper()}:")
            print(f"  Priority: {config['priority']}")
            print(f"  Visual:")
            print(f"    Color: {config['visual']['color']}")
            print(f"    Flash: {config['visual']['flash']}")
            if config['visual']['flash']:
                print(f"    Flash Rate: {config['visual']['flash_rate']} Hz")
            print(f"    Icon: {config['visual']['icon']}")
            print(f"    Message: {config['visual']['message']}")
            
            print(f"  Audio:")
            if config['audio']['enabled']:
                print(f"    Enabled: Yes")
                print(f"    Frequency: {config['audio']['frequency']} Hz")
                print(f"    Duration: {config['audio']['duration']}s")
                print(f"    Beeps: {config['audio']['beeps']}")
            else:
                print(f"    Enabled: No")
        
        print("\n" + "=" * 80)


# Testing function
def test_alert_manager():
    """Test the alert manager"""
    print("=" * 80)
    print("ALERT MANAGER TEST")
    print("=" * 80)
    
    # Initialize manager
    manager = AlertManager(cooldown_seconds=2.0)
    
    # Print configuration
    manager.print_alert_config()
    
    print("\n" + "=" * 80)
    print("TESTING ALERT TRIGGERING")
    print("=" * 80)
    
    # Test individual alerts
    test_cases = [
        {'level': 'safe', 'zone_id': 'Zone_1_1', 'severity': 15.0},
        {'level': 'moderate', 'zone_id': 'Zone_2_2', 'severity': 32.0},
        {'level': 'warning', 'zone_id': 'Zone_3_3', 'severity': 48.5},
        {'level': 'critical', 'zone_id': 'Zone_4_4', 'severity': 68.2},
        {'level': 'emergency', 'zone_id': 'Zone_5_5', 'severity': 89.7},
    ]
    
    triggered_alerts = []
    
    for test in test_cases:
        print(f"\nTriggering alert: {test['level'].upper()} - {test['zone_id']}")
        
        alert = manager.trigger_alert(
            level=test['level'],
            zone_id=test['zone_id'],
            severity=test['severity']
        )
        
        if alert:
            print(f"  ✓ Alert triggered")
            print(f"    Priority: {alert['priority']}")
            print(f"    Visual: {alert['visual']['icon']} {alert['visual']['message']}")
            print(f"    Flash: {alert['visual']['flash']}")
            
            if alert['audio']['enabled']:
                print(f"    Audio: {alert['audio']['beeps']} beep(s) at {alert['audio']['frequency']}Hz")
            else:
                print(f"    Audio: Disabled")
            
            triggered_alerts.append(alert)
        else:
            print(f"  ⊘ No alert (level: {test['level']})")
    
    # Test cooldown
    print("\n" + "=" * 80)
    print("TESTING COOLDOWN MECHANISM")
    print("=" * 80)
    
    print("\nAttempting to re-trigger same alert immediately...")
    duplicate = manager.trigger_alert('warning', 'Zone_3_3', 48.5)
    
    if duplicate:
        print("  ✗ FAIL - Cooldown not working")
    else:
        print("  ✓ PASS - Alert blocked by cooldown")
    
    print(f"\nWaiting {manager.cooldown_seconds + 0.5} seconds...")
    time.sleep(manager.cooldown_seconds + 0.5)
    
    print("Attempting to re-trigger after cooldown...")
    after_cooldown = manager.trigger_alert('warning', 'Zone_3_3', 48.5)
    
    if after_cooldown:
        print("  ✓ PASS - Alert triggered after cooldown")
    else:
        print("  ✗ FAIL - Alert still blocked")
    
    # Test visual generation
    print("\n" + "=" * 80)
    print("TESTING VISUAL ALERT GENERATION")
    print("=" * 80)
    
    for alert in triggered_alerts[:3]:
        visual = manager.generate_visual_alert(alert)
        print(f"\n{alert['zone_id']} ({alert['level'].upper()}):")
        print(f"  Icon: {visual['icon']}")
        print(f"  Message: {visual['message']}")
        print(f"  Color: {visual['color']}")
        print(f"  Flash State: {'ON' if visual['flash_on'] else 'OFF'}")
    
    # Test severity indicator
    print("\n" + "=" * 80)
    print("TESTING SEVERITY INDICATOR")
    print("=" * 80)
    
    test_severities = [15, 35, 55, 75, 95]
    
    for sev in test_severities:
        indicator = manager.get_severity_indicator(sev)
        bar = '█' * indicator['bar_filled'] + '░' * (50 - indicator['bar_filled'])
        
        print(f"\nSeverity: {sev}/100")
        print(f"  Level: {indicator['level_text']}")
        print(f"  Color: {indicator['color']}")
        print(f"  Bar: [{bar}]")
    
    # Test alert summary
    print("\n" + "=" * 80)
    print("TESTING ALERT SUMMARY")
    print("=" * 80)
    
    active = manager.get_active_alerts()
    summary = manager.generate_alert_summary(active)
    
    print(f"\nTotal Active Alerts: {summary['total_alerts']}")
    print(f"Zones Affected: {summary['zones_affected']}")
    print(f"Highest Severity: {summary['highest_severity']:.1f}/100")
    
    print("\nAlerts by Level:")
    for level in ['emergency', 'critical', 'warning']:
        count = summary['by_level'][level]
        if count > 0:
            print(f"  {level.capitalize():12} {count}")
    
    # Test banner
    print("\n" + "=" * 80)
    print("TESTING ALERT BANNER")
    print("=" * 80)
    
    banner = manager.create_alert_banner(active)
    print(f"\nAlert Banner: {banner}")
    
    # Test statistics
    print("\n" + "=" * 80)
    print("ALERT SYSTEM STATISTICS")
    print("=" * 80)
    
    stats = manager.get_statistics()
    print(f"\nTotal Alerts Triggered: {stats['total_alerts_triggered']}")
    print(f"Active Alerts: {stats['active_alerts_count']}")
    
    print("\nAlerts by Level:")
    for level, count in stats['alerts_by_level'].items():
        print(f"  {level.capitalize():12} {count}")
    
    print("\n" + "=" * 80)
    print("✅ ALERT MANAGER TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_alert_manager()