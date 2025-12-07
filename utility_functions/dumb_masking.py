import cv2
import numpy as np
import os
import glob
from pathlib import Path
from tqdm import tqdm # Optional: pip install tqdm for progress bar

# ==== USER SETTINGS ====
input_dir = "boreas-2021-09-14-20-00/camera_720p"  # Your image folder
output_dir = "boreas-2021-09-14-20-00/masks_dumb" # Where to save masks
# ========================

def main():
    # 1. Setup paths
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 2. Get all images
    # Supports png, jpg, jpeg. Add more if needed.
    extensions = ["*.png", "*.jpg", "*.jpeg"]
    files = []
    for ext in extensions:
        files.extend(glob.glob(str(input_path / ext)))
    
    files = sorted(files)
    
    if not files:
        print(f"No images found in {input_dir}")
        return

    print(f"Generating blank masks for {len(files)} images...")

    # 3. Process
    for filepath in tqdm(files):
        # Read image to get exact dimensions
        img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            print(f"Error reading {filepath}")
            continue

        # Create Black Mask (All Zeros)
        # 0 = Valid Region (Keep feature)
        # 255 = Masked Region (Ignore feature)
        mask = np.zeros_like(img) 

        # Save with exact same filename
        filename = os.path.basename(filepath)
        cv2.imwrite(str(output_path / filename), mask)

    print("Done! Masks saved to:", output_dir)

if __name__ == "__main__":
    main()