import cv2
import numpy as np
import os
import argparse
import sys

def process_single_image(img_path, output_dir_img, output_dir_mask):
    """
    Reads an image, applies Gamma -> CLAHE -> Bilateral -> Masking,
    and saves the processed image and the exclusion mask.
    """
    filename = os.path.basename(img_path)
    
    # 1. Read Image
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error reading {img_path}")
        return

    # 2. Gamma Correction (Brightness)
    gamma = 0.5
    lookUpTable = np.empty((1, 256), np.uint8)
    for i in range(256):
        lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    img_gamma = cv2.LUT(img, lookUpTable)

    # 3. CLAHE (Contrast) on Y channel
    lab = cv2.cvtColor(img_gamma, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    
    lab_clahe = cv2.merge((l_clahe, a, b))
    proc = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

    # 4. Denoise
    proc = cv2.bilateralFilter(proc, d=5, sigmaColor=75, sigmaSpace=75)

    # 5. Generate Exclusion Masks (Bright Lights + Deep Shadows)
    gray = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
    
    # sat_thr = 245    # Threshold for bright light
    sat_thr = 255
    dark_thr = 8     # Threshold for deep shadows
    
    sat = (gray >= sat_thr).astype(np.uint8) * 255
    dark = (gray <= dark_thr).astype(np.uint8) * 255

    dilate_bright_k = 25
    dilate_dark_k = 5
    
    k_bright = np.ones((dilate_bright_k, dilate_bright_k), np.uint8)
    k_dark = np.ones((dilate_dark_k, dilate_dark_k), np.uint8)
    
    sat = cv2.dilate(sat, k_bright, iterations=1)
    dark = cv2.dilate(dark, k_dark, iterations=1)
    
    # Combine bright + dark into base exclusion mask
    mask_exclude = cv2.bitwise_or(sat, dark)

    # === NEW: mask out bottom 1/4 of the image ===
    H, W = gray.shape
    bottom_mask = np.zeros_like(mask_exclude, dtype=np.uint8)
    bottom_start = int(0.75 * H)  # bottom quarter
    bottom_mask[bottom_start:H, :] = 255  # white = "bad / excluded"

    # OR this with the existing mask
    mask_exclude = cv2.bitwise_or(mask_exclude, bottom_mask)
    # =============================================

    # 6. Save Results
    save_path_img = os.path.join(output_dir_img, filename)
    cv2.imwrite(save_path_img, proc)
    
    filename_no_ext = os.path.splitext(filename)[0]
    save_path_mask = os.path.join(output_dir_mask, f"{filename_no_ext}.png")
    cv2.imwrite(save_path_mask, mask_exclude)
    
    print(f"Processed: {filename}")


def main():
    # Setup argument parser like dumb_masking.py
    parser = argparse.ArgumentParser(description='Process night images for VO')
    parser.add_argument('input_folder', type=str, help='Path to input images')
    parser.add_argument('output_folder', type=str, help='Path to save results')
    
    # If running in a notebook or without args, you can manually set them here for testing
    if len(sys.argv) == 1:
        # Example default usage
        print("Usage: python process_night.py <input_folder> <output_folder>")
        sys.exit(1)
        
    args = parser.parse_args()

    # Create output directories
    output_imgs = os.path.join(args.output_folder, "processed_images")
    output_masks = os.path.join(args.output_folder, "masks")
    
    os.makedirs(output_imgs, exist_ok=True)
    os.makedirs(output_masks, exist_ok=True)

    # Get list of images
    valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    files = [f for f in os.listdir(args.input_folder) if f.lower().endswith(valid_exts)]
    
    print(f"Found {len(files)} images in {args.input_folder}")
    print(f"Saving processed images to: {output_imgs}")
    print(f"Saving masks to: {output_masks}")
    
    for filename in files:
        img_path = os.path.join(args.input_folder, filename)
        process_single_image(img_path, output_imgs, output_masks)
        
    print("Done!")

if __name__ == "__main__":
    main()