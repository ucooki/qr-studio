# QR Studio Setup Tutorial

A complete walkthrough of setting up a Python FastAPI web app on WSL, accessed remotely via SSH.

---

## 1. Python Virtual Environments

### Why?

Modern Linux systems protect their system Python from being messed up by user-installed packages. If you try `pip install` directly, you'll get an "externally-managed-environment" error. A **virtual environment** (venv) is an isolated copy of Python just for your project — your packages live there and don't affect anything else.

### Setup

```bash
# Install the venv module (one-time, needs admin)
sudo apt install python3.12-venv

# Create a virtual environment in a folder called "venv"
python3 -m venv venv

# Activate it — tells your shell to use this Python instead of the system one
source venv/bin/activate

# Install your project's dependencies
pip install -r requirements.txt
```

### Key things to remember

- You need to **activate** the venv every time you open a new terminal: `source venv/bin/activate`
- Your terminal prompt will show `(venv)` when it's active
- The `venv/` folder should be added to `.gitignore` — it can always be recreated from `requirements.txt`
- `requirements.txt` is just a list of package names (and optionally versions) that pip reads

### What the commands mean

| Command | Meaning |
|---|---|
| `sudo` | Run as admin (superuser do) |
| `apt install` | Install a system package using Debian/Ubuntu's package manager |
| `python3 -m venv venv` | Run the `venv` module (`-m`) to create a folder called `venv` |
| `source venv/bin/activate` | Run the activate script in your current shell session |
| `pip install -r requirements.txt` | Install packages listed in the file (`-r` = read from file) |

---

## 2. Project Structure

```
qr-studio/
  main.py              # Your FastAPI application (Python backend)
  requirements.txt     # List of Python packages needed
  templates/
    index.html         # The frontend (HTML/CSS/JS)
  venv/                # Virtual environment (don't commit this)
```

### Why a templates/ folder?

Convention. Keeping HTML files separate from Python files keeps your project organized. FastAPI/Flask/Django all typically expect templates in their own folder.

---

## 3. Running the Server

```bash
# Make sure venv is active first
source venv/bin/activate

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8042
```

### What this means

| Part | Meaning |
|---|---|
| `uvicorn` | A fast Python web server for ASGI apps (like FastAPI) |
| `main:app` | In the file `main.py`, use the variable called `app` |
| `--host 0.0.0.0` | Listen on ALL network interfaces (not just localhost). Required for other devices to connect |
| `--port 8042` | Use port 8042. You access the app at `http://localhost:8042` |

### Host explained

- `127.0.0.1` (localhost) = only your own machine can connect
- `0.0.0.0` = any device can connect (needed for network/phone access)

### Alternative: Run directly with Python

If you add this to the bottom of `main.py`, you can run it with just `python main.py` (useful for PyCharm's run button):

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8042)
```

---

## 4. Accessing the App

### From the same machine (WSL)

```
http://localhost:8042
```

### From a laptop via SSH (JetBrains Gateway)

When you're SSH'd into a remote machine, `localhost` on your laptop refers to your laptop, NOT the remote machine. The server is running on the remote machine, so you need **port forwarding** — a tunnel that maps your laptop's port to the remote machine's port.

**Gateway trick:** If you run the server from PyCharm Gateway's terminal, you can open the browser from Python:

```bash
python3 -c "import webbrowser; webbrowser.open('http://localhost:8042')"
```

Gateway handles the forwarding for you in this case.

**Manual SSH tunnel** (if needed):

```bash
ssh -i ~/.ssh/id_ed25519 -L 8042:localhost:8042 user@remote-ip
```

`-L 8042:localhost:8042` means: "forward my laptop's port 8042 to the remote machine's localhost:8042"

### From other devices on the network (phone, other computers)

This requires two extra steps because WSL sits behind Windows — devices on your network talk to Windows, not WSL directly.

**Step 1: Port proxy** — Tell Windows to forward traffic from its port 8042 to WSL's internal IP:

```bash
# Find WSL's internal IP first
hostname -I
# e.g. 172.18.26.19

# Set up the port proxy (run from WSL using PowerShell)
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "netsh interface portproxy add v4tov4 listenport=8042 listenaddress=0.0.0.0 connectport=8042 connectaddress=172.18.26.19"
```

**Step 2: Firewall rule** — Allow incoming connections on that port:

```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "New-NetFirewallRule -DisplayName QRStudio -Direction Inbound -LocalPort 8042 -Protocol TCP -Action Allow"
```

Then any device on the same Wi-Fi can access:

```
http://<your-pc-ip>:8042
```

To find your PC's IP, run `ipconfig` in PowerShell and look for the Wi-Fi adapter's IPv4 address (e.g. `192.168.0.212`).

### Important notes about WSL networking

- WSL has its own **internal IP** (e.g. `172.18.26.19`) — this is NOT reachable from the outside
- Your **PC's IP** (e.g. `192.168.0.212`) is what other devices see on the network
- The **port proxy** bridges the gap: external traffic hits Windows, Windows forwards it to WSL
- WSL's internal IP can **change on reboot** — you may need to update the port proxy rule

---

## 5. Useful Commands Reference

```bash
# Check WSL's internal IP
hostname -I

# Check if the server is responding
curl http://localhost:8042

# See what's listening on which ports
ss -tlnp

# Kill a process using a specific port (if the port is stuck)
fuser -k 8042/tcp

# Remove the port proxy rule later
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "netsh interface portproxy delete v4tov4 listenport=8042 listenaddress=0.0.0.0"

# Remove the firewall rule later
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "Remove-NetFirewallRule -DisplayName QRStudio"
```

---

## 6. What I Learned

- Building and documenting FastAPI endpoints for file/image responses
- Validating and constraining API inputs (`Query` defaults and bounds)
- Connecting a lightweight frontend to backend generation endpoints
- Handling WSL networking details for LAN access (port proxy + firewall)
- Packaging a Python project to be reproducible with `requirements.txt`

---

## 7. Quick Start Checklist (for next time)

1. Create project folder
2. Create virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install packages: `pip install fastapi uvicorn <other-packages>`
5. Freeze dependencies: `pip freeze > requirements.txt`
6. Write your app in `main.py`
7. Put HTML in `templates/`
8. Run: `uvicorn main:app --host 0.0.0.0 --port 8042`
9. If remote: use Gateway or SSH tunnel for laptop access
10. If network-wide: set up Windows port proxy + firewall rule
