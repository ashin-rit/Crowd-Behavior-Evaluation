# Heatmap Design Guide

## Overview

This document describes the design principles and specifications for crowd monitoring heatmaps.

---

## Heatmap Types

### 1. Density Heatmap

**Purpose:** Visualize raw crowd density values across all zones

**Color Scheme:** Yellow-Orange-Red (YlOrRd)
- Yellow: Low density
- Orange: Medium density
- Red: High density

**Scale:** 0-8 people/m²

**Features:**
- Continuous color gradient
- Numerical annotations in each cell
- Colorbar with scale
- Grid lines for clarity
- Threshold reference annotations

**Use Case:**
- Real-time monitoring
- Density pattern analysis
- Historical comparison

**Example:**
```
┌─────┬─────┬─────┬─────┐
│ 1.2 │ 1.5 │ 2.1 │ 2.8 │  ← Values shown
│ 🟨  │ 🟨  │ 🟧  │ 🟧  │  ← Color coded
├─────┼─────┼─────┼─────┤
│ 3.4 │ 4.2 │ 5.6 │ 6.8 │
│ 🟧  │ 🟧  │ 🟥  │ 🟥  │
└─────┴─────┴─────┴─────┘
```

---

### 2. Classification Heatmap

**Purpose:** Show safety classification of each zone

