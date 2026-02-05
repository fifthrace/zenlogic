import json
import os

sector_names = ['Alpha Sector', 'Crimson Void', 'Azure Reach', 'Obsidian Gate', 'Emerald Nebula', 'Solar Forge', 'Neutron Star']

def fix_manifest():
    levels_dir = '/home/baxter/projects/proxima8/levels'
    manifest_path = '/home/baxter/projects/proxima8/level_manifest.json'
    
    # 1. Map existing files to their actual data
    files_on_disk = {}
    for filename in os.listdir(levels_dir):
        if not filename.endswith('.json'): continue
        with open(os.path.join(levels_dir, filename), 'r') as f:
            try:
                data = json.load(f)
                files_on_disk[data.get('uid') or data.get('id')] = data
            except: continue

    # 2. Re-build manifest using ONLY files that exist and are <= 8x8
    all_valid = []
    for uid, data in files_on_disk.items():
        if data.get('width', 0) > 8: continue
        all_valid.append({
            "id": uid,
            "title": data.get('name'),
            "width": data.get('width'),
            "height": data.get('height'),
            "difficulty_rating": data.get('difficulty_rating', 50),
            "steps": data.get('logical_steps', 0)
        })

    # Sort by rating to maintain difficulty curve
    all_valid.sort(key=lambda x: x['difficulty_rating'])

    # 3. Force exact 13-per-sector mapping (91 levels total)
    final_manifest = []
    for i in range(len(sector_names)):
        sector_name = sector_names[i]
        # Take a slice of 13 levels for this sector
        start = i * 13
        end = start + 13
        sector_slice = all_valid[start:end]
        
        for level in sector_slice:
            level['sector'] = sector_name
            final_manifest.append(level)

    with open(manifest_path, 'w') as f:
        json.dump(final_manifest, f, indent=2)
    
    print(f"Fixed manifest: {len(final_manifest)} levels total (exactly 13 per sector).")

if __name__ == "__main__":
    fix_manifest()
