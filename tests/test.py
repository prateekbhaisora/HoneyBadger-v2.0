import requests
from bs4 import BeautifulSoup

def fetch_contract_source_code(hash_or_address):
    url = "https://etherscan.io/address/{}/#code".format(hash_or_address)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        code_element = soup.find('pre', class_='js-sourcecopyarea')
        if code_element:
            source_code = code_element.text.strip()
            return source_code
        else:
            print("Contract source code not found.")
    else:
        print("Failed to fetch contract source code. Status code: {}".format(response.status_code))

# Example usage
hash_or_address = raw_input("Enter the hash code or address of the smart contract: ")
source_code = fetch_contract_source_code(hash_or_address)
if source_code:
    print("Contract Source Code:")
    print(source_code)
