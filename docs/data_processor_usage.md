# Data Processor Usage Guide

## Overview
The `CrowdDataProcessor` class provides utilities for loading, validating, and manipulating crowd behavior data.

---

## Basic Usage

### 1. Initialize Processor
```python
from src.utils.data_processor import CrowdDataProcessor

processor = CrowdDataProcessor(grid_size=(10, 10), zone_area=10.0)
```

### 2. Load a Scenario
```python
# Load scenario
df = processor.load_scenario('data/synthetic/normal_scenario.csv')

# View statistics
processor.print_statistics()
```

### 3. Extract Data

#### Get Specific Frame
```python
# Get all zones at timestamp 50
frame_50 = processor.get_frame(50)
```

#### Get Specific Zone
```python
# Get temporal data for Zone_5_3
zone_data = processor.get_zone('Zone_5_3')

# Or by coordinates
zone_data = processor.get_zone_by_coords(5, 3)
```

#### Get Single Zone at Specific Time
```python
zone_at_time = processor.get_zone_by_coords(5, 3, timestamp=50)
```

### 4. Create Grids for Visualization
```python
# Get 2D density grid
density_grid = processor.create_density_grid(timestamp=50)

# Get speed grid
speed_grid = processor.create_speed_grid(timestamp=50)

# Get direction variance grid
variance_grid = processor.create_variance_grid(timestamp=50)
```

### 5. Analyze Patterns

#### Temporal Profile (How zone changes over time)
```python
temporal_profile = processor.get_temporal_profile(x=5, y=5)
# Returns: timestamp, density, speed, variance for that zone
```

#### Spatial Profile (All zones at one time)
```python
spatial_profile = processor.get_spatial_profile(timestamp=50)
# Returns: all zones with their metrics at that timestamp
```

### 6. Find High-Risk Zones
```python
# Find zones exceeding density threshold
high_density_zones = processor.get_high_density_zones(
    timestamp=50,
    threshold=5.0
)
```

### 7. Calculate Zone Metrics
```python
zone_data = processor.get_zone_by_coords(5, 5, timestamp=50)
metrics = processor.calculate_zone_metrics(zone_data)

# Returns:
# {
#     'zone_id': 'Zone_5_5',
#     'density': 3.5,
#     'people_count': 35,
#     'movement_speed': 1.2,
#     'capacity_utilization': 43.75,
#     'flow_rate': 4.2
# }
```

### 8. Get Time Range
```python
min_ts, max_ts = processor.get_time_range()
print(f"Scenario spans from {min_ts} to {max_ts}")
```

### 9. Export Data
```python
# Export single frame to CSV
processor.export_frame_to_csv(
    timestamp=50,
    output_path='results/frame_50.csv'
)
```

---

## Complete Example
```python
from src.utils.data_processor import CrowdDataProcessor
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize
processor = CrowdDataProcessor()

# Load scenario
df = processor.load_scenario('data/synthetic/emergency_scenario.csv')

# Print stats
processor.print_statistics()

# Get middle frame
min_ts, max_ts = processor.get_time_range()
mid_ts = (min_ts + max_ts) // 2

# Create density grid
density_grid = processor.create_density_grid(mid_ts)

# Visualize
plt.figure(figsize=(10, 8))
sns.heatmap(density_grid, annot=True, fmt='.1f', cmap='YlOrRd')
plt.title(f'Emergency Scenario - Frame {mid_ts}')
plt.show()

# Find critical zones
critical_zones = processor.get_high_density_zones(mid_ts, threshold=7.0)
print(f"Found {len(critical_zones)} emergency zones")
```

---

## API Reference

### Core Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `load_scenario(filepath)` | Load CSV data | DataFrame |
| `get_frame(timestamp)` | Get all zones at time | DataFrame |
| `get_zone(zone_id)` | Get zone temporal data | DataFrame |
| `get_zone_by_coords(x, y, ts)` | Get specific zone | DataFrame |
| `create_density_grid(ts)` | Create 2D density array | ndarray |
| `get_temporal_profile(x, y)` | Zone over time | DataFrame |
| `get_spatial_profile(ts)` | All zones at time | DataFrame |
| `get_high_density_zones(ts, threshold)` | Find risky zones | DataFrame |
| `calculate_zone_metrics(zone_data)` | Compute metrics | Dict |
| `print_statistics()` | Display stats | None |

### Properties

| Property | Description |
|----------|-------------|
| `current_scenario` | Loaded DataFrame |
| `scenario_name` | Name of scenario |
| `scenario_stats` | Statistics dict |
| `grid_rows` | Number of rows |
| `grid_cols` | Number of columns |
| `zone_area` | Area per zone (m²) |

---

## Error Handling
```python
try:
    processor.load_scenario('data/synthetic/test.csv')
except FileNotFoundError:
    print("Scenario file not found")
except ValueError as e:
    print(f"Data validation failed: {e}")
```

---

## Best Practices

1. **Always validate data** - The processor automatically validates on load
2. **Check time range** - Use `get_time_range()` before accessing timestamps
3. **Handle missing zones** - Use try-except when accessing specific zones
4. **Reuse processor** - Create one processor instance and load different scenarios
5. **Memory management** - For long scenarios, process in chunks if needed

---

**Version:** 1.0  
**Last Updated:** January 2025