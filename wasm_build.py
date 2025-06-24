#!/usr/bin/env python3
"""
WASM Compilation Setup for NexusNet
Enables compilation to WebAssembly for browser deployment.
"""

import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..utils.logging import setup_logger


class WASMCompiler:
    """Compiles NexusNet components to WebAssembly."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = setup_logger(f"{__name__}.WASMCompiler")
        
        # Compilation settings
        self.optimization_level = self.config.get("optimization_level", "O2")
        self.target_features = self.config.get("target_features", ["simd128", "bulk-memory"])
        self.memory_size = self.config.get("memory_size", "256MB")
        
        # Output settings
        self.output_dir = Path(self.config.get("output_dir", "./wasm_build"))
        self.output_dir.mkdir(exist_ok=True)
    
    def check_dependencies(self) -> bool:
        """Check if required WASM compilation tools are available."""
        required_tools = ["emcc", "python", "node"]
        
        for tool in required_tools:
            try:
                result = subprocess.run([tool, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    self.logger.error(f"Tool {tool} not available or not working")
                    return False
                else:
                    self.logger.info(f"Found {tool}: {result.stdout.strip().split()[0]}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.error(f"Tool {tool} not found")
                return False
        
        return True
    
    def prepare_python_environment(self) -> bool:
        """Prepare Python environment for WASM compilation."""
        try:
            # Create requirements for WASM build
            wasm_requirements = [
                "numpy",
                "torch",  # Note: PyTorch WASM support is limited
                "typing-extensions",
                "dataclasses; python_version<'3.7'"
            ]
            
            requirements_path = self.output_dir / "requirements_wasm.txt"
            with open(requirements_path, 'w') as f:
                f.write('\n'.join(wasm_requirements))
            
            self.logger.info(f"Created WASM requirements: {requirements_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare Python environment: {e}")
            return False
    
    def create_wasm_module(self, module_name: str, source_files: List[str]) -> bool:
        """Create a WASM module from Python source files."""
        try:
            # Create module directory
            module_dir = self.output_dir / module_name
            module_dir.mkdir(exist_ok=True)
            
            # Copy source files
            for source_file in source_files:
                source_path = Path(source_file)
                if source_path.exists():
                    dest_path = module_dir / source_path.name
                    with open(source_path, 'r') as src, open(dest_path, 'w') as dst:
                        dst.write(src.read())
                    self.logger.info(f"Copied {source_file} to {dest_path}")
            
            # Create module entry point
            entry_point = module_dir / f"{module_name}_entry.py"
            self._create_entry_point(entry_point, module_name)
            
            # Create build script
            build_script = module_dir / "build.sh"
            self._create_build_script(build_script, module_name, module_dir)
            
            self.logger.info(f"Created WASM module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create WASM module {module_name}: {e}")
            return False
    
    def _create_entry_point(self, entry_path: Path, module_name: str):
        """Create entry point for WASM module."""
        entry_code = f'''#!/usr/bin/env python3
"""
WASM Entry Point for {module_name}
"""

import sys
import json
from typing import Dict, Any

# Simplified imports for WASM compatibility
try:
    import numpy as np
except ImportError:
    # Fallback for environments without numpy
    class MockNumpy:
        def array(self, data):
            return data
        def zeros(self, shape):
            return [0] * (shape if isinstance(shape, int) else shape[0])
    np = MockNumpy()

class {module_name.title()}WASM:
    """WASM-compatible version of {module_name}."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the module."""
        try:
            # Simplified initialization for WASM
            self.initialized = True
            return True
        except Exception as e:
            print(f"Initialization failed: {{e}}")
            return False
    
    def process(self, input_data: Any) -> Any:
        """Process input data."""
        if not self.initialized:
            self.initialize()
        
        # Simplified processing for WASM
        try:
            # Basic processing logic
            if isinstance(input_data, str):
                return {{"output": f"Processed: {{input_data}}", "type": "text"}}
            elif isinstance(input_data, (list, tuple)):
                return {{"output": len(input_data), "type": "count"}}
            else:
                return {{"output": str(input_data), "type": "string"}}
        except Exception as e:
            return {{"error": str(e)}}
    
    def get_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {{
            "name": "{module_name}",
            "version": "1.0.0-wasm",
            "initialized": self.initialized,
            "capabilities": ["basic_processing"]
        }}

