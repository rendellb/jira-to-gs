import time, argparse

from requests import get, post
from json import loads
from os import path
from argparse import ArgumentParser

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from gsjiraconfig import *

### Check if we have a credential file stored already for Google Sheets. If not, authenticate the user.
def getCredentials():
    credential_path = os.path.join('jira-to-gs.json')

    parser = argparse.ArgumentParser(parents=[tools.argparser])
    flags = parser.parse_args()

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print ('Storing credentials to ' + credential_path)
    return credentials

def getValues(issues, *args):
    values = []
    extra = []

    ### Loop through each row.
    for issue in issues:
        ### Set default values we're pulling from JIRA
        issueKey = issue['key']
        issueId = ''
        issueType = ''
        summary = ''
        assignee = ''
        created = ''
        resolved = ''
        updated = ''
        reporter = ''
        status = ''
        resolution = ''

        ### Try to get the values for all the defaults.
        issueId = issue['id']
        issueType = issue['fields']['issuetype']['name']

        try:
            summary = issue['fields']['summary']
        except:
            pass

        try:
            assignee = issue['fields']['assignee']['emailAddress']
        except:
            pass

        try:
            created = issue['fields']['created'].replace('T', ' ')[:issue['fields']['created'].index('.')]
        except:
            pass

        try:
            resolved = issue['fields']['resolutiondate'].replace('T', ' ')[:issue['fields']['resolutiondate'].index('.')]
        except:
            pass

        try:
            updated = issue['fields']['updated']
        except:
            pass

        try:
            reporter = issue['fields']['reporter']['emailAddress']
        except:
            pass

        try:
            status = issue['fields']['status']['statusCategory']['name']
        except:
            pass

        try:
            resolution = issue['fields']['resolution']['name']
        except:
            pass

        ### Define any additional custom args here.
        if 'typecat' in args:
            try:
                first = issue['fields']['customfield_19331']
                typecat = first['value'] + ' -> ' + first['child']['value']
                extra.append(typecat)
            except:
                pass
            
        ### Use this if you're trying to grab values from a change log. It's often pretty time consuming, so if there's any other methods of retrieving the same data without diving into the change log, use that.
        ''' 
        getUrl = apiBase + '/issue/' + issueKey + '?expand=changelog'
        getResponse = requests.get(getUrl, headers=headersGetJira)
        data = json.loads(getResponse.text)

        for change in data['changelog']['histories']:
            if change['items'][0]['fromString'] == 'Open':
                if change['items'][0]['toString'] == 'Approved':
                    extra.append(change['author']['name'])
                    extra.append(change['created'].replace('T', ' ')[:change['created'].index('.')])
        '''

        ### Create our array of core default values.
        core = [issueKey, issueId, issueType, summary, assignee, created, resolved, reporter, status, resolution]
        
        ### Add the core and any extra values to the final values variable to return.
        values.append((core + extra))

    return values

def getFullJSON(issueKey):
    getUrl =  apiBase + '/issue/' + issueKey
    getResponse = requests.get(getUrl, headers=headersGetJira)
    data = json.loads(getResponse.text)
    
    print data
            
def writeSheet(sheet, tab, values, service, clear):
    
    ### We'll always only clear and use the exact number of columns we need, so we can figure out what column letter it needs to go based on the length of the first value, up to 52.
    columnLetters = [0, 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ']
    
    rangeName = tab + '!A2:' + columnLetters[len(values[0])]
    
    ### We'll clear if it needs to be written to clean sheet, otherwise, we'll append it to historic values.
    if clear:
        service.spreadsheets().values().clear(spreadsheetId=sheet, range=rangeName, body={}).execute()
    
    ### Prepare body payload with values for API.
    body = {
      'values': values
    }

    ### Append our values to the Google Sheet.
    service.spreadsheets().values().append(spreadsheetId=sheet, range=rangeName, valueInputOption="USER_ENTERED", body=body).execute()

def queryData(query, start, *args):
    values = []

    ### Escape quotations before constructing the payload to send as a JSON.
    query = query.replace('"', '\'')
    payload = '{"jql": "' + str(query) + '", "maxResults": 1000, "startAt": ' + str(start) + '}'

    ### Send payload to search URL to get data.
    searchUrl = apiBase + '/search'
    getResponse = requests.post(searchUrl, headers=headersPostJira, data=payload)
    
    ### Try to convert JSON to use in Python. We'll pass if nothing that can be converted comes back.
    try:
        data = json.loads(getResponse.text)
        values += getValues(data['issues'], *args)
    except:
        pass

    ### The JIRA API can only return a max of 1000 results. If we get 1000, we're going to recurse this function and offset our starting row by 1000 so we can get the next 1000 results.
    if len(values) == 1000:
        values += queryData(query, start + 1000, *args)

    return values

def queryAndWrite(sheet, tab, query, service, clear, *args):
    print 'Getting data for ' + tab + ': '
    values = queryData(query, 0, *args)
    print len(values) + ' rows found'
    
    if len(values) > 0:
        writeSheet(sheet, tab, values, service, clear)

def run():
    ### Time when this script started.
    start = time.time()
    
    ### Run through OAuth with Google Sheets.
    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    ### Set the spreadsheet ID and tab for Google Sheets as well as the JQL query we're using to pull data from JIRA. We'll also be passing the service we created to interact with the Google Sheets API.
    sheet = 'SPREADSHEET_ID'
    tab = 'TABNAME'
    query = 'QUERY'
    
    ### Query the data and write it to the sheet!
    queryAndWrite(sheet, tab, query, service, True)
    
    ### Print the time it took to run this script.
    end = time.time()
    print ('Time Elapsed: ' + str(int(end - start))) + 's'
    
run()