# My Data Center

A terminal game you play over SSH.

## Playing

The game is served at `play.ronakbuilds.tech` through a Cloudflare Tunnel, so you need
`cloudflared` installed to connect.

### 1. Install cloudflared

- **macOS:** `brew install cloudflared`
- **Windows:** `winget install --id Cloudflare.cloudflared`
- **Linux:** download the package for your distro from
  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

### 2. Add this to `~/.ssh/config`

On Windows the file is `C:\Users\<you>\.ssh\config`.

```
Host play.ronakbuilds.tech
  ProxyCommand cloudflared access ssh --hostname %h
```

### 3. Connect

```bash
ssh play.ronakbuilds.tech
```

No SSH account or password is needed; the game handles registration and login itself.

## Hosting

The server runs on Nest (`fourtysevencode@hackclub.app`):

- `ssh_server.py` listens on port 2222 (set `GAME_HOST` to change the bind address).
- A Cloudflare Tunnel named `play-game` routes `play.ronakbuilds.tech` to `ssh://localhost:2222`
  (config in `~/.cloudflared/config.yml`).
- `~/start-game.sh` starts both in the background if they aren't already running. Run it after
  the container restarts. Logs go to `server.log` and `tunnel.log` in this directory.

To run locally:

```bash
python3 -m venv .venv && .venv/bin/pip install paramiko
.venv/bin/python ssh_server.py
ssh -p 2222 localhost
```
