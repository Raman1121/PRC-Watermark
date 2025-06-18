# sequential_attack_script.py

import os
import io
import argparse
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

# ==============================================================================
# ==                           ATTACK IMPLEMENTATIONS                         ==
# ==============================================================================
# (These functions remain unchanged)

def apply_jpeg_compression(image: Image.Image, quality: int) -> Image.Image:
    """Simulates JPEG compression by saving and reloading the image in memory."""
    buffer = io.BytesIO()
    # Convert to RGB before saving as JPEG to avoid issues with alpha channels
    image.convert("RGB").save(buffer, format="JPEG", quality=quality)
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
    if gamma <= 0: return image
    inv_gamma = 1.0 / gamma
    lut = [int(((i / 255.0) ** inv_gamma) * 255) for i in range(256)]
    return image.point(lut * len(image.getbands()))

def apply_rotation(image: Image.Image, angle: int) -> Image.Image:
    """Applies rotation to an image, expanding the frame to fit."""
    return image.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor='black')

def apply_center_crop(image: Image.Image, scale_factor: float) -> Image.Image:
    """Applies a center crop to an image, keeping a specified fraction."""
    if not 0.0 < scale_factor <= 1.0: return image
    ow, oh = image.size
    nw, nh = int(ow * scale_factor), int(oh * scale_factor)
    left, top = (ow - nw) / 2, (oh - nh) / 2
    return image.crop((left, top, left + nw, top + nh))

def apply_scaling(image: Image.Image, scale_factor: float) -> Image.Image:
    """Scales an image down and then back up."""
    original_size = image.size
    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
    downscaled_img = image.resize(new_size, Image.Resampling.BICUBIC)
    return downscaled_img.resize(original_size, Image.Resampling.BICUBIC)

def apply_shear(image: Image.Image, angle: int) -> Image.Image:
    """Applies a shear transformation."""
    return image.transform(image.size, Image.AFFINE, (1, angle / 100, 0, 0, 1, 0))

def apply_flip(image: Image.Image, _: bool) -> Image.Image: # Add dummy arg to match structure
    """Applies a horizontal flip."""
    return ImageOps.mirror(image)


