# Zone-Specific Instruction System

## Overview

The Instruction Generation System provides contextually aware, zone-specific guidance for crowd management and evacuation based on real-time classification levels and spatial positioning.

---

## Exit Region Mapping

### Grid Division (10×10 Zones)

The venue is divided into five regions based on proximity to exits.

Region | Zones | Exit Assignment | Zone Count
------|-------|-----------------|-----------
North | Rows 0–2 (all columns) | North Exit | 30
South | Rows 7–9 (all columns) | South Exit | 30
East | Columns 7–9 (rows 3–6) | East Exit | 12
West | Columns 0–2 (rows 3–6) | West Exit | 12
Central | Rows 3–6, Columns 3–6 | Multiple Options | 16

---

### Exit Locations (Conceptual Layout)

        [North Exit]
             ↓
    [West]   VENUE   [East]
             ↑
        [South Exit]

---

## Instruction Templates

### Level 1: SAFE

Icon: ✓  
Priority: LOW  
Action Required: No  

Template:  
Zone {zone_id}: ✓ NORMAL OPERATIONS.  
Continue monitoring conditions.  
Nearest exit: {exit_name}.

Example:  
Zone Zone_2_4: ✓ NORMAL OPERATIONS.  
Continue monitoring conditions.  
Available exits: North and South.

---

### Level 2: MODERATE

Icon: ⚠  
Priority: MEDIUM  
Action Required: No (Monitor)

Template:  
Zone {zone_id}: ⚠ INCREASED DENSITY detected.  
Maintain orderly movement.  
If evacuation needed, proceed toward {exit_name} exit.  
Monitor for escalation.

Example:  
Zone Zone_5_7: ⚠ INCREASED DENSITY detected.  
Maintain orderly movement.  
If evacuation needed, available exits: East and North.  
Monitor for escalation.

---

### Level 3: WARNING

Icon: ⚠️  
Priority: HIGH  
Action Required: Yes

Template:  
Zone {zone_id}: ⚠️ HIGH DENSITY WARNING!  
Slow crowd movement immediately.  
Prepare for possible redirection to {exit_name} exit.  
Deploy security personnel.  
Restrict new entries to this zone.

Example:  
Zone Zone_4_8: ⚠️ HIGH DENSITY WARNING!  
Slow crowd movement immediately.  
Prepare for possible redirection.  
Optimal exit routes: East and North.  
Deploy security personnel.  
Restrict new entries to this zone.

---

### Level 4: CRITICAL

Icon: 🔴  
Priority: CRITICAL  
Action Required: Yes (Immediate)

Template:  
Zone {zone_id}: 🔴 CRITICAL CONGESTION!  
IMMEDIATE ACTION REQUIRED.  
RESTRICT all entry to this zone.  
BEGIN controlled evacuation via {exit_name} exit.  
Deploy all available personnel.  
Situation severity: {severity}/100.  
Potential for escalation to emergency.

Example:  
Zone Zone_6_5: 🔴 CRITICAL CONGESTION!  
IMMEDIATE ACTION REQUIRED.  
RESTRICT all entry to this zone.  
BEGIN controlled evacuation.  
Direct crowd to: East and West.  
Deploy all available personnel.  
Situation severity: 72.3/100.  
Potential for escalation to emergency.

---

### Level 5: EMERGENCY

Icon: 🚨  
Priority: EMERGENCY  
Action Required: Yes (Urgent)

Template:  
Zone {zone_id}: 🚨 EMERGENCY – EVACUATE NOW!  
IMMEDIATE evacuation required via {exit_name} exit.  
ALL PERSONNEL: Priority response needed.  
Severity: {severity}/100.  
⚠️ POTENTIAL STAMPEDE RISK.  
Activate emergency protocols.  
Clear evacuation path.  
Prevent entry from all directions.

Example:  
Zone Zone_2_1: 🚨 EMERGENCY – EVACUATE NOW!  
IMMEDIATE evacuation required.  
Direct to nearest: West and North.  
ALL PERSONNEL: Priority response needed.  
Severity: 89.5/100.  
⚠️ POTENTIAL STAMPEDE RISK.  
Activate emergency protocols.  
Clear all evacuation paths.  
Prevent entry from all directions.

