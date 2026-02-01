from ultralytics import YOLO

# Cache the model at module level to avoid reloading on every call
_yolo_model = None

def _get_model():
    global _yolo_model
    if _yolo_model is None:
        _yolo_model = YOLO('weights/best.pt')
    return _yolo_model

def IdentifyForm(image):
    model = _get_model()
    result = model(image)            # Tell our model to find the form on our image, and create potential bounding boxes of location
    x1, y1 = 0, 0
    x2, y2 = image.size
    
    # Initialize variables to store Best Bounding Box
    bestBox = None
    bestConf = 0
    
    # Iterate through each outputted bbox, and store the one with the highest confidence score
    for box in result[0].boxes:
        conf = box.conf.cpu().numpy()[0]
        if conf > bestConf:
            bestConf = conf
            bestBox = box
    
    # If a bbox was returned, store its coordinates
    if bestBox is not None:
        coords = bestBox.xyxy.cpu().numpy()[0]
        x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
        
    # Crop image to coordinates of best box (If not found, will just be the original image) and return 
    img = image.crop((x1, y1, x2, y2))
    return img