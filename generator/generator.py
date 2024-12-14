import numpy as np
import pandas as pd
import scipy.signal as signal

class ECGSimulator:
    def __init__(self, 
                 duration=10,  # seconds
                 sampling_rate=250,  # Hz
                 heart_rate=72,  # beats per minute
                 noise_level=0.05):
        """
        Initialize ECG Simulator with configurable parameters
        
        Parameters:
        - duration: Total simulation duration in seconds
        - sampling_rate: Number of samples per second
        - heart_rate: Simulated heart rate in beats per minute
        - noise_level: Amount of random noise to add to the signal
        """
        self.duration = duration
        self.sampling_rate = sampling_rate
        self.heart_rate = heart_rate
        self.noise_level = noise_level
        
        # Generate time array
        self.time = np.linspace(0, duration, int(duration * sampling_rate), endpoint=False)
        
        # Generate the ECG signal
        self.ecg_signal = self._generate_ecg_signal()
    
    def _generate_ecg_signal(self):
        """
        Generate a realistic ECG signal with multiple components
        """
        # Basic signal parameters
        beats = self.duration * (self.heart_rate / 60)
        
        # Initialize signal
        signal_base = np.zeros_like(self.time)
        
        # P Wave
        for i in range(int(beats)):
            p_center = i * 60 / self.heart_rate
            p_wave = self._gaussian_wave(
                self.time, 
                center=p_center, 
                amplitude=0.1, 
                width=0.1
            )
            signal_base += p_wave
        
        # QRS Complex (Primary Heart Signal)
        for i in range(int(beats)):
            qrs_center = i * 60 / self.heart_rate
            qrs_wave = self._qrs_complex(
                self.time, 
                center=qrs_center
            )
            signal_base += qrs_wave
        
        # T Wave
        for i in range(int(beats)):
            t_center = i * 60 / self.heart_rate + 0.4
            t_wave = self._gaussian_wave(
                self.time, 
                center=t_center, 
                amplitude=-0.3, 
                width=0.15
            )
            signal_base += t_wave
        
        # Add noise
        noise = np.random.normal(0, self.noise_level, self.time.shape)
        signal_with_noise = signal_base + noise
        
        return signal_with_noise
    
    def _gaussian_wave(self, x, center, amplitude=1.0, width=0.1):
        """
        Generate a Gaussian-shaped wave
        """
        return amplitude * np.exp(-((x - center)**2) / (2 * width**2))
    
    def _qrs_complex(self, x, center, amplitude=1.0):
        """
        Generate a more complex QRS wave using multiple Gaussian curves
        """
        # Q wave
        q_wave = self._gaussian_wave(x, center-0.05, amplitude=-0.5, width=0.02)
        
        # R wave (main peak)
        r_wave = self._gaussian_wave(x, center, amplitude=amplitude, width=0.03)
        
        # S wave
        s_wave = self._gaussian_wave(x, center+0.05, amplitude=-0.3, width=0.02)
        
        return q_wave + r_wave + s_wave
    
    def export_to_csv(self, filename='ecg_data.csv'):
        """
        Export ECG signal to CSV file
        
        Parameters:
        - filename: Output CSV file name
        """
        df = pd.DataFrame({
            'time': self.time,
            'ecg_signal': self.ecg_signal
        })
        df.to_csv(filename, index=False)
        print(f"ECG data exported to {filename}")
    
    def calculate_heart_rate(self):
        """
        Calculate heart rate from the generated signal using peak detection
        """
        # Find peaks
        peaks, _ = signal.find_peaks(self.ecg_signal, height=0)
        
        # Calculate intervals between peaks
        peak_intervals = np.diff(self.time[peaks])
        
        # Convert to beats per minute
        estimated_heart_rate = 60 / np.mean(peak_intervals)
        
        return estimated_heart_rate

# Example usage
def main():
    # Create ECG simulator with default parameters
    ecg_sim = ECGSimulator(
        duration=10,  # 10 seconds of data
        sampling_rate=250,  # 250 Hz sampling rate
        heart_rate=72,  # 72 beats per minute
        noise_level=0.05  # 5% noise
    )
    
    # Export to CSV
    ecg_sim.export_to_csv('ecg_simulation_data.csv')
    
    # Verify heart rate calculation
    print(f"Estimated Heart Rate: {ecg_sim.calculate_heart_rate():.2f} BPM")

if __name__ == '__main__':
    main()

"""
Key Features:
1. ECG signal generation
2. Realistic simulation of P, QRS, and T waves
3. CSV export
4. Heart rate estimation

Usage Instructions:
- Adjust parameters in ECGSimulator initialization
- Run the script to generate ECG data
- Exports data to CSV for further analysis
"""