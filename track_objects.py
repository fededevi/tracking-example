import cv2
import numpy as np
import pandas as pd
import random

# Open the video file
video_path = 'input.mp4'  # Path to your input video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Get the original width and height of the frame
original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set the new resolution to half
new_width = original_width // 2
new_height = original_height // 2
cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)

print(f"Video resolution set to: {new_width}x{new_height}")

# Create Background Subtractor
back_sub = cv2.createBackgroundSubtractorMOG2()

# To track the previous positions of objects and their IDs
tracked_objects = {}
object_id_counter = 0
max_untracked_frames = 30  # Keep track of object position for 30 frames when not detected
max_overlap_distance = 20  # Maximum distance to consider objects overlapping
object_colors = {}  # Store unique colors for each tracked object

# Data storage for exporting to CSV
tracking_data = []

# Function to smooth the positions
def smooth_positions(positions):
    if len(positions) < 2:
        return positions
    smoothed_positions = []
    for i in range(len(positions)):
        if i == 0:
            smoothed_positions.append(positions[i])  # First position remains unchanged
        elif i == len(positions) - 1:
            smoothed_positions.append(positions[i])  # Last position remains unchanged
        else:
            # Average the current position with the previous and next positions
            smoothed_x = int((positions[i-1][0] + positions[i][0] + positions[i+1][0]) / 3)
            smoothed_y = int((positions[i-1][1] + positions[i][1] + positions[i+1][1]) / 3)
            smoothed_positions.append((smoothed_x, smoothed_y))
    return smoothed_positions

# Function to update tracked objects
def update_tracked_objects():
    for obj_id in list(tracked_objects.keys()):
        if tracked_objects[obj_id]['untracked_frames'] >= max_untracked_frames:
            # Remove object if it has not been tracked for a long time
            del tracked_objects[obj_id]
            del object_colors[obj_id]  # Remove the color associated with this object
        else:
            tracked_objects[obj_id]['untracked_frames'] += 1  # Increment untracked frame count

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("End of video or error reading frame.")
        break

    # Apply background subtraction to get the foreground mask
    fg_mask = back_sub.apply(frame)

    # Convert the frame to black and white using a binary threshold
    _, bw_frame = cv2.threshold(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY)

    # Invert the binary frame to track black objects
    black_objects_mask = cv2.bitwise_not(bw_frame)

    # Combine the masks to highlight black moving objects
    combined_mask = cv2.bitwise_and(fg_mask, black_objects_mask)

    # Morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

    # Find contours of the black objects
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a set to keep track of currently detected object IDs
    current_object_ids = set()

    # Process each contour
    for contour in contours:
        if cv2.contourArea(contour) > 5:  # Minimum area to consider
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2

            # Draw the center of the tracked object
            cv2.circle(frame, (center_x, center_y), 3, (0, 255, 0), -1)  # Draw smaller center point

            # Use a simple logic to identify objects uniquely
            obj_id = None
            distances = []

            for key in tracked_objects.keys():
                last_position = tracked_objects[key]['positions'][-1]
                distance = np.sqrt((last_position[0] - center_x) ** 2 + (last_position[1] - center_y) ** 2)
                distances.append((key, distance))

            # Sort distances and determine if any existing objects are close enough
            distances.sort(key=lambda x: x[1])
            closest_objects = [dist for dist in distances if dist[1] < max_overlap_distance]

            # Check for overlap events
            overlap_events = []
            for close_obj_id, distance in closest_objects:
                overlap_events.append((close_obj_id, distance))

            if closest_objects:
                # Assign the ID of the closest object
                obj_id = closest_objects[0][0]

            if obj_id is None:
                obj_id = object_id_counter
                object_id_counter += 1  # Increment the object ID counter
                tracked_objects[obj_id] = {
                    'positions': [(center_x, center_y)],  # Initialize with the current position
                    'untracked_frames': 0  # Reset untracked frames count
                }
                # Assign a random color for the new object
                object_colors[obj_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            else:
                tracked_objects[obj_id]['positions'].append((center_x, center_y))  # Add new position
                tracked_objects[obj_id]['untracked_frames'] = 0  # Reset untracked frames count

            current_object_ids.add(obj_id)  # Mark this object as currently detected

            # Smooth the positions before drawing
            smoothed_positions = smooth_positions(tracked_objects[obj_id]['positions'])

            # Draw lines connecting previous smoothed positions with the unique color for each object
            for i in range(len(smoothed_positions) - 1):
                cv2.line(frame, smoothed_positions[i], smoothed_positions[i + 1], object_colors[obj_id], 2)  # Use object's color

            # Limit the history of positions to the last 100 points (keeps lines for a longer time)
            if len(tracked_objects[obj_id]['positions']) > 100:
                tracked_objects[obj_id]['positions'].pop(0)

            # Store tracking data
            tracking_data.append({
                'Frame': cap.get(cv2.CAP_PROP_POS_FRAMES),
                'Object ID': obj_id,
                'Center X': center_x,
                'Center Y': center_y,
                'Overlap Events': overlap_events
            })

    # Update tracked objects, remove those that have been untracked for too long
    update_tracked_objects()

    # For objects that are currently not detected, draw their last known position
    for obj_id in tracked_objects.keys():
        if obj_id not in current_object_ids:
            last_position = tracked_objects[obj_id]['positions'][-1]
            # Draw the last known position with a smaller circle
            cv2.circle(frame, last_position, 3, (0, 255, 255), -1)  # Draw last position with a different color

            # Optionally draw a line to indicate persistence
            if len(tracked_objects[obj_id]['positions']) > 1:
                smoothed_positions = smooth_positions(tracked_objects[obj_id]['positions'])
                cv2.line(frame, smoothed_positions[-2], smoothed_positions[-1], (0, 255, 255), 1)  # Dotted line for lost object

    # Display the original frame with overlays
    cv2.imshow('Video - Tracking Separate Fish', frame)

    # Exit on ESC key
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

# Release the capture object
cap.release()

# Save tracking data to CSV
tracking_df = pd.DataFrame(tracking_data)
tracking_df.to_csv('out.csv', index=False)  # Save the tracking data

# Close all OpenCV windows
cv2.destroyAllWindows()
