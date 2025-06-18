# comprehensive_attack_script.py

import os
import io
import argparse
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

# ==============================================================================
# ==                           ATTACK IMPLEMENTATIONS                         ==
# ==============================================================================

# --- Photometric (Signal Processing) Attacks ---

def apply_jpeg_compression(image: Image.Image, quality: int) -> Image.Image:
    """Simulates JPEG compression by saving and reloading the image in memory."""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")

def apply_gaussian_noise(image: Image.Image, std_dev: float) -> Image.Image:
    """Adds Gaussian noise to the image."""
    img_array = np.array(image).astype(np.float32)
    noise = np.random.normal(0, std_dev, img_array.shape)
    noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_array)

def apply_blur(image: Image.Image, radius: float) -> Image.Image:
    """Applies a Gaussian blur filter."""
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

def apply_brightness(image: Image.Image, factor: float) -> Image.Image:
    """Adjusts the image brightness."""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def apply_contrast(image: Image.Image, factor: float) -> Image.Image:
    """Adjusts the image contrast."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def apply_gamma_correction(image: Image.Image, gamma: float) -> Image.Image:
    """Applies gamma correction."""
    if gamma <= 0:
        raise ValueError("Gamma must be > 0.")
    inv_gamma = 1.0 / gamma
    # Create a lookup table (LUT)
    lut = [int(((i / 255.0) ** inv_gamma) * 255) for i in range(256)]
    # Apply LUT to all channels if image is not grayscale
    if image.mode == 'L':
        return image.point(lut)
    else:
        return image.point(lut * image.getbands().__len__())

# --- Geometric Attacks ---

def apply_scaling(image: Image.Image, scale_factor: float) -> Image.Image:
    """Scales an image down and then back up."""
    original_size = image.size
    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
    # Scale down
    downscaled_img = image.resize(new_size, Image.Resampling.BICUBIC)
    # Scale back up to original size
    upscaled_img = downscaled_img.resize(original_size, Image.Resampling.BICUBIC)
    return upscaled_img

def apply_shear(image: Image.Image, angle: int) -> Image.Image:
    """Applies a shear transformation."""
    return image.transform(image.size, Image.AFFINE, (1, angle / 100, 0, 0, 1, 0))

def apply_flip(image: Image.Image) -> Image.Image:
    """Applies a horizontal flip."""
    return ImageOps.mirror(image)


# ==============================================================================
# ==                            MAIN SCRIPT LOGIC                             ==
# ==============================================================================

def main():
    """Main function to parse arguments and apply all defined attacks."""
    parser = argparse.ArgumentParser(
        description="A comprehensive script to apply various attacks to a folder of images for watermarking robustness testing.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_folder", help="Path to the folder containing source images.")

    # --- Attack Strength Arguments ---
    parser.add_argument("--jpeg_q", type=int, nargs='+', default=[75, 50, 25], help="Space-separated JPEG quality levels.")
    parser.add_argument("--noise_std", type=float, nargs='+', default=[10.0, 20.0], help="Space-separated standard deviations for Gaussian noise.")
    parser.add_argument("--blur_r", type=float, nargs='+', default=[1.0, 2.0], help="Space-separated radii for Gaussian blur.")
    parser.add_argument("--bright_f", type=float, nargs='+', default=[0.8, 1.2], help="Space-separated brightness factors.")
    parser.add_argument("--contrast_f", type=float, nargs='+', default=[0.7, 1.3], help="Space-separated contrast factors.")
    parser.add_argument("--gamma_v", type=float, nargs='+', default=[0.8, 1.2], help="Space-separated gamma correction values.")
    parser.add_argument("--scale_f", type=float, nargs='+', default=[0.5, 0.7], help="Space-separated scaling factors.")
    parser.add_argument("--shear_a", type=int, nargs='+', default=[10, 20], help="Space-separated shear angles (integer part of percentage).")
    parser.add_argument("--no_flip", action="store_true", help="Disable the flip attack.")

    args = parser.parse_args()

    # --- Setup ---
    if not os.path.isdir(args.input_folder):
        print(f"Error: Input folder not found at '{args.input_folder}'")
        return

    base_output_dir = "attack_results"
    os.makedirs(base_output_dir, exist_ok=True)

    image_files = [f for f in os.listdir(args.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    if not image_files:
        print(f"No images found in '{args.input_folder}'.")
        return

    print(f"Found {len(image_files)} images. Starting attack simulation...")

    # --- Main Loop ---
    for filename in image_files:
        try:
            image_path = os.path.join(args.input_folder, filename)
            with Image.open(image_path) as img:
                img = img.convert("RGB") # Standardize to RGB

                # --- Define attacks and their parameters from args ---
                attacks_to_run = {
                    "jpeg_quality": (apply_jpeg_compression, args.jpeg_q),
                    "gaussian_noise_std": (apply_gaussian_noise, args.noise_std),
                    "blur_radius": (apply_blur, args.blur_r),
                    "brightness_factor": (apply_brightness, args.bright_f),
                    "contrast_factor": (apply_contrast, args.contrast_f),
                    "gamma_value": (apply_gamma_correction, args.gamma_v),
                    "scale_factor": (apply_scaling, args.scale_f),
                    "shear_angle": (apply_shear, args.shear_a),
                }

                # --- Apply each attack with its specified strengths ---
                for name, (func, strengths) in attacks_to_run.items():
                    for strength in strengths:
                        attack_name = f"{name}_{strength}"
                        output_dir = os.path.join(base_output_dir, attack_name)
                        os.makedirs(output_dir, exist_ok=True)

                        attacked_img = func(img.copy(), strength)
                        output_filename = os.path.splitext(filename)[0] + '.jpg'
                        output_path = os.path.join(output_dir, output_filename)
                        attacked_img.save(output_path, "JPEG", quality=95)

                # --- Handle flip separately as it has no strength parameter ---
                if not args.no_flip:
                    output_dir = os.path.join(base_output_dir, "flip_horizontal")
                    os.makedirs(output_dir, exist_ok=True)
                    flipped_img = apply_flip(img.copy())
                    output_filename = os.path.splitext(filename)[0] + '.jpg'
                    output_path = os.path.join(output_dir, output_filename)
                    flipped_img.save(output_path, "JPEG", quality=95)

            print(f"Processed attacks for: {filename}")

        except Exception as e:
            print(f"Could not process {filename}. Reason: {e}")

    print(f"\nAttack simulation complete. Results are in '{base_output_dir}'.")


if __name__ == "__main__":
    # --- HOW TO RUN ---
    # 1. Save this script as `comprehensive_attack_script.py`.
    # 2. Create a folder with your source images (e.g., `my_watermarked_images`).
    #
    # 3. Run from your terminal.
    #
    # Example 1: Run with default settings
    # python comprehensive_attack_script.py my_watermarked_images
    #
    # Example 2: Test only specific JPEG qualities and a single noise level
    # python comprehensive_attack_script.py my_watermarked_images --jpeg_q 90 60 30 --noise_std 15.0
    #
    # Example 3: Run only scaling and blurring with custom strengths
    # python comprehensive_attack_script.py my_watermarked_images --jpeg_q --noise_std --blur_r 1.5 3.0 --bright_f --contrast_f --gamma_v --scale_f 0.6 --shear_a --no_flip
    # (Note: Providing an attack argument with no values uses its default. To truly disable, a more complex setup is needed, but this shows customization.)
    main()