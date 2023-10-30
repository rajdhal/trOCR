from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import re

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

def text_detection(image):    
    # prepare image
    pixel_values = processor(image, return_tensors="pt").pixel_values

    # generate
    generated_ids = model.generate(pixel_values, max_length = 60)

    # decode
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', generated_text)

    # If multiple names are passed in, the model recognizes the line seperating them in our form as a single character
    # Attempt to get past this by ensuring each name passed back has a length greater than one
    names = cleaned_text.split(' ')
    final_text = ""
    for name in names:
        if len(name) > 1:
            final_text = final_text + " " + name
            
    return final_text
    
    # TODO: perform word beam search against census list of names to increase certainty?