# QR Studio

A local network QR code generator — no subscriptions, no watermarks, no data leaving your home.

## Setup

```bash
cd qr-studio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8042
```

Then open in your browser:
- **From your WSL machine:** http://localhost:8042
- **From other devices on your network:** http://<your-pc-ip>:8042

### Finding your IP

In WSL, your Windows host IP is what other devices will use. From PowerShell:

```powershell
ipconfig
```

Look for your Wi-Fi adapter's IPv4 address (something like `192.168.1.xxx`).

### WSL port forwarding (if needed)

If devices on your network can't reach the WSL server, you may need to forward the port from Windows to WSL. In an **admin PowerShell**:

```powershell
netsh interface portproxy add v4tov4 listenport=8042 listenaddress=0.0.0.0 connectport=8042 connectaddress=$(wsl hostname -I | ForEach-Object { $_.Trim() })
```

And allow it through Windows Firewall:

```powershell
New-NetFirewallRule -DisplayName "QR Studio" -Direction Inbound -LocalPort 8042 -Protocol TCP -Action Allow
```

## Features

- **Live preview** as you type
- **PNG & SVG downloads** at high resolution
- **9 colour presets** plus custom colour pickers
- **4 error correction levels** (L/M/Q/H)
- Works with URLs, plain text, Wi-Fi configs, vCards — anything you can encode in a QR code
- Runs entirely on your local network — nothing is sent to the internet

## What I Learned

- Building and documenting FastAPI endpoints for file/image responses
- Validating and constraining API inputs (`Query` defaults and bounds)
- Connecting a lightweight frontend to backend generation endpoints
- Handling WSL networking details for LAN access (port proxy + firewall)
- Packaging a Python project to be reproducible with `requirements.txt`

## Project Structure

```
qr-studio/
├── main.py             # FastAPI backend
├── templates/
│   └── index.html      # Frontend (served by FastAPI)
├── requirements.txt
└── README.md
```
