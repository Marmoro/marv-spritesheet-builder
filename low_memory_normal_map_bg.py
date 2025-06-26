#!/usr/bin/env python3
"""
Low Memory Normal Map Generator

This script generates normal maps from height/bump maps for use in 3D graphics,
optimized for low memory usage. It processes the image in small chunks to avoid
memory issues and doesn't use multiprocessing.
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
    # Create shifted arrays for gradient calculation
    height, width = height_map.shape
    
    # Pad the height map for edge handling
    padded = np.pad(height_map, height_distance, mode='edge')
    
    # Calculate gradients using array slicing
    dx = padded[height_distance:-height_distance, 2*height_distance:] - padded[height_distance:-height_distance, :-2*height_distance]
    dy = padded[2*height_distance:, height_distance:-height_distance] - padded[:-2*height_distance, height_distance:-height_distance]
    
    # Normalize by distance
    dx = dx / (2 * height_distance)
    dy = dy / (2 * height_distance)
    
    return dx, dy


def process_chunk(height_map, start_row, end_row, strength=1.0, height_distance=1):
    """
    Process a chunk of the height map to generate normal map data.
    
    Args:
        height_map: 2D numpy array of the height map
        start_row, end_row: Row range to process
        strength: Strength/intensity of the normal map
        height_distance: Sampling distance for height calculations
        
    Returns:
        Chunk of the normal map as a 3D numpy array
    """
    chunk_height = end_row - start_row
    
    # Extract the chunk plus padding for gradient calculation
    pad = height_distance
    padded_chunk = height_map[max(0, start_row-pad):min(height_map.shape[0], end_row+pad), :]
    
    # Calculate gradients for the padded chunk
    dx, dy = sobel_filters(padded_chunk, height_distance)
    
    # Adjust for padding in the output
    if start_row > 0:
        dx = dx[pad:, :]
        dy = dy[pad:, :]
    if end_row < height_map.shape[0]:
        dx = dx[:-pad, :]
        dy = dy[:-pad, :]
    
    # Apply strength
    dx = dx * strength
    dy = dy * strength
    
    # Create normal vectors [dx, dy, 1]
    normals = np.zeros((chunk_height, height_map.shape[1], 3), dtype=np.float32)
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
    
    return normals


def generate_normal_map_low_memory(input_image, strength=1.0, invert=False, wrap_edges=False, 
                                  height_distance=1, chunk_size=100):
    """
    Generate a normal map from a height/bump map using low memory approach.
    
    Args:
        input_image: PIL Image object of the height/bump map
        strength: Float value to control the intensity of the normal map (default: 1.0)
        invert: Boolean to invert the height map before processing (default: False)
        wrap_edges: Boolean to wrap edges for seamless textures (default: False)
        height_distance: Integer value for sampling distance (default: 1)
        chunk_size: Size of chunks to process at once (default: 100 rows)
        
    Returns:
        PIL Image object of the generated normal map with preserved transparency
    """
    # Check if input has alpha
    has_alpha = input_image.mode == 'RGBA'
    
    # Convert to RGB for processing
    rgb_image = input_image.convert('RGB')
    
    # Convert to grayscale for height map
    gray_image = input_image.convert('L')
    
    # Convert to numpy array for processing
    height_map = np.array(gray_image).astype(np.float32) / 255.0
    
    # Invert if requested
    if invert:
        height_map = 1.0 - height_map
    
    # Handle edge wrapping if requested
    if wrap_edges:
        # For wrapped edges, we use a different padding approach
        height_map = np.pad(height_map, height_distance, mode='wrap')
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
            height_distance=height_distance
        )
        
        # Add to output array
        normal_map[start_row:end_row, :, :] = chunk_normals
        
        # Free memory
        del chunk_normals
    
    print()  # New line after progress
    
    # Crop back to original size if we padded for wrapping
    if crop_later:
        normal_map = normal_map[height_distance:-height_distance, height_distance:-height_distance]
    
    # Convert to 8-bit RGB
    normal_map = (normal_map * 255).astype(np.uint8)
    
    # Create PIL image from numpy array
    result = Image.fromarray(normal_map, mode='RGB')
    
    # Apply alpha channel if present, processing in chunks to save memory
    if has_alpha:
        # Convert result to RGBA
        result = result.convert('RGBA')
        result_array = np.array(result)
        
        # Process alpha in chunks
        for start_row in range(0, height, chunk_size):
            end_row = min(start_row + chunk_size, height)
            print(f"Applying alpha for rows {start_row} to {end_row} of {height}...", end='\r')
            sys.stdout.flush()
            
            # Get chunk of alpha channel
            alpha_chunk = np.array(input_image.crop((0, start_row, width, end_row)).split()[3])
            
            # Apply to result
            result_array[start_row:end_row, :, 3] = alpha_chunk
            
            # Free memory
            del alpha_chunk
        
        print()  # New line after progress
        result = Image.fromarray(result_array, mode='RGBA')
    
    return result


def main():
    """Main function to parse arguments and process the image."""
    parser = argparse.ArgumentParser(description='Generate a normal map from a height/bump map (low memory version).')
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
    parser.add_argument('-c', '--chunk-size', type=int, default=100,
                        help='Number of rows to process at once (default: 100)')
    
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
        print(f"Chunk size: {args.chunk_size} rows")
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
        normal_map = generate_normal_map_low_memory(
            input_image,
            strength=args.strength,
            invert=args.invert,
            wrap_edges=args.wrap,
            height_distance=args.distance,
            chunk_size=args.chunk_size
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