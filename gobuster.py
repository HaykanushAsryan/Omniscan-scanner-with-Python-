import argparse
import requests

# Function to scan a single URL and print status if found
def scan_url(base_url, word, timeout):
    url = f"{base_url}/{word}"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"Found: {url}")
    except requests.RequestException as e:
        print(f"Error accessing: {url} (Error: {e})")

# Main function to handle arguments and perform scanning
def main():
    parser = argparse.ArgumentParser(description='Simple directory scanner')
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-w', '--wordlist', required=True, help='Wordlist file')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    args = parser.parse_args()

    base_url = args.url
    wordlist_file = args.wordlist
    timeout = args.timeout

    # Read the wordlist file
    try:
        with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_file}' not found.")
        return

    # Scan each URL
    for word in words:
        scan_url(base_url, word, timeout)

if __name__ == "__main__":
    main()
