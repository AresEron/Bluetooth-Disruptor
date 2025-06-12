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

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3 and the necessary Bluetooth development libraries installed.

#### For Full Linux Distributions (Debian/Ubuntu-based):

```bash
sudo apt update
sudo apt install python3-pip libbluetooth-dev bluez
pip3 install pybluez
