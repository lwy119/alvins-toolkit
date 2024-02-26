from utility import menu, success, err
import requests, json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class SNA_PoC:

    def workflow_starter(self, workflow_id):
        if workflow_id == 0:
            self.done = True
        elif workflow_id == 1:
            self.enable_custom_events()
        elif workflow_id == 2:
            self.enable_relationship_events()
        elif workflow_id == 3:
            self.enable_core_events()
        elif workflow_id == 4:
            self.enable_all_policies()

    def authenticate(self):
        if not self._ip:
            self._ip = input("SNA IP: ")
            self._username = input("SNA Username: ")
            self._password = input("SNA Password: ")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = f"username={self._username}&password={self._password}"
        try:
            response = self._session.post(f"https://{self._ip}/token/v2/authenticate", headers=headers, data=payload, verify=False)
            self._jwt = response.cookies['stealthwatch.jwt']
            self._xsrf_token = response.cookies['XSRF-TOKEN']
            self.get_tenant_id()
        except Exception as e:
            err("Incorrect IP/username/password!")

    def get_tenant_id(self):
        response = self._session.get(f"https://{self._ip}/sw-reporting/v2/tenants", verify=False)
        self._tenant_id = json.loads(response.text)['data'][0]['id']

    def get_custom_events(self):
        response = self._session.get(f"https://{self._ip}/smc-configuration/rest/v1/tenants/{self._tenant_id}/policy/customEvents")
        return json.loads(response.text)['data']['customSecurityEvents']

    def enable_custom_events(self):
        custom_events = self.get_custom_events()
        disabled_custom_events = [ce for ce in custom_events if ce['enabled'] == False]
        headers = {
            "X-XSRF-TOKEN": self._xsrf_token,
            "Content-Type": "application/json"
        }
        for dce in disabled_custom_events:
            payload = {
                "timestamp": dce['timestamp']
            }
            response = self._session.put(f"https://{self._ip}/smc-configuration/rest/v1/tenants/{self._tenant_id}/policy/customEvents/{dce['id']}/enable", headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                success(f"Enabled customer event #{dce['id']} {dce['name']}")

    def get_relationship_events(self):
        response = self._session.get(f"https://{self._ip}/smc-configuration/rest/v1/tenants/{self._tenant_id}/policy/relationship/events", verify=False)
        return json.loads(response.text)['data']

    def enable_relationship_events(self):
        relationship_events = self.get_relationship_events()
        disabled_relationship_events = [re for re in relationship_events if re['alarmSettings']['enabled'] == False]
        headers = {
            "X-XSRF-TOKEN": self._xsrf_token,
            "Content-Type": "application/json"
        }
        for dre in disabled_relationship_events:
            dre_payload = [{
                "id": dre['id'],
                "policyId": dre['policy']['id'],
                "alarmSettings": {
                    "tolerance": dre['alarmSettings']['tolerance'],
                    "minimum": dre['alarmSettings']['minimum'],
                    "maximum": dre['alarmSettings']['maximum'],
                    "duration": dre['alarmSettings']['duration'],
                    "enabled": True
                }
            }]
            response = self._session.put(f"https://{self._ip}/smc-configuration/rest/v1/tenants/{self._tenant_id}/policy/relationship/events", headers=headers, data=json.dumps(dre_payload))
            if response.status_code == 200:
                success(f"Enabled relationship event #{dre['id']} {dre['name']}")
            else:
                failed(f"Failed at relationship event #{dre['id']} {dre['name']}")

    def get_core_events(self):
        response = self._session.get(f"https://{self._ip}/smc-configuration/rest/v1/tenants/{self._tenant_id}/policy/system/events", verify=False)
        return json.loads(response.text)['data']

    def enable_core_events(self):
        core_events = self.get_core_events()
        disabled_core_events = []
        for ce in core_events:
            if ce['eventSettings']['eventStatus']['sourceStatus'] == "DISABLED":
                disabled_core_events.append(ce)
            if "targetStatus" in ce['eventSettings']['eventStatus']:
                if ce['eventSettings']['eventStatus']['targetStatus'] == "DISABLED":
                    if ce not in disabled_core_events:
                        disabled_core_events.append(ce)
        headers = {
            "X-XSRF-TOKEN": self._xsrf_token,
            "Content-Type": "application/json"
        }
        for dce in disabled_core_events:
            dce_payload = [{
                "id": dce['id'],
                "policyId": dce['policy']['id'],
                "eventSettings": {
                    "eventStatus": {
                        "sourceStatus": "ENABLED"
                    },
                    "alarmSettings": []
                }
            }]
            if "targetStatus" in dce['eventSettings']['eventStatus']:
                if dce['eventSettings']['eventStatus']['targetStatus'] != "NOT_APPLICABLE":
                    dce_payload[0]['eventSettings']['eventStatus']['targetStatus'] = "ENABLED"
            if dce['eventSettings']['alarmSettings'] != []:
                for settings in dce['eventSettings']['alarmSettings']:
                    dce_payload[0]['eventSettings']['alarmSettings'].append({
                        "key": settings['key'],
                        "value": settings['value']
                    })
            response = self._session.put(f"https://{self._ip}/smc-configuration/rest/v1/tenants/{self._tenant_id}/policy/system/events", headers=headers, data=json.dumps(dce_payload))
            if response.status_code == 200:
                success(f"Enabled core event #{dce['id']} {dce['name']}")
            else:
                err(f"Failed at core event #{dce['id']} {dce['name']}")

    def enable_all_policies(self):
        self.enable_custom_events()
        self.enable_relationship_events()
        self.enable_core_events()

    def run(self):
        if not self._ip:
            self.authenticate()
        workflow_id = menu(self.workflows, "Which SNA PoC workflow do you want to run? ")
        self.workflow_starter(int(workflow_id))

    def __init__(self):
        self._ip = None
        self._username = None
        self._password = None
        self._session = requests.Session()
        self.done = False
        self.workflows = [
            "Back to previous menu",
            "Enable Custom Events",
            "Enable Relationship Events",
            "Enable Core Events",
            "Enable All Policies"
        ]
        while not self.done:
            self.run()

        

