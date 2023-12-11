import cv2 as cv

# WIP
# Find a better crop of each cell bounding box from draw2
def name_crop(img):
    crop = img.copy()
    # Convert to grayscale
    crop = cv.cvtColor(crop, cv.COLOR_BGR2GRAY)
    crop = cv.threshold(crop, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    # Remove top and side borders by shaving the crop closer to the center
    crop = crop[5:crop.shape[0], 5:crop.shape[1] - 6]

    y2 = crop.shape[0]

    x1, y1, x2 = 0, crop.shape[0], 0
    found = False

    for x in range(0, crop.shape[1]):
        for y in range(0, crop.shape[0] - 8):
            if crop[y, x] == 0:
                if not found:
                    x1 = x
                    found = True
                if y < y1:
                    y1 = y
                if x > x2:
                    x2 = x

    if x1 > 1:
        x1 -= 2
    if y1 > 1:
        y1 -= 2
    if x2 < crop.shape[1] - 1:
        x2 += 2

    bboxes = [x1, y1, x2, y2]
    n_crop = img[bboxes[1]:bboxes[3], bboxes[0]:bboxes[2]]

    return n_crop
