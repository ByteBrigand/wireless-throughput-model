from math import pi, log2, log10, pow
import matplotlib.pyplot as plt
import numpy as np

# Utility functions
def absolute_to_dB(value):
    return 10 * log10(value)

def dB_to_absolute(dB):
    return pow(10, dB / 10)

def W_to_dBm(W):
    return absolute_to_dB(W) + 30

def dBm_to_W(dBm):
    return dB_to_absolute(dBm - 30)

# Class for wireless parameters
class WirelessParams:
    def __init__(self, tx_power_dBm=20, bandwidth_Hz=20e6, temperature_K=290, frequency_Hz=2.4e9, 
                 number_of_transmit_antennas=1, number_of_receive_antennas=1, other_rf_noise_dBm=-95, 
                 receiver_losses_dB=25, wall_loss_dB=0):
        self.tx_power_dBm = tx_power_dBm
        self.bandwidth_Hz = bandwidth_Hz
        self.temperature_K = temperature_K
        self.frequency_Hz = frequency_Hz
        self.number_of_transmit_antennas = number_of_transmit_antennas
        self.number_of_receive_antennas = number_of_receive_antennas
        self.other_rf_noise_dBm = other_rf_noise_dBm
        self.receiver_losses_dB = receiver_losses_dB
        self.wall_loss_dB = wall_loss_dB
        
        self.speed_of_light = 3e8  # Speed of light in m/s
        self.boltzmann_constant = 1.38e-23
        self.wavelength = self.speed_of_light / frequency_Hz
        self.thermal_noise_W = self.boltzmann_constant * temperature_K * bandwidth_Hz
        self.beamforming_gain_dB = absolute_to_dB(number_of_receive_antennas)
        self.noise_level_dBm = W_to_dBm(self.thermal_noise_W)
        self.total_noise_dBm = W_to_dBm(dBm_to_W(self.noise_level_dBm) + dBm_to_W(other_rf_noise_dBm))

# Polynomial formula for throughput calculation
def polynomial_formula(BW, SNR_dB):
    return ( -2.3328149e+01-2.4910219e-09*BW+5.9596095e-04*SNR_dB-1.6030769e-08*BW**2+9.5333136e-03*BW*SNR_dB
            -2.6536985e-02*SNR_dB**2-6.4408110e-07*BW**3+1.0886969e-01*BW**2*SNR_dB-3.0310919e-01*BW*SNR_dB**2
            +2.6790413e-01*SNR_dB**3-1.8400823e-05*BW**4-3.2985096e-03*BW**3*SNR_dB+6.8250356e-03*BW**2*SNR_dB**2
            +1.6734471e-03*BW*SNR_dB**3-9.7540191e-03*SNR_dB**4+1.9652095e-07*BW**5+2.5496150e-05*BW**4*SNR_dB
            -5.1368460e-05*BW**3*SNR_dB**2+8.8503436e-06*BW**2*SNR_dB**3-3.9838122e-05*BW*SNR_dB**4+1.3092017e-04*SNR_dB**5 )

def calculate_fspl_dB(params, distance):
    return 20 * log10(distance) + 20 * log10(params.frequency_Hz) - 147.55

def calculate_distance_from_path_loss(params, fspl_dB):
    return pow(10, (fspl_dB + 147.55 - 20 * log10(params.frequency_Hz)) / 20)

def calculate_total_path_loss(params, distance):
    fspl_dB = calculate_fspl_dB(params, distance)
    total_path_loss_dB = fspl_dB + params.wall_loss_dB
    return total_path_loss_dB

def calculate_snr(params, distance):
    total_path_loss_dB = calculate_total_path_loss(params, distance)
    rx_power_dBm = params.tx_power_dBm - total_path_loss_dB + params.beamforming_gain_dB - params.receiver_losses_dB
    rx_power_W = dBm_to_W(rx_power_dBm)
    snr_linear = rx_power_W / (dBm_to_W(params.total_noise_dBm))
    snr_dB = absolute_to_dB(snr_linear)
    return snr_dB

def calculate_distance(params, snr_dB):
    snr_linear = dB_to_absolute(snr_dB)
    rx_power_W = snr_linear * dBm_to_W(params.total_noise_dBm)
    rx_power_dBm = W_to_dBm(rx_power_W)
    fspl_dB = params.tx_power_dBm - rx_power_dBm + params.beamforming_gain_dB - params.receiver_losses_dB
    total_path_loss_dB = fspl_dB + params.wall_loss_dB
    distance = calculate_distance_from_path_loss(params, total_path_loss_dB - params.wall_loss_dB)
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

# Function to initialize wall configurations
def initialize_wall_config(wall_config):
    wall_attenuations = {
        "Drywall": 3,
        "Bookshelf": 2,
        "Exterior Glass": 3,
        "Solid Wood Door": 6,
        "Marble": 6,
        "Brick": 10,
        "Concrete": 12,
        "Elevator Shaft": 30
    }
    
    total_wall_loss_dB = sum(wall_config[wall] * wall_attenuations[wall] for wall in wall_config)
    return total_wall_loss_dB

# Main function
def main():
    wall_config = {
        "Drywall": 1,
        "Bookshelf": 0,
        "Exterior Glass": 0,
        "Solid Wood Door": 0,
        "Marble": 0,
        "Brick": 0,
        "Concrete": 0,
        "Elevator Shaft": 0
    }
    
    total_wall_loss_dB = initialize_wall_config(wall_config)
    
    params = WirelessParams(
        tx_power_dBm=20,
        bandwidth_Hz=20e6,
        temperature_K=290,
        frequency_Hz=2.4e9,
        number_of_transmit_antennas=1,
        number_of_receive_antennas=1,
        other_rf_noise_dBm=-95,
        receiver_losses_dB=25,
        wall_loss_dB=total_wall_loss_dB
    )
    
    distances = range(2, 101)
    
    throughputs = [calculate_throughput(params, d) for d in distances]
    snrs_dB = [calculate_snr(params, d) for d in distances]
    
    # Variable to toggle polynomial throughput display
    display_polynomial = False
    if display_polynomial:
        poly_throughputs = [polynomial_formula(params.bandwidth_Hz / 1e6, snr_dB) for snr_dB in snrs_dB]
    
    plt.figure(figsize=(10, 6))
    plt.plot(distances, throughputs, label='TCP Throughput')
    if display_polynomial:
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
            total_path_loss_dB = calculate_total_path_loss(params, distance)
            rx_power_dBm = params.tx_power_dBm - total_path_loss_dB + params.beamforming_gain_dB - params.receiver_losses_dB
            rx_power_W = dBm_to_W(rx_power_dBm)
            snr_linear = rx_power_W / dBm_to_W(params.total_noise_dBm)
            snr_dB = absolute_to_dB(snr_linear)
            print(f"Distance: {distance} m, Total Path Loss: {total_path_loss_dB:.2f} dB, RX Power: {rx_power_dBm:.2f} dBm, SNR: {snr_dB:.2f} dB")

if __name__ == "__main__":
    main()
