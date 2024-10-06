import cv2

def open_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None

    # Get the original width and height of the frame
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Set the new resolution to half
    new_width = original_width // 2
    new_height = original_height // 2
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)

    print(f"Video resolution set to: {new_width}x{new_height}")
    return cap

def read_frame(cap):
    ret, frame = cap.read()
    if not ret:
        print("End of video or error reading frame.")
        return None
    return frame

if __name__ == "__main__":
    video_path = 'input.mp4'  # Path to your input video
    cap = open_video(video_path)
    while cap:
        frame = read_frame(cap)
        if frame is None:
            break
        # Process the frame
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC key
            break
    cap.release()
    cv2.destroyAllWindows()
