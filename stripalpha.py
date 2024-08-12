from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, filedialog
import argparse
import sys

from PIL import Image
from alive_progress import alive_bar
import numpy as np

def wrap(val: int): # ok its stupid but its funny
    return val & 255

def hex_to_rgb(hexcolour: str):
    hexcolour = hexcolour.lstrip('#')
    return tuple(int(hexcolour[i:i+2], 16) for i in (0, 2, 4))

def parse_color(value):
    if value.startswith('#'):
        return hex_to_rgb(value)
    else:    
        try:
            parts = [wrap(int(x)) for x in value.replace(',', ' ').split()]
            if len(parts) == 3:
                return tuple(parts)
        except ValueError:
            pass
    
    # Raise an error if neither format is matched
    raise argparse.ArgumentTypeError("Color must be a hex code (e.g., #FF5733) or a list of 3 integers (e.g., 255, 87, 51)")

def blend_with_background(original_rgb, background_rgb, alpha):
    """
    Blends the original RGB values with the background RGB based on the alpha value.
    The alpha should be in the range [0, 255].
    """
    background_rgb = np.array(background_rgb).reshape(1, 1, 3)

    return (1 - alpha[..., None] / 255) * background_rgb + (alpha[..., None] / 255) * original_rgb


def strip_alpha(img: Image.Image, rgb: tuple):
    """
    Replaces fully transparent pixels with the specified RGB color and blends semi-transparent pixels
    with the specified RGB background color. Sets alpha to 255 for all pixels.
    """
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    npimg = np.array(img).astype(np.float32) # minimize rounding issues
    original_rgb = npimg[:, :, :3]
    alpha_channel = npimg[:, :, 3]
    transparent_mask = alpha_channel == 0
    blended_rgb = blend_with_background(original_rgb, np.array(rgb), alpha_channel)
    blended_rgb[transparent_mask] = rgb
    final_image = np.dstack((blended_rgb, np.full_like(alpha_channel, 255)))
    final_image = np.clip(final_image, 0, 255).astype(np.uint8) # return to range 0-255
    
    return Image.fromarray(final_image, 'RGBA')

def batch_process_folder(folder_path, replacement_rgb, create_subfolder=True):
    """
    Batch processes all images in a folder with the specified replacement color.
    """
    png_files = [f for f in Path(folder_path).glob('**/*.png') if f.is_file()]
    len_files = len(png_files)
    if create_subfolder:
        processed_folder = Path(folder_path) / 'processed'
        processed_folder.mkdir(exist_ok=True)
        with alive_bar(len_files) as bar:
            for png_file in png_files:
                img = Image.open(png_file)
                processed_img = strip_alpha(img, replacement_rgb)
                processed_img.save(processed_folder / png_file.name)
                bar()
    else:
        with alive_bar(len_files) as bar:
            for png_file in png_files:
                img = Image.open(png_file)
                _image_path = Path(png_file)
                processed_img = strip_alpha(img, replacement_rgb)
                new_image_path = _image_path.with_name(f'{_image_path.stem}_processed{_image_path.suffix}')
                processed_img.save(new_image_path)
                bar()

def process_image(image_path, replacement_rgb):
    """
    Processes an image with the specified replacement color.
    """

    img = Image.open(image_path)
    _image_path = Path(image_path)

    processed_img = strip_alpha(img, replacement_rgb)

    new_image_path = _image_path.with_name(f'{_image_path.stem}_processed{_image_path.suffix}')
    processed_img.save(new_image_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Alpha Remover for PNG images. If called without arguments, opens GUI dialogs for selecting a folder and a colour, images are saved to a subfolder. If called with -i, the path to an image is required. If called with -f, the path to a folder is required.')
    
    io_group = parser.add_mutually_exclusive_group()
    io_group.add_argument('-f', '--folder', 
                          type=str, 
                          help='Path to folder containing images, exlusive to -i', 
                          action="store")
    io_group.add_argument('-i', '--image', 
                          type=str, 
                          help='Path to single image, exclusive to -f', 
                          action="store")
    
    parser.add_argument('-c', '--color',
                         type=parse_color, help='Hex string (eg. #FFFFFF) or string of numbers (eg. "255, 255, 255") of replacement color, numbers outside of range 0-255 are wrapped, have fun. Default ("0, 0, 0")', 
                         default=("0, 0, 0"), 
                         action="store")
    parser.add_argument('-ns', '--no-subfolder',
                        help='Skip creating subfolder for processed images, defaults to creating a new folder', 
                        action="store_false")
    
    args = parser.parse_args()

    if len(sys.argv) == 1:
        root = tk.Tk()
        root.withdraw()

        folder_path = filedialog.askdirectory(title="Select Folder")
        if not folder_path:
            print("No folder selected.")
            exit()

        # Prompt user to select a color
        color_result = colorchooser.askcolor(title="Choose Replacement Color")
        if not color_result or not color_result[1]:
            print("No color selected.")
            exit()

        replacement_rgb = hex_to_rgb(color_result[1])

        batch_process_folder(folder_path, replacement_rgb)

    else:
        print(f'Starting with args: {args}')
        if args.folder:
            batch_process_folder(args.folder, args.color, args.no_subfolder)
        elif args.image:
            process_image(args.image, args.color)
        else:
            print("No folder or image selected.")
            exit()