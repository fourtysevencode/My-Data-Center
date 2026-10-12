import curses
import time
import threading
import database

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
active_username = None
balance_lock = threading.RLock()


database.setup()


def user_exists(username):
    with database.connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM player where username = ?", (username,)
        ).fetchone()

        return row


def authenticate(username, password):
    return database.authenticate(username, password)


def create_account(username, password):
    database.create_player(username, password)


def load_game_state(username):
    global balance, owned, name, active_username

    player = database.load_player(username)
    if player is None:
        raise ValueError(f"Cannot load missing player {username!r}.")

    with balance_lock:
        balance = player["balance"]
        name = player["name"]
        owned = {
            key: int(player["infrastructure"].get(key, 0))
            for key in SERVERS
        }
        active_username = username


def save_game_state():
    with balance_lock:
        username = active_username
        current_balance = balance
        current_name = name
        current_owned = owned.copy()

    if username is not None:
        database.save_player(
            username, current_balance, current_name, current_owned
        )


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
        save_game_state()


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
    mode = "login_username"
    selected = ""
    input_buffer = ""
    login_username = ""

    while True:
        # Process keyboard input without blocking.
        key = stdscr.getch()

        if key != -1:
            if mode == "login_username":
                if key in (10, 13, curses.KEY_ENTER):
                    login_username = input_buffer.strip()
                    if login_username:
                        if user_exists(login_username):
                            mode = "login_password"
                            message = "Account found. Enter your password."
                        else:
                            mode = "signup_password"
                            message = "Account not found. Set a password."
                        input_buffer = ""
                    else:
                        message = "Enter a username."
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    input_buffer = input_buffer[:-1]
                elif 32 <= key <= 126:
                    input_buffer += chr(key)

            elif mode in ("login_password", "signup_password"):
                if key in (10, 13, curses.KEY_ENTER):
                    password = input_buffer
                    if not password:
                        message = "Enter a password."
                    elif mode == "login_password":
                        if authenticate(login_username, password):
                            load_game_state(login_username)
                            message = f"Welcome back, {login_username}!"
                            mode = "menu"
                        else:
                            message = "Incorrect password. Try again."
                            input_buffer = ""
                    else:
                        create_account(login_username, password)
                        load_game_state(login_username)
                        message = f"Account created for {login_username}."
                        mode = "menu"
                    if mode == "menu":
                        input_buffer = ""
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    input_buffer = input_buffer[:-1]
                elif 32 <= key <= 126:
                    input_buffer += chr(key)

            elif mode == "menu":
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
                            save_game_state()
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
                                    save_game_state()
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

        if mode == "login_username":
            write(8, 2, "Log in to your Data Center")
            write(9, 2, "Username:")
            write(10, 2, input_buffer + "_")
            write(12, 2, "Press Enter to continue.")

        elif mode in ("login_password", "signup_password"):
            write(8, 2, "Log in to your Data Center")
            prompt = (
                "Password:"
                if mode == "login_password"
                else "Set a password:"
            )
            write(9, 2, prompt)
            write(10, 2, "*" * len(input_buffer) + "_")
            write(12, 2, "Press Enter to continue.")

        elif mode == "menu":
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
        input_rows = (
            {10}
            if mode in ("login_username", "login_password", "signup_password")
            else {9}
            if mode == "name"
            else {17}
            if mode == "buy"
            else set()
        )
        while message_y in input_rows and message_y > 0:
            message_y -= 1
        write(message_y, 2, message)
        stdscr.refresh()

        # Earn money once per second, independently of keyboard input.
        # The UI refreshes every 100 ms.
        time.sleep(0.01)

    save_game_state()


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass