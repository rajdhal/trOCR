import gradio as gr
import os
import draw as draw


title = "Interactive Demo of our 4990 Form Reader"
description = "Demo of our 499 project"

# Load in demo images from the example_images folder, if it exists
if os.path.exists("example_images"): images = [f"example_images/{image}" for image in os.listdir("example_images")]

demo = gr.Interface(fn=draw.draw_BBOX, 
                    inputs=gr.Image(type="pil", label="Upload an image"),
                    outputs=[gr.Image(type="pil", label="Annotated Image"),
                             gr.DataFrame(row_count=(2, "dynamic"), col_count=(2,"fixed"), headers=["First Name", "Last Name"], label="Recognized Text"),
                             gr.File(label="CSV File Download")],        
                    title=title,
                    description=description,
                    examples=images)

demo.queue().launch()