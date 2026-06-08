import subprocess
import os
from typing import List, Dict, Any, Tuple

class CommandError(Exception):
    def __init__(self, cmd: List[str], returncode: int, stdout: str, stderr: str):
        super().__init__(f"Command failed: {' '.join(cmd)} (code {returncode})")
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

def debug_log(msg: str) -> None:
    print(f"[ParchDM] {msg}")

class SystemProber:
    @staticmethod
    def run_command(command: List[str], check: bool = False) -> Tuple[int, str, str]:
        debug_log(f"Running command: {' '.join(command)}")
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc.communicate()
        if check and proc.returncode != 0:
            raise CommandError(command, proc.returncode, out, err)
        return proc.returncode, out, err

    @staticmethod
    def get_lspci() -> str:
        code, out, err = SystemProber.run_command(["lspci", "-nnk"])
        if code != 0:
            debug_log(f"lspci failed: {err.strip()}")
            return ""
        return out

    @staticmethod
    def get_hardware_devices() -> List[Dict[str, Any]]:
        lspci = SystemProber.get_lspci()
        devices = []
        current_dev = {}
        
        for line in lspci.splitlines():
            if not line.startswith('\t') and not line.startswith(' ') and line.strip():
                if current_dev:
                    devices.append(current_dev)
                
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    pci_id = parts[0].split(' ')[0]
                    device_desc = parts[1]
                    device_type = parts[0].split(': ')[0] if ': ' in parts[0] else ''
                    
                    current_dev = {
                        'pci': pci_id,
                        'name': device_desc,
                        'category': 'Other',
                        'driver': None,
                        'modules': []
                    }
                    
                    lower_line = line.lower()
                    lower_type = device_type.lower()
                    
                    if 'vga compatible controller' in lower_line or '3d controller' in lower_line or 'display controller' in lower_line:
                        current_dev['category'] = 'GPU'
                    elif 'audio device' in lower_line or 'audio controller' in lower_line or 'multimedia audio' in lower_line:
                        current_dev['category'] = 'Audio'
                    elif 'network controller' in lower_line or 'ethernet controller' in lower_line or 'wireless' in lower_line:
                        current_dev['category'] = 'Network'
                    elif 'bluetooth' in lower_line:
                        current_dev['category'] = 'Bluetooth'
            else:
                line = line.strip()
                if line.startswith('Kernel driver in use:'):
                    driver = line.split(':', 1)[1].strip()
                    current_dev['driver'] = driver
                elif line.startswith('Kernel modules:'):
                    modules_str = line.split(':', 1)[1].strip()
                    current_dev['modules'] = [m.strip() for m in modules_str.split(',')]
        
        if current_dev:
            devices.append(current_dev)
            
        return devices

    @staticmethod
    def get_gpu_info() -> Dict[str, Any]:
        lspci = SystemProber.get_lspci()
        vendor = "Unknown"
        gpu_model = ""
        gpu_line = ""

        for line in lspci.splitlines():
            lower = line.lower()
            if ("vga compatible controller" in lower or 
                "3d controller" in lower or 
                "display controller" in lower):
                gpu_line = line
                
                if "intel corporation" in lower or "[8086:" in lower:
                    vendor = "Intel"
                elif "nvidia" in lower or "[10de:" in lower:
                    vendor = "NVIDIA"
                elif ("amd" in lower or "ati" in lower or 
                      "advanced micro devices" in lower or "[1002:" in lower):
                    vendor = "AMD"
                
                if ':' in line and ']' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        gpu_model = parts[1].split('[')[0].strip()
                break

        return {"vendor": vendor, "model": gpu_model, "raw": lspci}

    @staticmethod
    def get_session_type() -> str:
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type in ("wayland", "x11"):
            return session_type
        if os.environ.get("WAYLAND_DISPLAY"):
            return "wayland"
        if os.environ.get("DISPLAY"):
            return "x11"
        return "unknown"

    @staticmethod
    def is_hybrid_graphics() -> bool:
        devices = SystemProber.get_hardware_devices()
        gpus = [d for d in devices if d['category'] == 'GPU']
        
        if len(gpus) < 2:
            return False
        
        vendors = set()
        for gpu in gpus:
            name_lower = gpu['name'].lower()
            if 'nvidia' in name_lower:
                vendors.add('nvidia')
            elif 'intel' in name_lower:
                vendors.add('intel')
            elif 'amd' in name_lower or 'ati' in name_lower or 'radeon' in name_lower:
                vendors.add('amd')
        
        return len(vendors) >= 2

    @staticmethod
    def get_kernel_info() -> Dict[str, str]:
        code, out, err = SystemProber.run_command(["uname", "-r"])
        kernel_version = out.strip() if code == 0 else "Unknown"
        
        kernel_flavor = "default"
        if "-lts" in kernel_version:
            kernel_flavor = "lts"
        elif "-zen" in kernel_version:
            kernel_flavor = "zen"
        elif "-hardened" in kernel_version:
            kernel_flavor = "hardened"
        elif "-cachyos" in kernel_version:
            kernel_flavor = "cachyos"
        
        return {
            "version": kernel_version,
            "flavor": kernel_flavor
        }

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        info = {}
        
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        info['cpu'] = line.split(':', 1)[1].strip()
                        break
        except:
            info['cpu'] = "Unknown"
        
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        gb = round(kb / 1024 / 1024, 1)
                        info['memory'] = f"{gb} GB"
                        break
        except:
            info['memory'] = "Unknown"
        
        try:
            code, out, err = SystemProber.run_command(["hostnamectl", "hostname"])
            info['hostname'] = out.strip() if code == 0 else "Unknown"
        except:
            info['hostname'] = "Unknown"
        
        try:
            code, out, err = SystemProber.run_command(["hostnamectl"])
            for line in out.splitlines():
                if "Operating System:" in line:
                    info['os'] = line.split(':', 1)[1].strip()
                elif "Chassis:" in line:
                    chassis = line.split(':', 1)[1].strip()
                    info['chassis'] = chassis.split()[0] if chassis else "desktop"
                elif "Hardware Vendor:" in line:
                    info['vendor'] = line.split(':', 1)[1].strip()
                elif "Hardware Model:" in line:
                    info['model'] = line.split(':', 1)[1].strip()
        except:
            pass
        
        return info

    @staticmethod
    def has_secure_boot() -> bool:
        paths = [
            "/sys/firmware/efi/vars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c/data",
            "/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c"
        ]
        
        for path in paths:
            try:
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        data = f.read()
                        if len(data) >= 5:
                            return data[4] == 1
                        elif len(data) >= 1:
                            return data[0] == 1
            except Exception as e:
                debug_log(f"SecureBoot detection failed for {path}: {e}")
                continue
        
        return False

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        info = {}
        
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        info['cpu'] = line.split(':', 1)[1].strip()
                        break
        except:
            info['cpu'] = "Unknown"
        
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        gb = round(kb / 1024 / 1024, 1)
                        info['memory'] = f"{gb} GB"
                        break
        except:
            info['memory'] = "Unknown"
        
        try:
            code, out, err = SystemProber.run_command(["hostnamectl", "hostname"])
            info['hostname'] = out.strip() if code == 0 else "Unknown"
        except:
            info['hostname'] = "Unknown"
        
        try:
            code, out, err = SystemProber.run_command(["hostnamectl"])
            for line in out.splitlines():
                if "Operating System:" in line:
                    info['os'] = line.split(':', 1)[1].strip()
                elif "Chassis:" in line:
                    chassis = line.split(':', 1)[1].strip()
                    info['chassis'] = chassis.split()[0] if chassis else "desktop"
                elif "Hardware Vendor:" in line:
                    info['vendor'] = line.split(':', 1)[1].strip()
                elif "Hardware Model:" in line:
                    info['model'] = line.split(':', 1)[1].strip()
        except:
            pass
        
        return info
        
        for path in paths:
            try:
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        data = f.read()
                        if len(data) >= 5:
                            return data[4] == 1
                        elif len(data) >= 1:
                            return data[0] == 1
            except Exception as e:
                debug_log(f"SecureBoot detection failed for {path}: {e}")
                continue
        
        return False
