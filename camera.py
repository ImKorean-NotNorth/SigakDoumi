import cv2
import numpy as np

def init_camera():
    """Initializes and returns a persistent webcam capture object."""
    cap = cv2.VideoCapture(0)  # Open the webcam (adjust the index if needed)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")
    return cap

def capture_image(cap, save_path="memo_image.jpg"):
    """
    Captures an image from the given webcam capture object with ROI selection and effects.
    The user sees a live feed with a drawn ROI and can adjust settings via trackbars.
    Press 's' to capture the processed ROI image or 'q' to cancel.
    """
    print("Press 's' to capture an image, or 'q' to cancel.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4096)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

    # Define ROI coordinates (modify these values as needed)
    box_width, box_height = 800, 650  # Target area dimensions
    start_x, start_y = 300, 100       # Starting coordinates of ROI
    end_x = start_x + box_width
    end_y = start_y + box_height

    # Create a window for settings and add trackbars for real-time adjustment
    cv2.namedWindow("Settings")
    cv2.createTrackbar("ClipLimit", "Settings", 2, 10, lambda x: None)      # CLAHE clipLimit (1-10)
    cv2.createTrackbar("Erosion", "Settings", 0, 5, lambda x: None)           # Erosion iterations (0-5)
    cv2.createTrackbar("Kernel Size", "Settings", 0, 10, lambda x: None)      # Kernel size (1-10)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not capture frame.")
            return None

        # Draw the ROI rectangle on the live feed
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

        # Crop the ROI from the frame
        roi = frame[start_y:end_y, start_x:end_x]

        # Retrieve settings from the trackbars
        clip_val = cv2.getTrackbarPos("ClipLimit", "Settings")
        erosion_iter = cv2.getTrackbarPos("Erosion", "Settings")
        kernel_size = cv2.getTrackbarPos("Kernel Size", "Settings")
        if kernel_size < 1:
            kernel_size = 1
        if kernel_size % 2 == 0:
            kernel_size += 1

        # --- Image Processing Pipeline on the ROI ---
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=float(clip_val), tileGridSize=(8, 8))
        contrast_roi = clahe.apply(gray_roi)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        processed_roi = cv2.erode(contrast_roi, kernel, iterations=erosion_iter)
        # --- End Processing Pipeline ---

        # Display the original frame and the processed ROI in separate windows
        cv2.imshow("Webcam Feed", frame)
        cv2.imshow("Processed ROI", processed_roi)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cv2.imwrite(save_path, processed_roi)
            print(f"Image captured and saved as {save_path}")
            cv2.destroyWindow("Webcam Feed")
            cv2.destroyWindow("Processed ROI")
            cv2.destroyWindow("Settings")
            return save_path
        elif key == ord('q'):
            print("Image capture cancelled.")
            cv2.destroyWindow("Webcam Feed")
            cv2.destroyWindow("Processed ROI")
            cv2.destroyWindow("Settings")
            return None

def release_camera(cap):
    """Releases the camera and closes all OpenCV windows."""
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    cap = init_camera()
    capture_image(cap)
    release_camera(cap)
