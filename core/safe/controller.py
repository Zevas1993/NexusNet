
import os, time, json
import psutil

def gpu_info():
    try:
        import pynvml
        pynvml.nvmlInit()
        h=pynvml.nvmlDeviceGetHandleByIndex(0)
        mem=pynvml.nvmlDeviceGetMemoryInfo(h)
        temp=int(pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU))
        return {"vram_used": int(mem.used/1048576), "vram_total": int(mem.total/1048576), "temp": temp}
    except Exception:
        return None

def advise(vram_high_pct:int=92, cpu_max:int=88, gpu_max:int=84)->dict:
    cpu_temp = psutil.sensors_temperatures().get("coretemp",[{"current":0}])[0]["current"] if hasattr(psutil,"sensors_temperatures") else 0
    g=gpu_info()
    vram_pct = int(g["vram_used"]*100/max(g["vram_total"],1)) if g else 0
    gpu_temp = g["temp"] if g else 0
    risk = any([cpu_temp>cpu_max, gpu_temp>gpu_max, vram_pct>vram_high_pct])
    action="resume"
    if risk and vram_pct>vram_high_pct: action="throttle"
    if risk and (gpu_temp>gpu_max or cpu_temp>cpu_max): action="pause"
    return {"risk": risk, "vram_pct": vram_pct, "cpu_temp": cpu_temp, "gpu_temp": gpu_temp, "action": action}
