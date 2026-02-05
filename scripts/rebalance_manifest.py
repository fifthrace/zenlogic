import json
import os

sector_names = ['Alpha Sector', 'Crimson Void', 'Azure Reach', 'Obsidian Gate', 'Emerald Nebula', 'Solar Forge', 'Neutron Star']

def rebalance_manifest():
    levels_dir = '/home/baxter/projects/proxima8/levels'
    manifest_path = '/home/baxter/projects/proxima8/level_manifest.json'
    
    all_levels = []
    for filename in os.listdir(levels_dir):
        if not filename.endswith('.json'): continue
        with open(os.path.join(levels_dir, filename), 'r') as f:
            level = json.load(f)
            all_levels.append({
                "id": level.get('uid') or level.get('id'),
                "title": level.get('name'),
                "width": level.get('width'),
                "height": level.get('height'),
                "difficulty_rating": level.get('difficulty_rating', 50),
                "steps": level.get('logical_steps', 0)
            })
            
    # Sort everything by difficulty rating
    all_levels.sort(key=lambda x: x['difficulty_rating'])
    
    # We want 13 levels per sector across 7 sectors = 91 levels total
    total_needed = 13 * len(sector_names)
    
    # Pick 91 levels evenly spread across the difficulty range
    # Or just the first 91 if we want it to stay easy-to-hard overall
    selected_levels = all_levels[:total_needed]
    
    # Assign sectors: 13 per sector
    new_manifest = []
    for i, level in enumerate(selected_levels):
        sector_idx = i // 13
        level['sector'] = sector_names[sector_idx]
        new_manifest.append(level)
        
    with open(manifest_path, 'w') as f:
        json.dump(new_manifest, f, indent=2)
        
    print(f"Rebalanced manifest: {len(new_manifest)} levels total (13 per sector).")

if __name__ == "__main__":
    rebalance_manifest()
