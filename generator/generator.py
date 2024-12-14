import numpy as np
import pandas as pd
import time

class ECGSimulator:
    def __init__(self, 
                 duration=1,  # seconds of data generated in each iteration
                 sampling_rate=250,  # Hz
                 heart_rate=72,  # beats per minute
                 noise_level=0.05,
                 output_file='../ecg_simulation_data.csv'):
        """
        Initialize ECG Simulator with configurable parameters
        
        Parameters:
        - duration: Duration of data per iteration (seconds)
        - sampling_rate: Number of samples per second
        - heart_rate: Simulated heart rate in beats per minute
        - noise_level: Amount of random noise to add to the signal
        - output_file: File to write the data continuously
        """
        self.duration = duration
        self.sampling_rate = sampling_rate
        self.heart_rate = heart_rate
        self.noise_level = noise_level
        self.output_file = output_file
        
        # Generate time array
        self.time = np.linspace(0, duration, int(duration * sampling_rate), endpoint=False)
        
    def _generate_ecg_signal(self):
        """
        Generate a realistic ECG signal with P, QRS, and T waves and added noise
        """
        beats = self.duration * (self.heart_rate / 60)
        signal_base = np.zeros_like(self.time)
        
        # QRS Complex
        for i in range(int(beats)):
            center = i * 60 / self.heart_rate
            qrs_wave = self._qrs_complex(self.time, center)
            signal_base += qrs_wave
        
        # Add noise
        noise = np.random.normal(0, self.noise_level, self.time.shape)
        return signal_base + noise
    
    def _qrs_complex(self, x, center, amplitude=1.0):
        """
        Generate a simplified QRS complex
        """
        q_wave = self._gaussian_wave(x, center-0.05, amplitude=-0.5, width=0.02)
        r_wave = self._gaussian_wave(x, center, amplitude=amplitude, width=0.03)
        s_wave = self._gaussian_wave(x, center+0.05, amplitude=-0.3, width=0.02)
        return q_wave + r_wave + s_wave
    
    def _gaussian_wave(self, x, center, amplitude=1.0, width=0.1):
        return amplitude * np.exp(-((x - center)**2) / (2 * width**2))
    
    def write_data(self):
        """
        Continuously write ECG data to a file
        """
        while True:
            ecg_signal = self._generate_ecg_signal()
            df = pd.DataFrame({
                'time': self.time,
                'ecg_signal': ecg_signal
            })
            df.to_csv(self.output_file, mode='a', header=False, index=False)
            print(f"Generated and appended {len(self.time)} data points.")
            time.sleep(self.duration)  # Simulate real-time behavior

if __name__ == '__main__':
    generator = ECGSimulator(output_file='../ecg_simulation_data.csv')
    generator.write_data()