import subprocess
import requests
import threading
from urllib.parse import urlparse
from bs4 import BeautifulSoup

###################################################################################

def nmap(target):
    print("Running Nmap")

    # Check if nmap is installed
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

    # Check if python-nmap is installed
    try:
        import nmap
        print("python-nmap is installed")
    except ImportError:
        print("python-nmap is not installed")
        subprocess.run(['pip', 'install', 'python-nmap'])
        import nmap

    # Initialize the Nmap scanner
    scanner = nmap.PortScanner()

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

###################################################################################

def gobuster(base_url, wordlist_file, timeout):
    print("Running gobuster")

    # Function to scan a single URL and print status if found
    def scan_url(base_url, word, timeout):
        url = f"{base_url}/{word}"
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print(f"Found: {url}")
        except requests.RequestException as e:
            print(f"Error accessing: {url} (Error: {e})")

    # Read the wordlist file
    try:
        with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_file}' not found.")
        return

    # Scan each URL
    for word in words:
        scan_url(base_url, word, timeout)

###################################################################################

def subdomain(domain):
    print("Running Subdomain")

    def get_subdomains_crtsh(domain):
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            subdomains = set()
            for entry in data:
                if "name_value" in entry:
                    names = entry["name_value"].split("\n")
                    for name in names:
                        if domain in name:
                            subdomains.add(name.strip())
            return subdomains
        return set()

    def get_subdomains_threatcrowd(domain):
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/"
        params = {"domain": domain}
        try:
            response = requests.get(url, params=params, verify=False)  # Ignore SSL errors
            if response.status_code == 200:
                data = response.json()
                if "subdomains" in data:
                    return set(data["subdomains"])
        except requests.exceptions.RequestException:
            pass
        return set()

    def get_subdomains_rapiddns(domain):
        url = f"https://rapiddns.io/subdomain/{domain}?full=1#result"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            subdomains = set()
            for td in soup.find_all("td"):
                if domain in td.text:
                    subdomains.add(td.text.strip())
            return subdomains
        return set()

    def find_subdomains(domain):
        subdomains = set()
        subdomains.update(get_subdomains_crtsh(domain))
        subdomains.update(get_subdomains_threatcrowd(domain))
        subdomains.update(get_subdomains_rapiddns(domain))
        return subdomains

    subdomains = find_subdomains(domain)
    for subdomain in subdomains:
        print(subdomain)

###################################################################################

def run_all(target, base_url, wordlist_file, timeout):
    # Extract domain from base_url
    parsed_url = urlparse(base_url)
    domain = parsed_url.netloc

    # Create threads for each function
    thread1 = threading.Thread(target=nmap, args=(target,))
    thread2 = threading.Thread(target=gobuster, args=(base_url, wordlist_file, timeout))
    thread3 = threading.Thread(target=subdomain, args=(domain,))

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for all threads to complete
    thread1.join()
    thread2.join()
    thread3.join()

    print("All parts completed")

if __name__ == "__main__":
    # Collect inputs first
    target = input("Please enter the target IP address or hostname for Nmap: ")
    base_url = input("Please enter the target URL for Gobuster: ")
    wordlist_file = input("Please enter the path to the wordlist file for Gobuster: ")
    timeout = int(input("Please enter the request timeout in seconds for Gobuster: "))

    # Run all parts simultaneously
    run_all(target, base_url, wordlist_file, timeout)
