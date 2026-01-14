"""
Test Instruction Generator with Real Scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_processor import CrowdDataProcessor
from src.classification.zone_classifier import ZoneClassifier
from src.alerts.instruction_generator import InstructionGenerator


def test_scenario_instructions(scenario_name: str, timestamp: int):
    """Test instruction generation with real scenario"""
    
    print("\n" + "=" * 80)
    print(f"SCENARIO: {scenario_name.upper()} - Frame {timestamp}")
    print("=" * 80)
    
    # Load and process data
    processor = CrowdDataProcessor()
    filepath = f'data/synthetic/{scenario_name}_scenario.csv'
    processor.load_scenario(filepath)
    
    frame_data = processor.get_frame(timestamp)
    
    # Classify zones
    classifier = ZoneClassifier()
    classified = classifier.classify_all_zones(frame_data)
    
    # Generate instructions
    generator = InstructionGenerator()
    instructions = generator.generate_batch_instructions(classified)
    
    # Get summary
    summary = generator.generate_summary_report(instructions)
    class_summary = classifier.get_classification_summary(classified)
    
    # Print classification summary
    print("\n--- Classification Summary ---")
    print(f"Total Zones: {class_summary['total_zones']}")
    print(f"Average Severity: {class_summary['average_severity']:.1f}/100")
    print(f"Zones Requiring Action: {class_summary['zones_requiring_action']}")
    
    print("\nLevel Distribution:")
    for level in ['safe', 'moderate', 'warning', 'critical', 'emergency']:
        count = class_summary['level_counts'][level]
        pct = class_summary['level_percentages'][level]
        if count > 0:
            print(f"  {level.capitalize():12} {count:3} ({pct:5.1f}%)")
    
    # Print instruction summary
    print("\n--- Instruction Summary ---")
    print(f"Total Instructions Generated: {summary['total_instructions']}")
    print(f"Immediate Action Required: {summary['requires_immediate_action']}")
    
    print("\nPriority Breakdown:")
    for priority in ['EMERGENCY', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = summary['priority_breakdown'][priority]
        if count > 0:
            print(f"  {priority:12} {count}")
    
    print("\nExit Load Distribution:")
    for exit_name, count in sorted(summary['exit_usage'].items()):
        pct = (count / summary['total_instructions']) * 100
        print(f"  {exit_name:12} {count:3} zones ({pct:5.1f}%)")
    
    # Show priority instructions
    priority_instructions = generator.get_priority_instructions(instructions)
    
    if priority_instructions:
        print("\n" + "=" * 80)
        print("HIGH-PRIORITY INSTRUCTIONS")
        print("=" * 80)
        
        for inst in priority_instructions[:10]:  # Show top 10
            print(f"\n{generator.format_instruction_display(inst)}")
    
    # Export instructions
    output_dir = 'results/instructions'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/{scenario_name}_frame_{timestamp}_instructions.json'
    generator.export_instructions(instructions, output_file)
    
    return instructions, summary


def run_all_scenario_tests():
    """Run instruction tests on all scenarios"""
    
    print("=" * 80)
    print("COMPREHENSIVE INSTRUCTION GENERATION TEST")
    print("=" * 80)
    
    test_cases = [
        ('normal', 100),
        ('rush_hour', 100),
        ('emergency', 75),
        ('event_end', 200)
    ]
    
    all_results = []
    
    for scenario, timestamp in test_cases:
        instructions, summary = test_scenario_instructions(scenario, timestamp)
        all_results.append({
            'scenario': scenario,
            'timestamp': timestamp,
            'summary': summary
        })
    
    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    for result in all_results:
        print(f"\n{result['scenario'].upper()} (Frame {result['timestamp']}):")
        print(f"  Total Instructions: {result['summary']['total_instructions']}")
        print(f"  Immediate Action: {result['summary']['requires_immediate_action']}")
        print(f"  Emergency: {result['summary']['priority_breakdown']['EMERGENCY']}")
        print(f"  Critical: {result['summary']['priority_breakdown']['CRITICAL']}")
    
    print("\n" + "=" * 80)
    print("✅ ALL SCENARIO TESTS COMPLETE")
    print("=" * 80)
    print("\nCheck 'results/instructions/' for exported JSON files")


if __name__ == '__main__':
    run_all_scenario_tests()