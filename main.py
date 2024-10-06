from video_input import open_video, read_frame
from tracking import track_objects
from csv_output import save_tracking_data
import cv2

def main():
    video_path = 'input.mp4'
    cap = open_video(video_path)

    if not cap:
        return

    back_sub = cv2.createBackgroundSubtractorMOG2()
    tracking_data = []
    frame_no = 0

    while True:
        frame = read_frame(cap)
        if frame is None:
            break

        frame_no += 1
        frame = track_objects(frame, back_sub, tracking_data, frame_no)

        # Show the frame with tracking
        cv2.imshow('Tracked Video', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save the tracking data
    save_tracking_data(tracking_data)

if __name__ == "__main__":
    main()
