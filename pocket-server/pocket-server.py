import pandas as pd
import requests
import time
from threading import Thread, Event
from datetime import datetime
import os
from dotenv import load_dotenv

class ECGDataReceiver:
    def __init__(self):
        """
        Initialize ECG Data Receiver with configurable parameters from the .env file
        """
        # Load environment variables from .env file
        load_dotenv()

        self.user_id = os.getenv('USER_ID', '67FD20')
        self.csv_file_path = os.getenv('CSV_FILE_PATH', '../ecg_simulation_data.csv')
        self.api_endpoint = os.getenv('API_ENDPOINT', 'http://localhost:8000/api/ecg-data')
        self.batch_size = int(os.getenv('BATCH_SIZE', 250))
        self.send_interval = int(os.getenv('SEND_INTERVAL', 1))
        self.stop_event = Event()
        self.last_sent_row = 0  # To track the last row processed

    def send_data_to_api(self, data_batch):
        """
        Send a batch of data to the backend API
        """
        try:
            response = requests.post(self.api_endpoint, json={'user_id': self.user_id, 'data': data_batch})
            if response.status_code in [200, 201]:
                print(f"Sent {len(data_batch)} data points successfully.")
            else:
                print(f"Failed to send data. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
    
    def process_data(self):
        """
        Continuously read CSV data and send it to the backend at intervals
        """
        while not self.stop_event.is_set():
            try:
                # Read only new data since the last sent row
                data = pd.read_csv(self.csv_file_path, names=['time', 'ecg_signal'], header=None, skiprows=self.last_sent_row)
                if not data.empty:
                    # Add a unique timestamp for each row
                    data['timestamp'] = [datetime.now().isoformat() for _ in range(len(data))]
                    
                    # Remove 'time' field
                    data.drop(columns=['time'], inplace=True)

                    # Process in batches
                    for i in range(0, len(data), self.batch_size):
                        batch = data.iloc[i:i+self.batch_size].to_dict(orient='records')
                        self.send_data_to_api(batch)

                        # Pause for the specified interval between sending batches
                        if not self.stop_event.is_set():
                            time.sleep(self.send_interval)

                    # Update the last row sent
                    self.last_sent_row += len(data)
            except FileNotFoundError:
                print(f"CSV file {self.csv_file_path} not found. Retrying...")
                time.sleep(self.send_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(self.send_interval)

    def start(self):
        """
        Start the processing thread
        """
        self.thread = Thread(target=self.process_data)
        self.thread.start()

    def stop(self):
        """
        Stop the processing thread
        """
        self.stop_event.set()
        self.thread.join()
        print("ECG Data Receiver stopped.")

if __name__ == '__main__':
    receiver = ECGDataReceiver()
    try:
        receiver.start()
    except KeyboardInterrupt:
        receiver.stop()