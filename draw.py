import cv2
import numpy as np
import predict_crop
import easyocr
import trocr
import namecheck2 as namecheck
import csv

# Draws the bounding boxes around each name, and then sends them to trOCR for recognition
def draw_BBOX(img):
    
    # Convert the output image from our custom trained Form Detector (YOLOv8)
    # to a numpy array representation of the image for easyOCR/openCV to write
    # bounding box rectangles and names onto.
    img_np = np.array(predict_crop.IdentifyForm(img))
    
    # Create a copy of the image that doesn't get any bounding boxes written onto it
    # so that our name recognizer can cleanly read the text
    img_clean = img_np.copy()
    
    # Use easyOCR to first detect and attempt to read EVERY name on the form
    # (SLOW AND NOT ACCURATE - used just to see where column headers are)
    reader = easyocr.Reader(['en'])
    text_ = reader.readtext(img_np)

    # Obtain the bounding box (BBOX) coordinates for the column headers
    bboxes = []
    firstName_BBOX, program_BBOX = None, None
    for t in text_:
        bbox, text, score = t
        if (text == 'FIRST NAME' or text == 'First Name'): firstName_BBOX = bbox
        elif (text == 'PROGRAM' or text == 'Program'): program_BBOX = bbox
        
        # Artificially increase size of bounding boxes for better recognition
        bbox[0][0] = int(bbox[0][0]) - 5    # Top left corner x value
        bbox[0][1] = int(bbox[0][1])        # Top left corner y value
        bbox[2][0] = int(bbox[2][0]) + 20   # Bottom right x value
        bbox[2][1] = int(bbox[2][1])        # Bottom right y value

        # Extract and keep only the BBOX coordinates of each image
        # Discard easyOCR's detected text and confidence scores
        bboxes.append(bbox)
        
          
    # If BBOX for column headers were found, create constraints such that only
    # BBOXes in these columns are read and output (ignore signatures/program)
    if (firstName_BBOX is None or program_BBOX is None):
        allowed_x_range = img_np.shape[1]
        allowed_y_range = 0
    else:
        allowed_x_range = program_BBOX[0][0]
        allowed_y_range = firstName_BBOX[2][1]
    
    # Remove bounding boxes that are outside the allowed ranges
    # Sort bboxes based on x and y position, such that a 2D array is created
    # Where each element of the outer array contains bboxes of a fullname of a student, and the
    # inner array contains the firstName, lastName bbox coords of that student
    sorted_bboxes = sort_and_correct(bboxes, allowed_x_range, allowed_y_range)

    
    # Use bbox coords of a name to crop each image to just the name, then run
    # trOCR name recognition on each of these cropped images
    all_names = []                  # Holds a list of lists of students full names (fullname)
    fullname = []                   # Holds a list of single students first name, last name
    for grouped_bboxes in sorted_bboxes:    # Iterate through each students fullname
        for i, bbox in enumerate(grouped_bboxes, start=1):  # Iterate through each students firstname(s) and lastname
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]
            
            # Create a cropped image based on bbox coords
            cropped_image = img_clean[y1:y2, x1:x2]
                
            # Name recognition of the name using trOCR (Very accurate)
            name = trocr.text_recognition(cropped_image)
            name = name.strip()             # Remove whitespace before and after outputted name
            name = namecheck.check(name)    # Apply edit distance algorithm (spell check) with database of names
            
            # Append recognized name to current students fullname list, and 
            fullname.append(name)
            
            # Draw bounding box onto img_np
            cv2.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 1)
            text_width = cv2.getTextSize(name, cv2.FONT_HERSHEY_COMPLEX, 0.65, 2)[0][0] # Obtain width of text
            # Apply correct positioning of text for first name and last name onto the output image (img_np)
            if i != len(grouped_bboxes): # First name
                cv2.putText(img_np, name, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)
            else: # Last name
                cv2.putText(img_np, name, (x2 - text_width, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)


        all_names.append(fullname)  # Append students fullname as a single element in the all_names list
        fullname = []               # Reset fullname list

    # Format data for writing to CSV
    output = "output.csv"
    csv_data = []
    for fullname in all_names:
        for i, name in enumerate(fullname, start=1):         # Inner loop that accounts for middle names
            name = name.strip().capitalize()                 # Remove whitespace and capitalize name
            if (i == 1):                  
                combined_first_name = name                   # Add first name to variable combined_first_name
            elif (i != len(fullname)):                  
                combined_first_name += " " + name            # Continually add any middle names etc. to variable (WILL NOT ADD LAST NAME)
            else:
                csv_data.append([combined_first_name, name]) # Add first name/middle name to first element of list, last name as second element

    # Write above formatted data to the CSV file
    with open(output, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["First Name", "Last Name"])
        csv_writer.writerows(csv_data)
    
    # Returns final image and CSV file for output to gradio output elements, in order
    return img_np, output, output


# Will sort and remove incorrect bounding boxes
# Sorts based on y coordinate first - effectively creates "rows" of bounding boxes
# Then will sort on the x coordinate - takes each "row" and determines which is the first name bbox and which is the last name bbox
def sort_and_correct(bboxes, allowed_x_range, allowed_y_range):
    
    bboxes = sorted(bboxes, key=lambda bbox: bbox[0][1]) # Sorts all bboxes based on y coordinate (bbox[0][1])
    
    
    correct_bboxes = []     # Stores only the correct bboxes that are within the allowed x and y range (in the first two columns)
    previous_bbox = None    # Store the previous pair of bbox and names to compare to the next
    sorted_bboxes = []      # Stores final list of lists, where inner list contains full name of one person
    fullname_bbox = []      # Stores a singular full name of a person
    
    # Checks if the bbox is within the allowed x and y range
    for bbox in bboxes:
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        
        # Calculate midpoint of current text BBOX for greater accuracy
        midpoint_x = (x1 + x2) // 2
        midpoint_y = (y1 + y2) // 2
        
        # Check if the bounding box is in the correct columns and append to correct_bboxes
        if ((midpoint_x < allowed_x_range) and (midpoint_y > allowed_y_range)):
            correct_bboxes.append(bbox)
    
    # Iterate through correct_bboxes to check for overlap issues and then sort based on x coord
    # This for loop is bad, but essentially stores the previous bbox for comparison to the next one
    # to see if they are part of the same row, and effectively are apart of single students name
    for bbox in correct_bboxes:
        current_y1, current_y2 = bbox[0][1], bbox[2][1]
        midpoint_y = (current_y1 + current_y2) // 2
        
        # If not on first iteration of for loop
        if previous_bbox is not None:
            previous_y1, previous_y2 = previous_bbox[0][1], previous_bbox[2][1]

            # If fullname_bbox is empty, append previous bbox coords to it (Will only execute as true on the SECOND iteration)
            if not fullname_bbox: fullname_bbox.append(previous_bbox)
            
            # if current names bbox matches previous y space, append current name to fullname - (bboxes are on same row thus same person)
            # else, write fullname to all_names and set fullname to contain the new persons first name
            if (midpoint_y >= previous_y1 and midpoint_y <= previous_y2):
                fullname_bbox.append(bbox)
            else:
                # Sort first and last name (or middle) based on x coord
                fullname_bbox = sorted(fullname_bbox, key = lambda bbox: bbox[0][0])
                
                # If a row is found to have more than 2 bboxes, potential candidate for having an OVERLAP ISSUE, check 
                if (len(fullname_bbox) > 2): fullname_bbox = check_overlap(fullname_bbox)
                
                
                sorted_bboxes.append(fullname_bbox) # Add the bbox corresponding to the full name of a single student to sorted_bboxes
                fullname_bbox = [bbox]              # Empty fullname_bbox, start with new students bbox
        
        # Store previous names bbox for future comparison
        previous_bbox = bbox
    
    # Once for loop finishes, fullname will have contents - write them and check for overlaps  
    fullname_bbox = sorted(fullname_bbox, key = lambda bbox: bbox[0][0])
    if (len(fullname_bbox) > 2): fullname_bbox = check_overlap(fullname_bbox)
    
    # Append final students bbox to sorted_bboxes
    sorted_bboxes.append(fullname_bbox)
    
    # Return the sorted bboxes
    return sorted_bboxes

# Checks for overlaps by looking at specifically the x coordinate space
# Since the argument is guaranteed to already be sorted, we can use this to see if they overlap
# The top left corner of the next bbox (next_x1) should come AFTER the current bboxes top right corner (current_x2) - if not, there is an overlap
def check_overlap(bboxes):
    new_bboxes = []
    for i in range(len(bboxes) - 1): # Iterates up the second last element of the list of bboxes
        # BBOX 1 coords saved
        current_bbox = bboxes[i]
        current_x1, current_y1 = current_bbox[0]
        current_x2, current_y2 = current_bbox[2]
        
        # BBOX 2 coords saved
        next_bbox = bboxes[i + 1]
        next_x1, next_y1 = next_bbox[0]
        next_x2, next_y2 = next_bbox[2]
        
        # If the top left corner of the next bbox (next_x1) comes AFTER the current bboxes top right corner (current_x2)
        # then THERE IS AN OVERLAP, COMBINE THE BBOXES
        if (((next_x1 <= current_x2)) or (current_x1 == next_x1)):
            new_x1 = min(current_x1, next_x1)
            new_y1 = min(current_y1, next_y1)
            new_x2 = max(current_x2, next_x2)
            new_y2 = max(current_y2, next_y2)
            new_bboxes.append([[new_x1, new_y1], [new_x2, new_y1], [new_x2, new_y2], [new_x1, new_y2]])
            continue
        # If on the last iteration and no overlap was found, add the next bbox to the list
        elif (i == (len(bboxes) - 2)):
            new_bboxes.append(next_bbox)
            
        # if no overlap found, just add the current bbox coords with no modifications to the list
        new_bboxes.append(current_bbox)
        
    # Handles edge case where potentially 3 or more bboxes overlap, continually check new_bboxes
    # If input list of bboxes matches what is output, no bboxes overlap and thus return
    if (bboxes != new_bboxes and len(new_bboxes) > 2): check_overlap(new_bboxes)
    else: return new_bboxes