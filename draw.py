import cv2
import numpy as np
import predict_crop
import easyocr
import trocr
import namecheck2 as namecheck
import csv

# Draws the bounding boxes around each name, and then sends them to trOCR for recognition
def draw_BBOX(img):
    # For drawing rectangles on
    img_np = np.array(predict_crop.IdentifyForm(img))
    
    # Clean image for text recognition by trOCR
    img_clean = img_np.copy()
    
    # detect text on image
    reader = easyocr.Reader(['en'])
    text_ = reader.readtext(img_np)

    # Obtain bbox for column headers to determine range, remove easyOCR's text and score
    bboxes = []
    firstName_BBOX, program_BBOX = None, None
    for t in text_:
        bbox, text, score = t
        if (text == 'FIRST NAME' or text == 'First Name'): firstName_BBOX = bbox
        elif (text == 'PROGRAM' or text == 'Program'): program_BBOX = bbox
        
        # Artificially increase size of bounding boxes for better recognition
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        x1, y1, x2, y2 = int(x1) - 5, int(y1), int(x2) + 20, int(y2)
        bbox[0] = x1, y1
        bbox[2] = x2, y2
        bboxes.append(bbox)
          
    # Create constraints for columns if column headers are found
    if (firstName_BBOX == None or program_BBOX == None):
        allowed_x_range = img_np.shape[1]
        allowed_y_range = 0
    else:
        allowed_x_range = program_BBOX[0][0]
        allowed_y_range = firstName_BBOX[2][1]
    
    sorted_bboxes = sort_and_correct(bboxes, allowed_x_range, allowed_y_range)

    sorted_bbox_name_pairs = []
    grouped_bbox_name_pairs = []
    fullname = []
    all_names = []
    for grouped_bboxes in sorted_bboxes:
        for i, bbox in enumerate(grouped_bboxes, start=1):
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]
            
            cropped_image = img_clean[y1:y2, x1:x2]
                
            # Detect names using trOCR
            name = trocr.text_recognition(cropped_image)
            name = name.strip()
            name = namecheck.check(name)
            
            fullname.append(name)
            grouped_bbox_name_pairs.append([bbox, name])
            
            # Draw bounding box on image_np
            if i != len(grouped_bboxes):
                cv2.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.putText(img_np, name, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)
            else:
                cv2.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 1)
                text_width, text_height = cv2.getTextSize(name, cv2.FONT_HERSHEY_COMPLEX, 0.65, 2)[0]
                cv2.putText(img_np, name, (x2 - text_width, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)


        all_names.append(fullname)
        sorted_bbox_name_pairs.append(grouped_bbox_name_pairs)
        fullname = []
        grouped_bbox_name_pairs = []

    # Format data and write to CSV
    output = "output.csv"
    csv_data = []
    for fullname in all_names:
        for i, name in enumerate(fullname, start=1):
            name = name.strip().capitalize()
            if (i == 1):
                combined_first_name = name
            elif (i != len(fullname)): 
                combined_first_name = combined_first_name + " " + name
            else:
                csv_data.append([combined_first_name, name])

    with open(output, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["First Name", "Last Name"])
        csv_writer.writerows(csv_data)
    
    return img_np, output, output



def sort_and_correct(bboxes, allowed_x_range, allowed_y_range):
    bboxes = sorted(bboxes, key=lambda bbox: bbox[0][1])
    
    previous_bbox = None    # Store the previous pair of bbox and names to compare to the next
    correct_bboxes = []
    sorted_bboxes = []      # Stores final list of lists, where inner list contains full name of one person
    fullname_bbox = []      # Stores a singular full name of a person
    
    # Remove pairs out of range
    for bbox in bboxes:
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        
        # Calculate midpoint of current text BBOX
        midpoint_x = (x1 + x2) // 2
        midpoint_y = (y1 + y2) // 2
        
        # Check if the bounding box is in the correct columns
        if ((midpoint_x < allowed_x_range) and (midpoint_y > allowed_y_range)):
            correct_bboxes.append(bbox)
    
    # Sort pairs
    for bbox in correct_bboxes:
        current_y1, current_y2 = bbox[0][1], bbox[2][1]
        midpoint_y = (current_y1 + current_y2) // 2
        
        # If not on first iteration of for loop
        if previous_bbox is not None:
            previous_y1, previous_y2 = previous_bbox[0][1], previous_bbox[2][1]

            if not fullname_bbox: fullname_bbox.append(previous_bbox) # Only executes on second iteration
            
            # if current names bbox matches previous, append current name to fullname - (bboxes are on same row thus same person)
            # else, write fullname to all_names and set fullname to contain new persons first name
            if (midpoint_y >= previous_y1 and midpoint_y <= previous_y2):
                fullname_bbox.append(bbox)
            else:
                # Sort first and last name (or middle) based on x coord
                fullname_bbox = sorted(fullname_bbox, key = lambda bbox: bbox[0][0])
                if (len(fullname_bbox) > 2):
                    fullname_bbox = check_overlap(fullname_bbox)
                sorted_bboxes.append(fullname_bbox)
                fullname_bbox = [bbox]
        
        # Store previous names bbox for future comparison
        previous_bbox = bbox
    
    # Once for loop finishes, fullname will have contents - write them     
    fullname_bbox = sorted(fullname_bbox, key = lambda bbox: bbox[0][0])
    if (len(fullname_bbox) > 2):
        fullname_bbox = check_overlap(fullname_bbox)
    sorted_bboxes.append(fullname_bbox)
    return sorted_bboxes

# checks overlaps - dont worry about how
def check_overlap(bboxes):
    new_bboxes = []
    for i in range(len(bboxes) - 1):
        current_bbox = bboxes[i]
        current_x1, current_y1 = current_bbox[0]
        current_x2, current_y2 = current_bbox[2]
        next_bbox = bboxes[i + 1]
        next_x1, next_y1 = next_bbox[0]
        next_x2, next_y2 = next_bbox[2]
        
        if (((next_x1 < current_x2)) or (current_x1 == next_x1)):
            new_x1 = min(current_x1, next_x1)
            new_y1 = min(current_y1, next_y1)
            new_x2 = max(current_x2, next_x2)
            new_y2 = max(current_y2, next_y2)
            new_bboxes.append([[new_x1, new_y1], [new_x2, new_y1], [new_x2, new_y2], [new_x1, new_y2]])
            continue
        elif (i == (len(bboxes) - 2)):
            new_bboxes.append(current_bbox)
            new_bboxes.append(next_bbox)
        else:
            new_bboxes.append(current_bbox)
            
    if (bboxes != new_bboxes and len(new_bboxes) > 2): check_overlap(new_bboxes)
    else: return new_bboxes