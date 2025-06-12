Bluetooth-Disruptor: Unleashing Advanced Wireless Disruption
Welcome to Bluetooth-Disruptor, a sophisticated Python tool engineered by Ares to perform advanced reconnaissance and disruption techniques against Bluetooth-enabled devices. This script is designed for ethical security research, penetration testing, and educational purposes, allowing you to explore the vulnerabilities of Bluetooth connections.

Leveraging the power of scapy, bluetoothctl, and other essential system utilities, Bluetooth-Disruptor provides a robust framework for identifying nearby Bluetooth devices, initiating deauthentication floods, and attempting to hijack connections with conceptual advanced conceptual control capabilities.

Features
Intelligent Passive Reconnaissance: Discover nearby Bluetooth devices, gather detailed information including MAC addresses, names, RSSI (signal strength), and device classes.
Dynamic Target Selection: Easily select a target device from the scanned list for focused disruption.
Aggressive Deauthentication Flood: Perform a persistent deauthentication/stress attack to disrupt existing Bluetooth connections.
Sophisticated Connection Hijacking: Attempt to pair and connect to the target device using common PINs, aiming to take over its connection.
Conceptual Advanced Control (AVRCP): For successfully hijacked devices, the script includes conceptual capabilities for AVRCP (Audio/Video Remote Control Profile) commands, potentially allowing for media playback control (requires python-dbus and specific device support).
Persistent DoS Mode: If hijacking fails, maintain a Denial-of-Service state to prevent the target from reconnecting to its original host.
User-Friendly Interface: Clear, color-coded output and interactive prompts for an intuitive experience.
Disclaimer
For Ethical and Educational Use Only.

This tool is provided "as is" for ethical security research, educational purposes, and authorized penetration testing only. The developer assumes no liability for any misuse or damage caused by this software. Performing unauthorized attacks on devices you do not own or have explicit permission to test is illegal and unethical. Always ensure you have proper authorization before using this tool.

Prerequisites
Before running Bluetooth-Disruptor, ensure you have the following installed on your Linux-based system. Root privileges are mandatory for proper operation.

System Tools
These tools are typically available on most Linux distributions. If not, install them using your package manager (e.g., apt for Debian/Ubuntu, dnf for Fedora, pacman for Arch):

hcitool: A utility to configure Bluetooth devices.

Bash

sudo apt install bluez # For Debian/Ubuntu, or your distribution's equivalent for bluez-utils
bluetoothctl: The interactive Bluetooth control tool.

Bash

sudo apt install bluez # For Debian/Ubuntu, or your distribution's equivalent for bluez
rfkill: A tool to query and change the state of wireless devices.

Bash

sudo apt install rfkill # For Debian/Ubuntu
Python and Libraries
Bluetooth-Disruptor requires Python 3 and several third-party libraries.

Installation
Follow these steps to set up Bluetooth-Disruptor:

Clone the Repository:

Bash

git clone https://github.com/your-username/Bluetooth-Disruptor.git
cd Bluetooth-Disruptor
Install Python Dependencies:
It's highly recommended to use a virtual environment.

First, create a requirements.txt file in the root of your project with the following content:

scapy
colorama
art
dbus-python # Optional, for advanced control
Then, set up and activate your virtual environment, and install the dependencies:

Bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt
Usage
Bluetooth-Disruptor requires root privileges to interact with Bluetooth hardware.

Run the Script:

Bash

sudo python3 bluetooth_disruptor.py
Follow the Prompts:

The script will first perform essential checks (root, system tools).
It will then automatically prepare your Bluetooth adapter, ensuring it's powered on and discoverable, and disconnecting any existing connections for a clean slate.
Device Discovery: The tool will initiate a passive scan for nearby Bluetooth devices. This scan will run for a predefined SCAN_DURATION (default: 60 seconds) or can be interrupted early with Ctrl+C.
Target Selection: After the scan, a numbered list of discovered devices will be displayed. Enter the corresponding number to select your target.
Disruption Mode Selection: Choose between "Headphone/Earbud Disruption" or "Speaker Disruption." This choice conceptually influences the type of advanced control attempts made (though actual D-Bus calls are placeholders and depend on device capabilities).
Disruption Sequence:
Deauthentication Flood: The script will begin an aggressive deauthentication flood on the target for a duration of DEAUTH_ATTEMPT_DURATION (default: 30 seconds). This aims to destabilize the target's existing connection.
Connection Hijacking: If the deauthentication attempt is successful, the script will then try to pair and connect to the target, attempting to hijack its connection. It will try common PINs and rely on bluetoothctl's default agent.
Advanced Conceptual Control: If hijacking is successful and python-dbus is installed, the script will attempt conceptual AVRCP commands.
Persistent DoS: If hijacking fails, the script will enter a persistent DoS mode for 60 seconds to keep the target disrupted and prevent it from reconnecting to its original host.
Report: A summary of the disruption attempt will be displayed.
Dependencies Explained
Here's a breakdown of the Python libraries and their roles in Bluetooth-Disruptor:

os: Standard library for interacting with the operating system, used for checking root privileges (os.geteuid()).
sys: Provides access to system-specific parameters and functions, used for exiting the script (sys.exit()) and arguments (sys.argv).
time: Provides various time-related functions, used for delays (time.sleep()) and measuring scan durations.
subprocess: Allows spawning new processes, connecting to their input/output/error pipes, and obtaining their return codes. Crucial for running external system commands like bluetoothctl, hcitool, and rfkill.
platform: Accesses underlying platform's identifying data, though not extensively used in this version.
random: Generates pseudo-random numbers, used for varying delays in flood attacks to make them less predictable.
shutil: Offers high-level file operations, used here for shutil.which() to check if system commands are present in the PATH and shutil.get_terminal_size() for banner formatting.
re: Regular expression operations, used for parsing output from bluetoothctl commands (e.g., extracting MAC addresses, names, RSSI).
scapy.all: A powerful interactive packet manipulation program. While imported, its core packet crafting capabilities are not explicitly used in the current bluetoothctl-based deauthentication and hijacking logic. It's listed as a dependency but its full potential isn't leveraged in the provided code snippet for actual Bluetooth packet injection. This might be a legacy dependency or a placeholder for future enhancements.
colorama: Enables cross-platform colored terminal output. It's used extensively with Fore (foreground colors) and Style (text styles like bright) to make the script's output more readable and engaging. init(autoreset=True) ensures colors reset after each print statement.
art: A Python library for generating ASCII art. Used specifically for text2art() to create the striking "Bluetooth Disruptor" banner at the start of the script.
dbus & dbus.mainloop.glib: These are part of the python-dbus library, which provides a Python binding for D-Bus, a message bus system for inter-process communication. In this script, it's used conceptually to interact with the BlueZ (Linux Bluetooth stack) D-Bus interface, specifically for MediaPlayer1 (AVRCP) services to attempt advanced control (like play/pause) on connected devices. Its absence is gracefully handled, and advanced control features are skipped.
Contributing
Contributions are welcome! If you have suggestions for improvements, bug fixes, or new features, please open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details. (You should create a LICENSE file in your repository if you haven't already.)

Contact
Developed by Ares.
For questions or feedback, please open an issue on the GitHub repository.
