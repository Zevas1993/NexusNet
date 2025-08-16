import psutil, subprocess, platform
from typing import Dict, Any, List

class HardwareScanner:
    def __init__(self):
        self.specs = {}
    
    def scan_system(self) -> Dict[str, Any]:
        """Comprehensive system scan"""
        return {
            'cpu': self._scan_cpu(),
            'memory': self._scan_memory(),
            'gpu': self._scan_gpu(),
            'storage': self._scan_storage(),
            'platform': self._scan_platform()
        }
    
    def _scan_cpu(self) -> Dict[str, Any]:
        return {
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'usage': psutil.cpu_percent(interval=1)
        }
    
    def _scan_memory(self) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used
        }
    
    def _scan_gpu(self) -> List[Dict[str, Any]]:
        gpus = []
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    gpus.append({
                        'name': props.name,
                        'memory': props.total_memory,
                        'compute_capability': f"{props.major}.{props.minor}"
                    })
        except ImportError:
            pass
        return gpus
    
    def _scan_storage(self) -> List[Dict[str, Any]]:
        disks = []
        for disk in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                disks.append({
                    'device': disk.device,
                    'mountpoint': disk.mountpoint,
                    'fstype': disk.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free
                })
            except PermissionError:
                pass
        return disks
    
    def _scan_platform(self) -> Dict[str, str]:
        return {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }