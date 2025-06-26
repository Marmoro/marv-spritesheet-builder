#!/usr/bin/env python3
"""
Fast Normal Map Generator

This script generates normal maps from height/bump maps for use in 3D graphics,
optimized for speed using vectorized operations and multiprocessing.
It calculates surface normals based on the gradient of the height map and
encodes them as RGB colors in the output image. The script preserves transparency
from the input image, ensuring that transparent areas remain transparent in the
output normal map.
"""

import argparse
import numpy as np
from PIL import Image
import os
import time
import multiprocessing
from functools import partial


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
    
    # Calculate gradients using array slicing (much faster than pixel-by-pixel)
    dx = padded[height_distance:-height_distance, 2*height_distance:] - padded[height_distance:-height_distance, :-2*height_distance]
    dy = padded[2*height_distance:, height_distance:-height_distance] - padded[:-2*height_distance, height_distance:-height_distance]
    
    # Normalize by distance
    dx = dx / (2 * height_distance)
    dy = dy / (2 * height_distance)
    
    return dx, dy


def process_chunk(height_map, chunk_info, strength=1.0, height_distance=1):
    """
    Process a chunk of the height map to generate normal map data.
    
    Args:
        height_map: 2D numpy array of the height map
        chunk_info: Tuple of (start_row, end_row)
        strength: Strength/intensity of the normal map
        height_distance: Sampling distance for height calculations
        
    Returns:
        Chunk of the normal map as a 3D numpy array
    """
    start_row, end_row = chunk_info
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


def generate_normal_map_fast(input_image, strength=1.0, invert=False, wrap_edges=False, 
                             height_distance=1, num_processes=None):
    """
    Generate a normal map from a height/bump map using vectorized operations and multiprocessing.
    
    Args:
        input_image: PIL Image object of the height/bump map
        strength: Float value to control the intensity of the normal map (default: 1.0)
        invert: Boolean to invert the height map before processing (default: False)
        wrap_edges: Boolean to wrap edges for seamless textures (default: False)
        height_distance: Integer value for sampling distance (default: 1)
        num_processes: Number of processes to use (default: None, uses CPU count)
        
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
    
    # Determine number of processes to use
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    # Split the image into chunks for parallel processing
    chunk_size = max(1, height // num_processes)
    chunks = [(i, min(i + chunk_size, height)) for i in range(0, height, chunk_size)]
    
    # Process chunks in parallel
    with multiprocessing.Pool(processes=num_processes) as pool:
        process_func = partial(process_chunk, height_map, 
                              strength=strength, height_distance=height_distance)
        normal_chunks = pool.map(process_func, chunks)
    
    # Combine chunks
    normal_map = np.vstack(normal_chunks)
    
    # Crop back to original size if we padded for wrapping
    if crop_later:
        normal_map = normal_map[height_distance:-height_distance, height_distance:-height_distance]
    
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
    parser = argparse.ArgumentParser(description='Generate a normal map from a height/bump map (fast version).')
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
    parser.add_argument('-p', '--processes', type=int, default=None,
                        help='Number of processes to use (default: auto)')
    
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
        print(f"Processes: {args.processes if args.processes else 'auto'}")
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
        normal_map = generate_normal_map_fast(
            input_image,
            strength=args.strength,
            invert=args.invert,
            wrap_edges=args.wrap,
            height_distance=args.distance,
            num_processes=args.processes
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