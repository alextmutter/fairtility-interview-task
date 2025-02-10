import os
import numpy as np
from PIL import Image
import time
from InferenceFunction import inference
import pandas as pd
from datetime import datetime
import json


with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


def OptimisedProcess(
                input_dir=None, # Image directory path
                output_dir="performance_data", # Metric data directory path
                window=8, # Length of fixed sliding window
                poll_interval=10, # Poll every X seconds
                max_idle=2, # Maximum consecutive idle intervals before ending script
                save_metrics=True, # Save metric logs as graphs
                print_metrics=True # Display live metric logs
            ):
    
    idle_count = 0  # Counter to track consecutive idle intervals
    processing_count = 0 # Tracks number of inference computations
    total_processing_time = 0 # Tracks total time for each inference computation

    processed_windows = [] # Stores output values from processed windows
    processed_images = [] # Stores filenames of processed images
    processing_count_tracker = [] # Tracks number of real inference computations per necessary
    necessary_count_tracker = [] # Tracks number of necessary inference computations

    if not input:
        print("Path to image directory required!\n")
        idle_count = max_idle+1

    while idle_count < max_idle:
        start_time = time.time()
        input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), input_dir)
        new_image_files = []
        for file in os.listdir(input_dir):
            if file.endswith(('.png', '.jpg', '.jpeg')) and file not in processed_images:
                new_image_files.append(file)

        # Sort images by date added
        new_image_files.sort(key=lambda file: os.path.getctime(os.path.join(input_dir, file)))
        
        # Removing duplicate images from pipeline and directory
        for file in new_image_files:
            if "copy" in file:
                new_image_files.remove(file)
                os.remove(os.path.join(input_dir, file))
                print(file, "identified as a duplicate and has been removed.\n")

        # Checking for late images and finding correct position
        for a in range(0, len(new_image_files)):
            if a == 0 and len(processed_images) >= 1:
                current_img = new_image_files[a]
                prev_img = processed_images[-1]
            elif a == 0 and len(processed_images) < 1:
                current_img = new_image_files[a+1]
                prev_img = new_image_files[a]
            else:
                current_img = new_image_files[a]
                prev_img = new_image_files[a-1]

            current_timestamp = datetime.strptime(current_img.split("_")[1].split(".")[0], "%Y-%m-%d-%H-%M-%S-%f")
            prev_timestamp = datetime.strptime(prev_img.split("_")[1].split(".")[0], "%Y-%m-%d-%H-%M-%S-%f")

            if current_timestamp < prev_timestamp:
                print("late file detected:", current_img)
                new_image_files.remove(current_img) # Remove late file from current location

                # Finding correct position of late image
                if len(processed_images) == 0: # For processing all images at once
                    for j in range(len(new_image_files)):
                        if datetime.strptime(new_image_files[j].split("_")[1].split(".")[0], "%Y-%m-%d-%H-%M-%S-%f") > current_timestamp:
                            correct_position = j
                            new_image_files.insert(j, current_img)
                            print("image inserted at index:", j, "\n")
                            break
                else: # For processing live video stream
                    for j in range(len(processed_images)):
                        if datetime.strptime(processed_images[j].split("_")[1].split(".")[0], "%Y-%m-%d-%H-%M-%S-%f") > current_timestamp:
                            correct_position = j
                            print("restarting processing from index:", correct_position, '\n')
                            
                            # Take the 7 images before the correct position to be reprocessed
                            new_image_files = processed_images[j-(window-1):j] + [current_img]
                            
                            # Remove the same images to avoid double processing
                            processed_images = processed_images[:j-(window-1)]

                            # Remove void window computations to avoid double processing
                            if j >= (2*window-1): # Minimum frames needed to not reproces all windows
                                processed_windows = [len(processed_images)-(window-1)] 
                            else:
                                processed_windows = []
                            break
        
        # Frame and window processing                
        if len(new_image_files) > 0:
            idle_count = 0  # Reset idle counter when new images are found
            if len(new_image_files)+len(processed_images) >= window: # Check there are enough frames to process a window
                for n in range(len(new_image_files)):
                    processed_images.append(new_image_files[n])
                    i = len(processed_images)
                    if i >= window: # Finding index at which a batch can be computed
                        batch = processed_images[i-window:i] # Creates batches for the window
                        processed_windows.append(inference(batch))
                        processing_count+=1

                processing_count_tracker.append(processing_count)
                necessary_count_tracker.append(len(processed_windows))
                
                end_time = time.time()
                total_processing_time += (end_time-start_time)

                if print_metrics == True:
                    print("Current total processing time:", total_processing_time)
                    print("Current processing count:", processing_count)
                    print("Current length of processed windows:", len(processed_windows), '\n')
                        
        else:
            idle_count += 1 # Increment idle counter if no new images are found compared to previous count
        
        time.sleep(poll_interval)

    print("No new images found for two consecutive intervals. Ending the script.")
    
    # Final metric totals
    if print_metrics == True:
        print("Total windows processed:", processing_count)
        print("Sum of processed windows:", sum(processed_windows))
        print("Total processing time:", total_processing_time)

    # Exporting live and total metrics data to .csv
    if save_metrics == True:

        output_dir = os.path.join(os.path.dirname(__file__), output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Saving running log to .csv
        windows_processed = {
            "optimised_processes": necessary_count_tracker,
            "real_processes": processing_count_tracker
            }
        
        df = pd.DataFrame(windows_processed)
        csv_filename = "optimised_real_vs_necessary_computations.csv"
        df.to_csv(os.path.join(output_dir, csv_filename), index=False)


        # Final metric totals to .csv
        outputs = {
            "inference_function_totals": [sum(processed_windows)],
            "total_processing_time": [total_processing_time],
            "total_processes": [processing_count]
            }

        df = pd.DataFrame(outputs)
        csv_filename = "optimised_outputs.csv"
        df.to_csv(os.path.join(output_dir, csv_filename), index=False)

if __name__ == "__main__":
    OptimisedProcess(
                input_dir=config["IMAGE_DIR"],
                output_dir=config["METRIC_DATA_DIR"],
                window=config["WINDOW_LENGTH"],
                poll_interval=config["POLL_INTERVAL"],
                max_idle=config["MAX_IDLE_COUNT"]
            )









    
