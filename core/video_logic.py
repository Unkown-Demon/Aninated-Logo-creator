import imageio.v3 as iio
from PIL import Image
from typing import List

# Configuration for rendering (must match render_logic.py)
FPS = 30

def create_gif(frames: List[Image.Image], output_path: str):
    """
    Creates a GIF from a list of PIL Image frames.
    
    :param frames: List of PIL Image objects.
    :param output_path: Path to save the output GIF file.
    """
    # Convert PIL Images to numpy arrays (required by imageio)
    np_frames = [iio.core.asarray(frame) for frame in frames]
    
    # Save as GIF
    iio.imwrite(
        output_path, 
        np_frames, 
        duration=1000/FPS, # Duration of each frame in milliseconds
        loop=0, # Loop forever
        codec='gif'
    )

def create_video(frames: List[Image.Image], output_path: str):
    """
    Creates a video (MP4) from a list of PIL Image frames.
    
    :param frames: List of PIL Image objects.
    :param output_path: Path to save the output MP4 file.
    """
    # Convert PIL Images to numpy arrays (required by imageio)
    np_frames = [iio.core.asarray(frame) for frame in frames]
    
    # Save as MP4
    iio.imwrite(
        output_path, 
        np_frames, 
        fps=FPS,
        codec='libx264', # H.264 codec
        quality=8, # Quality scale (0-10, 10 is best)
        pixelformat='yuv420p' # For compatibility
    )

if __name__ == '__main__':
    print("Video/GIF logic is ready.")
