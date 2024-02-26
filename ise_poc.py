from utility import menu, success, err
from pypsrp.client import Client as PSClient
from jinja2 import Environment, FileSystemLoader

class ISE_PoC:

    def workflow_starter(self, workflow_id):
        if workflow_id == 0:
            self.done = True
        if workflow_id == 1:
            self.prepare_adcs()

    def prepare_adcs(self):
        # Create certificate templates GPO_User and GPO_Computer
        adcs_host = input("AD CS IP / hostname? ")
        adcs_username = input("AD CS username? ")
        adcs_password = input("AD CS password? ")
        adcs_dc = input("AD CS DC? (e.g. DC=alvlau,DC=com) ")
        with PSClient(adcs_host, username=adcs_username, password=adcs_password, ssl=False) as psclient:
            # Create C:\temp
            output, streams, had_errors = psclient.execute_ps("New-Item -Path \"C:\\\" -Name \"temp\" -ItemType \"directory\"")
            # Create certificate template with DC info
            file_loader = FileSystemLoader('adcs')
            env = Environment(loader=file_loader)
            gpo_computer_template = env.get_template('gpo_computer.j2')
            gpo_computer = gpo_computer_template.render(DC=adcs_dc)
            with open('./adcs/gpo_computer.ldf', 'w') as gpo_computer_ldf:
                gpo_computer_ldf.write(gpo_computer)
            gpo_user_template = env.get_template('gpo_user.j2')
            gpo_user = gpo_user_template.render(DC=adcs_dc)
            with open('./adcs/gpo_user.ldf', 'w') as gpo_user_ldf:
                gpo_user_ldf.write(gpo_user)
            # pxgrid_template = env.get_template('pxgrid.j2')
            # pxgrid = pxgrid_template.render(DC=adcs_dc)
            # with open('./adcs/pxgrid.ldf', 'w') as pxgrid_ldf:
            #     pxgrid_ldf.write(pxgrid)
            # Copy certificate template metadata
            psclient.copy("./adcs/gpo_user.ldf", "C:\\temp\\gpo_user.ldf")
            psclient.copy("./adcs/gpo_computer.ldf", "C:\\temp\\gpo_computer.ldf")
            # Import certificate templates
            stdout, stderr, rc = psclient.execute_cmd("ldifde -i -k -f C:\\temp\\gpo_user.ldf")
            stdout, stderr, rc = psclient.execute_cmd("ldifde -i -k -f C:\\temp\\gpo_computer.ldf")
            # Enable the newly created templates
            output, streams, had_errors = psclient.execute_ps("Add-CATemplate -Name \"GPO_User\" -Force")
            output, streams, had_errors = psclient.execute_ps("Add-CATemplate -Name \"GPO_Computer\" -Force")
        return

    def run(self):
        workflow_id = menu(self.workflows, "Which ISE PoC workflow do you want to run? ")
        self.workflow_starter(int(workflow_id))

    def __init__(self):
        self.done = False
        self.workflows = [
            "Back to previous menu",
            "Prepare Microsoft AD CS",
            "TACACS+ Authentication & Authorization & Command Accounting",
            "RADIUS Dot1x EAP-PEAP Wired Authentication",
            "RADIUS Dot1x EAP-TLS Wired Authentication",
            "RADIUS Dot1x EAP-PEAP Wireless Authentication",
            "RADIUS Dot1x EAP-TLS Wireless Authentication",
            "RADIUS MAB Authentication",
            "Agent-based Posture",
            "Agentless Posture"
        ]
        while not self.done:
            self.run()