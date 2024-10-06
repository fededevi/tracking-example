# csv_output.py

import pandas as pd

def save_tracking_data(tracking_data, output_file='out.csv'):
    df = pd.DataFrame(tracking_data)
    df.to_csv(output_file, index=False)
    print(f"Tracking data saved to {output_file}")

if __name__ == "__main__":
    # Sample data for testing
    tracking_data = [
        {'Frame': 1, 'Object ID': 1, 'Center X': 100, 'Center Y': 150},
        {'Frame': 2, 'Object ID': 1, 'Center X': 105, 'Center Y': 152},
    ]
    save_tracking_data(tracking_data)
