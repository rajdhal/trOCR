import gradio as gr
import draw


title = "Interactive demo of Form Reader"
description = "Demo of our 499 project"

iface = gr.Interface(fn=draw.draw_BBOX, 
                     inputs=gr.components.Image(type="pil", label="Upload an image"),
                     outputs=[gr.components.Textbox(default="Text Output"), gr.components.Image(type="pil")],        
                     title=title,
                     description=description)

iface.launch(debug=True)