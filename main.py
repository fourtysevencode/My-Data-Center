

print("""
█   █ █   █    ████   ███  █████  ███      ███  █████ █   █ █████ █████ ████    
██ ██░ █ █ ░   █░░░█ █ ░░█  ░█░░░█ ░░█    █ ░░░ █░░░░░██  █░ ░█░░░█░░░░░█░░░█   
█░█ █░░ █ ░ ░  █░░░█░█████░  █░░░█████░   █░ ░░░████░░█░█ █░░ █░░░████░░████░░  
█░░░█░░ █░ ░   █░░ █░█░░░█░░ █░░ █░░░█░░  █░░   █░░░░ █░░██░░ █░░ █░░░░ █░░█░ ░ 
█░░ █░░ █░░    ████ ░█░░░█░░ █░░ █░░░█░░   ███  █████░█░░ █░░ █░░ █████░█░░░█░  
 ░░  ░░  ░░     ░░░░ ░░░  ░░  ░░  ░░  ░░    ░░░  ░░░░░ ░░  ░░  ░░  ░░░░░ ░░  ░  
  ░   ░   ░      ░░░░  ░   ░   ░   ░   ░     ░░░  ░░░░░ ░   ░   ░   ░░░░░ ░   ░ """)
print("_"*79)

name = ""
balance = 500
print("Your Data Center: ", name)
print("Balance: ", balance)

print("1. Name your data center!")
print("2. Buy servers")
print("3. Exit")

while True:
    print("Choose an option!")
    choice = input("> ")

    match choice:
        case "1":
            name = input("New name: ")
            print("Your Data Center:", name)

        case "2":
            print("You chose to buy")

        case "3":
            print("Bye!")
            break