#!/usr/bin/env python3
"""
Advanced Low Memory Normal Map Generator

This script generates professional-quality normal maps from height/bump maps
for use in 3D graphics, optimized for low memory usage while offering
Laigter-like features.
"""

import argparse
import numpy as np
from PIL import Image
from scipy import ndimage
import os
import time
import sys

def enhance_edges(height_map, edge_strength=5.0, threshold=0.05):
    """
    Enhance edges in a height map to create sharper normal maps similar to Laigter
    
    Args:
        height_map: 2D numpy array of the height map
        edge_strength: Multiplier for edge enhancement (higher = sharper)
        threshold: Minimum gradient magnitude to consider as an edge
        
    Returns:
        Height map with enhanced edges
    """
    # Calculate edge gradients using Sobel
    dx = ndimage.sobel(height_map, axis=1)
    dy = ndimage.sobel(height_map, axis=0)
    
    # Calculate gradient magnitude
    gradient_magnitude = np.sqrt(dx**2 + dy**2)
    
    # Normalize gradient magnitude to [0,1]
    if gradient_magnitude.max() > 0:
        gradient_magnitude = gradient_magnitude / gradient_magnitude.max()
    
    # Create edge mask where gradient exceeds threshold
    edge_mask = gradient_magnitude > threshold
    
    # Apply edge enhancement
    enhanced_map = height_map.copy()
    
    # Where we have edges, make them more extreme
    edge_enhancement = edge_mask * gradient_magnitude * edge_strength
    
    # Apply enhancement - this creates sharper transitions at edges
    enhanced_map = np.clip(height_map + edge_enhancement * (height_map - 0.5), 0, 1)
    
    return enhanced_map


def enhance_contrast(height_map, contrast=1.5):
    """
    Enhance contrast in the height map
    
    Args:
        height_map: 2D numpy array of the height map
        contrast: Contrast enhancement factor
        
    Returns:
        Height map with enhanced contrast
    """
    # Center around 0.5
    centered = height_map - 0.5
    # Apply contrast
    enhanced = centered * contrast
    # Recenter and clip
    return np.clip(enhanced + 0.5, 0, 1)

def apply_gaussian_blur(height_map, blur_radius=0):
    """
    Apply Gaussian blur to the height map for smoothing
    
    Args:
        height_map: 2D numpy array of the height map
        blur_radius: Radius for Gaussian blur (0 means no blur)
        
    Returns:
        Blurred height map
    """
    if blur_radius <= 0:
        return height_map
    
    return ndimage.gaussian_filter(height_map, sigma=blur_radius)


def calculate_gradients(height_map, kernel_type='sobel', kernel_size=3):
    """
    Calculate gradients using different kernel types
    
    Args:
        height_map: 2D numpy array of the height map
        kernel_type: Type of kernel to use ('sobel', 'prewitt', 'scharr')
        kernel_size: Size of the kernel (3, 5, 7, etc.)
        
    Returns:
        Tuple of (dx, dy) gradient maps
    """
    if kernel_type == 'sobel':
        # Use proper Sobel kernels from scipy
        dx = ndimage.sobel(height_map, axis=1)
        dy = ndimage.sobel(height_map, axis=0)
    elif kernel_type == 'prewitt':
        # Prewitt kernels detect edges differently
        dx = ndimage.prewitt(height_map, axis=1)
        dy = ndimage.prewitt(height_map, axis=0)
    elif kernel_type == 'scharr':
        # Scharr kernels have better rotation invariance
        # Custom implementation since scipy doesn't have Scharr by default
        dx = ndimage.convolve(height_map, np.array([[ 3, 0, -3], 
                                                   [10, 0, -10], 
                                                   [ 3, 0, -3]]))
        dy = ndimage.convolve(height_map, np.array([[ 3, 10,  3], 
                                                   [ 0,  0,  0], 
                                                   [-3, -10, -3]]))
    else:
        # Default to simple gradient calculation
        dx = ndimage.sobel(height_map, axis=1)
        dy = ndimage.sobel(height_map, axis=0)
    
    return dx, dy


