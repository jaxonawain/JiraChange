import conf, Outbound_Webhook
import ipaddress


class Fields:
    def __init__(self, json_payload):
        self.json_payload = json_payload
        self.validation_results = []
        self.issue_type = str(self.json_payload['fields']['issuetype']['name'])
        self.ip_address = str(self.json_payload['fields']['customfield_10065'])

    # Function to provide ease in adding Error messages to the ticket. Just specify a string to errmsg param.
    def add_errmsg_comment(self, errmsg):
        outbound_webhook = Outbound_Webhook.NewOutboundWebhook(self.json_payload)
        outbound_webhook.create_errmsg_comment(errmsg)

    def validate_ip_network(self):
        ip_data = self.ip_address.replace(" ", "").replace("\r", "").split('\n')
        for ip in ip_data:
            try:
                ip_network_check = ipaddress.ip_network(ip)
            except Exception as e:
                self.add_errmsg_comment(e)
                return conf.validation_failure
        return conf.validation_success

    def validate_ip_global(self):
        ip_data = self.ip_address.replace(" ", "").replace("\r", "").split('\n')
        for ip in ip_data:
            try:
                ip_network_check = ipaddress.ip_network(ip)
                ip_is_global = ip_network_check.is_global
                if not ip_is_global:
                    self.add_errmsg_comment(f'{ip} is a private IP address')
                    return conf.validation_failure
            except Exception as e:
                self.add_errmsg_comment(e)
                return conf.validation_failure
        return conf.validation_success

    # Master validation functions. The following functions should be all-inclusive of the functions required to validate
    # custom fields, per ticket type. Need to return false, or true based on the child validation functions (included in
    # the list
    def validate_ip_grammar(self):
        validation_result_list = [self.validate_ip_network(), self.validate_ip_global()]
        if conf.validation_failure in validation_result_list:
            return conf.validation_failure
        else:
            return conf.validation_success

    # Function to map a ticket type, to a master validation function, and append the result to the validation_results
    # list. Pass validation_results back to the main class for success/failure action
    def validate_customfields(self):
        customfield_validation_mapper = {
            'IP-Whitelist': self.validate_ip_grammar()
        }
        self.validation_results.append(customfield_validation_mapper.get(self.issue_type))
        print(self.validation_results)
        return self.validation_results
