import pandas as pd
import requests
import time
from threading import Thread, Event
from datetime import datetime

class ECGDataReceiver:
    def __init__(self, 
                 csv_file_path='../ecg_simulation_data.csv', 
                 api_endpoint='http://localhost:8000/api/ecg-data', 
                 batch_size=250, 
                 send_interval=1):
        """
        Initialize ECG Data Receiver
        
        Parameters:
        - csv_file_path: Path to the CSV file with ECG data
        - api_endpoint: URL of the backend API endpoint
        - batch_size: Number of data points to send in each API request
        - send_interval: Time in seconds between sending batches
        """
        self.csv_file_path = csv_file_path
        self.api_endpoint = api_endpoint
        self.batch_size = batch_size
        self.send_interval = send_interval
        self.stop_event = Event()
        self.last_sent_row = 0  # To track the last row processed

    def send_data_to_api(self, data_batch):
        """
        Send a batch of data to the backend API
        """
        try:
            response = requests.post(self.api_endpoint, json=data_batch)
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