# Global instance
_module_instance = None

def get_module():
    """Get module instance."""
    global _module_instance
    if _module_instance is None:
        _module_instance = {module_name.title()}WASM()
    return _module_instance

# WASM-compatible API functions
def wasm_initialize(config_json: str = "{{}}") -> str:
    """Initialize module from WASM."""
    try:
        config = json.loads(config_json)
        module = get_module()
        success = module.initialize()
        return json.dumps({{"success": success}})
    except Exception as e:
        return json.dumps({{"success": False, "error": str(e)}})

def wasm_process(input_json: str) -> str:
    """Process input from WASM."""
    try:
        input_data = json.loads(input_json)
        module = get_module()
        result = module.process(input_data)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({{"error": str(e)}})

def wasm_get_info() -> str:
    """Get module info from WASM."""
    try:
        module = get_module()
        info = module.get_info()
        return json.dumps(info)
    except Exception as e:
        return json.dumps({{"error": str(e)}})

if __name__ == "__main__":
    # Test the module
    module = get_module()
    module.initialize()
    
    test_input = "Hello, WASM!"
    result = module.process(test_input)
    print(f"Test result: {{result}}")
'''
        
        with open(entry_path, 'w') as f:
            f.write(entry_code)
    
    def _create_build_script(self, script_path: Path, module_name: str, module_dir: Path):
        """Create build script for WASM compilation."""
        build_script = f'''#!/bin/bash
# WASM Build Script for {module_name}

set -e

echo "Building {module_name} for WASM..."

# Set up environment
export EMCC_DEBUG=1
export PYTHONPATH="{module_dir}"

# Compile to WASM
emcc \\
    --bind \\
    -s WASM=1 \\
    -s EXPORTED_FUNCTIONS="['_main']" \\
    -s EXPORTED_RUNTIME_METHODS="['ccall', 'cwrap']" \\
    -s ALLOW_MEMORY_GROWTH=1 \\
    -s INITIAL_MEMORY={self._parse_memory_size()} \\
    -s MODULARIZE=1 \\
    -s EXPORT_NAME="'{module_name}Module'" \\
    -{self.optimization_level} \\
    {' '.join([f'-s USE_{feature.upper()}=1' for feature in self.target_features])} \\
    -o {module_name}.js \\
    {module_name}_entry.py

echo "WASM build completed: {module_name}.js, {module_name}.wasm"

