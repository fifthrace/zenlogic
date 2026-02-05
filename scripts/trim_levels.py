import json
import os

def trim_manifest():
    manifest_path = '/home/baxter/projects/proxima8/level_manifest.json'
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Track counts per size
    counts = {}
    new_manifest = []
    
    # Loop through manifest and keep only first 25 of each size
    for level in manifest:
        size = level['width']
        counts[size] = counts.get(size, 0) + 1
        
        if counts[size] <= 25:
            new_manifest.append(level)
            
    # Save new manifest
    with open(manifest_path, 'w') as f:
        json.dump(new_manifest, f, indent=2)
    
    print("Manifest trimmed to max 25 levels per category.")
    for size, total in counts.items():
        kept = min(total, 25)
        print(f"Size {size}x{size}: kept {kept}/{total}")

if __name__ == "__main__":
    trim_manifest()
