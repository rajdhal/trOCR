from ultralytics import YOLO
from PIL import Image

def IdentifyForm(image):
    model = YOLO('weights/best.pt')  # load our custom model
    result = model(image)
    x1, y1 = 0, 0
    x2, y2 = image.size
    
    # Best Bounding Box
    bestBox = None
    bestConf = 0
    
    for box in result[0].boxes:
        if box.conf.cpu().numpy()[0] > bestConf:
            bestConf = box.conf.item()
            bestBox = box
    
    # IF BESTBOX is not NONE get COORDS
    if bestBox is not None:
        x1 = bestBox.xyxy.cpu().numpy()[0][0]
        y1 = bestBox.xyxy.cpu().numpy()[0][1]
        x2 = bestBox.xyxy.cpu().numpy()[0][2]
        y2 = bestBox.xyxy.cpu().numpy()[0][3]
        
        
    img = image.crop((x1, y1, x2, y2))
    return(img)