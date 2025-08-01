import socket
import json
import sqlite3
import os
import subprocess
from datetime import datetime
import threading

class NetworkScannerCLI:
    def __init__(self):
        self.stop_flag = False
        self.selected_hosts = []

    def log(self, msg):
        print(msg)

    def run(self):
        try:
            base_ip = input("Enter Base IP (e.g., 192.168.10): ").strip()
            if not base_ip:
                self.log("Error: Base IP cannot be empty.")
                return

            port_range = input("Enter Port Range (e.g., 1-100) [default 1-100]: ").strip() or "1-100"
            try:
                start_port, end_port = map(int, port_range.split("-"))
                ports = list(range(start_port, end_port + 1))
            except Exception:
                self.log("Invalid port range, defaulting to 1-100.")
                ports = list(range(1, 101))

            self.log(f"[INFO] Discovering active hosts on {base_ip}.1-254...")
            active_hosts = self.scan_host_range(base_ip)

            if not active_hosts:
                self.log("[INFO] No active hosts found.")
                return

            self.log(f"[INFO] Found {len(active_hosts)} active host(s):")
            for i, host in enumerate(active_hosts, 1):
                self.log(f"{i}. {host}")

            self.selected_hosts = self.select_hosts(active_hosts)
            if not self.selected_hosts:
                self.log("[INFO] No hosts selected. Exiting.")
                return

            self.start_port_scan(self.selected_hosts, ports)

        except KeyboardInterrupt:
            self.log("\n[INFO] Scan stopped by user.")

    def scan_host_range(self, base_ip):
        active = []
        threads = []

        def is_host_up(ip):
            try:
                # Ping once, timeout 1 second
                subprocess.check_output(['ping', '-c', '1', '-W', '1', ip], stderr=subprocess.DEVNULL)
                return True
            except:
                # Check common ports if ping fails
                for port in [22, 80, 443]:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.5)
                            if s.connect_ex((ip, port)) == 0:
                                return True
                    except:
                        continue
            return False

        def ping(ip):
            if self.stop_flag:
                return
            if is_host_up(ip):
                active.append(ip)

        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            t = threading.Thread(target=ping, args=(ip,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return sorted(active)

    def select_hosts(self, hosts):
        self.log("\nSelect host(s) to scan by typing numbers separated by commas (e.g., 1,3,5), or 'all' to select all:")
        selection = input("> ").strip().lower()
        if selection == 'all':
            return hosts
        else:
            try:
                indexes = [int(i.strip()) for i in selection.split(",") if i.strip().isdigit()]
                selected = [hosts[i-1] for i in indexes if 0 < i <= len(hosts)]
                return selected
            except Exception:
                self.log("Invalid selection.")
                return []

    def start_port_scan(self, selected_hosts, ports):
        all_scan_data = []

        for ip in selected_hosts:
            if self.stop_flag:
                break
            self.log(f"\n[INFO] Scanning ports on {ip}...")
            host_result = []
            for port in ports:
                if self.stop_flag:
                    break
                # Use direct print with carriage return for smooth scanning display
                print(f"Checking port {port}...", end="\r", flush=True)
                result = self.scan_port(ip, port)
                if result and result[1] == "Open":
                    self.log(f"Port {result[0]}: {result[1]}")
                    host_result.append(result)

            if host_result:
                self.log(f"\n[INFO] Summary of open ports for {ip}:")
                for port, status in host_result:
                    service = self.get_service_name(port)
                    self.log(f"Port {port} - {service} : {status}")

            all_scan_data.append({"ip": ip, "ports": host_result})

        self.save_to_json(all_scan_data)
        self.save_to_sqlite(all_scan_data)
        self.log("\n[INFO] Results saved to JSON and SQLite.")

    def scan_port(self, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                return (port, "Open" if result == 0 else "Closed")
        except Exception as e:
            return (port, f"Error: {str(e)}")

    def get_service_name(self, port):
        services = {
            20: "FTP Data", 21: "FTP Control", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            3306: "MySQL", 3389: "RDP", 5900: "VNC", 8080: "HTTP Proxy"
        }
        return services.get(port, "Unknown Service")

    def save_to_json(self, data, filename="results/scans.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        timestamp = datetime.now().isoformat()
        record = {"timestamp": timestamp, "results": data}

        try:
            with open(filename, "r") as f:
                all_data = json.load(f)
        except FileNotFoundError:
            all_data = []

        all_data.append(record)

        with open(filename, "w") as f:
            json.dump(all_data, f, indent=4)

    def save_to_sqlite(self, data, db_file="data/scans.db"):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        for entry in data:
            for port_result in entry["ports"]:
                c.execute("INSERT INTO scans (target, port, status) VALUES (?, ?, ?)",
                          (entry["ip"], port_result[0], port_result[1]))

        conn.commit()
        conn.close()


if __name__ == "__main__":
    scanner = NetworkScannerCLI()
    scanner.run()
