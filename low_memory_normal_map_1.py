#!/usr/bin/env python3
"""
Normal Map Generator

This script generates normal maps from height/bump maps for use in 3D graphics.
Modified for simplicity and to prevent accidental double-processing.
"""

import argparse
import numpy as np
from PIL import Image
import os
import time
import sys


def sobel_filters(height_map, height_distance=1):
    """
    Apply Sobel-like filters to the height map using vectorized operations.
    
    Args:
        height_map: 2D numpy array of the height map
        height_distance: Sampling distance for height calculations
        
    Returns:
        Tuple of (dx, dy) gradient maps
    """
    # Pad the height map for edge handling
    padded = np.pad(height_map, height_distance, mode='edge')
    
    # Calculate gradients using array slicing
    dx = padded[height_distance:-height_distance, 2*height_distance:] - padded[height_distance:-height_distance, :-2*height_distance]
    dy = padded[2*height_distance:, height_distance:-height_distance] - padded[:-2*height_distance, height_distance:-height_distance]
    
    # Normalize by distance
    dx = dx / (2 * height_distance)
    dy = dy / (2 * height_distance)
    
    return dx, dy


def generate_normal_map(input_image, strength=1.0, invert=False, wrap_edges=False, height_distance=1):
    """
    Generate a normal map from a height/bump map.
    
    Args:
        input_image: PIL Image object of the height/bump map
        strength: Float value to control the intensity of the normal map (default: 1.0)
        invert: Boolean to invert the height map before processing (default: False)
        wrap_edges: Boolean to wrap edges for seamless textures (default: False)
        height_distance: Integer value for sampling distance (default: 1)
        
    Returns:
        PIL Image object of the generated normal map with preserved transparency
    """
    # Check if input has alpha
    has_alpha = input_image.mode == 'RGBA'
    
    # Convert to grayscale for height map
    gray_image = input_image.convert('L')
    
    # Convert to numpy array for processing
    height_map = np.array(gray_image).astype(np.float32) / 255.0
    
    # Invert if requested
    if invert:
        height_map = 1.0 - height_map
    
    # Handle edge wrapping if requested
    pad_mode = 'wrap' if wrap_edges else 'edge'
    
    # Calculate gradients
    dx, dy = sobel_filters(height_map, height_distance)
    
    # Apply strength
    dx = dx * strength
    dy = dy * strength
    
    # Create normal vectors [dx, dy, 1]
    height, width = dx.shape
    normals = np.zeros((height, width, 3), dtype=np.float32)
    normals[:, :, 0] = -dx
    normals[:, :, 1] = -dy
    normals[:, :, 2] = 1.0
    
    # Normalize vectors
    norm = np.sqrt(np.sum(normals**2, axis=2, keepdims=True))
    # Avoid division by zero
    norm[norm == 0] = 1.0
    normals = normals / norm
    
    # Convert from [-1, 1] to [0, 1] range
    normals = (normals + 1.0) * 0.5
    
    # Convert to 8-bit RGB
    normal_map = (normals * 255).astype(np.uint8)
    
    # Create PIL image from numpy array
    result = Image.fromarray(normal_map, mode='RGB')
    
    # Apply alpha channel if present
    if has_alpha:
        alpha = input_image.split()[3]
        result = result.convert('RGBA')
        result.putalpha(alpha)
    
    return result


def main():
    """Main function to parse arguments and process the image."""
    parser = argparse.ArgumentParser(description='Generate a normal map from a height/bump map.')
    parser.add_argument('input', help='Input height/bump map image file')
    parser.add_argument('-o', '--output', help='Output normal map image file')
    parser.add_argument('-s', '--strength', type=float, default=1.0,
                        help='Strength/intensity of the normal map (default: 1.0)')
    parser.add_argument('-d', '--distance', type=int, default=1,
                        help='Sampling distance for height calculations (default: 1)')
    parser.add_argument('-i', '--invert', action='store_true',
                        help='Invert the height map before processing')
    parser.add_argument('-w', '--wrap', action='store_true',
                        help='Wrap edges for seamless textures')
    
    args = parser.parse_args()
    
    # Check if input file already looks like a normal map (to prevent double processing)
    if "_n" in os.path.basename(args.input):
        print(f"Warning: Input file '{args.input}' appears to already be a normal map (has '_n' in filename).")
        print("Operation cancelled to prevent double processing.")
        return 0
    
    # Determine output filename if not specified
# Determine output filename if not specified
    if not args.output:
        # Extract base name and extension
        base, ext = os.path.splitext(args.input)
        
        # Check if the filename follows the pattern filename_digits.ext
        import re
        match = re.search(r'(.+)_(\d+)$', base)
        
        if match:
            # If it matches the pattern, insert _n before the digits
            filename_part = match.group(1)
            digits_part = match.group(2)
            args.output = f"{filename_part}_n_{digits_part}{ext}"
        else:
            # Otherwise, just append _n to the base name
            if not base.endswith("_n"):
                args.output = f"{base}_n{ext}"
            else:
                args.output = f"{base}{ext}"
    
    try:
        # Load input image
        input_image = Image.open(args.input)
        
        print(f"Generating normal map from '{args.input}'...")
        print(f"Strength: {args.strength}")
        print(f"Height sampling distance: {args.distance}")
        if args.invert:
            print("Inverting height map")
        if args.wrap:
            print("Wrapping edges for seamless texture")
        
        # Check if input has transparency
        has_transparency = input_image.mode == 'RGBA'
        if has_transparency:
            print("Preserving transparency from input image")
        
        # Time the operation
        start_time = time.time()
        
        # Generate normal map
        normal_map = generate_normal_map(
            input_image,
            strength=args.strength,
            invert=args.invert,
            wrap_edges=args.wrap,
            height_distance=args.distance
        )
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Save output image
        normal_map.save(args.output)
        print(f"Normal map saved to '{args.output}'")
        print(f"Processing time: {elapsed_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())