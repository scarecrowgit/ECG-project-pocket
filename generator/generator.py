import numpy as np
import pandas as pd
import time
import os
from dotenv import load_dotenv

class ECGSimulator:
    def __init__(self):
        """
        Initialize ECG Simulator with configurable parameters from the .env file
        """
        # Load environment variables from .env file
        load_dotenv()

        self.duration = float(os.getenv("DURATION", 1))
        self.sampling_rate = int(os.getenv("SAMPLING_RATE", 250))
        self.heart_rate = int(os.getenv("HEART_RATE", 72))
        self.noise_level = float(os.getenv("NOISE_LEVEL", 0.05))
        self.amplitude = float(os.getenv("AMPLITUDE", 1.0))
        self.output_file = os.getenv("OUTPUT_FILE", "../ecg_simulation_data.csv")
        
        # Generate time array
        self.time = np.linspace(0, self.duration, int(self.duration * self.sampling_rate), endpoint=False)
        
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
    
    def _qrs_complex(self, x, center):
        """
        Generate a simplified QRS complex
        """
        q_wave = self._gaussian_wave(x, center-0.05, amplitude=-0.5 * self.amplitude, width=0.02)
        r_wave = self._gaussian_wave(x, center, amplitude=self.amplitude, width=0.03)
        s_wave = self._gaussian_wave(x, center+0.05, amplitude=-0.3 * self.amplitude, width=0.02)
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
    generator = ECGSimulator()
    generator.write_data()