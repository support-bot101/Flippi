import os

def run_command(command):
    os.system(command)

def setup():
    # Update the system and install necessary dependencies
    print("Updating system and installing dependencies...")
    run_command("sudo apt update && sudo apt upgrade -y")

    # Install Python 3 and pip
    print("Installing Python 3 and pip...")
    run_command("sudo apt install -y python3 python3-pip")

    # Install required Python packages
    print("Installing Python packages (pygame, scapy)...")
    run_command("pip3 install pygame scapy")

    # Install necessary tools for Wi-Fi and Bluetooth (wireless-tools, aircrack-ng, bluez)
    print("Installing Wi-Fi and Bluetooth tools...")
    run_command("sudo apt install -y wireless-tools aircrack-ng bluez")

    # Enable Bluetooth service
    print("Enabling and starting Bluetooth service...")
    run_command("sudo systemctl enable bluetooth")
    run_command("sudo systemctl start bluetooth")

    # Allow user to access Wi-Fi and Bluetooth interfaces (netdev, bluetooth groups)
    print("Adding user to netdev and bluetooth groups...")
    run_command(f"sudo usermod -aG netdev {os.getlogin()}")
    run_command(f"sudo usermod -aG bluetooth {os.getlogin()}")

    # Set up capabilities for scapy to send raw packets without root
    print("Allowing scapy to send raw packets...")
    run_command(f"sudo setcap cap_net_raw+ep $(which python3)")

    # Enable monitor mode for Wi-Fi interface (wlan0)
    print("Setting wlan0 to monitor mode...")
    run_command("sudo ip link set wlan0 down")
    run_command("sudo iw dev wlan0 set type monitor")
    run_command("sudo ip link set wlan0 up")

    # Prompt to reboot or run the script
    reb = input("Would you like to reboot the system now? (y/n): ").strip().lower()
    if reb == "y":
        print("Rebooting the system...")
        run_command("sudo reboot")
    else:
        run_script = input("Would you like to run the Flippi script now? (y/n): ").strip().lower()
        if run_script == "y":
            print("Running Flippi script...")
            run_command("sudo python3 flippi.py")
        else:
            print("You can run the script later by executing: sudo python3 flippi.py")

if __name__ == "__main__":
    setup()