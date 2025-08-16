import json, gzip, pathlib
from typing import List, Dict

class DataPackager:
    def __init__(self, output_dir='runtime/state/packages'):
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def package(self, batch: List[Dict], name: str) -> str:
        """Package batch data into compressed format for training"""
        output_file = self.output_dir / f"{name}.jsonl.gz"
        
        with gzip.open(output_file, 'wt', encoding='utf-8') as f:
            for item in batch:
                f.write(json.dumps(item) + '\n')
        
        return str(output_file)
    
    def list_packages(self) -> List[str]:
        return [str(f) for f in self.output_dir.glob('*.jsonl.gz')]