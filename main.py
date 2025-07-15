import sqlite3
import subprocess
import time
import re

# Function to create an SQLite database and table to store SSIDs
def create_db():
    conn = sqlite3.connect('wifi_networks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS networks (id INTEGER PRIMARY KEY, ssid TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Function to insert SSID into the SQLite database
def insert_ssid(ssid):
    conn = sqlite3.connect('wifi_networks.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO networks (ssid) VALUES (?)", (ssid,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting SSID {ssid}: {e}")
    finally:
        conn.close()

# Function to scan networks and store SSIDs in the database (passive listening)
def scan_networks(interface="wlan0"):
    print(f"Scanning for Wi-Fi networks on {interface} (Passive Mode)...")

    while True:
        time.sleep(1)  # 1-second delay before each scan cycle

        start_time = time.time()  # Start time of the scan

        # Use `iw` to monitor for beacon frames and extract SSIDs
        process = subprocess.Popen(
            ["sudo", "iw", interface, "scan"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        end_time = time.time()  # End time of the scan
        scan_duration = end_time - start_time  # Calculate duration

        print(f"Scan completed in {scan_duration:.2f} seconds")

        # Check if there's an error while running iw
        if process.returncode != 0:
            print(f"Error running iw: {stderr.decode()}")
            time.sleep(5)
            continue

        # Decode the output from iw
        output = stdout.decode("utf-8")

        # Extract SSID data from the output
        networks = set()
        for line in output.splitlines():
            if "SSID:" in line:  # Check if "SSID:" exists in the line
                parts = line.split("SSID:", 1)  # Split only once
                if len(parts) > 1:  # Ensure there is a second part
                    ssid = parts[1].strip()
                    if ssid and ssid not in networks:
                        networks.add(ssid)
                        print(f"Network found: SSID={ssid}")
                        insert_ssid(ssid)

        # Sleep before scanning again to avoid overwhelming the system
        time.sleep(10)

if __name__ == "__main__":
    create_db()  # Create the database if it doesn't exist

    # Start scanning for Wi-Fi networks in a continuous loop
    interface = "wlan0"  # Assumes the user has manually set the interface to monitor mode
    scan_networks(interface)
