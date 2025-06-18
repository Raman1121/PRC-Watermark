import os
import argparse
from PIL import Image

def apply_rotation(image: Image.Image, angle: int) -> Image.Image:
    """
    Applies rotation to an image.

    Args:
        image (Image.Image): The input PIL Image.
        angle (int): The rotation angle in degrees.

    Returns:
        Image.Image: The rotated image. The background is filled with black.
    """
    # Use 'expand=True' to prevent the rotated image from being cropped.
    # 'fillcolor' can be set to 'white', a specific RGB tuple, etc.
    return image.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor='black')

def apply_center_crop(image: Image.Image, scale_factor: float) -> Image.Image:
    """
    Applies a center crop to an image.

    Args:
        image (Image.Image): The input PIL Image.
        scale_factor (float): The fraction of the image to keep (e.g., 0.8 for 80%).

    Returns:
        Image.Image: The center-cropped image.
    """
    original_width, original_height = image.size
    new_width, new_height = int(original_width * scale_factor), int(original_height * scale_factor)

    left = (original_width - new_width) / 2
    top = (original_height - new_height) / 2
    right = (original_width + new_width) / 2
    bottom = (original_height + new_height) / 2

    return image.crop((left, top, right, bottom))

def main():
    """
    Main function to parse arguments and apply attacks to images in a folder.
    """
    parser = argparse.ArgumentParser(
        description="Apply translational attacks to a folder of watermarked images. Attack strengths are configurable via command-line arguments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "input_folder",
        type=str,
        help="Path to the folder containing the watermarked images."
    )
    parser.add_argument(
        "--rotations",
        type=int,
        nargs='+',  # Accept one or more values
        default=[15, 45, 90],
        help="One or more space-separated integer rotation angles to apply."
    )
    parser.add_argument(
        "--crop_factor",
        type=float,
        default=0.8,
        help="Fraction of the image to keep for the center crop (e.g., 0.8 for 80%%)."
    )
    args = parser.parse_args()

    # --- Input Validation ---
    if not os.path.isdir(args.input_folder):
        print(f"Error: Input folder not found at '{args.input_folder}'")
        return
    if not 0.0 < args.crop_factor <= 1.0:
        print(f"Error: Crop factor must be a value between 0 and 1. Got {args.crop_factor}.")
        return

    base_output_dir = "attacked_images"
    os.makedirs(base_output_dir, exist_ok=True)

    image_files = [
        f for f in os.listdir(args.input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
    ]

    print(f"Found {len(image_files)} images in '{args.input_folder}'.")
    print(f"Applying rotations: {args.rotations} degrees")
    print(f"Applying center crop with scale factor: {args.crop_factor}")

    for filename in image_files:
        try:
            image_path = os.path.join(args.input_folder, filename)
            with Image.open(image_path) as img:
                img = img.convert("RGB") # Standardize image mode

                # --- Apply Rotation Attacks ---
                for angle in args.rotations:
                    attack_name = f"rotation_{angle}"
                    output_dir = os.path.join(base_output_dir, attack_name)
                    os.makedirs(output_dir, exist_ok=True)

                    rotated_img = apply_rotation(img, angle)
                    output_filename = os.path.splitext(filename)[0] + '.jpg'
                    output_path = os.path.join(output_dir, output_filename)
                    rotated_img.save(output_path, "JPEG")
                    print(f"  -> Saved {output_path}")

                # --- Apply Cropping Attack ---
                crop_name = f"center_crop_{int(args.crop_factor*100)}_percent"
                output_dir = os.path.join(base_output_dir, crop_name)
                os.makedirs(output_dir, exist_ok=True)

                cropped_img = apply_center_crop(img, args.crop_factor)
                output_filename = os.path.splitext(filename)[0] + '.jpg'
                output_path = os.path.join(output_dir, output_filename)
                cropped_img.save(output_path, "JPEG")
                print(f"  -> Saved {output_path}")

        except Exception as e:
            print(f"Could not process {filename}. Reason: {e}")

    print("\nAttack simulation complete.")
    print(f"Attacked images are saved in appropriately named subdirectories inside '{base_output_dir}'.")


if __name__ == "__main__":
    # --- HOW TO RUN ---
    # 1. Save this script as a Python file (e.g., `attack_script.py`).
    # 2. Create a folder with your source images (e.g., `my_watermarked_images`).
    #
    # 3. Run from your terminal with desired arguments.
    #
    # Example 1: Use default values (rotations 15, 45, 90; crop 80%)
    # python attack_script.py my_watermarked_images
    #
    # Example 2: Specify custom rotation angles and a different crop factor
    # python attack_script.py my_watermarked_images --rotations 10 20 30 --crop_factor 0.5
    #
    # Example 3: Test only a single rotation
    # python attack_script.py my_watermarked_images --rotations 25 --crop_factor 0.9
    main()