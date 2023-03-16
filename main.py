import os
import json
import requests
import time
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


def upload_to_dradis(dradis_config, project_id, nessus_file_path):
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--headless')  # Add this line to run Chrome in headless mode
    chrome_options.add_argument('window-size=1920x1080')  # Set a larger window size

    driver = webdriver.Chrome(options=chrome_options)


    # Login
    driver.get(f"{dradis_config['base_url']}/pro/login")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "login"))
    )

    driver.find_element(By.ID, "login").click()
    driver.find_element(By.ID, "login").send_keys(dradis_config['username'])
    driver.find_element(By.ID, "password").click()
    driver.find_element(By.ID, "password").send_keys(dradis_config['password'])
    driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

    # Upload Nessus file
    driver.get(f"{dradis_config['base_url']}/pro/projects/{project_id}")
    driver.find_element(By.LINK_TEXT, "Upload").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "uploader"))
    )

    driver.find_element(By.ID, "uploader").click()
    driver.find_element(By.XPATH, "//option[. = 'Dradis::Plugins::Nessus']").click()
    driver.find_element(By.ID, "file").send_keys(nessus_file_path)

    # Wait for the upload process to complete and close the browser
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.ID, "file"))
    )
    time.sleep(10)
    driver.quit()


def main():
    with open("config.json", "r") as file:
        config = json.load(file)

    dradis_config = config["dradis"]

    for nessus_config in config["nessus_instances"]:
        headers = {'Content-Type': 'application/json'}
        session_token = create_session(nessus_config['username'], nessus_config['password'], nessus_config['base_url'], headers)
        headers['X-Cookie'] = f'token={session_token}'

        for mapping in nessus_config["scan_project_map"]:
            scan_id = mapping["scan_id"]
            project_id = mapping["project_id"]
            client_na = mapping["client"]

            print(f"Downloading scan for {client_na} with ID: {scan_id}")
            scan_data = download_scan(scan_id, nessus_config['base_url'], headers)

            scan_file_name = f"scan_{scan_id}.nessus"
            scan_file_path = os.path.join(os.getcwd(), scan_file_name)

            with open(scan_file_path, "wb") as file:
                file.write(scan_data)

            print(f"Downloaded scan {scan_id} to {scan_file_path}")

            print(f"Uploading scan {scan_id} to Dradis project {project_id}")
            upload_to_dradis(dradis_config, project_id, scan_file_path)

            print(f"Scan {scan_id} uploaded to Dradis project {project_id}")

        delete_session(nessus_config['base_url'], headers)


if __name__ == "__main__":
    main()
