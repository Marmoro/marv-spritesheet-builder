#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from PIL import Image

# Configuration constants
CREATE_BACKUPS = False  # Set to False to disable creation of backup files

def resize_image(input_path, output_path, target_size=(512, 512), use_webp=False):
    """
    Resize an image to the target size while preserving quality and transparency.
    
    Args:
        input_path: Path to the source image
        output_path: Path where the resized image will be saved
        target_size: Tuple of (width, height) for the target size
        use_webp: If True, convert to WebP format; otherwise, maintain original format
    """
    try:
        # Open the image and preserve transparency
        with Image.open(input_path) as img:
            # Check if the image is already the target size
            if img.size == target_size:
                print(f"Skipping {input_path} - already {target_size[0]}x{target_size[1]}")
                return
            
            # Only process 1024x1024 images
            if img.size != (1024, 1024):
                print(f"Skipping {input_path} - not 1024x1024 (current size: {img.size[0]}x{img.size[1]})")
                return
            
            # Resize using Lanczos resampling for high quality
            resized_img = img.resize(target_size, Image.LANCZOS)
            
            # Determine output format
            if use_webp:
                output_path = output_path.with_suffix('.webp')
                resized_img.save(output_path, 'WEBP', quality=95, lossless=True)
            else:
                # For PNG, maintain the format and use maximum quality
                if img.format == 'PNG':
                    resized_img.save(output_path, 'PNG', optimize=True)
                else:
                    # For other formats, maintain the original format
                    resized_img.save(output_path, img.format)
            
            orig_size = os.path.getsize(input_path)
            new_size = os.path.getsize(output_path)
            reduction = (1 - new_size/orig_size) * 100
            
            print(f"Resized {input_path.name} from {img.size[0]}x{img.size[1]} to {target_size[0]}x{target_size[1]}")
            print(f"Size reduction: {orig_size/1024:.2f}KB → {new_size/1024:.2f}KB ({reduction:.1f}%)")
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def process_directory(directory, use_webp=False, output_dir=None):
    """
    Process all images in the given directory.
    
    Args:
        directory: Path to the directory containing images
        use_webp: If True, convert images to WebP format
        output_dir: Directory where processed images will be saved. If None, originals are replaced.
    """
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: {directory} is not a valid directory")
        return
    
    # Set up output directory
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(exist_ok=True, parents=True)
    else:
        out_path = None
    
    # Find all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
    image_files = [f for f in dir_path.iterdir() 
                  if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"No image files found in {directory}")
        return
    
    print(f"Found {len(image_files)} image files to process")
    
    # Process each image
    for img_path in image_files:
        if out_path:
            # If output directory is specified, save there with the same name
            output_path = out_path / img_path.name
            resize_image(img_path, output_path, use_webp=use_webp)
        else:
            # If we're replacing the original file
            if CREATE_BACKUPS:
                # Create a backup and then replace
                backup_path = img_path.with_suffix(img_path.suffix + '.backup')
                if not backup_path.exists():
                    os.rename(img_path, backup_path)
                resize_image(backup_path, img_path, use_webp=use_webp)
            else:
                # Create a temporary file for the resized image
                temp_output = img_path.with_suffix(img_path.suffix + '.temp')
                resize_image(img_path, temp_output, use_webp=use_webp)
                
                # If successful, replace the original file
                if temp_output.exists():
                    if use_webp:
                        # If converting to WebP, we need to handle the different file extension
                        webp_path = img_path.with_suffix('.webp')
                        os.replace(temp_output, webp_path)
                        if webp_path != img_path:  # Only remove original if name changed
                            os.remove(img_path)
                    else:
                        os.replace(temp_output, img_path)

def main():
    parser = argparse.ArgumentParser(description='Resize 1024x1024 images to 512x512 with minimal quality loss')
    parser.add_argument('directory', help='Directory containing images to resize')
    parser.add_argument('--webp', action='store_true', help='Convert images to WebP format')
    parser.add_argument('--output', '-o', help='Output directory (if not specified, originals will be replaced)')
    parser.add_argument('--backup', action='store_true', help='Create backup files of originals (default depends on CREATE_BACKUPS constant)')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup files of originals')
    
    args = parser.parse_args()
    
    # Handle backup options
    global CREATE_BACKUPS
    if args.backup:
        CREATE_BACKUPS = True
    elif args.no_backup:
        CREATE_BACKUPS = False
    
    process_directory(args.directory, use_webp=args.webp, output_dir=args.output)

if __name__ == '__main__':
    main()