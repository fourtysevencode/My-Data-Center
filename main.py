import threading
import time

SERVERS = {
    "1": {"name": "Budget VPS", "cost": 100, "income": 2, "power": 1},
    "2": {"name": "Compute Node", "cost": 600, "income": 14, "power": 2},
    "3": {"name": "GPU Cluster", "cost": 3000, "income": 80, "power": 4},
    "4": {"name": "AI Datacenter", "cost": 15000, "income": 450, "power": 8},
    "5": {"name": "Quantum Farm", "cost": 80000, "income": 2500, "power": 16},
    "6": {"name": "Orbital Cloud", "cost": 400000, "income": 15000, "power": 32},
}

balance = 500
owned = {key: 0 for key in SERVERS}
balance_lock = threading.Lock()


def calculate_income():
    return sum(
        owned[key] * server["income"]
        for key, server in SERVERS.items()
    )


def list_items(items, owned):
    print("\nSERVER MARKETPLACE")
    print("-" * 55)

    for key, server in items.items():
        cost = int(server["cost"] * (1.15 ** owned[key]))

        print(
            f"{key}. {server['name']} | "
            f"Cost: ${cost:,} | "
            f"Income: +${server['income']:,}/sec | "
            f"Owned: {owned[key]}"
        )


def buy(menu_choice):
    global balance

    if menu_choice not in SERVERS:
        print("Invalid server selection.")
        return

    server = SERVERS[menu_choice]
    cost = int(server["cost"] * (1.15 ** owned[menu_choice]))

    with balance_lock:
        if balance < cost:
            print(f"Not enough money! You need ${cost:,}.")
            return

        balance -= cost
        owned[menu_choice] += 1
        remaining_balance = balance

    print(f"\nPurchased {server['name']} for ${cost:,}!")
    print(f"Income increased by ${server['income']:,}/sec.")
    print(f"Remaining balance: ${remaining_balance:,}")


def passive_income():
    global balance

    while True:
        time.sleep(1)

        income = calculate_income()

        with balance_lock:
            balance += income


def update_balance_display():
    """Update the balance on the main menu without redrawing everything."""
    with balance_lock:
        current_balance = balance

    # Move to the balance line and clear that line.
    print("\033[s", end="")
    print("\033[3;1H\033[2K", end="")
    print(f"Balance: ${current_balance:,}", end="")
    print("\033[u", end="", flush=True)


def main():
    global balance

    name = ""

    print(r"""
█   █ █   █    ████   ███  █████  ███      ███  █████ █   █ █████ █████ ████
██ ██░ █ █ ░   █░░░█ █ ░░█  ░█░░░█ ░░█    █ ░░░ █░░░░░██  █░ ░█░░░█░░░░░█░░░█
█░█ █░░ █ ░ ░  █░░░█░█████░  █░░░█████░   █░ ░░░████░░█░█ █░░ █░░░████░░████░░
█░░░█░░ █░ ░   █░░ █░█░░░█░░ █░░ █░░░█░░  █░░   █░░░░ █░░██░░ █░░ █░░░░ █░░█░
█░░ █░░ █░░    ████ ░█░░░█░░ █░░ █░░░█░░   ███  █████░█░░ █░░ █░░ █████░█░░░█░
 ░░  ░░  ░░     ░░░░ ░░░  ░░  ░░  ░░  ░░    ░░░  ░░░░░ ░░  ░░  ░░  ░░░░░ ░░  ░
  ░   ░   ░      ░░░░  ░   ░   ░   ░   ░     ░░░  ░░░░░ ░   ░   ░   ░░░░░ ░   ░
""")

    # Start passive income in the background.
    income_thread = threading.Thread(
        target=passive_income,
        daemon=True
    )
    income_thread.start()

    while True:
        print("\n" + "=" * 45)
        print(f"Your Data Center: {name or 'Unnamed'}")
        print(f"Balance: ${balance:,}")
        print(f"Servers owned: {sum(owned.values())}")
        print("=" * 45)

        print("1. Name your data center")
        print("2. Buy servers")
        print("3. View infrastructure")
        print("4. Exit")

        choice = input("\nChoose an option > ").strip()

        match choice:
            case "1":
                new_name = input("New name: ").strip()

                if new_name:
                    name = new_name
                    print(f"Your Data Center is now called {name}.")

            case "2":
                list_items(SERVERS, owned)

                server_choice = input(
                    "\nChoose a server to buy (Enter to cancel) > "
                ).strip()

                if server_choice:
                    buy(server_choice)

            case "3":
                print("\nYOUR INFRASTRUCTURE")
                print("-" * 55)

                for key, server in SERVERS.items():
                    count = owned[key]
                    income = count * server["income"]

                    print(
                        f"{server['name']:<20} "
                        f"x{count:<3} +${income:,}/sec"
                    )

                print(f"\nTotal income: ${calculate_income():,}/sec")

            case "4":
                print("Bye!")
                break

            case _:
                print("Invalid option.")


if __name__ == "__main__":
    main()
