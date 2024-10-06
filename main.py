from video_input import open_video, read_frame
from tracking import track_objects
from csv_output import save_tracking_data
import cv2
import sys

def main(video_path, start_frame, end_frame):
    cap = open_video(video_path)

    if not cap:
        return

    # Get total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total number of frames in the video: {total_frames}")

    # Ensure end_frame does not exceed total_frames
    if end_frame > total_frames:
        end_frame = total_frames
        print(f"End frame adjusted to total frames: {end_frame}")

    back_sub = cv2.createBackgroundSubtractorMOG2()
    tracking_data = []
    frame_no = 0
    last_frame = None

    while True:
        frame = read_frame(cap)
        if frame is None or frame_no > end_frame:  # Stop if no frame or exceeds end_frame
            break

        if frame_no >= start_frame:  # Start processing frames only from start_frame
            frame_no += 1
            frame = track_objects(frame, back_sub, tracking_data, frame_no)

            # Show the frame with tracking
            cv2.imshow('Tracked Video', frame)
            last_frame = frame.copy()  # Store a copy of the last frame to display it after the video ends

        else:
            frame_no += 1  # Increment frame number if not processing

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit early
            break

    # Release the video capture object
    cap.release()

    # Display the last frame indefinitely until the user presses ESC
    if last_frame is not None:
        while True:
            cv2.imshow('Tracked Video', last_frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key to close the window
                break

    # Close all OpenCV windows
    cv2.destroyAllWindows()

    # Save the tracking data
    save_tracking_data(tracking_data)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_path = sys.argv[1]  # Take the video file path as a command-line argument
        start_frame = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # Starting frame (default 0)
        end_frame = int(sys.argv[3]) if len(sys.argv) > 3 else float('inf')  # Ending frame (default to infinity)
    else:
        video_path = 'input.mp4'  # Default file name
        start_frame = 0
        end_frame = float('inf')

    main(video_path, start_frame, end_frame)
