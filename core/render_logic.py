import os
import numpy as np
from PIL import Image
from core.renderer import OffscreenRenderer
from core.models import MODELS, perspective, lookat, rotate, translate
from math import radians

# Configuration for rendering
RENDER_WIDTH = 512
RENDER_HEIGHT = 512
FPS = 30
DURATION = 5 # seconds
TOTAL_FRAMES = FPS * DURATION

def render_animation(images_paths, shape_name, output_path):
    """
    Renders a 3D animation of the given shape textured with the provided images.
    
    :param images_paths: List of local file paths for the images.
    :param shape_name: The name of the 3D shape ('cube', 'coin', 'pyramid').
    :param output_path: The path to save the final GIF/Video.
    :return: List of PIL Image objects (frames).
    """
    
    # 1. Initialize Renderer
    renderer = OffscreenRenderer(RENDER_WIDTH, RENDER_HEIGHT)
    
    # 2. Setup Camera
    # Simple camera setup: looking at the origin from a distance
    eye = np.array([0.0, 0.0, 3.0])
    center = np.array([0.0, 0.0, 0.0])
    up = np.array([0.0, 1.0, 0.0])
    
    view_matrix = lookat(eye, center, up)
    projection_matrix = perspective(fovy=45.0, aspect=RENDER_WIDTH/RENDER_HEIGHT, near=0.1, far=100.0)
    
    renderer.set_camera(view_matrix, projection_matrix)
    
    # 3. Load Model
    if shape_name not in MODELS:
        raise ValueError(f"Unknown shape: {shape_name}")
        
    vertices, indices = MODELS[shape_name]()
    renderer.load_geometry(vertices, indices)
    
    # 4. Load Textures
    textures = []
    for path in images_paths:
        try:
            img = Image.open(path).convert('RGBA')
            texture = renderer.ctx.texture(img.size, 4, img.tobytes())
            textures.append(texture)
        except Exception as e:
            print(f"Error loading texture {path}: {e}")
            # Use a placeholder texture if loading fails
            textures.append(renderer.ctx.texture((1, 1), 4, bytes([255, 0, 255, 255]))) # Magenta placeholder
            
    # Handle texture count mismatch for cube (6 faces)
    if shape_name == 'cube' and len(textures) < 6:
        # Repeat textures if not enough are provided for a cube
        while len(textures) < 6:
            textures.extend(textures)
        textures = textures[:6]
    
    # For other shapes, we'll just use the first texture for now
    if shape_name != 'cube' and not textures:
        # Fallback if no textures are loaded
        textures.append(renderer.ctx.texture((1, 1), 4, bytes([255, 255, 255, 255]))) # White placeholder
        
    # 5. Render Loop
    frames = []
    for frame_num in range(TOTAL_FRAMES):
        # Calculate rotation angle (360 degrees over the duration)
        angle = (frame_num / TOTAL_FRAMES) * 360.0
        
        # Simple rotation around the Y-axis
        model_matrix = rotate(angle, np.array([0.0, 1.0, 0.0]))
        
        # Select texture based on shape and frame (simple cycling for cube)
        if shape_name == 'cube':
            # Cube faces are rendered sequentially, so we need to handle texture switching
            # This is a simplification. Proper cube texturing requires 6 draw calls or a texture array.
            # For now, we'll use the first texture for the whole object.
            current_texture = textures[0]
        elif shape_name == 'coin':
            # For coin, we can alternate between the first two textures for front/back
            # This requires a more complex shader or multiple draw calls, which is too complex for this phase.
            # For now, use the first texture.
            current_texture = textures[0]
        else:
            current_texture = textures[0]
            
        # Render the frame
        frame_image = renderer.render_frame(model_matrix, current_texture)
        frames.append(frame_image)
        
    # 6. Cleanup
    for texture in textures:
        texture.release()
    renderer.release()
    
    return frames

if __name__ == '__main__':
    # Example usage for testing (requires dummy files)
    print("Render logic is ready. Needs integration with bot and video/gif creation.")
