import os

# ==== USER SETTINGS ====
# Point this to your downsampled image folder
image_folder_path = "boreas-2021-09-14-20-00/camera_720p"

# Name of the output file
output_filename = "boreas-2021-09-14-20-00/timestamps.txt"
# ========================

def main():
    # 1. Get all PNG files
    try:
        # List all files in the directory
        files = os.listdir(image_folder_path)
        
        # Filter for .png and sort them (Sorting is CRITICAL for SLAM)
        png_files = sorted([f for f in files if f.endswith(".png")])
        
        if not png_files:
            print(f"Error: No .png files found in '{image_folder_path}'")
            return

        print(f"Found {len(png_files)} images.")

        # 2. Write to text file
        with open(output_filename, "w") as f:
            for filename in png_files:
                # Remove the extension (e.g., "1611663720200000.png" -> "1611663720200000")
                timestamp = os.path.splitext(filename)[0]
                
                # Write to file with a newline
                f.write(timestamp + "\n")

        print(f"Success! Generated '{output_filename}' with {len(png_files)} entries.")
        print(f"You can now use this file as the 5th argument for mono_euroc.")

    except FileNotFoundError:
        print(f"Error: The folder '{image_folder_path}' does not exist.")

if __name__ == "__main__":
    main()