"""Hardware auto-tuning for optimal performance"""
from typing import Dict, Any
from .scan import scan_hardware, get_optimal_settings
from core.config import save_config, load_config
import json

def apply_autotune() -> Dict[str, Any]:
    """Apply automatic hardware optimization"""
    try:
        # Scan current hardware
        hardware = scan_hardware()
        optimal_settings = get_optimal_settings()
        
        # Update configurations
        results = {
            "hardware_detected": hardware,
            "applied_settings": optimal_settings,
            "success": True,
            "message": "Auto-tuning applied successfully"
        }
        
        # Update RAG configuration
        rag_config = load_config("rag")
        if optimal_settings.get("use_gpu"):
            rag_config["retrievers"]["colbert"]["enabled"] = True
            rag_config["retrievers"]["colbert"]["batch_size"] = optimal_settings.get("gpu_batch_size", 8)
        else:
            # Disable intensive operations on CPU-only systems
            rag_config["retrievers"]["colbert"]["enabled"] = False
        
        save_config("rag", rag_config)
        
        # Update expert configuration
        expert_config = load_config("experts")
        memory_gb = hardware["memory"].get("total_gb", 4)
        
        # Adjust expert settings based on available memory
        if memory_gb < 8:
            # Disable resource-intensive experts on low-memory systems
            for expert_name in ["vision", "datascience"]:
                if expert_name in expert_config:
                    expert_config[expert_name]["enabled"] = False
                    results["applied_settings"][f"{expert_name}_disabled"] = "Low memory"
        
        save_config("experts", expert_config)
        
        # Update HiveMind configuration
        hivemind_config = load_config("hivemind")
        cpu_cores = hardware["cpu"].get("cores_logical", 1)
        hivemind_config["execution"]["max_concurrent_experts"] = min(cpu_cores, 5)
        save_config("hivemind", hivemind_config)
        
        return results
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Auto-tuning failed"
        }

def get_autotune_recommendations() -> Dict[str, Any]:
    """Get recommendations without applying them"""
    hardware = scan_hardware()
    optimal_settings = get_optimal_settings()
    
    recommendations = {
        "hardware_summary": {
            "cpu_cores": hardware["cpu"].get("cores_logical", "Unknown"),
            "memory_gb": hardware["memory"].get("total_gb", "Unknown"),
            "gpu_available": hardware["gpu"]["cuda_available"],
            "gpu_count": len(hardware["gpu"]["gpus"])
        },
        "recommended_settings": optimal_settings,
        "performance_notes": []
    }
    
    # Add performance notes
    memory_gb = hardware["memory"].get("total_gb", 0)
    if memory_gb < 8:
        recommendations["performance_notes"].append(
            "Low memory detected. Consider upgrading RAM for better performance."
        )
    
    if not hardware["gpu"]["cuda_available"]:
        recommendations["performance_notes"].append(
            "No CUDA GPU detected. Some features will run on CPU only."
        )
    
    cpu_cores = hardware["cpu"].get("cores_logical", 1)
    if cpu_cores < 4:
        recommendations["performance_notes"].append(
            "Limited CPU cores. Parallel processing will be restricted."
        )
    
    return recommendations
