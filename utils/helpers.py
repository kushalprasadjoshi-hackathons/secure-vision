import os
import cv2

def ensure_dir(directory):
    """Ensure a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def resize_image(image, width, height):
    """Resize an image to specified dimensions."""
    return cv2.resize(image, (width, height))

def draw_rectangle(image, top, right, bottom, left, color=(0, 255, 0), thickness=2):
    """Draw a rectangle on the image."""
    cv2.rectangle(image, (left, top), (right, bottom), color, thickness)
    return image

def draw_text(image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, color=(255, 255, 255), thickness=1):
    """Draw text on the image."""
    cv2.putText(image, text, position, font, font_scale, color, thickness)
    return image

# Future: add more utility functions for image processing, time handling, etc.