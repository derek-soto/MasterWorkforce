import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx

# Define model parameters
grid_size = (100, 100)
time_steps = 365 * 10  # 10 years of daily steps

# Convert lat/lon to grid indices
def lat_lon_to_grid(lat, lon, grid_size, bounds):
    lat_min, lat_max, lon_min, lon_max = bounds
    lat_idx = int((lat - lat_min) / (lat_max - lat_min) * (grid_size[0] - 1))
    lon_idx = int((lon - lon_min) / (lon_max - lon_min) * (grid_size[1] - 1))
    return lat_idx, lon_idx

# Bounding box for Puerto Rico
bounds = (17.881540, 18.515978, -67.945831, -65.220703)

# Initialize populations
initial_distribution = np.zeros(grid_size)
coords = [(17.8951, -66.5179), (17.896767, -66.987410)]
for lat, lon in coords:
    lat_idx, lon_idx = lat_lon_to_grid(lat, lon, grid_size, bounds)
    initial_distribution[lat_idx, lon_idx] = 1

# Define environmental suitability (random example)
suitability = np.random.rand(*grid_size)

# Initialize larval dispersal kernel (example)
def dispersal_kernel(size, spread):
    kernel = np.zeros((size, size))
    center = size // 2
    for i in range(size):
        for j in range(size):
            dist = np.sqrt((i - center)**2 + (j - center)**2)
            kernel[i, j] = np.exp(-dist / spread)
    return kernel / kernel.sum()

kernel = dispersal_kernel(11, 3)

# Simulation loop
distribution = initial_distribution.copy()
for t in range(time_steps):
    # Dispersal step
    new_distribution = np.zeros_like(distribution)
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            if distribution[i, j] > 0:
                for di in range(-5, 6):
                    for dj in range(-5, 6):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid_size[0] and 0 <= nj < grid_size[1]:
                            new_distribution[ni, nj] += distribution[i, j] * kernel[di + 5, dj + 5]

    # Apply suitability filter
    distribution = new_distribution * suitability

    # Optional: add growth, mortality, etc.

    # Record results (e.g., save distribution at intervals)
    if t % 365 == 0:
        plt.figure(figsize=(10, 10))

        # Load Puerto Rico shapefile
        puerto_rico = gpd.read_file('/Users/dereksoto/natural_earth_data/ne_10m_admin_0_countries.shp')
        puerto_rico = puerto_rico[puerto_rico.NAME == "Puerto Rico"]

        # Plot map of Puerto Rico
        ax = puerto_rico.plot(figsize=(10, 10), edgecolor='black')
        ctx.add_basemap(ax, zoom=10)

        # Overlay simulation results
        extent = [0, grid_size[1], 0, grid_size[0]]
        plt.imshow(distribution, cmap='hot', interpolation='nearest', extent=extent, alpha=0.6)
        plt.title(f'Time Step: {t}')
        plt.colorbar(label='Xenia umbellata Density')
        plt.show()