**Color Scheme:** Discrete 5-level system
- 🟢 Green (#00FF00): Safe
- 🟢 Yellow-Green (#7FFF00): Moderate
- 🟡 Yellow (#FFFF00): Warning
- 🟠 Orange (#FF8C00): Critical
- 🔴 Red (#FF0000): Emergency

**Features:**
- Discrete color blocks (no gradient)
- Severity scores annotated
- Clear zone boundaries
- Comprehensive legend
- White grid lines for separation

**Use Case:**
- Quick safety assessment
- Alert prioritization
- Decision support

**Example:**
```
┌──────┬──────┬──────┬──────┐
│ Safe │ Mod  │ Warn │ Crit │
│  15  │  32  │  52  │  71  │  ← Severity scores
│ 🟢   │ 🟢   │ 🟡   │ 🟠   │
└──────┴──────┴──────┴──────┘
```

---

### 3. Dual Heatmap

**Purpose:** Side-by-side comparison of density and classification

**Layout:**
```
┌─────────────────────────────────────────┐
│  Density Distribution | Classification  │
│                       |                 │
│    [Density Map]      | [Class Map]    │
│                       |                 │
└─────────────────────────────────────────┘
```

**Features:**
- Split view for comprehensive analysis
- Shared axis labels
- Individual colorbars/legends
- Synchronized scale

**Use Case:**
- Presentations
- Reports
- Training materials

---

### 4. Annotated Heatmap

**Purpose:** Comprehensive status with alerts and instructions

**Features:**
- Classification background colors
- Density values in cells
- Alert icons (⚠️, 🔴, 🚨)
- Alert count indicator
- Legend for all elements

**Example:**
```
┌──────┬──────┬──────┐
│ 1.5  │ 4.2  │ 6.8  │
│      │ ⚠️   │ 🔴   │  ← Alert icons
│ 🟢   │ 🟡   │ 🟠   │  ← Classification
└──────┴──────┴──────┘
     [3 Active Alerts]
```

**Use Case:**
- Real-time operations
- Emergency response
- Situational awareness

---

## Color Mapping Specifications

### Density Colormap (YlOrRd)

**Color Gradient:**
```
0.0 → #FFFFCC (Light Yellow)
2.0 → #FFD700 (Gold)
4.0 → #FF8C00 (Orange)
6.0 → #FF4500 (Orange-Red)
8.0 → #8B0000 (Dark Red)
```

**Rationale:**
- Intuitive hot/cold metaphor
- High contrast for quick reading
- Colorblind-friendly (warm spectrum)
- Industry standard for density visualization

---

### Classification Colors

| Level | Color | Hex Code | RGB | Psychology |
|-------|-------|----------|-----|------------|
| Safe | Green | #00FF00 | 0,255,0 | Calm, Go |
| Moderate | Yellow-Green | #7FFF00 | 127,255,0 | Caution |
| Warning | Yellow | #FFFF00 | 255,255,0 | Alert |
| Critical | Orange | #FF8C00 | 255,140,0 | Danger |
| Emergency | Red | #FF0000 | 255,0,0 | Stop, Emergency |

**Design Principles:**
- Progression from cool to warm
- Each level distinctly identifiable
- High contrast between adjacent levels
- Universal color language

---

## Scale and Range Definitions

### Density Scale

**Primary Scale:** 0-8 people/m²

**Reasoning:**
- 0-2: Normal walking space
- 2-4: Crowded but manageable
- 4-6: Very crowded, movement difficult
- 6-8: Dangerous density
- 8+: Extreme risk (off-scale)

**Threshold Lines:**
```
  8 |─────────────────────| Emergency
  7 |─────────────────────| Critical
  5 |─────────────────────| Warning
3.5 |─────────────────────| Moderate
  2 |─────────────────────| Safe
  0 |─────────────────────|
```

---

## Grid Specifications

### Layout
- **Size:** 10×10 zones
- **Cell Shape:** Square (equal aspect ratio)
- **Grid Lines:** White, 1.5-2px width
- **Cell Padding:** Minimal (for readability)

### Annotations

**Density Values:**
- Font Size: 8-10pt
- Font Weight: Bold
- Format: 1 decimal place (e.g., "3.5")
- Color: Black for light backgrounds, White for dark

**Severity Scores:**
- Font Size: 9-11pt
- Font Weight: Bold
- Format: Integer (e.g., "72")
- Position: Center of cell

**Alert Icons:**
- Size: 14pt (emojis scale well)
- Position: Below density value
- Icons: ✓, ⚠, ⚠️, 🔴, 🚨

---

## Legend Design

### Classification Legend

**Layout:**
- Position: Right side, outside plot area
- Orientation: Vertical
- Border: Black, 1px
- Background: White

**Content:**
```
Classification Levels
┌─────────────────────────┐
│ ■ Safe (0-2)           │
│ ■ Moderate (2-3.5)     │
│ ■ Warning (3.5-5)      │
│ ■ Critical (5-7)       │
│ ■ Emergency (7+)       │
└─────────────────────────┘
```

### Colorbar (Density)

**Features:**
- Label: "Density (people/m²)"
- Orientation: Vertical
- Ticks: 0, 2, 4, 6, 8
- Height: 80% of plot height

---

## Typography

### Title
- Font Size: 16pt
- Font Weight: Bold
- Position: Top, centered
- Padding: 20px from plot

### Axis Labels
- Font Size: 13pt
- Font Weight: Bold
- Labels: "Zone Row", "Zone Column"

### Tick Labels
- Font Size: 10pt
- Font Weight: Normal
- Format: Integer (0-9)

### Annotations
- Font Size: 9pt (varies by element)
- Font Weight: Bold for values
- Alignment: Center

---

## Best Practices

### Do's
✓ Use consistent color schemes across all heatmaps
✓ Annotate cells when space permits
✓ Include scale reference (colorbar or legend)
✓ Maintain high contrast for readability
✓ Use white grid lines for clear separation
✓ Save at high resolution (150+ DPI)

### Don'ts
✗ Mix continuous and discrete colormaps
✗ Over-annotate small cells
✗ Use colors without legend
✗ Create heatmaps without titles
✗ Ignore colorblind accessibility
✗ Save at low resolution (<100 DPI)

---

## Accessibility Considerations

### Colorblind Friendliness
- Primary colormap (YlOrRd) works for most colorblind types
- Green-Red system includes brightness variation
- Always include text annotations
- Provide numerical data alongside colors

### Screen Display
- Minimum cell size: 30x30 pixels
- High contrast text
- Legible fonts at standard viewing distance

### Print Considerations
- Test in grayscale
- Ensure annotations visible without color
- Use minimum 150 DPI for printing

---

## File Format Specifications

### Output Formats
- **PNG:** Standard, web-friendly (recommended)
- **SVG:** Vector, scalable (for reports)
- **PDF:** Print-ready (for documentation)

### Resolution
- Screen: 150 DPI
- Print: 300 DPI
- Poster: 600 DPI

### Naming Convention
Examples:

- emergency_density_frame_075.png
- normal_classification_frame_100.png
- rushhour_dual_frame_150.png

## Example Use Cases

### 1. Real-Time Monitoring
- **Heatmap:** Annotated  
- **Update Frequency:** Every 1–5 seconds  
- **Focus:** Quick assessment with alerts  

---

### 2. Historical Analysis
- **Heatmap:** Density or Dual  
- **Update Frequency:** Static snapshots  
- **Focus:** Pattern identification  

---

### 3. Incident Reports
- **Heatmap:** Dual or Annotated  
- **Update Frequency:** Key moments  
- **Focus:** Documentation and analysis  

---

### 4. Training Materials
- **Heatmap:** All types  
- **Update Frequency:** Static  
- **Focus:** Education and examples  

---

**Version:** 1.0  
**Last Updated:** January 2026


