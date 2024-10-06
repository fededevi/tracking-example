import cv2
import numpy as np
import random

# To track the previous positions of objects and their IDs
tracked_objects = {}
object_id_counter = 0
max_overlap_distance = 20  # Maximum distance to consider objects overlapping
object_colors = {}  # Store unique colors for each tracked object

def track_objects(frame, back_sub, tracking_data, frame_no):
    global tracked_objects, object_id_counter

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

            if closest_objects:
                # Assign the ID of the closest object
                obj_id = closest_objects[0][0]

            if obj_id is None:
                obj_id = object_id_counter
                object_id_counter += 1  # Increment the object ID counter
                tracked_objects[obj_id] = {
                    'positions': [(center_x, center_y)],  # Initialize with the current position
                }
                # Assign a random color for the new object
                object_colors[obj_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            else:
                tracked_objects[obj_id]['positions'].append((center_x, center_y))  # Add new position

            current_object_ids.add(obj_id)  # Mark this object as currently detected

            # Store tracking data
            tracking_data.append({
                'Frame': frame_no,
                'Object ID': obj_id,
                'Center X': center_x,
                'Center Y': center_y
            })

    # Draw all points for each tracked object
    for obj_id in tracked_objects.keys():
        for position in tracked_objects[obj_id]['positions']:
            # Draw a point for each position
            cv2.circle(frame, position, 0, object_colors[obj_id], -1)  # Draw with object color

    return frame
