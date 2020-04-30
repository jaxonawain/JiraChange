import requests, json, secure_conf, conf, Syslog_Client
from requests.auth import HTTPBasicAuth


# File to handle all outbound webhooks, mostly back to Jira. Possible for other places, such as Mattermost.
# Purely for informational webhooks. Any webhooks to trigger automation need to have it
def send_splunk_notice(errmsg):
    log = Syslog_Client.Syslog('35.194.20.71')
    log.send(errmsg, Syslog_Client.Level.NOTICE)


def send_splunk_warning(errmsg):
    log = Syslog_Client.Syslog('35.194.20.71')
    log.send(errmsg, Syslog_Client.Level.NOTICE)


class NewOutboundWebhook:
    def __init__(self, json_payload):
        self.original_json_payload = json_payload
        self.jira_comment_endpoint = conf.jiraFQDN + "/rest/servicedeskapi/request/" + self.original_json_payload['key'] + "/comment"
        self.jira_reqd_headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

    def create_jira_approval_comment(self):
        comment_payload = json.dumps({
            "public": True,
            "body": "Automation field validation completed. Awaiting manager approval"
        })
        requests.request("POST", self.jira_comment_endpoint, data=comment_payload, headers=self.jira_reqd_headers,
                         auth=HTTPBasicAuth(secure_conf.jira_username, secure_conf.jira_api_token))

    def create_jira_denial_comment(self):
        comment_payload = json.dumps({
            "public": True,
            "body": "Automation field validation failed. Please try again."
        })
        requests.request("POST", self.jira_comment_endpoint, data=comment_payload, headers=self.jira_reqd_headers,
                         auth=HTTPBasicAuth(secure_conf.jira_username, secure_conf.jira_api_token))

    def create_jira_comment(self, comment):
        comment_payload = json.dumps({
            "public": True,
            "body": str(comment)
        })
        requests.request("POST", self.jira_comment_endpoint, data=comment_payload, headers=self.jira_reqd_headers,
                         auth=HTTPBasicAuth(secure_conf.jira_username, secure_conf.jira_api_token))



