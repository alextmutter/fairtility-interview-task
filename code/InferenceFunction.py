import os
import numpy as np
from PIL import Image
from pathlib import Path


WINDOW_LENGTH = 8
#IMAGE_DIR = "../incoming_images"
IMAGE_DIR = Path(__file__).resolve().parent.parent / "incoming_images"


def inference(
        image_batch, # List of images
        input_dir=IMAGE_DIR, # Path to image directory
        window=WINDOW_LENGTH # Number of frames in fixed sliding window 
    ):
    
    if len(image_batch) != window:
        print(len(image_batch), "Not enough images for inference.")
        return None
    
    else:
        images = []
        for file in image_batch:
            img_path = os.path.join(input_dir, file)
            img = np.array(Image.open(img_path))
            images.append(img)

        images = np.stack(images)  # Shape: (WINDOW_LENGTH, 256, 256, 2)
        avg_pixel = np.mean(images, axis=0)  # Compute average pixel per channel
        sum_avg_pixel = np.sum(avg_pixel)  # Compute sum of average pixels

        return sum_avg_pixel