def process_chunk(height_map, start_row, end_row, strength=1.0, 
                  kernel_type='sobel', kernel_size=3, 
                  specular_intensity=0.0, height_distance=1,
                  invert_x=False, invert_y=False, edge_enhancement=5.0,
                  sharpness=1.0):
    """
    Process a chunk of the height map to generate normal map data.
    
    Args:
        height_map: 2D numpy array of the height map
        start_row: Starting row index for this chunk
        end_row: Ending row index for this chunk
        strength: Float value to control the intensity of the normal map
        kernel_type: Type of kernel to use ('sobel', 'prewitt', 'scharr')
        kernel_size: Size of the kernel (3, 5, 7, etc.)
        specular_intensity: Controls the specular highlight effect
        height_distance: Integer value for sampling distance
        invert_x: Invert the x component of the normal
        invert_y: Invert the y component of the normal
        edge_enhancement: Factor to enhance edge sharpness
        sharpness: Overall sharpness factor
        
    Returns:
        Chunk of the normal map as a 3D numpy array
    """
    chunk_height = end_row - start_row
    
    # Extract the chunk plus padding for gradient calculation
    pad = max(kernel_size // 2, height_distance)
    padded_chunk = height_map[max(0, start_row-pad):min(height_map.shape[0], end_row+pad), :]
    
    # Calculate gradients for the padded chunk
    dx, dy = calculate_gradients(padded_chunk, kernel_type, kernel_size)
    
    # Adjust for padding in the output
    if start_row > 0:
        dx = dx[pad:, :]
        dy = dy[pad:, :]
    if end_row < height_map.shape[0]:
        dx = dx[:-pad, :]
        dy = dy[:-pad, :]
    
    # Apply edge enhancement to make transitions more dramatic
    if edge_enhancement > 1.0:
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(dx**2 + dy**2)
        
        # Normalize the magnitude
        if gradient_magnitude.max() > 0:
            gradient_magnitude = gradient_magnitude / gradient_magnitude.max()
        
        # Enhance dx and dy based on gradient magnitude
        edge_factor = 1.0 + (gradient_magnitude * (edge_enhancement - 1.0))
        dx = dx * edge_factor
        dy = dy * edge_factor
    
    # Apply sharpness enhancement - increases contrast in the gradient
    if sharpness > 1.0:
        # Enhance gradients by increasing their magnitude
        dx_sign = np.sign(dx)
        dy_sign = np.sign(dy)
        dx_abs = np.abs(dx)
        dy_abs = np.abs(dy)
        
        # Apply power function to increase contrast
        dx = dx_sign * (dx_abs ** sharpness)
        dy = dy_sign * (dy_abs ** sharpness)
    
    # Apply strength and optional inversion
    dx = dx * strength * (-1 if invert_x else 1)
    dy = dy * strength * (-1 if invert_y else 1)
    
    # Apply specular intensity by enhancing the z component
    z_component = 1.0 + specular_intensity
    
    # Create normal vectors [dx, dy, z]
    normals = np.zeros((chunk_height, height_map.shape[1], 3), dtype=np.float32)
    normals[:, :, 0] = -dx  # x component (red)
    normals[:, :, 1] = -dy  # y component (green)
    normals[:, :, 2] = z_component  # z component (blue)
    
    # Normalize vectors
    norm = np.sqrt(np.sum(normals**2, axis=2, keepdims=True))
    # Avoid division by zero
    norm[norm < 0.0001] = 1.0
    normals = normals / norm
    
    # Convert from [-1, 1] to [0, 1] range
    normals = (normals + 1.0) * 0.5
    
    return normals

def generate_normal_map_low_memory(input_image, strength=1.0, invert=False, 
                                  wrap_edges=True, height_distance=1, 
                                  blur_radius=0, kernel_type='sobel',
                                  kernel_size=3, specular_intensity=0.0,
                                  invert_x=False, invert_y=False,
                                  chunk_size=100, edge_enhancement=5.0,
                                  contrast_enhancement=1.5, sharpness=1.0):
    """
    Generate a normal map from a height/bump map using low memory approach.
    
    Args:
        input_image: PIL Image object of the height/bump map
        strength: Float value to control the intensity of the normal map
        invert: Boolean to invert the height map before processing
        wrap_edges: Boolean to wrap edges for seamless textures
        height_distance: Integer value for sampling distance
        blur_radius: Amount of gaussian blur to apply before processing
        kernel_type: Type of kernel to use ('sobel', 'prewitt', 'scharr')
        kernel_size: Size of the kernel (3, 5, 7, etc.)
        specular_intensity: Controls the specular highlight effect
        invert_x: Invert the x component of the normal
        invert_y: Invert the y component of the normal
        chunk_size: Size of chunks to process at once (rows)
        edge_enhancement: Factor to enhance edge sharpness
        contrast_enhancement: Factor to enhance contrast
        sharpness: Overall sharpness factor
        
    Returns:
        PIL Image object of the generated normal map with preserved transparency
    """
    # Check if input has alpha
    has_alpha = input_image.mode == 'RGBA'  # Fixed: Correctly check for RGBA mode
    
    # Convert to RGB for processing
    rgb_image = input_image.convert('RGB')
    
    # Convert to grayscale for height map
    gray_image = input_image.convert('L')
    
    # Convert to numpy array for processing
    height_map = np.array(gray_image).astype(np.float32) / 255.0
    
    # Invert if requested
    if invert:
        height_map = 1.0 - height_map

    # Apply contrast enhancement
    if contrast_enhancement > 1.0:
        height_map = enhance_contrast(height_map, contrast_enhancement)
    
    # Apply edge enhancement
    if edge_enhancement > 0:
        height_map = enhance_edges(height_map, edge_enhancement)
    
    # Apply Gaussian blur if specified (only once)
    if blur_radius > 0:
        height_map = apply_gaussian_blur(height_map, blur_radius)
    
    # Handle edge wrapping if requested
    pad_size = max(kernel_size // 2, height_distance)
    if wrap_edges:
        print("IM RWAPPING")
        # For wrapped edges, we use a different padding approach
        height_map = np.pad(height_map, pad_size, mode='wrap')
        # We'll crop back to original size later
        original_shape = (gray_image.height, gray_image.width)
        crop_later = True
    else:
        crop_later = False
    
    # Get dimensions
    height, width = height_map.shape
    
    # Create output array
    normal_map = np.zeros((height, width, 3), dtype=np.float32)
    
    # Process in small chunks to reduce memory usage
    for start_row in range(0, height, chunk_size):
        end_row = min(start_row + chunk_size, height)
        print(f"Processing rows {start_row} to {end_row} of {height}...", end='\r')
        sys.stdout.flush()
        
        # Process this chunk
        chunk_normals = process_chunk(
            height_map, 
            start_row, 
            end_row, 
            strength=strength, 
            kernel_type=kernel_type,
            kernel_size=kernel_size,
            specular_intensity=specular_intensity,
            height_distance=height_distance,
            invert_x=invert_x,
            invert_y=invert_y,
            edge_enhancement=edge_enhancement,
            sharpness=sharpness
        )
        
        # Add to output array
        normal_map[start_row:end_row, :, :] = chunk_normals
        
        # Free memory
        del chunk_normals
    
    print()  # New line after progress
    
    # Crop back to original size if we padded for wrapping
    if crop_later:
        normal_map = normal_map[pad_size:-pad_size, pad_size:-pad_size]
    
    # Convert to 8-bit RGB
    normal_map = (normal_map * 255).astype(np.uint8)
    
    # Create PIL image from numpy array
    result = Image.fromarray(normal_map, mode='RGB')
    
    # # Apply alpha channel if present, processing in chunks to save memory
    # if has_alpha:
    #     # Convert result to RGBA
    #     result = result.convert('RGBA')
    #     result_array = np.array(result)
        
    #     # Process alpha in chunks
    #     for start_row in range(0, result_array.shape[0], chunk_size):
    #         end_row = min(start_row + chunk_size, result_array.shape[0])
    #         print(f"Applying alpha for rows {start_row} to {end_row} of {result_array.shape[0]}...", end='\r')
    #         sys.stdout.flush()
            
    #         # Get chunk of alpha channel
    #         alpha_chunk = np.array(input_image.crop((0, start_row, width, end_row)).split()[3])
            
    #         # Apply to result
    #         result_array[start_row:end_row, :, 3] = alpha_chunk
            
    #         # Free memory
    #         del alpha_chunk
        
    #     print()  # New line after progress
    #     result = Image.fromarray(result_array, mode='RGBA')
    
    # return result

    if has_alpha:
        # Convert result to RGBA
        result = result.convert('RGBA')
        result_array = np.array(result)
        
        # Get the alpha channel from the original image
        alpha_channel = np.array(input_image.split()[3])
        
        # Ensure alpha channel has the same dimensions as the result
        if alpha_channel.shape != result_array.shape[:2]:
            # Resize alpha channel to match result dimensions
            alpha_img = Image.fromarray(alpha_channel)
            alpha_img = alpha_img.resize((result_array.shape[1], result_array.shape[0]))
            alpha_channel = np.array(alpha_img)
        
        # Process alpha in chunks
        for start_row in range(0, result_array.shape[0], chunk_size):
            end_row = min(start_row + chunk_size, result_array.shape[0])
            print(f"Applying alpha for rows {start_row} to {end_row} of {result_array.shape[0]}...", end='\r')
            sys.stdout.flush()
            
            # Apply alpha to result
            result_array[start_row:end_row, :, 3] = alpha_channel[start_row:end_row]
        
        print()  # New line after progress
        result = Image.fromarray(result_array, mode='RGBA')
    
    return result

def main():
    """Main function to parse arguments and process the image."""
    parser = argparse.ArgumentParser(
        description='Generate professional-quality normal maps from height/bump maps (low memory version).'
    )
    parser.add_argument('input', help='Input height/bump map image file')
    parser.add_argument('-o', '--output', help='Output normal map image file')
    parser.add_argument('-s', '--strength', type=float, default=1.0,
                        help='Strength/intensity of the normal map (default: 1.0)')
    parser.add_argument('-d', '--distance', type=int, default=1,
                        help='Sampling distance for height calculations (default: 1)')
    parser.add_argument('-i', '--invert', action='store_true',
                        help='Invert the height map before processing')
    parser.add_argument('-w', '--wrap', action='store_true', default=True,
                        help='Wrap edges for seamless textures (default: True)')
    parser.add_argument('--no-wrap', action='store_false', dest='wrap',
                        help='Disable edge wrapping for non-seamless textures')
    parser.add_argument('-b', '--blur', type=float, default=0.0,
                        help='Gaussian blur radius to apply (default: 0.0)')
    parser.add_argument('-k', '--kernel', choices=['sobel', 'prewitt', 'scharr'], 
                        default='sobel', help='Filter kernel type (default: sobel)')
    parser.add_argument('-ks', '--kernel-size', type=int, default=3,
                        help='Filter kernel size (default: 3)')
    parser.add_argument('-sp', '--specular', type=float, default=0.0,
                        help='Specular intensity effect (default: 0.0)')
    parser.add_argument('-ix', '--invert-x', action='store_true',
                        help='Invert the X component of the normal')
    parser.add_argument('-iy', '--invert-y', action='store_true',
                        help='Invert the Y component of the normal')
    parser.add_argument('-c', '--chunk-size', type=int, default=100,
                        help='Number of rows to process at once (default: 100)')
    parser.add_argument('-e', '--edge-enhancement', type=float, default=5.0,
                        help='Edge enhancement factor (default: 5.0)')
    parser.add_argument('-ce', '--contrast-enhancement', type=float, default=1.5,
                        help='Contrast enhancement factor (default: 1.5)')
    parser.add_argument('-sh', '--sharpness', type=float, default=1.0,
                        help='Overall sharpness of the normal map (default: 1.0)')

    args = parser.parse_args()
    
    # Determine output filename if not specified
    if not args.output:
        base, ext = os.path.splitext(args.input)
        # Insert '_n' before the numbers at the end of the filename
        import re
        numeric_suffix = re.search(r'_\d+$', base)
        if numeric_suffix:
            # If there are numbers at the end, insert '_n' before them
            suffix_pos = numeric_suffix.start()
            args.output = f"{base[:suffix_pos]}_n{base[suffix_pos:]}{ext}"
        else:
            # Otherwise, just append '_n' to the base name
            args.output = f"{base}_n{ext}"
    
    try:
        # Load input image
        input_image = Image.open(args.input)
        
        print(f"Generating normal map from '{args.input}'...")
        print(f"Strength: {args.strength}")
        print(f"Height sampling distance: {args.distance}")
        print(f"Blur radius: {args.blur}")
        print(f"Kernel type: {args.kernel}")
        print(f"Kernel size: {args.kernel_size}")
        print(f"Specular intensity: {args.specular}")
        print(f"Chunk size: {args.chunk_size} rows")
        print(f"Edge enhancement: {args.edge_enhancement}")
        print(f"Contrast enhancement: {args.contrast_enhancement}")
        print(f"Sharpness: {args.sharpness}")
        
        if args.invert:
            print("Inverting height map")
        if args.invert_x:
            print("Inverting X component")
        if args.invert_y:
            print("Inverting Y component")
        if args.wrap:
            print("Wrapping edges for seamless texture")
        else:
            print("Not wrapping edges (non-seamless texture)")
        
        # Check if input has transparency
        has_transparency = input_image.mode == 'RGBA'
        if has_transparency:
            print("Preserving transparency from input image")
        
        # Time the operation
        start_time = time.time()
        
        # Generate normal map
        normal_map = generate_normal_map_low_memory(
            input_image,
            strength=args.strength,
            invert=args.invert,
            wrap_edges=args.wrap,
            height_distance=args.distance,
            blur_radius=args.blur,
            kernel_type=args.kernel,
            kernel_size=args.kernel_size,
            specular_intensity=args.specular,
            invert_x=args.invert_x,
            invert_y=args.invert_y,
            chunk_size=args.chunk_size,
            edge_enhancement=args.edge_enhancement,
            contrast_enhancement=args.contrast_enhancement,
            sharpness=args.sharpness
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