from ise_poc import ISE_PoC
from sna_poc import SNA_PoC
from utility import menu, banner

solutions = [
    "End",
    "Identity Service Engine (ISE)",
    "Secure Network Analytics (SNA)"
]

# initiated user selected workflow
def poc_starter(id):
    global done
    if id == 0:
        done = True
    elif id == 1:
        ise_workflow = ISE_PoC()
    elif id == 2:
        sna_workflow = SNA_PoC()

# initialize app
if __name__ == '__main__':
    banner()
    done = False
    while not done:
        solution_id = menu(solutions, "Which PoC are you working on? ")
        poc_starter(int(solution_id))