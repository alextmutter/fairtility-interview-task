import os
import numpy as np
from PIL import Image
import time
from InferenceFunction import inference
import pandas as pd
from pathlib import Path
import json


with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


def NaiveProcess(
            input_dir=None, # Image directory path
            output_dir="performance_data", # Metric data directory path
            window=8, # Length of fixed sliding window
            poll_interval=10, # Poll every X seconds
            max_idle=2, # Maximum consecutive idle intervals before ending script
            save_metrics=True, # Save metric logs as graphs
            print_metrics=True, # Display live metric logs
            reorder_for_late=False, # Retrospectively run as True if late image was generated
            late_image_info=["",0]
        ):

    idle_count = 0  # Counter to track consecutive idle intervals
    prev_total_files_count = 0 # Counting previous total files for each interval
    processing_count = 0 # Tracks number of inference computations
    total_processing_time = 0 # Tracks total time for each inference computation
    
    processing_count_tracker = [] # Tracks number of real inference computations per necessary
    necessary_count_tracker = [] # Tracks number of necessary inference computations

    if not input:
        print("Path to image directory required!\n")
        idle_count = max_idle+1
    
    while idle_count < max_idle:
        start_time = time.time()
        input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), input_dir)
        new_image_files = [file for file in os.listdir(input_dir) if file.endswith(('.png', '.jpg', '.jpeg'))]

        # Sort images by date added
        new_image_files.sort(key=lambda file: os.path.getctime(os.path.join(input_dir, file)))
    
        # For validating optimised pipeline with late images
        if reorder_for_late == True:
            late_image = late_image_info[0] # image file name
            late_index = late_image_info[1] # correct image index
            new_image_files.remove(late_image)
            new_image_files.insert(late_index, late_image)
        
        # Removing duplicate images from pipeline and directory
        for file in new_image_files:
            if "copy" in file:
                new_image_files.remove(file)
                os.remove(os.path.join(input_dir, file))
                print(file, "identified as a duplicate and has been removed.\n")
            
        # Frame and window processing
        if len(new_image_files) > prev_total_files_count:
            idle_count = 0  # Reset idle counter when new images are found
            processed_windows = [] # Tracks processed windows (resets with each new frame)
            if len(new_image_files) >= window: # Check there are enough frames to process a window
                for i in range(len(new_image_files) - window + 1): # Always starts from the first frame
                    batch = new_image_files[i:i + window] # Creates batches for the window
                    processed_windows.append(inference(batch))
                    processing_count+=1

            processing_count_tracker.append(processing_count)
            necessary_count_tracker.append(len(processed_windows))
        
            prev_total_files_count = len(new_image_files) # Tracking previous number of frames for activity
            end_time = time.time()
            total_processing_time += (end_time-start_time)

            # Live metric logs
            if print_metrics == True:
                print("Current total processing time:", total_processing_time)
                print("Current processing count:", processing_count)
                print("Current length of processed windows:", len(processed_windows), '\n')

        else:
            idle_count += 1 # Increment idle counter if no new images are found compared to previous count
                
        time.sleep(poll_interval)
    
    print("No new images found for", max_idle, "consecutive intervals. Ending the script.")
        
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
            "necessary_processes": necessary_count_tracker,
            "real_processes": processing_count_tracker
            }
        
        df = pd.DataFrame(windows_processed)
        csv_filename = "naive_real_vs_necessary_computations.csv"
        df.to_csv(os.path.join(output_dir, csv_filename), index=False)

        # Final metric totals to .csv
        outputs = {
            "inference_function_totals": [sum(processed_windows)],
            "total_processing_time": [total_processing_time],
            "total_processes": [processing_count]
            }

        df = pd.DataFrame(outputs)
        csv_filename = "naive_outputs.csv"
        df.to_csv(os.path.join(output_dir, csv_filename), index=False)
        

if __name__ == "__main__":
    NaiveProcess(
            input_dir=config["IMAGE_DIR"],
            output_dir=config["METRIC_DATA_DIR"],
            window=config["WINDOW_LENGTH"],
            poll_interval=config["POLL_INTERVAL"],
            #reorder_for_late=True,
            #late_image_info=["image_2025-02-10-21-25-14-554630.png", 10],
            max_idle=config["MAX_IDLE_COUNT"]
        )







    
