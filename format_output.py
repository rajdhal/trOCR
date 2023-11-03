def format(bbox_name_pairs):
    # easyOCR doesn't put bboxes in order, sort based on y-coord first
    bbox_name_pairs = sorted(bbox_name_pairs, key=lambda bbox: round(bbox[1][0][1] / 32))
    
    
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
    temp_name =[]
    for list in fullname: 
        temp_name.append(list[0])
        
    all_names.append(temp_name)
    
    
    # Convert list of lists to string
    final = ""
    for list in all_names:
        for name in list:
            final = final + name.strip() + " "
        final = final + "\n"
        
    return final

'''
# Debugging output function  
text_ = [['muhammad', [[99, 277], [209, 277], [209, 315], [99, 315]]], ['ali', [[288, 276], [336, 276], [336, 306], [288, 306]]], 
         ['sonia', [[103, 308], [187, 308], [187, 352], [103, 352]]], [' ngoyen', [[275, 308], [383, 308], [383, 357], [275, 357]]], 
         [' priya secret', [[104, 354], [248, 354], [248, 386], [104, 386]]], ['patel', [[284, 352], [362, 352], [362, 378], [284, 378]]], 
         ['alexandra', [[104, 386], [235, 386], [235, 427], [104, 427]]], [' rodriguez', [[277, 381], [416, 381], [416, 423], [277, 423]]], 
         ['ahmed', [[111, 425], [197, 425], [197, 461], [111, 461]]], ['vishal', [[286, 426], [350, 426], [350, 456], [286, 456]]], 
         ['aisha', [[110, 464], [192, 464], [192, 494], [110, 494]]], ['kim', [[296, 462], [354, 462], [354, 488], [296, 488]]], 
         ['amir', [[105, 499], [180, 499], [180, 535], [105, 535]]], ['abu', [[291, 503], [311, 503], [311, 529], [291, 529]]], 
         ['isabelle', [[103, 533], [197, 533], [197, 569], [103, 569]]], ['hope', [[286, 538], [356, 538], [356, 568], [286, 568]]], 
         ['wei', [[106, 572], [160, 572], [160, 602], [106, 602]]], ['chen', [[282, 572], [354, 572], [354, 602], [282, 602]]], 
         ['lucy', [[108, 614], [190, 614], [190, 644], [108, 644]]], ['santosh', [[284, 612], [380, 612], [380, 640], [284, 640]]], 
         ['fatima', [[108, 650], [206, 650], [206, 678], [108, 678]]], ['hussein', [[289, 647], [396, 647], [396, 678], [289, 678]]], 
         ['ravi', [[115, 681], [187, 681], [187, 717], [115, 717]]], ['kumar', [[290, 684], [370, 684], [370, 714], [290, 714]]], 
         ['mia', [[118, 720], [160, 720], [160, 752], [118, 752]]], ['martins', [[298, 722], [438, 722], [438, 750], [298, 750]]], 
         ['khan', [[118, 760], [190, 760], [190, 792], [118, 792]]], ['muhammad', [[288, 758], [426, 758], [426, 788], [288, 788]]], 
         [' allilho', [[111, 793], [203, 793], [203, 829], [111, 829]]], [' tancilia', [[290, 794], [408, 794], [408, 824], [290, 824]]], 
         [' mendoza', [[289, 829], [400, 829], [400, 865], [289, 865]]], [' olivia', [[114, 874], [196, 874], [196, 902], [114, 902]]], 
         [' epigma', [[120, 910], [180, 910], [180, 940], [120, 940]]], ['chen', [[296, 908], [352, 908], [352, 936], [296, 936]]], 
         ['charles', [[104, 948], [190, 948], [190, 980], [104, 980]]], ['fernandes', [[293, 945], [428, 945], [428, 975], [293, 975]]], 
         ['jamal', [[107, 983], [204, 983], [204, 1015], [107, 1015]]], ['ram', [[292, 978], [344, 978], [344, 1010], [292, 1010]]], 
         ['aman', [[347, 991], [399, 991], [399, 1007], [347, 1007]]], ['sandeep', [[105, 1016], [226, 1016], [226, 1058], [105, 1058]]], 
         ['nidhi', [[293, 1011], [375, 1011], [375, 1047], [293, 1047]]], ['sonia', [[107, 1055], [187, 1055], [187, 1093], [107, 1093]]], 
         ['ravi', [[300, 1056], [340, 1056], [340, 1088], [300, 1088]]], ['ahmed', [[109, 1097], [189, 1097], [189, 1133], [109, 1133]]], 
         ['ravi', [[306, 1094], [348, 1094], [348, 1126], [306, 1126]]], ['jamal', [[107, 1135], [187, 1135], [187, 1173], [107, 1173]]], 
         ['rahman', [[303, 1127], [418, 1127], [418, 1165], [303, 1165]]], 
         ['mike', [[112, 1178], [178, 1178], [178, 1210], [112, 1210]]], [' morables', [[300, 1158], [415, 1158], [415, 1206], [300, 1206]]], 
         ['vijay', [[114, 1214], [182, 1214], [182, 1246], [114, 1246]]], ['hope', [[296, 1212], [390, 1212], [390, 1244], [296, 1244]]], 
         ['lisa', [[113, 1251], [187, 1251], [187, 1289], [113, 1289]]], ['rana', [[289, 1242], [374, 1242], [374, 1282], [289, 1282]]], 
         ['amit', [[116, 1290], [184, 1290], [184, 1322], [116, 1322]]], ['desai', [[304, 1284], [380, 1284], [380, 1316], [304, 1316]]], 
         [' thacki', [[305.46153846153845, 499.3076923076923], [368.3282011773514, 494.7811992150991], [369.53846153846155, 530.6923076923077], [307.6717988226486, 535.218800784901]]], 
         [' santiago', [[108.05576303174938, 823.0899677650967], [220.9221378775424, 843.1210468075817], [211.94423696825064, 884.9100322349033], [99.07786212245759, 864.8789531924183]]], 
         ['wang', [[297.1970684086417, 866.1094462711102], [384.9377812585213, 877.3921831878921], [379.8029315913583, 907.8905537288898], [292.0622187414787, 896.6078168121079]]]]

print(format(text_))
'''