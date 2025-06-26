#!/usr/bin/env python3
"""
Normal Map Generator

This script generates normal maps from height/bump maps for use in 3D graphics.
It calculates surface normals based on the gradient of the height map and
encodes them as RGB colors in the output image. The script preserves transparency
from the input image, ensuring that transparent areas remain transparent in the
output normal map.
"""

import argparse
import numpy as np
from PIL import Image
import os


def generate_normal_map(input_image, strength=1.0, invert=False, wrap_edges=False, height_distance=1):
    """
    Generate a normal map from a height/bump map.
    
    Args:
        input_image: PIL Image object of the height/bump map
        strength: Float value to control the intensity of the normal map (default: 1.0)
        invert: Boolean to invert the height map before processing (default: False)
        wrap_edges: Boolean to wrap edges for seamless textures (default: False)
        height_distance: Integer value for sampling distance when calculating gradients (default: 1)
                         Higher values create more pronounced but less detailed normal maps
        
    Returns:
        PIL Image object of the generated normal map with preserved transparency
    """
    # Store original alpha channel if present
    has_alpha = input_image.mode == 'RGBA'
    if has_alpha:
        # Split the image into RGB and alpha channels
        rgb_image, alpha_channel = input_image.convert('RGB'), input_image.split()[3]
        alpha_array = np.array(alpha_channel)
    else:
        rgb_image = input_image.convert('RGB')
    
    # Convert to grayscale for height map
    gray_image = input_image.convert('L')
    
    # Convert to numpy array for processing
    height_map = np.array(gray_image).astype(np.float32) / 255.0
    
    # Invert if requested
    if invert:
        height_map = 1.0 - height_map
    
    # Get dimensions
    height, width = height_map.shape
    
    # Create empty normal map (RGB)
    normal_map = np.zeros((height, width, 3), dtype=np.float32)
    
    # Calculate gradients using Sobel-like approach
    for y in range(height):
        for x in range(width):
            # Get neighboring pixels with wrapping if enabled, using height_distance
            if wrap_edges:
                left = height_map[y, (x - height_distance) % width]
                right = height_map[y, (x + height_distance) % width]
                top = height_map[(y - height_distance) % height, x]
                bottom = height_map[(y + height_distance) % height, x]
            else:
                # Handle edges without wrapping
                left = height_map[y, max(0, x - height_distance)]
                right = height_map[y, min(width - 1, x + height_distance)]
                top = height_map[max(0, y - height_distance), x]
                bottom = height_map[min(height - 1, y + height_distance), x]
            
            # Calculate gradient (dx, dy)
            dx = (right - left) * strength
            dy = (bottom - top) * strength
            
            # Create normal vector (dx, dy, 1)
            # The z component is 1 because we're looking at the surface from above
            normal = np.array([-dx, -dy, 1.0])
            
            # Normalize the vector
            length = np.sqrt(np.sum(normal**2))
            if length > 0:
                normal = normal / length
            
            # Convert from [-1, 1] to [0, 1] range for RGB
            normal = (normal + 1.0) * 0.5
            
            # Store in normal map
            normal_map[y, x] = normal
    
    # Convert to 8-bit RGB
    normal_map = (normal_map * 255).astype(np.uint8)
    
    # Create PIL image from numpy array
    result = Image.fromarray(normal_map, mode='RGB')
    
    # Apply original alpha channel if present
    if has_alpha:
        # Convert result to RGBA
        result = result.convert('RGBA')
        # Create a new image with the same alpha channel
        result_array = np.array(result)
        result_array[:, :, 3] = alpha_array
        result = Image.fromarray(result_array, mode='RGBA')
    
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
    
    # Determine output filename if not specified
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_normal{ext}"
    
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
        
        # Generate normal map
        normal_map = generate_normal_map(
            input_image,
            strength=args.strength,
            invert=args.invert,
            wrap_edges=args.wrap,
            height_distance=args.distance
        )
        
        # Save output image
        normal_map.save(args.output)
        print(f"Normal map saved to '{args.output}'")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())