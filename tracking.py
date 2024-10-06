import cv2
import numpy as np
import random

tracked_objects = {}
object_id_counter = 0
max_untracked_frames = 30
max_overlap_distance = 20
object_colors = {}

# Function to smooth positions
def smooth_positions(positions):
    if len(positions) < 2:
        return positions
    smoothed_positions = []
    for i in range(len(positions)):
        if i == 0 or i == len(positions) - 1:
            smoothed_positions.append(positions[i])
        else:
            smoothed_x = int((positions[i-1][0] + positions[i][0] + positions[i+1][0]) / 3)
            smoothed_y = int((positions[i-1][1] + positions[i][1] + positions[i+1][1]) / 3)
            smoothed_positions.append((smoothed_x, smoothed_y))
    return smoothed_positions

# Function to update objects
def update_tracked_objects():
    for obj_id in list(tracked_objects.keys()):
        if tracked_objects[obj_id]['untracked_frames'] >= max_untracked_frames:
            del tracked_objects[obj_id]
            del object_colors[obj_id]
        else:
            tracked_objects[obj_id]['untracked_frames'] += 1

# Main tracking function
def track_objects(frame, back_sub, tracking_data, frame_no):
    fg_mask = back_sub.apply(frame)
    _, bw_frame = cv2.threshold(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY)
    black_objects_mask = cv2.bitwise_not(bw_frame)
    combined_mask = cv2.bitwise_and(fg_mask, black_objects_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    current_object_ids = set()

    for contour in contours:
        if cv2.contourArea(contour) > 5:
            x, y, w, h = cv2.boundingRect(contour)
            center_x, center_y = x + w // 2, y + h // 2
            cv2.circle(frame, (center_x, center_y), 3, (0, 255, 0), -1)

            global object_id_counter
            obj_id = None
            distances = []
            for key in tracked_objects.keys():
                last_position = tracked_objects[key]['positions'][-1]
                distance = np.sqrt((last_position[0] - center_x) ** 2 + (last_position[1] - center_y) ** 2)
                distances.append((key, distance))

            distances.sort(key=lambda x: x[1])
            closest_objects = [dist for dist in distances if dist[1] < max_overlap_distance]

            if closest_objects:
                obj_id = closest_objects[0][0]

            if obj_id is None:
                obj_id = object_id_counter
                object_id_counter += 1
                tracked_objects[obj_id] = {'positions': [(center_x, center_y)], 'untracked_frames': 0}
                object_colors[obj_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            else:
                tracked_objects[obj_id]['positions'].append((center_x, center_y))
                tracked_objects[obj_id]['untracked_frames'] = 0

            current_object_ids.add(obj_id)
            smoothed_positions = smooth_positions(tracked_objects[obj_id]['positions'])
            for i in range(len(smoothed_positions) - 1):
                cv2.line(frame, smoothed_positions[i], smoothed_positions[i + 1], object_colors[obj_id], 2)

            if len(tracked_objects[obj_id]['positions']) > 100:
                tracked_objects[obj_id]['positions'].pop(0)

            tracking_data.append({
                'Frame': frame_no,
                'Object ID': obj_id,
                'Center X': center_x,
                'Center Y': center_y
            })

    update_tracked_objects()
    return frame
