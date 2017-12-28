token = 'TOKEN' # Your JIRA token goes here!
apiBase = 'https://jira.YOURJIRADOMAIN.com/rest/api/2' # You'll need to put your company's JIRA domain.

headersGetJira = {
    'Cookie': 'auth-openid=' + token
}

headersPostJira = {
    'Cookie': 'auth-openid=' + token,
    'Content-Type' : 'application/json',
    'X-Atlassian-Token': 'no-check'
}

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'JIRA to Google Sheets Script'