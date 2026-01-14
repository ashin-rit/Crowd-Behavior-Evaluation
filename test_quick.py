from src.utils.data_processor import CrowdDataProcessor
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize processor
processor = CrowdDataProcessor()

# Load normal scenario
df = processor.load_scenario('data/synthetic/normal_scenario.csv')

# Print statistics
processor.print_statistics()

# Get a frame
frame_50 = processor.get_frame(50)
print(f"\nFrame 50 has {len(frame_50)} zones")

# Create density grid
density_grid = processor.create_density_grid(50)
print(f"Density grid shape: {density_grid.shape}")

# Visualize
plt.figure(figsize=(10, 8))
sns.heatmap(density_grid, annot=True, fmt='.1f', cmap='YlOrRd', 
            cbar_kws={'label': 'Density (people/m²)'})
plt.title('Normal Scenario - Frame 50')
plt.xlabel('Column')
plt.ylabel('Row')
plt.tight_layout()
plt.savefig('test_output.png', dpi=150)
print("✅ Saved test visualization to test_output.png")

# Find high density zones
high_density = processor.get_high_density_zones(50, threshold=3.0)
print(f"\nHigh density zones (>3.0): {len(high_density)}")

# Get zone metrics
zone_data = processor.get_zone_by_coords(5, 5, timestamp=50)
metrics = processor.calculate_zone_metrics(zone_data)
print(f"\nZone (5,5) metrics:")
for key, value in metrics.items():
    print(f"  {key}: {value}")