---

## Instruction Personalization

### Zone-Specific Elements

Zone Identifier  
• Unique ID in every instruction  
• Format: Zone_X_Y (X = row, Y = column)  
• Example: Zone_5_3  

Exit Assignment  
• Primary exit based on Manhattan distance  
• Alternative exits for central zones  
• Dynamic route selection  

Severity Score  
• Included for WARNING and above  
• Scale: 0–100  
• Quantifies urgency  

Regional Context  
• Single-exit templates for border zones  
• Multi-exit options for central zones  

---

## Priority System

### Priority Levels

Priority | Level | Action Timeline | Display Order
---------|-------|-----------------|--------------
EMERGENCY | Emergency | Immediate (seconds) | 1st
CRITICAL | Critical | Urgent (< 1 minute) | 2nd
HIGH | Warning | Soon (< 5 minutes) | 3rd
MEDIUM | Moderate | Monitor | 4th
LOW | Safe | Normal operations | 5th

---

### Filtering Logic

priority_instructions =  
[inst for inst in all_instructions  
if inst['priority'] in ['EMERGENCY', 'CRITICAL', 'HIGH']]

---

## Exit Load Balancing

### Load Distribution Tracking

exit_usage = {  
'North': 15 zones,  
'South': 12 zones,  
'East': 8 zones,  
'West': 5 zones  
}

This information is used to:  
• Balance crowd flow across exits  
• Identify bottlenecks  
• Adjust routing in real time  

---

## Usage Examples

### Example 1: Normal Operations

Input:  
Zone: Zone_3_6  
Level: SAFE  
Severity: 15.2  

Output:  
✓ Zone Zone_3_6: ✓ NORMAL OPERATIONS.  
Continue monitoring conditions.  
Available exits: East and North.

---

### Example 2: Developing Situation

Input:  
Zone: Zone_7_4  
Level: WARNING  
Severity: 48.7  

Output:  
⚠️ Zone Zone_7_4: ⚠️ HIGH DENSITY WARNING!  
Slow crowd movement immediately.  
Prepare for possible redirection to South exit.  
Deploy security personnel.  
Restrict new entries to this zone.

---

### Example 3: Emergency Response

Input:  
Zone: Zone_1_2  
Level: EMERGENCY  
Severity: 91.3  

Output:  
🚨 Zone Zone_1_2: 🚨 EMERGENCY – EVACUATE NOW!  
IMMEDIATE evacuation required.  
Direct to nearest: North and West.  
ALL PERSONNEL: Priority response needed.  
Severity: 91.3/100.  
⚠️ POTENTIAL STAMPEDE RISK.  
Activate emergency protocols.  
Clear all evacuation paths.  
Prevent entry from all directions.

---

## Integration with Classification

### Data Flow

Classified Zone Data  
↓  
Zone Location (x, y)  
↓  
Determine Region and Nearest Exits  
↓  
Select Template Based on Level  
↓  
Personalize with Zone ID, Exit, Severity  
↓  
Assign Priority  
↓  
Generated Instruction

---

## API Reference

Main Methods

Generate single instruction:  
instruction = generator.generate_instruction(  
zone_id='Zone_5_3',  
x=5,  
y=3,  
level='critical',  
severity=72.5  
)

Generate batch instructions:  
instructions = generator.generate_batch_instructions(classified_zones_df)

Filter by priority:  
priority_only = generator.get_priority_instructions(instructions)

Generate summary report:  
summary = generator.generate_summary_report(instructions)

---

## Best Practices

### For Operators

1. Prioritize EMERGENCY and CRITICAL alerts  
2. Act quickly on WARNING levels (within 5 minutes)  
3. Communicate instructions verbatim  
4. Monitor zones for escalation  
5. Document actions taken  

### For System Integration

1. Regenerate instructions frequently  
2. Filter non-critical zones  
3. Track recurring alert zones  
4. Export data for analysis  
5. Test exit logic regularly  

---

Version: 1.0  
Last Updated: January 2026
