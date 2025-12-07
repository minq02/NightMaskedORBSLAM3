import os
import glob
import cv2
import numpy as np
from pathlib import Path

# ==== USER SETTINGS ====
input_dir = "boreas-2021-09-14-20-00/camera"
output_dir = "boreas-2021-09-14-20-00/camera_720p"
target_height = 720
downsample_step = 1 
# ========================

def resize_proportional(img, target_h):
    """Resize preserving aspect ratio based on target height."""
    h, w = img.shape[:2]
    scale = target_h / h
    new_w = int(w * scale)
    new_h = int(target_h)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

def main():
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Get all images
    files = sorted(glob.glob(str(input_path / "*.png")))
    if not files:
        print("No PNG files found in", input_dir)
        return

    print(f"Total source frames: {len(files)}")

    # 2. Simple Slicing (The "Every 5th" Logic)
    # Syntax: list[start:stop:step]
    selected_files = files[::downsample_step]

    print(f"Selected frames (Step={downsample_step}): {len(selected_files)}")
    print("Processing...")

    for i, filepath in enumerate(selected_files):
        # Read
        img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue

        # Resize
        resized_img = resize_proportional(img, target_height)

        # ==== RENAME LOGIC START ====
        # 1. Get original filename (e.g., "1636224955123456.png")
        original_name = os.path.basename(filepath)
        
        # 2. Split name and extension
        name_part, extension = os.path.splitext(original_name)
        
        # 3. Add three zeros to the name
        new_name_part = name_part # + "000"
        
        # 4. Reassemble (e.g., "1636224955123456000.png")
        new_filename = new_name_part + extension
        # ==== RENAME LOGIC END ====

        # Save
        cv2.imwrite(str(output_path / new_filename), resized_img)

        if i % 500 == 0:
            print(f"Saved {i}/{len(selected_files)}...")

    print("Done! Saved to:", output_dir)

if __name__ == "__main__":
    main()