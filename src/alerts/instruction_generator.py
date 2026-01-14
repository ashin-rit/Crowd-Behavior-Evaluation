"""
Instruction Generator Module
Generates zone-specific evacuation and crowd control instructions
"""

from typing import Dict, List, Tuple, Optional
import json


class InstructionGenerator:
    """
    Generates zone-specific instructions based on classification and location
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (10, 10)):
        """
        Initialize instruction generator
        
        Args:
            grid_size: Tuple of (rows, cols) for venue grid
        """
        self.grid_rows = grid_size[0]
        self.grid_cols = grid_size[1]
        
        # Define exit mappings
        self.exit_map = self._define_exit_regions()
        
        # Define instruction templates
        self.instruction_templates = self._create_instruction_templates()
        
        # Track generated instructions
        self.instruction_history = []
    
    def _define_exit_regions(self) -> Dict[str, List[Tuple[int, int]]]:
        """
        Define which zones belong to which exit regions
        
        Returns:
            Dictionary mapping exit names to zone coordinates
        """
        exit_regions = {
            'North': [],
            'South': [],
            'East': [],
            'West': [],
            'Central': []
        }
        
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                # North exit region (rows 0-2)
                if i <= 2:
                    exit_regions['North'].append((i, j))
                
                # South exit region (rows 7-9)
                elif i >= 7:
                    exit_regions['South'].append((i, j))
                
                # East exit region (columns 7-9)
                elif j >= 7:
                    exit_regions['East'].append((i, j))
                
                # West exit region (columns 0-2)
                elif j <= 2:
                    exit_regions['West'].append((i, j))
                
                # Central region (middle zones)
                else:
                    exit_regions['Central'].append((i, j))
        
        return exit_regions
    
    def _create_instruction_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Create instruction templates for each classification level
        
        Returns:
            Dictionary of instruction templates
        """
        templates = {
            'safe': {
                'single_exit': "Zone {zone_id}: ✓ NORMAL OPERATIONS. Continue monitoring conditions. Nearest exit: {exit_name}.",
                
                'multiple_exits': "Zone {zone_id}: ✓ NORMAL OPERATIONS. Continue monitoring conditions. Available exits: {exit_list}.",
                
                'icon': '✓',
                'priority': 'LOW'
            },
            
            'moderate': {
                'single_exit': "Zone {zone_id}: ⚠ INCREASED DENSITY detected. Maintain orderly movement. "
                              "If evacuation needed, proceed toward {exit_name} exit. Monitor for escalation.",
                
                'multiple_exits': "Zone {zone_id}: ⚠ INCREASED DENSITY detected. Maintain orderly movement. "
                                 "If evacuation needed, available exits: {exit_list}. Monitor for escalation.",
                
                'icon': '⚠',
                'priority': 'MEDIUM'
            },
            
            'warning': {
                'single_exit': "Zone {zone_id}: ⚠️ HIGH DENSITY WARNING! Slow crowd movement immediately. "
                              "Prepare for possible redirection to {exit_name} exit. "
                              "Deploy security personnel. Restrict new entries to this zone.",
                
                'multiple_exits': "Zone {zone_id}: ⚠️ HIGH DENSITY WARNING! Slow crowd movement immediately. "
                                 "Prepare for possible redirection. Optimal exit routes: {exit_list}. "
                                 "Deploy security personnel. Restrict new entries to this zone.",
                
                'icon': '⚠️',
                'priority': 'HIGH'
            },
            
            'critical': {
                'single_exit': "Zone {zone_id}: 🔴 CRITICAL CONGESTION! IMMEDIATE ACTION REQUIRED. "
                              "RESTRICT all entry to this zone. BEGIN controlled evacuation via {exit_name} exit. "
                              "Deploy all available personnel. Situation severity: {severity}/100. "
                              "Potential for escalation to emergency.",
                
                'multiple_exits': "Zone {zone_id}: 🔴 CRITICAL CONGESTION! IMMEDIATE ACTION REQUIRED. "
                                 "RESTRICT all entry to this zone. BEGIN controlled evacuation. "
                                 "Direct crowd to: {exit_list}. Deploy all available personnel. "
                                 "Situation severity: {severity}/100. Potential for escalation to emergency.",
                
                'icon': '🔴',
                'priority': 'CRITICAL'
            },
            
            'emergency': {
                'single_exit': "Zone {zone_id}: 🚨 EMERGENCY - EVACUATE NOW! "
                              "IMMEDIATE evacuation required via {exit_name} exit. "
                              "ALL PERSONNEL: Priority response needed. Severity: {severity}/100. "
                              "⚠️ POTENTIAL STAMPEDE RISK. Activate emergency protocols. "
                              "Clear evacuation path. Prevent entry from all directions.",
                
                'multiple_exits': "Zone {zone_id}: 🚨 EMERGENCY - EVACUATE NOW! "
                                 "IMMEDIATE evacuation required. Direct to nearest: {exit_list}. "
                                 "ALL PERSONNEL: Priority response needed. Severity: {severity}/100. "
                                 "⚠️ POTENTIAL STAMPEDE RISK. Activate emergency protocols. "
                                 "Clear all evacuation paths. Prevent entry from all directions.",
                
                'icon': '🚨',
                'priority': 'EMERGENCY'
            }
        }
        
        return templates
    
    def get_zone_region(self, x: int, y: int) -> str:
        """
        Determine which exit region a zone belongs to
        
        Args:
            x: Row coordinate
            y: Column coordinate
            
        Returns:
            Region name (North, South, East, West, Central)
        """
        for region, zones in self.exit_map.items():
            if (x, y) in zones:
                return region
        
        return 'Central'  # Default
    
    def get_nearest_exits(self, x: int, y: int, max_exits: int = 2) -> List[str]:
        """
        Get nearest exits for a zone, ordered by distance
        
        Args:
            x: Row coordinate
            y: Column coordinate
            max_exits: Maximum number of exits to return
            
        Returns:
            List of exit names, ordered by proximity
        """
        # Define exit locations (approximate centers of exit zones)
        exit_locations = {
            'North': (0, 5),
            'South': (9, 5),
            'East': (5, 9),
            'West': (5, 0)
        }
        
        # Calculate distances
        distances = []
        for exit_name, (ex, ey) in exit_locations.items():
            distance = abs(x - ex) + abs(y - ey)  # Manhattan distance
            distances.append((distance, exit_name))
        
        # Sort by distance and return nearest exits
        distances.sort()
        nearest = [exit_name for _, exit_name in distances[:max_exits]]
        
        return nearest
    
    def generate_instruction(self, 
                           zone_id: str,
                           x: int,
                           y: int,
                           level: str,
                           severity: float) -> Dict:
        """
        Generate zone-specific instruction
        
        Args:
            zone_id: Zone identifier
            x: Row coordinate
            y: Column coordinate
            level: Classification level
            severity: Severity score (0-100)
            
        Returns:
            Dictionary with instruction details
        """
        # Get nearest exits
        nearest_exits = self.get_nearest_exits(x, y)
        primary_exit = nearest_exits[0]
        
        # Get region
        region = self.get_zone_region(x, y)
        
        # Get template
        template_data = self.instruction_templates.get(level, self.instruction_templates['safe'])
        
        # Choose template based on number of nearby exits
        if region == 'Central' or len(nearest_exits) > 1:
            template = template_data['multiple_exits']
            exit_list = ' and '.join(nearest_exits)
            instruction_text = template.format(
                zone_id=zone_id,
                exit_list=exit_list,
                severity=f"{severity:.1f}"
            )
        else:
            template = template_data['single_exit']
            instruction_text = template.format(
                zone_id=zone_id,
                exit_name=primary_exit,
                severity=f"{severity:.1f}"
            )
        
        # Create instruction object
        instruction = {
            'zone_id': zone_id,
            'x': x,
            'y': y,
            'level': level,
            'severity': severity,
            'primary_exit': primary_exit,
            'alternative_exits': nearest_exits[1:] if len(nearest_exits) > 1 else [],
            'region': region,
            'instruction_text': instruction_text,
            'icon': template_data['icon'],
            'priority': template_data['priority']
        }
        
        # Track instruction
        self.instruction_history.append(instruction)
        
        return instruction
    
    def generate_batch_instructions(self, classified_zones) -> List[Dict]:
        """
        Generate instructions for multiple classified zones
        
        Args:
            classified_zones: DataFrame or list of classified zones
            
        Returns:
            List of instruction dictionaries
        """
        instructions = []
        
        for _, zone in classified_zones.iterrows():
            instruction = self.generate_instruction(
                zone_id=zone['zone_id'],
                x=int(zone['x']),
                y=int(zone['y']),
                level=zone['level'],
                severity=zone['severity']
            )
            instructions.append(instruction)
        
        return instructions
    
    def get_priority_instructions(self, instructions: List[Dict]) -> List[Dict]:
        """
        Filter and sort instructions by priority
        
        Args:
            instructions: List of instruction dictionaries
            
        Returns:
            Sorted list of high-priority instructions
        """
        priority_order = {
            'EMERGENCY': 0,
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4
        }
        
        # Filter for actionable instructions
        priority_instructions = [
            inst for inst in instructions 
            if inst['priority'] in ['EMERGENCY', 'CRITICAL', 'HIGH']
        ]
        
        # Sort by priority
        priority_instructions.sort(
            key=lambda x: (priority_order[x['priority']], -x['severity'])
        )
        
        return priority_instructions
    
    def format_instruction_display(self, instruction: Dict) -> str:
        """
        Format instruction for display
        
        Args:
            instruction: Instruction dictionary
            
        Returns:
            Formatted string for display
        """
        return f"{instruction['icon']} {instruction['instruction_text']}"
    
    def generate_summary_report(self, instructions: List[Dict]) -> Dict:
        """
        Generate summary report of instructions
        
        Args:
            instructions: List of instruction dictionaries
            
        Returns:
            Summary statistics
        """
        total = len(instructions)
        
        # Count by priority
        priority_counts = {
            'EMERGENCY': 0,
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for inst in instructions:
            priority_counts[inst['priority']] += 1
        
        # Count by exit
        exit_usage = {}
        for inst in instructions:
            exit_name = inst['primary_exit']
            exit_usage[exit_name] = exit_usage.get(exit_name, 0) + 1
        
        summary = {
            'total_instructions': total,
            'priority_breakdown': priority_counts,
            'exit_usage': exit_usage,
            'requires_immediate_action': priority_counts['EMERGENCY'] + priority_counts['CRITICAL'],
            'zones_monitored': priority_counts['MEDIUM'] + priority_counts['LOW']
        }
        
        return summary
    
    def export_instructions(self, instructions: List[Dict], filepath: str):
        """
        Export instructions to JSON file
        
        Args:
            instructions: List of instruction dictionaries
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            json.dump(instructions, f, indent=2)
        
        print(f"✓ Instructions exported to: {filepath}")
    
    def print_instructions(self, instructions: List[Dict], filter_priority: Optional[str] = None):
        """
        Print instructions to console
        
        Args:
            instructions: List of instruction dictionaries
            filter_priority: Optional priority filter
        """
        if filter_priority:
            instructions = [i for i in instructions if i['priority'] == filter_priority]
        
        if not instructions:
            print("No instructions to display")
            return
        
        print("\n" + "=" * 80)
        print("ZONE-SPECIFIC INSTRUCTIONS")
        print("=" * 80)
        
        for inst in instructions:
            print(f"\n{self.format_instruction_display(inst)}")
        
        print("\n" + "=" * 80)


# Testing function
def test_instruction_generator():
    """Test the instruction generator"""
    print("=" * 80)
    print("INSTRUCTION GENERATOR TEST")
    print("=" * 80)
    
    generator = InstructionGenerator()
    
    # Print exit region mapping
    print("\n--- Exit Region Mapping ---")
    for region, zones in generator.exit_map.items():
        print(f"\n{region} Exit Region: {len(zones)} zones")
        if len(zones) <= 10:
            print(f"  Zones: {zones[:10]}")
    
    # Test individual instructions
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL INSTRUCTIONS")
    print("=" * 80)
    
    test_cases = [
        {'zone_id': 'Zone_1_5', 'x': 1, 'y': 5, 'level': 'safe', 'severity': 15.2},
        {'zone_id': 'Zone_8_6', 'x': 8, 'y': 6, 'level': 'moderate', 'severity': 32.5},
        {'zone_id': 'Zone_4_8', 'x': 4, 'y': 8, 'level': 'warning', 'severity': 51.7},
        {'zone_id': 'Zone_5_5', 'x': 5, 'y': 5, 'level': 'critical', 'severity': 72.3},
        {'zone_id': 'Zone_2_1', 'x': 2, 'y': 1, 'level': 'emergency', 'severity': 89.5}
    ]
    
    all_instructions = []
    
    for test in test_cases:
        print(f"\n--- {test['zone_id']} ({test['level'].upper()}) ---")
        
        instruction = generator.generate_instruction(
            zone_id=test['zone_id'],
            x=test['x'],
            y=test['y'],
            level=test['level'],
            severity=test['severity']
        )
        
        print(f"Region: {instruction['region']}")
        print(f"Primary Exit: {instruction['primary_exit']}")
        if instruction['alternative_exits']:
            print(f"Alternative Exits: {', '.join(instruction['alternative_exits'])}")
        print(f"Priority: {instruction['priority']}")
        print(f"\nInstruction:")
        print(f"  {generator.format_instruction_display(instruction)}")
        
        all_instructions.append(instruction)
    
    # Test priority filtering
    print("\n" + "=" * 80)
    print("HIGH-PRIORITY INSTRUCTIONS ONLY")
    print("=" * 80)
    
    priority_instructions = generator.get_priority_instructions(all_instructions)
    generator.print_instructions(priority_instructions)
    
    # Test summary report
    print("\n" + "=" * 80)
    print("INSTRUCTION SUMMARY REPORT")
    print("=" * 80)
    
    summary = generator.generate_summary_report(all_instructions)
    print(f"\nTotal Instructions: {summary['total_instructions']}")
    print(f"Requires Immediate Action: {summary['requires_immediate_action']}")
    print(f"Zones Monitored: {summary['zones_monitored']}")
    
    print("\nPriority Breakdown:")
    for priority, count in summary['priority_breakdown'].items():
        if count > 0:
            print(f"  {priority:12} {count}")
    
    print("\nExit Usage:")
    for exit_name, count in summary['exit_usage'].items():
        print(f"  {exit_name:12} {count} zone(s)")
    
    print("\n" + "=" * 80)
    print("✅ INSTRUCTION GENERATOR TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_instruction_generator()