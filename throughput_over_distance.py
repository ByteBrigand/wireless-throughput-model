from math import pi, log2, log10, pow
import matplotlib.pyplot as plt
import numpy as np

def absolute_to_dB(value):
    return 10 * log10(value)

def dB_to_absolute(dB):
    return pow(10, dB / 10)

def W_to_dBm(W):
    return absolute_to_dB(W) + 30

def dBm_to_W(dBm):
    return dB_to_absolute(dBm - 30)

class WirelessParams:
    def __init__(self, tx_power_dBm, bandwidth_Hz, temperature_K, frequency_Hz, 
                 number_of_transmit_antennas, number_of_receive_antennas, other_rf_noise_dBm, receiver_losses_dB):
        self.tx_power_dBm = tx_power_dBm
        self.bandwidth_Hz = bandwidth_Hz
        self.temperature_K = temperature_K
        self.frequency_Hz = frequency_Hz
        self.number_of_transmit_antennas = number_of_transmit_antennas
        self.number_of_receive_antennas = number_of_receive_antennas
        self.other_rf_noise_dBm = other_rf_noise_dBm
        self.receiver_losses_dB = receiver_losses_dB
        
        self.speed_of_light = 3e8  # Speed of light in m/s
        self.boltzmann_constant = 1.38e-23
        self.wavelength = self.speed_of_light / frequency_Hz
        self.thermal_noise_W = self.boltzmann_constant * temperature_K * bandwidth_Hz
        self.beamforming_gain_dB = absolute_to_dB(number_of_receive_antennas)
        self.noise_level_dBm = W_to_dBm(self.thermal_noise_W)
        self.total_noise_dBm = W_to_dBm(dBm_to_W(self.noise_level_dBm) + dBm_to_W(other_rf_noise_dBm))

def polynomial_formula(BW, SNR_dB):
    return (2.4775878e+01 - 1.0209642e+00 * BW - 1.0301549e+00 * SNR_dB - 4.7138541e-03 * BW**2 +
            1.8121958e-01 * BW * SNR_dB + 1.0329859e-02 * SNR_dB**2)

# Parameters
params = WirelessParams(
    tx_power_dBm=20,
    bandwidth_Hz=20e6,
    temperature_K=290,
    frequency_Hz=2.4e9,
    number_of_transmit_antennas=1,
    number_of_receive_antennas=1,
    other_rf_noise_dBm=-95,
    receiver_losses_dB=25
)

# Distance range (in meters)
distances = range(1, 101)

def calculate_fspl_dB(params, distance):
    return 20 * log10(distance) + 20 * log10(params.frequency_Hz) - 147.55

def calculate_distance_from_path_loss(params, fspl_dB):
    return pow(10, (fspl_dB + 147.55 - 20 * log10(params.frequency_Hz)) / 20)

def calculate_snr(params, distance):
    fspl_dB = calculate_fspl_dB(params, distance)
    rx_power_dBm = params.tx_power_dBm - fspl_dB + params.beamforming_gain_dB - params.receiver_losses_dB
    rx_power_W = dBm_to_W(rx_power_dBm)
    snr_linear = rx_power_W / (dBm_to_W(params.total_noise_dBm))
    snr_dB = absolute_to_dB(snr_linear)
    return snr_dB

def calculate_distance(params, snr_dB):
    snr_linear = dB_to_absolute(snr_dB)
    rx_power_W = snr_linear * dBm_to_W(params.total_noise_dBm)
    rx_power_dBm = W_to_dBm(rx_power_W)
    fspl_dB = params.tx_power_dBm - rx_power_dBm + params.beamforming_gain_dB - params.receiver_losses_dB
    distance = calculate_distance_from_path_loss(params, fspl_dB)
    return distance

def calculate_throughput(params, distance):
    snr_dB = calculate_snr(params, distance)
    snr_linear = dB_to_absolute(snr_dB)
    
    capacity_bps = params.bandwidth_Hz * log2(1 + snr_linear)
    
    number_of_spatial_streams = min(params.number_of_transmit_antennas, params.number_of_receive_antennas)
    diminishing_returns_factor = log2(1 + number_of_spatial_streams)
    
    capacity_bps_real = capacity_bps * 0.6 * diminishing_returns_factor
    capacity_Mbps = capacity_bps_real / 1e6
    
    return capacity_Mbps

# Print noise level in dBm
print(f"Thermal noise level: {params.noise_level_dBm:.2f} dBm")
print(f"Total noise level: {params.total_noise_dBm:.2f} dBm")

# Calculate throughput and SNR for each distance
throughputs = [calculate_throughput(params, d) for d in distances]
snrs_dB = [calculate_snr(params, d) for d in distances]

# Calculate polynomial formula throughput
poly_throughputs = [polynomial_formula(params.bandwidth_Hz / 1e6, snr_dB) for snr_dB in snrs_dB]

# Plot the graph
plt.figure(figsize=(10, 6))
plt.plot(distances, throughputs, label='Theoretical Throughput')
plt.plot(distances, poly_throughputs, 'r-', label='Polynomial Formula')
plt.xlabel('Distance (meters)')
plt.ylabel('Throughput (Mbit/s)')
plt.title('Throughput vs. Distance')
plt.ylim(bottom=0)
plt.grid(True)
plt.legend()
plt.show()

for distance in distances:
    if distance % 10 == 0:
        fspl_dB = calculate_fspl_dB(params, distance)
        rx_power_dBm = params.tx_power_dBm - fspl_dB + params.beamforming_gain_dB - params.receiver_losses_dB
        rx_power_W = dBm_to_W(rx_power_dBm)
        snr_linear = rx_power_W / dBm_to_W(params.total_noise_dBm)
        snr_dB = absolute_to_dB(snr_linear)
        print(f"Distance: {distance} m, FSPL: {fspl_dB:.2f} dB, RX Power: {rx_power_dBm:.2f} dBm, SNR: {snr_dB:.2f} dB")
