from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import re

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

def text_recognition(image):    
    # prepare image
    pixel_values = processor(image, return_tensors="pt").pixel_values

    # generate
    generated_ids = model.generate(pixel_values, max_length = 60)

    # decode
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', generated_text)

    return cleaned_text