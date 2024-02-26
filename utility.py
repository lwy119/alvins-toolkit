COLOR = {
    "RED": "\33[91m",
    "BLUE": "\33[94m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[93m",
    "PURPLE": "\033[0;35m",
    "CYAN": "\033[36m",
    "END": "\033[0m"
}

def menu(items, question):
    print()
    for i in range(len(items)):
        print(f"{COLOR['YELLOW']}{i}. {items[i]}")
    item_id = int(input(question))
    return item_id

def banner():
    font = f"""
        {COLOR['YELLOW']}
           _       _       _       _______          _ _    _ _   
     /\   | |     (_)     ( )     |__   __|        | | |  (_) |  
    /  \  | |_   ___ _ __ |/ ___     | | ___   ___ | | | ___| |_ 
   / /\ \ | \ \ / / | '_ \  / __|    | |/ _ \ / _ \| | |/ / | __|
  / ____ \| |\ V /| | | | | \__ \    | | (_) | (_) | |   <| | |_ 
 /_/    \_\_| \_/ |_|_| |_| |___/    |_|\___/ \___/|_|_|\_\_|\__|"""
    print(font)

def err(text):
    print(f"{COLOR['RED']}{text}")

def success(text):
    print(f"{COLOR['GREEN']}{text}")