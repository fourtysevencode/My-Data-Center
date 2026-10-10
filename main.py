import curses
import time
import threading

ascii_heading = """
                                welcome to
█   █ █   █    ████   ███  █████  ███      ███  █████ █   █ █████ █████ ████
██ ██░ █ █ ░   █░░░█ █ ░░█  ░█░░░█ ░░█    █ ░░░ █░░░░░██  █░ ░█░░░█░░░░░█░░░█
█░█ █░░ █ ░ ░  █░░░█░█████░  █░░░█████░   █░ ░░░████░░█░█ █░░ █░░░████░░████░░
█░░░█░░ █░ ░   █░░ █░█░░░█░░ █░░ █░░░█░░  █░░   █░░░░ █░░██░░ █░░ █░░░░ █░░█░
█░░ █░░ █░░    ████ ░█░░░█░░ █░░ █░░░█░░   ███  █████░█░░ █░░ █░░ █████░█░░░█░
 ░░  ░░  ░░     ░░░░ ░░░  ░░  ░░  ░░  ░░    ░░░  ░░░░░ ░░  ░░  ░░  ░░░░░ ░░  ░
  ░   ░   ░      ░░░░  ░   ░   ░   ░   ░     ░░░  ░░░░░ ░   ░   ░   ░░░░░ ░   ░
                      well.. its your data center!
  """

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
name = ""
balance_lock = threading.RLock()


def calculate_income():
    with balance_lock:
        return sum(
            owned[key] * server["income"]
            for key, server in SERVERS.items()
        )


def income_loop():
    global balance

    while True:
        time.sleep(1)
        income = calculate_income()
        with balance_lock:
            balance += income


income_thread = threading.Thread(target=income_loop, daemon=True)
income_thread.start()


def main(stdscr):
    global balance, name

    curses.curs_set(0)

    stdscr.erase()
    height, width = stdscr.getmaxyx()
    heading_lines = ascii_heading.splitlines()
    first_line = max(0, (height - len(heading_lines)) // 2)

    for row, line in enumerate(heading_lines):
        y = first_line + row
        if y >= height:
            break
        # Keep the heading's literal indentation and spacing unchanged.
        try:
            stdscr.addnstr(y, 0, line, max(0, width - 1))
        except curses.error:
            pass

    stdscr.refresh()
    time.sleep(2)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    message = "Welcome to your Data Center!"
    mode = "menu"
    selected = ""
    input_buffer = ""

    while True:
        # Process keyboard input without blocking.
        key = stdscr.getch()

        if key != -1:
            if mode == "menu":
                if key in (ord("1"), ord("2"), ord("3"), ord("4")):
                    choice = chr(key)

                    if choice == "1":
                        mode = "name"
                        input_buffer = ""
                    elif choice == "2":
                        mode = "buy"
                        input_buffer = ""
                    elif choice == "3":
                        mode = "infrastructure"
                    elif choice == "4":
                        break

            elif mode in ("name", "buy"):
                if key in (10, 13, curses.KEY_ENTER):
                    if mode == "name":
                        if input_buffer.strip():
                            name = input_buffer.strip()
                            message = f"Data center renamed to {name}."
                        mode = "menu"

                    elif mode == "buy":
                        selected = input_buffer.strip()

                        if not selected:
                            message = "Purchase cancelled."
                        elif selected in SERVERS:
                            server = SERVERS[selected]
                            cost = int(
                                server["cost"] * (1.15 ** owned[selected])
                            )

                            with balance_lock:
                                if balance >= cost:
                                    balance -= cost
                                    owned[selected] += 1
                                    message = (
                                        f"Purchased {server['name']} "
                                        f"for ${cost:,}!"
                                    )
                                else:
                                    message = (
                                        f"Not enough money! Need ${cost:,}."
                                    )
                        else:
                            message = "Invalid server selection."

                        mode = "menu"

                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    input_buffer = input_buffer[:-1]

                elif 32 <= key <= 126:
                    input_buffer += chr(key)

            elif mode == "infrastructure":
                if key in (ord("m"), ord("M"), ord("b"), ord("B"), 27):
                    mode = "menu"

        # Draw the interface afresh; only the display changes, not the game state.
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        def write(y, x, text):
            if 0 <= y < height and x < width:
                try:
                    stdscr.addnstr(y, x, text, max(0, width - x - 1))
                except curses.error:
                    pass

        write(0, 2, "")
        write(1, 2, "=" * min(40, max(0, width - 4)))
        write(3, 2, f"Your Data Center: {name or 'Unnamed'}")

        with balance_lock:
            current_balance = balance

        write(4, 2, f"Balance: ${current_balance:,}")
        write(5, 2, f"Income: ${calculate_income():,}/sec")
        write(6, 2, f"Servers owned: {sum(owned.values())}")

        if mode == "menu":
            write(8, 2, "1. Name your data center")
            write(9, 2, "2. Buy servers")
            write(10, 2, "3. View infrastructure")
            write(11, 2, "4. Exit")
            write(13, 2, "Choose an option using keys 1-4.")

        elif mode == "name":
            write(8, 2, "Enter your data center name:")
            write(9, 2, input_buffer + "_")
            write(11, 2, "Press Enter to confirm.")

        elif mode == "buy":
            write(8, 2, "SERVER MARKETPLACE")

            for i, (server_key, server) in enumerate(SERVERS.items()):
                cost = int(server["cost"] * (1.15 ** owned[server_key]))
                write(
                    9 + i, 2,
                    f"{server_key}. {server['name']} | "
                    f"${cost:,} | +${server['income']:,}/sec | "
                    f"Owned: {owned[server_key]}"
                )

            write(16, 2, "Enter server number and press Enter:")
            write(17, 2, input_buffer + "_")
            write(18, 2, "Press Enter with an empty input to cancel.")

        elif mode == "infrastructure":
            write(8, 2, "YOUR INFRASTRUCTURE")

            for i, (server_key, server) in enumerate(SERVERS.items()):
                count = owned[server_key]
                income = count * server["income"]
                write(
                    9 + i, 2,
                    f"{server['name']:<20} x{count:<3} +${income:,}/sec"
                )

            write(15, 2, "M. Return to the main menu")

        # Keep status messages away from active input fields on short terminals.
        message_y = height - 2
        input_rows = {9} if mode == "name" else {17} if mode == "buy" else set()
        while message_y in input_rows and message_y > 0:
            message_y -= 1
        write(message_y, 2, message)
        stdscr.refresh()

        # Earn money once per second, independently of keyboard input.
        # The UI refreshes every 100 ms.
        time.sleep(0.01)


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass