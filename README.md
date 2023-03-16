# Nessus-to-Dradis
This is a script that uses a config file to list scans and their associated projects in dradis. The main.py script, when run, will download a specified scan and upload it to the associated project in Dradis. This is mainly for people who deal with a lot of scans that frequently run (on a schedule) and are managed through Dradis.

# Prerequisites
You must have python3 installed in order to use this script. Once installed, you will then need to install the necessary libraries via requirements.txt:
`python3 -m pip install -r requirements.txt`

# Configuration
The config file may look a little strange, and this is because it supports multiple nessus instances (and only a single dradis instance). 

Make sure to change the details in the config file:
```
{
  "nessus_instances": [
    {
      "base_url": "https://<url>:8834",
      "username": "<username>",
      "password": "<password>",
      "scan_project_map": [
        {
	  "client": "Test 1",
          "scan_id": "8",
          "project_id": "15"
        },
        {
	  "client": "Test 2",
          "scan_id": "10",
          "project_id": "15"
        }
      ]
    },
    {
      "base_url": "https://<url>:8834",
      "username": "<username>",
      "password": "<password>",
      "scan_project_map": [
        {
	  "client": "Test 3",
          "scan_id": "178",
          "project_id": "15"
        },
      	{
	  "client": "Test 4",
	  "scan_id": "181",
	  "project_id": "15"
	}
      ]
    }
  ],
  "dradis": {
    "base_url": "https://<url>",
    "username": "<username>",
    "password": "<password>"
  }
}
```

# Using ness.py
I've included an extra script called ness.py, which can list all scans within a nessus instance and the associated ID.
`python3 ness.py`

ness.py uses the same config file to grab the details of the nessus server(s). It supports multiple servers and will prompt you to pick one, so it can list the scans. You can also download the scan using this script.

# Running the script
`python3 main.py`

# Notes
I can see many ways to make this script more efficient, but I can't be bothered to implement them. I'll optimise this sometime in the future.
