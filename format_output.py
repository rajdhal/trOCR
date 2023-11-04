import csv

def format(bbox_name_pairs):
    # easyOCR doesn't put bboxes in order, sort based on y-coord first
    bbox_name_pairs = sorted(bbox_name_pairs, key=lambda bbox: bbox[1][0][1])
    
    previous_pairs = None   # Store the previous pair of bbox and names to compare to the next
    all_names = []          # Stores final list of lists, where inner list contains full name of one person
    fullname = []           # Stores a singular full name of a person
    
    # sketchy for loop I made that works
    for name, bbox in bbox_name_pairs:
        current_x1 = int(bbox[0][0])
        current_y1, current_y2 = bbox[0][1], bbox[2][1]
        midpoint_y = (current_y1 + current_y2) // 2
        
        # If not on first iteration of for loop
        if previous_pairs is not None:
            previous_name = previous_pairs[0]
            previous_x1 = int(previous_pairs[1][0][0])
            previous_y1, previous_y2 = previous_pairs[1][0][1], previous_pairs[1][2][1]

            if not fullname: fullname.append([previous_name, previous_x1]) # Only executes on second iteration
            
            # if current names bbox matches previous, append current name to fullname - (bboxes are on same row thus same person)
            # else, write fullname to all_names and set fullname to contain new persons first name
            if (midpoint_y >= previous_y1 and midpoint_y <= previous_y2):
                fullname.append([name, current_x1])
            else:
                # Sort first and last name (or middle) based on x coord
                fullname = sorted(fullname, key = lambda x: x[1])
                temp_name = []
                for list in fullname:
                    temp_name.append(list[0])
                    
                all_names.append(temp_name)
                fullname = [[name, current_x1]]
        
        # Store previous names bbox for future comparison
        previous_pairs = [name, bbox]
    
    # Once for loop finishes, fullname will have contents - write them
    fullname = sorted(fullname, key = lambda x: x[1])
    temp_name =[]
    for list in fullname: 
        temp_name.append(list[0])
        
    all_names.append(temp_name)
    
    # Prepare data for CSV, combine all names before last name into one
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
    
    # Write data to CSV, return True on success
    try:
        with open("output.csv", mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["First Name", "Last Name"])
            csv_writer.writerows(csv_data)
        return True
    except Exception as e:
        print(f"Error occured: {e}")
        return False