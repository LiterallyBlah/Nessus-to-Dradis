# Nessus-to-Dradis
This is a script that uses a config file to list scans and their associated projects in dradis. The main.py script when run will download a specified scan and upload it to the associated project in Dradis. This is mainly for people who deal with a lot of scans that run frequently and are managed through Dradis.

# Configuration
Make sure to change the details in the config file:
```{
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
}```
