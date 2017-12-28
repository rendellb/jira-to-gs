# JIRA to Google Sheets

This Python script retrieves data using the JIRA API and writes it to Google Sheets using the Google Sheets API. You'll need to have your own JIRA token, client_secret data, and Google Sheet that you have access to.

## Setup

* Create and enable your virtual environment.

* Install dependencies from requirements.txt.
```
pip install -r requirements.txt
```

* Place your JIRA token into the token variable of gsjiraconfig.py.

* Download and replace the client_secrets.json file with yours from the Google Cloud Platform.

* Populate the sheet var with the Google Sheet spreadsheet ID, tab var with the tab name in the sheet, and query var with your JQL query.

* Run run!

If everything is correctly set up, you'll be prompted to select your Google account, which will then be stored as a file to the same directory and saved for future use. From there, the script will retrieve data from the JIRA API based on your query and write it to the Google Sheet based on your spreadsheet ID and tab.