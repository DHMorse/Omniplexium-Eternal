import json

def generate_reward_progression(max_level=300, output_file='rewards.json'):
    """
    Generate a dictionary of rewards with increasing XP and money rewards.
    Write the rewards to a JSON file.
    
    :param max_level: Maximum level to generate rewards for
    :param output_file: Name of the JSON file to write rewards to
    :return: Dictionary of rewards
    """
    rewards = {}
    xp_amount = 10
    xp_increment = 20
    
    for level in range(1, max_level + 1):
        # Every 5 levels, change to money reward
        if level % 5 == 0:
            rewards[level] = {
                "type": "money",
                "amount": level * 2
            }
            # Increase XP increment every 5 levels
            xp_increment += 10
        else:
            if level == 1:
                rewards[level] = {
                    "type": "xp",
                    "amount": xp_amount
                }
            else:
                xp_amount += xp_increment
                # XP rewards
                rewards[level] = {
                    "type": "xp",
                    "amount": xp_amount
                }
    
    # Write rewards to JSON file
    with open(output_file, 'w') as f:
        json.dump(rewards, f, indent=4)
    
    print(f"Rewards data written to {output_file}")
    return rewards

# Generate and write rewards to JSON
rewards_dict = generate_reward_progression()