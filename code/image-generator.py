import os
import numpy as np
import time
from PIL import Image
from datetime import datetime
import random
from pathlib import Path
import json


with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


# Generating frame images
def generate_random_image(width=256, height=256):
    image = np.random.randint(0, 256, (height, width, 2), dtype=np.uint8)
    return image


# Image data generator
def save_fake_data(
                output_dir=None, # Path to image directory
                total_images=64, # Total number of images that will be generated for the simulation.
                min_sleep_interval=1, # For simulating the randomness of a real world data stream
                max_sleep_interval=5,
                min_num_images=1,
                max_num_images=3,
                unit_test=False # Includes a duplicated and late image into the stream
            ):
    
    # Clear existing images from directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), output_dir)
    print(output_dir)
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Cleared existing directory.")
    else:
        os.makedirs(output_dir)
    
    time.sleep(6)  # Delay to allow setup of processing pipelines


    # Adding duplicate and late test images
    if unit_test == True:
        duplicate_image_num = 1 #random.randint(1, total_images)
        late_image_num = 10 #random.randint(1, total_images)
        if duplicate_image_num == late_image_num: # Making sure they are not the same and within bounds
            late_image_num -= 1

    images_generated = 0
    while images_generated < total_images:
    
        # Generate a random number of images for batch
        num_images = random.randint(min_num_images, max_num_images)
        num_images = min(num_images, total_images - images_generated) # Ensuring it doesn't exceed bounds
        
        for n in range(num_images):
            img = generate_random_image()
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")  # Timestamped files to mimic real world data
            img_path = os.path.join(output_dir, f"image_{timestamp}.png")
            
            if unit_test == True and images_generated == duplicate_image_num:
                Image.fromarray(img).save(img_path)
                print(f"Saved: {img_path}")

                # Saving duplicate file
                img_path = os.path.join(output_dir, f"image_{timestamp}_copy.png")
                Image.fromarray(img).save(img_path)
                
            elif unit_test == True and images_generated == late_image_num:
                # Storing late image file to be saved at the end 
                late_image = img
                late_path = img_path

            else:
                # Saving regularly generated images
                Image.fromarray(img).save(img_path)
                print(f"Saved: {img_path}")

            images_generated += 1
            print("images_generated:", images_generated)

        if images_generated < total_images:
            # Random sleep interval to mimic real world data stream
            interval = random.randint(min_sleep_interval, max_sleep_interval)
            time.sleep(interval)

    if unit_test == True and images_generated >= total_images: # Saving the late image test
        Image.fromarray(late_image).save(late_path)
        print(f"Saved: {late_path}")

    print("Finished generating", images_generated, "images")

if __name__ == "__main__":
    save_fake_data(
                output_dir=config["IMAGE_DIR"],
                total_images=config["TOTAL_IMAGES"],
                unit_test=config["INCLUDE_UNIT_TESTS"]
            )






