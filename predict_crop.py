from ultralytics import YOLO
from PIL import Image

def IdentifyForm(image):
    model = YOLO('weights/best.pt')  # Load our custom model
    result = model(image)            # Tell our model to find the form on our iamge, and create potential bounding boxes of location
    x1, y1 = 0, 0
    x2, y2 = image.size
    
    # Initialize variables to store Best Bounding Box
    bestBox = None
    bestConf = 0
    
    # Iterate through each outputted bbox, and store the one with the highest confidence score
    for box in result[0].boxes:
        if box.conf.cpu().numpy()[0] > bestConf:
            bestConf = box.conf.item()
            bestBox = box
    
    # If a bbox was returned, store its coordinates
    if bestBox is not None:
        x1 = bestBox.xyxy.cpu().numpy()[0][0]
        y1 = bestBox.xyxy.cpu().numpy()[0][1]
        x2 = bestBox.xyxy.cpu().numpy()[0][2]
        y2 = bestBox.xyxy.cpu().numpy()[0][3]
        
    # Crop image to coordinates of best box (If not found, will just be the original image) and return 
    img = image.crop((x1, y1, x2, y2))
    return(img)