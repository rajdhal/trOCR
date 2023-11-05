import cv2 as cv
import numpy as np
import predict_crop
import trocr
import namecheck
import pandas as pd
import name_crop


Y_OVERLAP_THRESHOLD = 0.15
X_OVERLAP_THRESHOLD = 0.5


def y_overlap(a, b):
    a_y_min = a[5] - a[3] * Y_OVERLAP_THRESHOLD
    a_y_max = a[5] + a[3] * Y_OVERLAP_THRESHOLD
    b_y_min = b[5] - b[3] * Y_OVERLAP_THRESHOLD
    b_y_max = b[5] + b[3] * Y_OVERLAP_THRESHOLD
    if (a_y_min >= b_y_min and a_y_min <= (b_y_max)) or (b_y_min >= a_y_min and b_y_min <= (a_y_max)):
        return True
    else:
        return False


def draw_BBOX(img):
    img = np.array(predict_crop.IdentifyForm(img))
    output = img.copy()

    # Preprocessing
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    # Find connected components in the binary image
    retval, labels, stats, centroids = cv.connectedComponentsWithStats(thresh, connectivity=8)

    # Estimate mode of bbox areas
    areas = stats[1:, cv.CC_STAT_AREA]
    median = np.median(areas)
    mean = np.mean(areas)
    mode = abs(3 * median - 2 * mean)

    bboxes = []

    # Clean list of components
    for i in range(1, retval):
        x = stats[i, cv.CC_STAT_LEFT]
        y = stats[i, cv.CC_STAT_TOP]
        w = stats[i, cv.CC_STAT_WIDTH]
        h = stats[i, cv.CC_STAT_HEIGHT]
        area = stats[i, cv.CC_STAT_AREA]
        (cX, cY) = centroids[i]
        # Remove small and large components by area
        if area > (mode * 2) or area < 1000:
            continue
        bbox = (x, y, w, h, cX, cY)
        bboxes.append(bbox)

    rows = [[bboxes[0]]]

    # Group bounding boxes into rows
    for i in range(1, len(bboxes)):
        for j in range(len(rows)):
            if y_overlap(bboxes[i], rows[j][-1]):
                rows[j].append(bboxes[i])
                break
        else:
            rows.append([bboxes[i]])

    # Sort each by x coordinate
    for row in rows:
        row.sort(key=lambda x: x[4])

    names = []
    # draw bounding boxes for rows
    for row in rows:
        names_in_row = []
        for i in range(2):
            (x, y, w, h, cX, cY) = row[i]
            
            # OCR
            name = trocr.text_recognition(name_crop.name_crop(img[y:y + h + 5, x:x + w]))
            name = name.strip()
            if i == 0:
                name = namecheck.check(name, False)
            else:
                name = namecheck.check(name, True)
            names_in_row.append(name)

            cv.rectangle(output, (x, y), (x + w, y + h), (0, j, 0), 2)
            cv.putText(output, name, (int(cX), int(cY)),cv.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)    
        names.append(names_in_row)

    # Create dataframe
    names_df = pd.DataFrame(names)
    names_csv = names_df.to_csv("output.csv")

    return output, names_df, names_csv

        


