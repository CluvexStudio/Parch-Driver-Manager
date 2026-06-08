<div align="center">

# Parch Driver Manager

A modern driver management tool for Arch-based distributions built with Python, GTK4, and Libadwaita.

![GTK4](https://img.shields.io/badge/GTK4-3D3D3D?style=flat-square&logo=gtk&logoColor=white)
![Libadwaita](https://img.shields.io/badge/Libadwaita-3584E4?style=flat-square)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square)

</div>

---

## Features

- **Automatic Hardware Detection** - Detects GPUs, network cards, audio devices, and Bluetooth controllers via lspci
- **Driver Management** - Install, remove, enable, and disable hardware drivers with secure privilege escalation
- **System Information** - View detailed hardware and system configuration including CPU, memory, GPU, kernel version, and more
- **Multi-language Support** - English and Persian (فارسی) interface with persistent language settings
- **Theme Selection** - Light, dark, and auto theme modes with instant switching
- **Confirmation Dialogs** - Safety prompts before critical operations
- **Progress Indicators** - Visual feedback during driver installation and removal
- **Operation Logging** - Real-time logs for troubleshooting and monitoring
- **Modern UI** - Clean, responsive interface following GNOME HIG guidelines

---

## Requirements

- Python 3.9 or higher
- GTK4
- Libadwaita
- PyGObject
- Polkit (pkexec)
- pacman
- pciutils (lspci)

---

## Installation

### System Dependencies

On Arch-based distributions:

```bash
sudo pacman -S gtk4 libadwaita python-gobject pciutils polkit
```

### Clone and Run

```bash
git clone https://github.com/parchlinux/Parch-Driver-Manager.git
cd Parch-Driver-Manager
pip install -r requirements.txt
python main.py
```

---

## Usage

Launch the application and navigate through the sidebar to manage different hardware categories. Select a driver profile and use the action buttons to install, remove, enable, or disable drivers. Administrative privileges will be requested when needed.

---

## Architecture

```
.
├── main.py           # Application entry point
├── ui.py             # GTK4/Libadwaita interface
├── manager.py        # Driver management logic
├── profiles.py       # Driver profile definitions
├── backend.py        # Privileged command execution
└── system_prober.py  # Hardware detection
```

---

## License

GPL-3.0 - See LICENSE file for details.

<div align="center">
Made for Parch Linux
</div>
