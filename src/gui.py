import tkinter as tk
from tkinter import messagebox, Toplevel, Checkbutton, IntVar
import threading
import socket
import json
import sqlite3
from datetime import datetime
import subprocess
import os

class NetworkScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Enumeration Tool")
        self.stop_flag = False
        self.selected_hosts = []

        tk.Label(root, text="Enter Base IP (e.g., 192.168.10):").pack(pady=5)
        self.ip_entry = tk.Entry(root, width=30)
        self.ip_entry.pack(pady=5)

        tk.Label(root, text="Port Range (e.g., 1-100):").pack(pady=5)
        self.port_entry = tk.Entry(root, width=30)
        self.port_entry.insert(tk.END, "1-100")
        self.port_entry.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Scan", command=self.start_scan)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.output = tk.Text(root, height=20, width=70)
        self.output.pack(pady=10)

    def log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)

    def start_scan(self):
        self.stop_flag = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        threading.Thread(target=self.run_host_discovery).start()

    def stop_scan(self):
        self.stop_flag = True
        self.log("[INFO] Scan stopped by user.")
        self.reset_buttons()

    def run_host_discovery(self):
        base_ip = self.ip_entry.get().strip()
        port_range = self.port_entry.get().strip()

        if not base_ip:
            messagebox.showerror("Error", "Please enter a valid base IP.")
            self.reset_buttons()
            return

        try:
            start_port, end_port = map(int, port_range.split("-"))
            ports = list(range(start_port, end_port + 1))
        except:
            self.log("[INFO] Invalid port range. Defaulting to 1-100.")
            ports = list(range(1, 101))

        self.log(f"[INFO] Discovering active hosts on {base_ip}.1-254...")
        active_hosts = self.scan_host_range(base_ip)

        if not active_hosts:
            self.log("[INFO] No active hosts found.")
            self.reset_buttons()
            return

        self.log(f"[INFO] Found {len(active_hosts)} active host(s).")

        # Ask user to select hosts from the main thread
        self.root.after(0, lambda: self.select_hosts_window(active_hosts, lambda selected: self.start_port_scan(selected, ports)))

    def start_port_scan(self, selected_hosts, ports):
        if not selected_hosts:
            self.log("[INFO] No hosts selected.")
            self.reset_buttons()
            return

        self.selected_hosts = selected_hosts
        all_scan_data = []

        for ip in selected_hosts:
            if self.stop_flag:
                break
            self.log(f"\n[INFO] Scanning ports on {ip}...")
            host_result = []
            for port in ports:
                if self.stop_flag:
                    break
                self.log(f"Checking port {port}...")
                result = self.scan_port(ip, port)
                if result and result[1] == "Open":
                    self.log(f"Port {result[0]}: {result[1]}")
                    host_result.append(result)

            if host_result:
                self.log("\n[INFO] Summary of open ports for " + ip)
                for port, status in host_result:
                    service = self.get_service_name(port)
                    self.log(f"Port {port} - {service} : {status}")

            all_scan_data.append({"ip": ip, "ports": host_result})

        self.save_to_json(all_scan_data)
        self.save_to_sqlite(all_scan_data)
        self.log("\n[INFO] Results saved to JSON and SQLite.")
        self.reset_buttons()

    def get_service_name(self, port):
        services = {
            20: "FTP Data", 21: "FTP Control", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            3306: "MySQL", 3389: "RDP", 5900: "VNC", 8080: "HTTP Proxy"
        }
        return services.get(port, "Unknown Service")

    def scan_host_range(self, base_ip):
        active = []
        threads = []

        def is_host_up(ip):
            try:
                subprocess.check_output(['ping', '-c', '1', ip], stderr=subprocess.DEVNULL)
                return True
            except:
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
            if is_host_up(ip):
                active.append(ip)

        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            t = threading.Thread(target=ping, args=(ip,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join(timeout=0.5)

        return sorted(active)

    def select_hosts_window(self, hosts, callback):
        selected = []
        top = Toplevel(self.root)
        top.title("Select Hosts to Scan")

        tk.Label(top, text="Select host(s) to scan:").pack(pady=5)

        vars = []
        for host in hosts:
            var = IntVar(value=1)
            chk = Checkbutton(top, text=host, variable=var)
            chk.pack(anchor="w")
            vars.append((host, var))

        def confirm():
            for host, var in vars:
                if var.get() == 1:
                    selected.append(host)
            top.destroy()
            callback(selected)

        tk.Button(top, text="Start Scanning Selected", command=confirm).pack(pady=10)

    def scan_port(self, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                return (port, "Open" if result == 0 else "Closed")
        except Exception as e:
            return (port, f"Error: {str(e)}")

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

    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerGUI(root)
    root.mainloop()
