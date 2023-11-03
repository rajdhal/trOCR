import cv2
import easyocr
import os
import numpy as np
import predict_crop
import trocr
import namecheck
import format_output

# Draws the bounding boxes around each name, and then sends them to trOCR for recognition
def draw_BBOX(img):
    # For drawing rectangles on
    img_np = np.array(predict_crop.IdentifyForm(img))
    
    # Clean image for text recognition by trOCR
    img_clean = img_np.copy()
    
    firstName_BBOX, program_BBOX, lastName_BBOX, signature_BBOX = None, None, None, None
    
    # instance text detector
    reader = easyocr.Reader(['en'])
    
    # detect text on image
    text_ = reader.readtext(img_np)

    # Obtain BBox for column headers - only loop through first 20 detected boxes
    # Uses easyOCR for text recognition - kinda sketchy
    for t in text_[:20]:
        bbox, text, score = t
        
        if (text == 'FIRST NAME' or text == 'First Name'): firstName_BBOX = bbox
        elif (text == 'PROGRAM' or text == 'Program'): program_BBOX = bbox
        elif (text == 'LAST NAME' or text == 'Last Name'): lastName_BBOX = bbox
        #elif (text == 'SIGNATURE' or text == 'Signature'): signature_BBOX = bbox
            
    # Output BBoxes that are between the range of first name header up to program header
    all_names = []
    bbox_name_pairs = []
    output_folder = "cropped"
    
    # Create constraints for columns if column headers are found
    if (firstName_BBOX == None or program_BBOX == None):
        allowed_x_range = img_np.shape[1]
        allowed_y_range = 0
    else:
        allowed_x_range = program_BBOX[0][0]
        allowed_y_range = firstName_BBOX[2][1]
    
    # Iterate over each detected text BBOX by easyOCR
    i = 0 # Counter for cropped image file name
    for t in text_:
        bbox, text, score = t
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        
        
        # Artificially increase size of bounding boxes for better coverage
        x1, y1, x2, y2 = int(x1) - 5, int(y1), int(x2) + 20, int(y2)
        
        # Calculate midpoint of current text BBOX
        midpoint_x = (x1 + x2) // 2
        midpoint_y = (y1 + y2) // 2
        
        # Check if the bounding box is in the correct columns
        if ((midpoint_x < allowed_x_range) and (midpoint_y > allowed_y_range)):
            i += 1
            # Create and save cropped image_clean based on bounding box
            cropped_image = img_clean[y1:y2, x1:x2]
            #image_path = os.path.join(output_folder, f"cropped_image_{i}.png")
            #cv2.imwrite(image_path, cropped_image)
            
            # Detect names using trOCR
            name = trocr.text_detection(cropped_image)
            name = namecheck.check(name)
            
            #all_names.append(name)
            bbox_name_pairs.append([name, bbox])
            
            # Draw bounding box on image_np
            cv2.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(img_np, name, (x1, y1),cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)
            
    all_names = format_output.format(bbox_name_pairs)
    
    # Weird edge case where easyOCR doesnt see anything in the image, let trOCR handle it
    if (len(all_names) == 1 and all_names[0] == ''):
        return trocr.text_detection(img), img
    
    return all_names, img_np