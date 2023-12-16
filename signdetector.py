import inspect
import queue
import time

import cv2
import numpy as np
from sic_framework.core.message_python2 import CompressedImageMessage
from sic_framework.devices import Nao
from sic_framework.devices.desktop import Desktop


def correct_white_balance(img, reference_area):
    # Compute the average color of the reference area
    reference_color = cv2.mean(reference_area)[:3]

    # Assume the reference color should be white (or neutral gray)
    # and calculate scale factors for each channel
    max_ref_color = max(reference_color)
    scale_factors = [max_ref_color / c if c > 0 else 0 for c in reference_color]

    # Apply scale factors to the image
    corrected_img = np.copy(img)
    for i in range(3):  # For each channel in BGR
        corrected_img[..., i] = np.clip(corrected_img[..., i] * scale_factors[i], 0, 255)

    return corrected_img


def detect_features(img, min_area, max_area, min_circularity, min_convexity):
    # Convert to grayscale and apply blur
    # img = cv2.GaussianBlur(img, (15, 15), 0)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Blob Detection
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = min_area
    params.maxArea = max_area
    params.filterByCircularity = True
    params.minCircularity = min_circularity
    params.filterByConvexity = True
    params.minConvexity = min_convexity
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs
    keypoints = detector.detect(gray_blurred)
    output_blobs = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                     cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return output_blobs, keypoints


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_colors(img, min_area=220, max_area=100000, min_circularity=0.8, min_convexity=0.8,
               ratio_threshold=0.6, saturation_threshold=120, draw=True, fix_white_balance=True):
    output_blobs, keypoints = detect_features(img, min_area, max_area, min_circularity, min_convexity)

    dominant_colors = []

    for keypoint in keypoints:
        x, y = int(keypoint.pt[0]), int(keypoint.pt[1])
        radius = int(keypoint.size / 2)  # Approximate radius of the blob

        # Define a small region around the center of the blob
        half_radius = int(radius / 2)
        x1, y1 = max(0, x - half_radius), max(0, y - half_radius)
        x2, y2 = min(img.shape[1], x + half_radius), min(img.shape[0], y + half_radius)

        # Compute the average color of the region
        blob_region = img[y1:y2, x1:x2]
        blob_color = tuple(int(val) for val in cv2.mean(blob_region)[:3])

        # Define a reference area for white balance (outside the blob)
        ref_x1, ref_y1 = max(0, x - radius + int(0.1 * radius)), max(0, y - radius + int(0.1 * radius))
        ref_size = max(1, int(radius / 6))
        ref_x2, ref_y2 = min(img.shape[1], ref_x1 + ref_size), min(img.shape[0], ref_y1 + ref_size)
        reference_area = img[ref_y1:ref_y2, ref_x1:ref_x2]

        # draw white balance ref. area
        cv2.rectangle(output_blobs, (ref_x1, ref_y1), (ref_x2, ref_y2), (255, 0, 0),
                      1)  # Small red circle at the center

        # Correct white balance of the blob region
        corrected_blob_region = correct_white_balance(blob_region, reference_area)
        corrected_blob_color = tuple(int(val) for val in cv2.mean(corrected_blob_region)[:3])

        if fix_white_balance:
            blob_color = corrected_blob_color

        # Rest of your code for displaying the color information...

        # Calculate the ratio of the brightest color to the sum of the other two colors
        max_color = max(blob_color)
        sum_other_colors = sum(blob_color) - max_color

        dominant_color = ""
        color_ratio = max_color / sum_other_colors if sum_other_colors > 0 else 0  # Avoid division by zero

        blob_color_hsv = cv2.cvtColor(corrected_blob_region, cv2.COLOR_BGR2HSV)
        saturation = blob_color_hsv[:, :, 1].mean()

        if color_ratio > ratio_threshold and saturation > saturation_threshold:
            cv2.circle(output_blobs, (x, y), 5, (0, 0, 255), -1)  # Small red circle at the center

            dominant_index = blob_color.index(max_color)
            dominant_color = ["blue", "green", "red"][dominant_index]
            dominant_colors.append(dominant_color)

        if draw:
            print(color_ratio)
            print(saturation)
            print(dominant_colors)

        # Prepare the text to display (BGR format, color ratio, and dominant color if applicable)
        color_text = f"R:{color_ratio:.2f} S:{saturation:.0f} BGR:{blob_color}, "
        if dominant_color:
            color_text += f", Dom: {dominant_color}"

        # Prepare the text to display (BGR format and color ratio)
        text_position = (x + 25, y) if x + 25 < img.shape[1] else (x - 25, y)  # Stay within image bounds

        # Put text on the image
        cv2.putText(output_blobs, color_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, blob_color, 1,
                    cv2.LINE_AA)

    if draw:
        # Combine images for display
        combined = np.hstack((img, output_blobs))

        cv2.imshow('Calibration', combined)
        cv2.waitKey(1)

    return dominant_colors


