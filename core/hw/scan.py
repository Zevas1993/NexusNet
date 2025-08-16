"""Hardware scanning and detection"""
import psutil
import platform
from typing import Dict, Any, Optional
import subprocess
import sys

def scan_hardware() -> Dict[str, Any]:
    """Scan and detect available hardware"""
    result = {
        "cpu": scan_cpu(),
        "memory": scan_memory(),
        "gpu": scan_gpu(),
        "platform": scan_platform()
    }
    return result

def scan_cpu() -> Dict[str, Any]:
    """Scan CPU information"""
    try:
        cpu_info = {
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency": psutil.cpu_freq(),
            "usage_percent": psutil.cpu_percent(interval=1),
            "architecture": platform.machine()
        }
        
        # Additional CPU details on Linux
        if platform.system() == "Linux":
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'model name' in cpuinfo:
                        model_line = [line for line in cpuinfo.split('\n') if 'model name' in line][0]
                        cpu_info['model'] = model_line.split(':')[1].strip()
            except:
                pass
        
        return cpu_info
    except Exception as e:
        return {"error": str(e)}

def scan_memory() -> Dict[str, Any]:
    """Scan memory information"""
    try:
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "usage_percent": mem.percent
        }
    except Exception as e:
        return {"error": str(e)}

def scan_gpu() -> Dict[str, Any]:
    """Scan GPU information"""
    gpu_info = {"gpus": [], "cuda_available": False}
    
    # Check PyTorch CUDA
    try:
        import torch
        gpu_info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            gpu_info["cuda_devices"] = torch.cuda.device_count()
            for i in range(torch.cuda.device_count()):
                gpu_info["gpus"].append({
                    "id": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_gb": round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                })
    except ImportError:
        pass
    
    # Try nvidia-ml-py3
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            if not any(gpu['name'] == name for gpu in gpu_info["gpus"]):
                gpu_info["gpus"].append({
                    "id": i,
                    "name": name,
                    "memory_gb": round(memory_info.total / (1024**3), 2),
                    "memory_used_gb": round(memory_info.used / (1024**3), 2),
                    "memory_free_gb": round(memory_info.free / (1024**3), 2)
                })
    except (ImportError, Exception):
        pass
    
    return gpu_info

def scan_platform() -> Dict[str, Any]:
    """Scan platform information"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version
    }

def get_optimal_settings() -> Dict[str, Any]:
    """Get optimal settings based on hardware"""
    hw = scan_hardware()
    settings = {}
    
    # CPU settings
    cpu_cores = hw["cpu"].get("cores_logical", 1)
    settings["num_threads"] = max(1, cpu_cores - 1)  # Leave one core free
    
    # Memory settings
    memory_gb = hw["memory"].get("total_gb", 4)
    if memory_gb >= 16:
        settings["batch_size"] = 8
        settings["context_length"] = 4096
    elif memory_gb >= 8:
        settings["batch_size"] = 4
        settings["context_length"] = 2048
    else:
        settings["batch_size"] = 1
        settings["context_length"] = 1024
    
    # GPU settings
    if hw["gpu"]["cuda_available"]:
        settings["use_gpu"] = True
        gpu_memory = max((gpu.get("memory_gb", 0) for gpu in hw["gpu"]["gpus"]), default=0)
        if gpu_memory >= 8:
            settings["gpu_batch_size"] = 16
            settings["use_half_precision"] = False
        elif gpu_memory >= 4:
            settings["gpu_batch_size"] = 8
            settings["use_half_precision"] = True
        else:
            settings["gpu_batch_size"] = 4
            settings["use_half_precision"] = True
    else:
        settings["use_gpu"] = False
    
    return settings
