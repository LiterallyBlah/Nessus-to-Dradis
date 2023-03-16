import requests
import xml.etree.ElementTree as ET
import json
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def create_session(username, password, base_url, headers):
    url = f'{base_url}/session'
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    return response.json()['token']

def delete_session(base_url, headers):
    url = f'{base_url}/session'
    requests.delete(url, headers=headers, verify=False)

def list_scans(base_url, headers):
    url = f'{base_url}/scans'
    response = requests.get(url, headers=headers, verify=False)
    return response.json()['scans']

def download_scan(scan_id, base_url, headers):
    url = f'{base_url}/scans/{scan_id}/export'
    data = {"format": "nessus"}
    response = requests.post(url, headers=headers, json=data, verify=False)
    export_uuid = response.json()['file']

    url = f'{base_url}/scans/{scan_id}/export/{export_uuid}/status'
    while requests.get(url, headers=headers, verify=False).json()['status'] != 'ready':
        pass

    url = f'{base_url}/scans/{scan_id}/export/{export_uuid}/download'
    response = requests.get(url, headers=headers, verify=False)
    return response.content

def parse_scan_results(scan_data):
    root = ET.fromstring(scan_data)
    vuln_levels = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}

    for report_host in root.findall('.//ReportHost'):
        for report_item in report_host.findall('ReportItem'):
            risk_factor = report_item.find('risk_factor')
            if risk_factor is not None:
                risk_text = risk_factor.text
                if risk_text in vuln_levels:
                    vuln_levels[risk_text] += 1

    return vuln_levels

def load_config(config_file):
    with open(config_file) as f:
        config = json.load(f)
    return config

def main():
    config = load_config("config.json")

    print("Nessus Instances:")
    for index, instance in enumerate(config["nessus_instances"]):
        print(f"{index + 1}. {instance['base_url']}")

    choice = int(input("Enter the number of the Nessus instance you want to use: "))
    chosen_instance = config["nessus_instances"][choice - 1]
    nessus_server = chosen_instance["base_url"]
    username = chosen_instance["username"]
    password = chosen_instance["password"]
    headers = {'Content-Type': 'application/json'}

    session_token = create_session(username, password, nessus_server, headers)
    headers['X-Cookie'] = f'token={session_token}'

    scans = list_scans(nessus_server, headers)
    print("List of scans:")
    for index, scan in enumerate(scans):
        print(f"{index + 1}. {scan['name']} (ID: {scan['id']})")

    choice = int(input("Enter the number of the scan you want to download: "))
    chosen_scan = scans[choice - 1]
    scan_id = chosen_scan['id']
    scan_name = chosen_scan['name']

    print(f"Downloading scan: {scan_name} (ID: {scan_id})")
    scan_data = download_scan(scan_id, nessus_server, headers)

    print("Parsing scan results")
    vuln_levels = parse_scan_results(scan_data)

    print("\nVulnerabilities by level:")
    for level, count in vuln_levels.items():
        print(f"{level}: {count}")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(script_dir, f"{scan_name}.nessus")

    with open(output_path, "wb") as file:
        file.write(scan_data)

    print(f"Downloaded {scan_name}.nessus to {output_path}")

    delete_session(nessus_server, headers)

if __name__ == "__main__":
    main()
