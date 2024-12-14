import csv
import time
import datetime
import requests
import threading
import queue

class ECGDataReceiver:
    def __init__(self, 
                 csv_file_path='ecg_simulation_data.csv', 
                 api_endpoint='http://localhost:3000/api/ecg-data',
                 batch_size=10):
        """
        Initialize ECG Data Receiver

        Parameters:
        - csv_file_path: Path to the CSV file with ECG data
        - api_endpoint: URL of the backend API endpoint
        - batch_size: Number of data points to send in each API request
        """
        self.csv_file_path = csv_file_path
        self.api_endpoint = api_endpoint
        self.batch_size = batch_size
        
        # Data queue for thread-safe processing
        self.data_queue = queue.Queue()
        
        # Flags for controlling threads
        self.is_running = False
    
    def read_csv_data(self):
        """
        Read ECG data from CSV file
        
        Returns:
        List of dictionaries with ECG data and timestamps
        """
        ecg_data = []
        try:
            with open(self.csv_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    ecg_data.append({
                        'timestamp': datetime.datetime.now().isoformat(),
                        'time': float(row['time']),
                        'ecg_signal': float(row['ecg_signal'])
                    })
        except FileNotFoundError:
            print(f"Error: CSV file {self.csv_file_path} not found.")
            return []
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []
        
        return ecg_data
    
    def send_data_to_api(self, data_batch):
        """
        Send data batch to backend API
        
        Parameters:
        - data_batch: List of data points to send
        
        Returns:
        Boolean indicating success or failure
        """
        try:
            response = requests.post(
                self.api_endpoint, 
                json=data_batch,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                print(f"Successfully sent {len(data_batch)} data points")
                return True
            else:
                print(f"Failed to send data. Status code: {response.status_code}")
                return False
        
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
            return False
    
    def process_data_thread(self):
        """
        Thread for processing and sending data
        """
        ecg_data = self.read_csv_data()
        data_batch = []
        
        for data_point in ecg_data:
            if not self.is_running:
                break
            
            data_batch.append(data_point)
            
            # Send batch when full
            if len(data_batch) >= self.batch_size:
                self.send_data_to_api(data_batch)
                data_batch = []
        
        # Send any remaining data
        if data_batch:
            self.send_data_to_api(data_batch)
    
    def start(self):
        """
        Start data receiver and sender
        """
        self.is_running = True
        
        # Create thread
        process_thread = threading.Thread(target=self.process_data_thread)
        
        # Start thread
        process_thread.start()
        
        return process_thread
    
    def stop(self):
        """
        Stop data receiver and sender
        """
        self.is_running = False
        print("Stopping ECG data receiver...")

def main():
    # Example usage
    receiver = ECGDataReceiver(
        csv_file_path='ecg_simulation_data.csv',
        api_endpoint='http://localhost:3000/api/ecg-data',
        batch_size=10
    )
    
    try:
        # Start receiving and sending data
        thread = receiver.start()
        
        # Wait for thread to complete
        thread.join()
    
    except KeyboardInterrupt:
        print("Manually stopped")
    
    finally:
        # Stop the receiver
        receiver.stop()

if __name__ == '__main__':
    main()

"""
Key Features:
1. CSV data processing
2. Adds timestamps to data points
3. API data sending
4. Batch processing
5. Error handling

Required Dependencies:
- requests

Installation:
pip install requests

Usage:
1. Configure API endpoint
2. Ensure CSV file is available
3. Run the script
4. Adjust batch size as needed
"""