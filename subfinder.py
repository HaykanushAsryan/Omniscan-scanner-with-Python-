import requests
from bs4 import BeautifulSoup

def get_subdomains_crtsh(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        subdomains = set()
        for entry in data:
            if 'name_value' in entry:
                names = entry['name_value'].split('\n')
                for name in names:
                    if domain in name:
                        subdomains.add(name.strip())
        return subdomains
    return set()

def get_subdomains_threatcrowd(domain):
    url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/"
    params = {'domain': domain}
    try:
        response = requests.get(url, params=params, verify=False)  # Ignore SSL errors
        if response.status_code == 200:
            data = response.json()
            if 'subdomains' in data:
                return set(data['subdomains'])
    except requests.exceptions.RequestException:
        pass
    return set()

def get_subdomains_rapiddns(domain):
    url = f"https://rapiddns.io/subdomain/{domain}?full=1#result"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        subdomains = set()
        for td in soup.find_all('td'):
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

def main():
    domain = input("Enter the domain to search for subdomains: ").strip()
    subdomains = find_subdomains(domain)
    for subdomain in subdomains:
        print(subdomain)

if __name__ == "__main__":
    main()