class ColorDetector:
    def __init__(self, ip=None, use_pc_webcam=False):

        self.imgs = queue.LifoQueue()  # LiFo queue to process most recent images first

        global camera_device
        if use_pc_webcam:
            print("USING PC WEBCAM")
            camera_device = Desktop().camera  # For some reason these need to be  global variables

        else:
            if not ip:
                raise RuntimeError("ERROR: provide ip or set use_pc_webcam=True")
            camera_device = Nao(ip).top_camera

        camera_device.register_callback(self.on_image)

    def on_image(self, image_message: CompressedImageMessage):
        self.imgs.put(image_message.image)

    def calibrate(self):
        with self.imgs.mutex:
            self.imgs.queue.clear()  # delete old images
        self.imgs = queue.Queue()  # switch to FiFo queue for smoother display

        # Create calibration windows and trackbars
        current_parameters = get_default_args(get_colors)
        print(current_parameters)

        window_name = 'Calibration'
        cv2.namedWindow(window_name)

        cv2.createTrackbar('Min Area', window_name, current_parameters["min_area"], 1000, self.trackbar_callback)
        cv2.createTrackbar('Max Area', window_name, current_parameters["max_area"], 10000, self.trackbar_callback)
        cv2.createTrackbar('Min Circularity', window_name, int(current_parameters["min_circularity"] * 100), 100,
                           self.trackbar_callback)
        cv2.createTrackbar('Min Convexity', window_name, int(current_parameters["min_convexity"] * 100), 100,
                           self.trackbar_callback)

        while True:
            if not self.imgs.empty():
                img = self.imgs.get()
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert color space
                img = cv2.flip(img, 1)
                img = cv2.flip(img, -1)

                # Get trackbar values
                min_area = cv2.getTrackbarPos('Min Area', 'Calibration')
                max_area = cv2.getTrackbarPos('Max Area', 'Calibration')
                min_circularity = cv2.getTrackbarPos('Min Circularity', 'Calibration') / 100.0
                min_convexity = cv2.getTrackbarPos('Min Convexity', 'Calibration') / 100.0

                # Detect colors
                get_colors(img, min_area, max_area, min_circularity, min_convexity)

    def trackbar_callback(self, x):
        # Callback function for trackbar event
        pass

    def detect_sign(self, max_duration=5):
        """
        :param max_duration:
        :return: "red", "green", "blue" or None
        """

        print("Detecting sign...")

        with self.imgs.mutex:
            self.imgs.queue.clear()  # delete old images
        start_time = time.time()

        i = 0
        while time.time() - start_time < max_duration:
            i += 1
            # print("detecting sign. Try nr. ", i + 1)

            if not self.imgs.empty():
                # print(self.imgs.qsize(), "self.imgs in queue")

                img = self.imgs.get()
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                colors = get_colors(img, draw=False)
                if len(colors) == 1:
                    with self.imgs.mutex:
                        self.imgs.queue.clear()  # delete old images

                    return colors[0]
            else:
                time.sleep(0.01)
                # print(" empty")

        return None  # if there is no color found, or if there are several


camera_device = None  # This needs to be global for some reason


def main():
    # color_detector = ColorDetector(use_pc_webcam=True)
    # color_detector = ColorDetector(ip="192.168.0.151")
    color_detector = ColorDetector(ip="10.0.0.91")
    color_detector.calibrate()
    # print(color_detector.detect_sign())


if __name__ == '__main__':
    main()
