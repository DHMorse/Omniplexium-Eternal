import json
import matplotlib.pyplot as plt

def plot_data(data):
    # Separate the data by type
    levels = sorted(data.keys(), key=int)  # Ensure levels are sorted numerically
    xp_levels = []
    xp_values = []
    money_levels = []
    money_values = []
    
    for level in levels:
        entry = data[level]
        if entry['type'] == 'xp':
            xp_levels.append(int(level))
            xp_values.append(entry['amount'])
        elif entry['type'] == 'money':
            money_levels.append(int(level))
            money_values.append(entry['amount'])
    
    # Plot XP progression (granular)
    if xp_levels:
        plt.figure(figsize=(10, 5))
        plt.plot(xp_levels, xp_values, marker='o', label="XP Increase", color='blue')
        plt.title("XP Progression (Granular View)")
        plt.xlabel("Level")
        plt.ylabel("XP Increase")
        plt.grid()
        plt.legend()
        plt.show()

    # Plot Money
    if money_levels:
        plt.figure(figsize=(10, 5))
        plt.plot(money_levels, money_values, marker='o', color='orange', label="Money")
        plt.title("Money Progression")
        plt.xlabel("Level")
        plt.ylabel("Money Amount")
        plt.grid()
        plt.legend()
        plt.show()

if __name__ == "__main__":
    # Example JSON data (replace this with a file read if needed)

    # To read from a file, uncomment the lines below:
    with open('rewards.json', 'r') as file:
        json_data = json.load(file)
    
    plot_data(json_data)
