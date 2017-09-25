import numpy as np
import cv2

# Define a function to draw bounding boxes
def draw_boxes(img, bboxes, color=(0, 0, 255), thick=4):
    # Make a copy of the image
    imcopy = np.copy(img)
    # Iterate through the bounding boxes
    for bbox in bboxes:
        # Draw a rectangle given bbox coordinates
        cv2.rectangle(imcopy, bbox[0], bbox[1], color, thick)
    # Return the image copy with boxes drawn
    return imcopy

# Define a function to draw rectangles (object oriented representation of bounding boxes)
def draw_rects(img, rects, color=(0, 0, 255), thick=4):
    # Make a copy of the image
    imcopy = np.copy(img)
    # Iterate through the rects
    for rect in rects:
        # Draw a rectangle given bbox coordinates
        cv2.rectangle(imcopy, (rect.p1.x, rect.p1.y), (rect.p2.x, rect.p2.y), color, thick)
    # Return the image copy with boxes drawn
    return imcopy