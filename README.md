# 🕵️‍♂️ Network Enumeration Tool

A **Python** GUI tool for network enumeration, including host discovery, port scanning, and saving results in JSON and SQLite databases.  
Simple, fast, and effective for your pentesting or network audit needs! 🔍🚀

---

## 🚀 Features

- 🖧 **Host Discovery:** Scan subnet for active hosts via ping and TCP port checks  
- 🔌 **Port Scanning:** Scan selected hosts for open TCP ports within a configurable range  
- 🖥️ **GUI Interface:** User-friendly Tkinter graphical interface  
- 💾 **Results Storage:** Save scans to JSON files and SQLite database automatically  
- ⚡ **Multi-threaded:** Faster scans with threading for host discovery  
- ⚙️ **Customizable:** Specify base IP and port ranges  

---

## ⚙️ Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Lekhanath-Bhattarai/Network-Enemuration-Tool.git
   cd Network-Enemuration-Tool
2. Create and activate a virtual environment (optional but recommended):
	python3 -m venv venv
	source venv/bin/activate   # Windows: venv\Scripts\activate

3. Install depenedencies:
	pip install -r requirements.txt

▶️ Usage
Run the application:
	python3 -m src.main
	
Enter the base IP (e.g., 192.168.1) to scan the subnet

Set port range (default: 1-100)

Click Start Scan

Select hosts to scan from the pop-up window

View live scan output in the GUI

Results saved automatically in results/scans.json and data/scans.db
