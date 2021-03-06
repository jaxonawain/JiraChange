import requests, json, secure_conf, conf, Syslog_Client
from requests.auth import HTTPBasicAuth


def send_splunk_notice(errmsg):
    log = Syslog_Client.Syslog('35.194.20.71')
    log.send(errmsg, Syslog_Client.Level.NOTICE)


def send_splunk_warning(errmsg):
    log = Syslog_Client.Syslog('35.194.20.71')
    log.send(errmsg, Syslog_Client.Level.NOTICE)


def create_jira_approval_comment(json_payload):
    outbound_webhook = NewOutboundWebhook(json_payload)
    outbound_webhook.create_jira_approval_comment()


def create_jira_denial_comment(json_payload):
    outbound_webhook = NewOutboundWebhook(json_payload)
    outbound_webhook.create_jira_denial_comment()


def push_jira_transition(json_payload, transition_id):
    outbound_webhook = NewOutboundWebhook(json_payload)
    outbound_webhook.push_jira_transition(transition_id)


class Jira_Transition:
    validation_succeeded = '21'
    validation_failed = '51'


class NewOutboundWebhook:
    def __init__(self, json_payload):
        self.original_json_payload = json_payload
        self.jira_comment_endpoint = conf.jiraFQDN + "/rest/servicedeskapi/request/" + self.original_json_payload[
            'key'] + "/comment"
        self.jira_transition_endpoint = conf.jiraFQDN + "/rest/api/latest/issue/" + self.original_json_payload[
            'key'] +'/transitions'
        self.jira_reqd_headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

    def jira_request(self, api_endpoint, request_body):
        requests.request("POST", api_endpoint, data=request_body, headers=self.jira_reqd_headers,
                         auth=HTTPBasicAuth(secure_conf.jira_username, secure_conf.jira_api_token))

    def create_jira_approval_comment(self):
        comment_payload = json.dumps({
            "public": True,
            "body": "Automation field validation completed. Awaiting manager approval"
        })
        self.jira_request(self.jira_comment_endpoint, comment_payload)

    def create_jira_denial_comment(self):
        comment_payload = json.dumps({
            "public": True,
            "body": "Automation field validation failed. Please try again."
        })
        self.jira_request(self.jira_comment_endpoint, comment_payload)

    def create_jira_comment(self, comment):
        comment_payload = json.dumps({
            "public": True,
            "body": str(comment)
        })
        self.jira_request(self.jira_comment_endpoint, comment_payload)

    def push_jira_transition(self, transition_id):
        json_payload = json.dumps({"transition": {"id": transition_id}})
        self.jira_request(self.jira_transition_endpoint, json_payload)
