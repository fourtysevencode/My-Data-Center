# My Data Center

*well.. its your data center!*

An idle tycoon game you play in your terminal over SSH. Start with $500, buy servers, and watch
the income roll in as you grow from a budget VPS to an orbital cloud.

```
ssh play.ronakbuilds.tech
```

## How to play

1. Connect (see [Connecting](#connecting) below).
2. Enter a username. If it's new, you'll be asked to set a password and an account is created;
   otherwise log in with your password.
3. Use the main menu with keys **1–4**:

   | Key | Action |
   |-----|--------|
   | 1 | Name your data center |
   | 2 | Buy servers: type the server number and press Enter (empty Enter cancels) |
   | 3 | View your infrastructure and per-server income (**M** to go back) |
   | 4 | Save and exit |

Every server you own earns money each second while you're connected. Each extra copy of the same
server costs 15% more than the last, so spread out or save up for the next tier.

| # | Server | Base cost | Income |
|---|--------|----------:|-------:|
| 1 | Budget VPS | $100 | $2/sec |
| 2 | Compute Node | $600 | $14/sec |
| 3 | GPU Cluster | $3,000 | $80/sec |
| 4 | AI Datacenter | $15,000 | $450/sec |
| 5 | Quantum Farm | $80,000 | $2,500/sec |
| 6 | Orbital Cloud | $400,000 | $15,000/sec |

Your progress (balance, name and servers) is saved automatically every second, so you can pick up
where you left off next time you log in.

## Connecting

The game is served at `play.ronakbuilds.tech` through a Cloudflare Tunnel, so you need
`cloudflared` installed to connect. You only have to set this up once.

### 1. Install cloudflared

- **macOS:** `brew install cloudflared`
- **Windows:** `winget install --id Cloudflare.cloudflared`
- **Linux:** download the package for your distro from
  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

### 2. Add this to your SSH config

The file is `~/.ssh/config` (on Windows, `C:\Users\<you>\.ssh\config`). Create it if it doesn't
exist.

```
Host play.ronakbuilds.tech
  ProxyCommand cloudflared access ssh --hostname %h
```

### 3. Connect

```bash
ssh play.ronakbuilds.tech
```

No SSH key or password is needed; the game has its own login. Use a terminal at least 80×24.

### Troubleshooting

- **`Permission denied (publickey)`**: the SSH config entry from step 2 is missing or misspelled,
  so you reached the host machine instead of the game. Add it, then run
  `ssh-keygen -R play.ronakbuilds.tech` to forget the wrong host key and connect again.
- **`remote error: tls: internal error`**: your computer has an old DNS record cached. On macOS,
  run `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` and try again.
- **`cloudflared: command not found`**: cloudflared isn't installed or isn't on your `PATH`.
- **Garbled screen**: make your terminal window bigger and reconnect.

## How it works

| File | Purpose |
|------|---------|
| `game.py` | The curses game: login screen, menus, server shop and income loop |
| `database.py` | SQLite storage (`data.db`) for accounts (hashed passwords) and saved progress |
| `ssh_server.py` | A Paramiko SSH server on port 2222 that runs `game.py` in a pseudo-terminal for each connection |

Each SSH connection gets its own game process, so players don't share state except through the
database.

## Running locally

```bash
python3 -m venv .venv
.venv/bin/pip install paramiko
ssh-keygen -t ed25519 -f host_key -N ""   # one-time: the server's SSH host key
.venv/bin/python ssh_server.py
```

Then, in another terminal:

```bash
ssh -p 2222 localhost
```

Set `GAME_HOST=127.0.0.1` to accept local
connections only (the default is all interfaces).

You can also play without SSH by running `python3 game.py` directly.

## Hosting

The live server runs on [Hack Club Nest](https://hackclub.app) (`fourtysevencode@hackclub.app`):

- `ssh_server.py` runs from `~/My-Data-Center` with the project's `.venv`.
- A Cloudflare Tunnel named `play-game` routes `play.ronakbuilds.tech` to `ssh://localhost:2222`.
  Its config is in `~/.cloudflared/config.yml`.
- `~/start-game.sh` starts the game server and tunnel in the background if they aren't already
  running. Run it after the container restarts.
- Logs are written to `server.log` and `tunnel.log` in `~/My-Data-Center`.

To deploy an update:

```bash
ssh fourtysevencode@hackclub.app
cd ~/My-Data-Center && git pull
pkill -f ssh_server.py; ~/start-game.sh
```
