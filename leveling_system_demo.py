import numpy as np
import matplotlib.pyplot as plt

# Set up the total levels and target XP values
total_levels = 100
xp_level_10 = 10e2
xp_level_100 = 10e12  # 1 trillion

# Calculate the exponential growth factor
base = (xp_level_100 / xp_level_10) ** (1 / (total_levels - 10))

# Calculate XP requirements for each level
levels = np.arange(1, total_levels + 1)
xp_requirements = np.array([xp_level_10 * base ** (level - 10) for level in levels])

print(levels)
print(xp_requirements)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(levels, xp_requirements, label="XP Required", color="blue")

# Customize the graph for readability
plt.yscale('log')  # Log scale for better readability of large values
plt.xticks(ticks=np.arange(0, total_levels + 1, 10), labels=np.arange(0, total_levels + 1, 10))
plt.xlabel("Level")
plt.ylabel("XP Required")
plt.title("XP Requirements per Level")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend()

# Customize the y-axis to display powers of ten starting from 100
plt.yticks([10e2, 10e3, 10e4, 10e5, 10e6, 10e7, 10e8, 10e9, 10e10, 10e11, 10e12], labels=['100', '1,000', '10,000', '100,000', '1,000,000', '10,000,000', '100,000,000', '1,000,000,000', '10,000,000,000', '100,000,000,000', '1,000,000,000,000'])

# Show the plot
plt.tight_layout()
plt.show()
