import subprocess

result = subprocess.run(["which", "nmap"], capture_output=True, text=True)

if result.returncode == 0:
    print("nmap is installed")
else:
    print("nmap is not installed. Installing...")

    try:
        subprocess.run(["sudo", "apt-get", "install", "nmap"], check=True)  # Adjust for your package manager if not using apt-get
        print("nmap installation successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing nmap: {e}")

try:
    import nmap
    print("python-nmap is installed")
except ImportError:
    print("python-nmap is not installed")
    import subprocess
    subprocess.run(['pip', 'install', 'python-nmap'])

import nmap

scanner = nmap.PortScanner()

# Define target IP address or hostname
target = "66.94.234.13"

# Define Nmap options
options = "-sS -sV -sC -A -O -p 1-1000"

# Run the Nmap scan with the specified options
scanner.scan(target, arguments=options)

# Print the scan results
for host in scanner.all_hosts():
    print("Host: ", host)
    print("State: ", scanner[host].state())
    for proto in scanner[host].all_protocols():
        print("Protocol: ", proto)
        ports = scanner[host][proto].keys()
        for port in ports:
            print("Port: ", port, "State: ", scanner[host][proto][port]['state'])
            service = scanner[host][proto][port]
            print("  Service: ", service['name'])
            print("  Product: ", service.get('product', ''))
            print("  Version: ", service.get('version', ''))
            print("  Extra Info: ", service.get('extrainfo', ''))

