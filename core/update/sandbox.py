import subprocess, os, hashlib, tempfile
from pathlib import Path
from typing import Dict, Any, Optional

class UpdateSandbox:
    def __init__(self, sandbox_dir: str = "runtime/state/sandbox"):
        self.sandbox_dir = Path(sandbox_dir)
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.trusted_keys = []  # ed25519 public keys for signature verification
    
    def verify_update(self, update_file: str, signature_file: str, expected_hash: str) -> Dict[str, Any]:
        """Verify update package integrity and authenticity"""
        update_path = Path(update_file)
        signature_path = Path(signature_file)
        
        if not update_path.exists() or not signature_path.exists():
            return {'valid': False, 'error': 'Missing files'}
        
        # Verify hash
        actual_hash = self._compute_hash(update_path)
        if actual_hash != expected_hash:
            return {'valid': False, 'error': 'Hash mismatch'}
        
        # Verify signature (simplified - would use cryptography library)
        signature_valid = self._verify_signature(update_path, signature_path)
        
        return {
            'valid': signature_valid,
            'hash_match': True,
            'signature_valid': signature_valid
        }
    
    def _compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _verify_signature(self, update_path: Path, signature_path: Path) -> bool:
        """Verify ed25519 signature (simplified implementation)"""
        # In production, use proper cryptographic verification
        return True  # Placeholder
    
    def apply_update(self, update_package: str) -> Dict[str, Any]:
        """Apply update in sandboxed environment"""
        try:
            # Extract update package to sandbox
            with tempfile.TemporaryDirectory(dir=self.sandbox_dir) as temp_dir:
                extract_cmd = ['unzip', '-q', update_package, '-d', temp_dir]
                result = subprocess.run(extract_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return {'success': False, 'error': 'Failed to extract update'}
                
                # Run update script in sandbox
                update_script = Path(temp_dir) / 'update.sh'
                if update_script.exists():
                    script_result = subprocess.run(
                        ['bash', str(update_script)],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    return {
                        'success': script_result.returncode == 0,
                        'output': script_result.stdout,
                        'error': script_result.stderr if script_result.returncode != 0 else None
                    }
                
                return {'success': False, 'error': 'No update script found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}