# ==============================================================================
# ==                            MAIN SCRIPT LOGIC                             ==
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Apply a sequential chain of attacks to images. Specify one or more attack flags to build the chain.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_folder", help="Path to the folder containing source images.")

    # --- CLI arguments now default to None to be inactive by default ---
    parser.add_argument("--crop_factor", type=float, default=None, help="Crop factor to keep (e.g., 0.8).")
    parser.add_argument("--rotation", type=int, default=None, help="Rotation angle in degrees.")
    parser.add_argument("--scale_factor", type=float, default=None, help="Downscaling factor before resizing up.")
    parser.add_argument("--shear_angle", type=int, default=None, help="Shear angle strength.")
    parser.add_argument("--flip", action="store_true", help="Apply a horizontal flip.")
    parser.add_argument("--brightness", type=float, default=None, help="Brightness factor (e.g., 1.5 for brighter).")
    parser.add_argument("--contrast", type=float, default=None, help="Contrast factor (e.g., 1.5 for higher contrast).")
    parser.add_argument("--gamma", type=float, default=None, help="Gamma value (e.g., 1.2).")
    parser.add_argument("--blur_radius", type=float, default=None, help="Gaussian blur radius.")
    parser.add_argument("--noise_std", type=float, default=None, help="Standard deviation for Gaussian noise.")
    parser.add_argument("--jpeg_q", type=int, default=None, help="Final JPEG quality (0-100).")

    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(f"Error: Input folder not found at '{args.input_folder}'")
        return

    # --- Build the attack chain based on provided arguments ---
    attack_chain = []
    dir_name_parts = []

    # The order of these 'if' statements determines the sequence of attacks.
    if args.crop_factor is not None:
        attack_chain.append((apply_center_crop, args.crop_factor))
        dir_name_parts.append(f"crop_{args.crop_factor}")
    if args.rotation is not None:
        attack_chain.append((apply_rotation, args.rotation))
        dir_name_parts.append(f"rotate_{args.rotation}")
    if args.scale_factor is not None:
        attack_chain.append((apply_scaling, args.scale_factor))
        dir_name_parts.append(f"scale_{args.scale_factor}")
    if args.shear_angle is not None:
        attack_chain.append((apply_shear, args.shear_angle))
        dir_name_parts.append(f"shear_{args.shear_angle}")
    if args.flip:
        attack_chain.append((apply_flip, True))
        dir_name_parts.append("flip")
    if args.brightness is not None:
        attack_chain.append((apply_brightness, args.brightness))
        dir_name_parts.append(f"bright_{args.brightness}")
    if args.contrast is not None:
        attack_chain.append((apply_contrast, args.contrast))
        dir_name_parts.append(f"contrast_{args.contrast}")
    if args.gamma is not None:
        attack_chain.append((apply_gamma_correction, args.gamma))
        dir_name_parts.append(f"gamma_{args.gamma}")
    if args.blur_radius is not None:
        attack_chain.append((apply_blur, args.blur_radius))
        dir_name_parts.append(f"blur_{args.blur_radius}")
    if args.noise_std is not None:
        attack_chain.append((apply_gaussian_noise, args.noise_std))
        dir_name_parts.append(f"noise_{args.noise_std}")
    # JPEG compression is often the last step, simulating a final save.
    if args.jpeg_q is not None:
        attack_chain.append((apply_jpeg_compression, args.jpeg_q))
        dir_name_parts.append(f"jpeg_{args.jpeg_q}")

    if not attack_chain:
        print("No attacks specified. Please provide at least one attack flag (e.g., --rotation 45).")
        return

    # --- Create the combined output directory ---
    base_output_dir = "attack_results_sequential"
    output_dir_name = "_".join(dir_name_parts)
    final_output_dir = os.path.join(base_output_dir, output_dir_name)
    os.makedirs(final_output_dir, exist_ok=True)
    print(f"Applying attack chain: {output_dir_name}")
    print(f"Output will be saved to: {final_output_dir}")

    # --- Process Images ---
    image_files = [f for f in os.listdir(args.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for filename in image_files:
        try:
            image_path = os.path.join(args.input_folder, filename)
            with Image.open(image_path) as img:
                attacked_img = img.copy().convert("RGB")

                # Apply each specified attack in sequence
                for func, strength in attack_chain:
                    attacked_img = func(attacked_img, strength)

                output_filename = os.path.splitext(filename)[0] + '.jpg'
                output_path = os.path.join(final_output_dir, output_filename)
                attacked_img.save(output_path, "JPEG", quality=100) # Save final result at high quality

        except Exception as e:
            print(f"Could not process {filename}. Reason: {e}")
    
    print("\nProcessing complete.")


if __name__ == "__main__":
    # --- HOW TO RUN ---
    # 1. Save this script as `sequential_attack_script.py`.
    # 2. Create a folder with your source images (e.g., `my_watermarked_images`).
    #
    # 3. Run from your terminal, specifying the attacks you want to chain together.
    #
    # Example 1: Apply only a single rotation
    # python sequential_attack_script.py my_watermarked_images --rotation 45
    #
    # Example 2: Apply only a single JPEG compression
    # python sequential_attack_script.py my_watermarked_images --jpeg_q 50
    #
    # Example 3: Chain three attacks: crop, then rotate, then save as JPEG
    # python sequential_attack_script.py my_watermarked_images --crop_factor 0.9 --rotation 15 --jpeg_q 75
    #
    # Example 4: A more complex chain of geometric and photometric attacks
    # python sequential_attack_script.py my_watermarked_images --rotation -10 --scale_factor 0.7 --brightness 1.1 --noise_std 5
    main()