# Create HTML wrapper
cat > {module_name}.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>{module_name} WASM Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .input-group {{ margin: 10px 0; }}
        .output {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        button {{ padding: 10px 20px; margin: 5px; cursor: pointer; }}
        input, textarea {{ width: 100%; padding: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{module_name} WASM Demo</h1>
        
        <div class="input-group">
            <label>Input Data:</label>
            <textarea id="inputData" rows="3" placeholder="Enter input data...">Hello, WASM!</textarea>
        </div>
        
        <div class="input-group">
            <button onclick="initializeModule()">Initialize</button>
            <button onclick="processInput()">Process</button>
            <button onclick="getModuleInfo()">Get Info</button>
        </div>
        
        <div class="output">
            <h3>Output:</h3>
            <pre id="output">Ready to process...</pre>
        </div>
    </div>

    <script src="{module_name}.js"></script>
    <script>
        let moduleInstance = null;
        
        {module_name}Module().then(function(Module) {{
            moduleInstance = Module;
            document.getElementById('output').textContent = 'Module loaded successfully!';
        }}).catch(function(err) {{
            document.getElementById('output').textContent = 'Failed to load module: ' + err;
        }});
        
        function initializeModule() {{
            if (!moduleInstance) {{
                document.getElementById('output').textContent = 'Module not loaded yet';
                return;
            }}
            
            try {{
                const result = moduleInstance.ccall('wasm_initialize', 'string', ['string'], ['{{}}']);
                document.getElementById('output').textContent = 'Initialize result: ' + result;
            }} catch (err) {{
                document.getElementById('output').textContent = 'Initialize error: ' + err;
            }}
        }}
        
        function processInput() {{
            if (!moduleInstance) {{
                document.getElementById('output').textContent = 'Module not loaded yet';
                return;
            }}
            
            const inputData = document.getElementById('inputData').value;
            
            try {{
                const inputJson = JSON.stringify(inputData);
                const result = moduleInstance.ccall('wasm_process', 'string', ['string'], [inputJson]);
                document.getElementById('output').textContent = 'Process result: ' + result;
            }} catch (err) {{
                document.getElementById('output').textContent = 'Process error: ' + err;
            }}
        }}
        
        function getModuleInfo() {{
            if (!moduleInstance) {{
                document.getElementById('output').textContent = 'Module not loaded yet';
                return;
            }}
            
            try {{
                const result = moduleInstance.ccall('wasm_get_info', 'string', [], []);
                document.getElementById('output').textContent = 'Module info: ' + result;
            }} catch (err) {{
                document.getElementById('output').textContent = 'Info error: ' + err;
            }}
        }}
    </script>
</body>
</html>
EOF

echo "Created HTML demo: {module_name}.html"
'''
        
        with open(script_path, 'w') as f:
            f.write(build_script)
        
        # Make script executable
        os.chmod(script_path, 0o755)
    
    def _parse_memory_size(self) -> str:
        """Parse memory size to bytes."""
        size_str = self.memory_size.upper()
        if size_str.endswith('MB'):
            return str(int(size_str[:-2]) * 1024 * 1024)
        elif size_str.endswith('KB'):
            return str(int(size_str[:-2]) * 1024)
        else:
            return "268435456"  # Default 256MB
    
    def compile_module(self, module_name: str) -> bool:
        """Compile a WASM module."""
        try:
            module_dir = self.output_dir / module_name
            build_script = module_dir / "build.sh"
            
            if not build_script.exists():
                self.logger.error(f"Build script not found: {build_script}")
                return False
            
            # Run build script
            result = subprocess.run(
                ["bash", str(build_script)],
                cwd=module_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully compiled {module_name} to WASM")
                self.logger.debug(f"Build output: {result.stdout}")
                return True
            else:
                self.logger.error(f"WASM compilation failed for {module_name}")
                self.logger.error(f"Build error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"WASM compilation timeout for {module_name}")
            return False
        except Exception as e:
            self.logger.error(f"WASM compilation error for {module_name}: {e}")
            return False
    
    def create_package_json(self) -> bool:
        """Create package.json for npm distribution."""
        try:
            package_data = {
                "name": "nexusnet-wasm",
                "version": "1.0.0",
                "description": "NexusNet WebAssembly modules",
                "main": "index.js",
                "files": [
                    "*.js",
                    "*.wasm",
                    "*.html",
                    "README.md"
                ],
                "scripts": {
                    "test": "node test.js",
                    "serve": "python -m http.server 8080"
                },
                "keywords": [
                    "webassembly",
                    "machine-learning",
                    "neural-networks",
                    "ai"
                ],
                "author": "NexusNet Team",
                "license": "MIT",
                "repository": {
                    "type": "git",
                    "url": "https://github.com/nexusnet/nexusnet-wasm.git"
                }
            }
            
            package_path = self.output_dir / "package.json"
            with open(package_path, 'w') as f:
                json.dump(package_data, f, indent=2)
            
            self.logger.info(f"Created package.json: {package_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create package.json: {e}")
            return False
    
    def create_index_js(self) -> bool:
        """Create main index.js file."""
        try:
            index_content = '''/**
 * NexusNet WASM Package
 * Main entry point for WebAssembly modules
 */

class NexusNetWASM {
    constructor() {
        this.modules = new Map();
        this.initialized = false;
    }
    
    async loadModule(moduleName) {
        try {
            // Dynamic import of the module
            const moduleFactory = await import(`./${moduleName}.js`);
            const moduleInstance = await moduleFactory.default();
            
            this.modules.set(moduleName, moduleInstance);
            console.log(`Loaded module: ${moduleName}`);
            
            return moduleInstance;
        } catch (error) {
            console.error(`Failed to load module ${moduleName}:`, error);
            throw error;
        }
    }
    
    getModule(moduleName) {
        return this.modules.get(moduleName);
    }
    
    async initialize(config = {}) {
        try {
            // Initialize all loaded modules
            for (const [name, module] of this.modules) {
                if (module.ccall) {
                    const result = module.ccall('wasm_initialize', 'string', ['string'], [JSON.stringify(config)]);
                    console.log(`Initialized ${name}:`, result);
                }
            }
            
            this.initialized = true;
            return true;
        } catch (error) {
            console.error('Initialization failed:', error);
            return false;
        }
    }
    
    async process(moduleName, inputData) {
        const module = this.getModule(moduleName);
        if (!module) {
            throw new Error(`Module not loaded: ${moduleName}`);
        }
        
        try {
            const inputJson = JSON.stringify(inputData);
            const result = module.ccall('wasm_process', 'string', ['string'], [inputJson]);
            return JSON.parse(result);
        } catch (error) {
            console.error(`Processing failed for ${moduleName}:`, error);
            throw error;
        }
    }
    
    getModuleInfo(moduleName) {
        const module = this.getModule(moduleName);
        if (!module) {
            throw new Error(`Module not loaded: ${moduleName}`);
        }
        
        try {
            const result = module.ccall('wasm_get_info', 'string', [], []);
            return JSON.parse(result);
        } catch (error) {
            console.error(`Failed to get info for ${moduleName}:`, error);
            throw error;
        }
    }
    
    listModules() {
        return Array.from(this.modules.keys());
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NexusNetWASM;
} else if (typeof window !== 'undefined') {
    window.NexusNetWASM = NexusNetWASM;
}

export default NexusNetWASM;
'''
            
            index_path = self.output_dir / "index.js"
            with open(index_path, 'w') as f:
                f.write(index_content)
            
            self.logger.info(f"Created index.js: {index_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create index.js: {e}")
            return False
    
    def build_all(self, modules: List[str]) -> bool:
        """Build all specified modules."""
        success_count = 0
        
        # Check dependencies first
        if not self.check_dependencies():
            self.logger.error("Missing required dependencies for WASM compilation")
            return False
        
        # Prepare environment
        if not self.prepare_python_environment():
            self.logger.error("Failed to prepare Python environment")
            return False
        
        # Build each module
        for module_name in modules:
            if self.compile_module(module_name):
                success_count += 1
            else:
                self.logger.error(f"Failed to build module: {module_name}")
        
        # Create package files
        self.create_package_json()
        self.create_index_js()
        
        self.logger.info(f"Built {success_count}/{len(modules)} modules successfully")
        return success_count == len(modules)


def create_wasm_build_config():
    """Create default WASM build configuration."""
    config = {
        "optimization_level": "O2",
        "target_features": ["simd128", "bulk-memory"],
        "memory_size": "256MB",
        "output_dir": "./wasm_build",
        "modules": [
            "encoder",
            "processor", 
            "attention",
            "compression"
        ]
    }
    
    config_path = Path("wasm_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created WASM build configuration: {config_path}")
    return config


def main():
    """Main WASM build function."""
    # Create default config if it doesn't exist
    config_path = Path("wasm_config.json")
    if not config_path.exists():
        config = create_wasm_build_config()
    else:
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Create compiler
    compiler = WASMCompiler(config)
    
    # Create modules
    modules = config.get("modules", ["encoder"])
    for module_name in modules:
        # For demo, create with empty source files
        compiler.create_wasm_module(module_name, [])
    
    # Build all modules
    success = compiler.build_all(modules)
    
    if success:
        print("WASM build completed successfully!")
        print(f"Output directory: {compiler.output_dir}")
        print("To test, run: python -m http.server 8080")
    else:
        print("WASM build failed!")


if __name__ == "__main__":
    main()

