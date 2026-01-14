"""
Complete Alert System Integration Test
Tests classification + instructions + alerts together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_processor import CrowdDataProcessor
from src.classification.zone_classifier import ZoneClassifier
from src.alerts.instruction_generator import InstructionGenerator
from src.alerts.alert_manager import AlertManager
import time


def test_complete_system(scenario_name: str, timestamp: int):
    """Test complete alert system with scenario"""
    
    print("\n" + "=" * 80)
    print(f"COMPLETE SYSTEM TEST: {scenario_name.upper()} - Frame {timestamp}")
    print("=" * 80)
    
    # Initialize all components
    processor = CrowdDataProcessor()
    classifier = ZoneClassifier()
    instructor = InstructionGenerator()
    alert_mgr = AlertManager(cooldown_seconds=0.5)  # Short cooldown for testing
    
    # Load and process data
    print("\n1. Loading scenario data...")
    filepath = f'data/synthetic/{scenario_name}_scenario.csv'
    processor.load_scenario(filepath)
    frame_data = processor.get_frame(timestamp)
    print(f"   ✓ Loaded {len(frame_data)} zones")
    
    # Classify zones
    print("\n2. Classifying zones...")
    classified = classifier.classify_all_zones(frame_data)
    class_summary = classifier.get_classification_summary(classified)
    print(f"   ✓ Classified {len(classified)} zones")
    print(f"   - Emergency: {class_summary['level_counts']['emergency']}")
    print(f"   - Critical: {class_summary['level_counts']['critical']}")
    print(f"   - Warning: {class_summary['level_counts']['warning']}")
    
    # Generate instructions
    print("\n3. Generating instructions...")
    instructions = instructor.generate_batch_instructions(classified)
    inst_summary = instructor.generate_summary_report(instructions)
    print(f"   ✓ Generated {len(instructions)} instructions")
    print(f"   - Immediate Action Required: {inst_summary['requires_immediate_action']}")
    
    # Trigger alerts
    print("\n4. Processing alerts...")
    triggered_alerts = alert_mgr.process_classified_zones(classified)
    print(f"   ✓ Triggered {len(triggered_alerts)} alerts")
    
    # Get active alerts
    active_alerts = alert_mgr.get_active_alerts()
    priority_alerts = alert_mgr.get_priority_alerts(active_alerts)
    
    # Display alert information
    if priority_alerts:
        print("\n" + "=" * 80)
        print("ACTIVE ALERTS (Priority Order)")
        print("=" * 80)
        
        for i, alert in enumerate(priority_alerts[:5], 1):
            visual = alert_mgr.generate_visual_alert(alert)
            
            print(f"\n{i}. {visual['icon']} {alert['zone_id']} - {alert['level'].upper()}")
            print(f"   Severity: {alert['severity']:.1f}/100")
            print(f"   Message: {visual['message']}")
            print(f"   Flash: {'Yes' if visual['flash'] else 'No'}")
            
            if alert['audio']['enabled']:
                audio = alert['audio']
                print(f"   Audio: {audio['beeps']} beep(s) at {audio['frequency']}Hz")
        
        if len(priority_alerts) > 5:
            print(f"\n   ... and {len(priority_alerts) - 5} more alerts")
    
    # Display alert banner
    print("\n" + "=" * 80)
    print("ALERT BANNER")
    print("=" * 80)
    banner = alert_mgr.create_alert_banner(active_alerts)
    print(f"\n{banner}")
    
    # Display severity indicator
    if priority_alerts:
        top_alert = priority_alerts[0]
        indicator = alert_mgr.get_severity_indicator(top_alert['severity'])
        bar = '█' * indicator['bar_filled'] + '░' * (50 - indicator['bar_filled'])
        
        print("\n" + "=" * 80)
        print("SEVERITY INDICATOR")
        print("=" * 80)
        print(f"\n[{bar}]")
        print(f"{indicator['severity']:.1f}/100 - {indicator['level_text']}")
    
    # Display summary statistics
    print("\n" + "=" * 80)
    print("SYSTEM SUMMARY")
    print("=" * 80)
    
    alert_summary = alert_mgr.generate_alert_summary(active_alerts)
    
    print(f"\nZone Statistics:")
    print(f"  Total Zones: {len(classified)}")
    print(f"  Safe Zones: {class_summary['level_counts']['safe']}")
    print(f"  Zones Requiring Action: {class_summary['zones_requiring_action']}")
    print(f"  Zones with Active Alerts: {alert_summary['zones_affected']}")
    
    print(f"\nAlert Statistics:")
    print(f"  Active Alerts: {alert_summary['total_alerts']}")
    print(f"  Emergency: {alert_summary['by_level']['emergency']}")
    print(f"  Critical: {alert_summary['by_level']['critical']}")
    print(f"  Warning: {alert_summary['by_level']['warning']}")
    print(f"  Highest Severity: {alert_summary['highest_severity']:.1f}/100")
    
    print(f"\nInstructions:")
    print(f"  Total Generated: {inst_summary['total_instructions']}")
    print(f"  Priority Actions: {inst_summary['requires_immediate_action']}")
    
    # Show top priority instruction
    if priority_alerts:
        top_alert = priority_alerts[0]
        top_instruction = next(
            (inst for inst in instructions if inst['zone_id'] == top_alert['zone_id']),
            None
        )
        
        if top_instruction:
            print("\n" + "=" * 80)
            print("TOP PRIORITY INSTRUCTION")
            print("=" * 80)
            print(f"\n{instructor.format_instruction_display(top_instruction)}")
    
    return {
        'classified': classified,
        'instructions': instructions,
        'alerts': active_alerts,
        'summary': {
            'classification': class_summary,
            'instructions': inst_summary,
            'alerts': alert_summary
        }
    }


def run_all_scenarios():
    """Run complete system test on all scenarios"""
    
    print("=" * 80)
    print("COMPLETE ALERT SYSTEM - ALL SCENARIOS TEST")
    print("=" * 80)
    
    test_cases = [
        ('normal', 100),
        ('rush_hour', 100),
        ('emergency', 75),
        ('event_end', 200)
    ]
    
    results = []
    
    for scenario, timestamp in test_cases:
        result = test_complete_system(scenario, timestamp)
        results.append({
            'scenario': scenario,
            'timestamp': timestamp,
            'data': result
        })
        
        # Small delay between scenarios
        time.sleep(1)
    
    # Overall comparison
    print("\n\n" + "=" * 80)
    print("SCENARIO COMPARISON")
    print("=" * 80)
    
    print(f"\n{'Scenario':<15} {'Alerts':<8} {'Emergency':<10} {'Critical':<10} {'Warning':<10}")
    print("-" * 80)
    
    for result in results:
        summary = result['data']['summary']['alerts']
        print(f"{result['scenario']:<15} "
              f"{summary['total_alerts']:<8} "
              f"{summary['by_level']['emergency']:<10} "
              f"{summary['by_level']['critical']:<10} "
              f"{summary['by_level']['warning']:<10}")
    
    print("\n" + "=" * 80)
    print("✅ ALL SCENARIOS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    run_all_scenarios()