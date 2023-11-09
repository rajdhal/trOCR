import gradio as gr
import os
import draw as draw

# Title and description that are on webpage
title = "Interactive Demo of our 4990 Form Reader"
description = "Demo of our 499 project"

# Load in demo images from the example_images folder, if it exists
if os.path.exists("example_images"): images = [f"example_images/{image}" for image in os.listdir("example_images")]

demo = gr.Interface(fn=draw.draw_BBOX, 
                    inputs=gr.Image(type="pil", label="Upload an image"),
                    outputs=[
                        gr.Image(type="pil", label="Annotated Image"),      # Output image
                        gr.DataFrame(row_count=(2, "dynamic"),              # Output table
                                     col_count=(2,"fixed"), 
                                     headers=["First Name", "Last Name"], 
                                     label="Recognized Text"), 
                        gr.File(label="CSV File Download")                  # Output CSV file for download
                        ],        
                    title=title,                # Output the title
                    description=description,    # Output the description
                    examples=images)            # Output the example images

# Launch the demo app
# Queue allows for output that takes longer than 2 minutes
demo.queue().launch()