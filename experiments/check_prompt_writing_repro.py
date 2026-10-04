import sys
import numpy as np
from PIL import Image
from pathlib import Path

def main():
    target_dir = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_prompt_writing")
    repro_path = target_dir / "REPRO_V1_Original_baseline_krea2_seed3141592_00001_.png"
    
    # benchmark_prompt_order keeps its images in the folder root; renders/ is empty (fixed by Claude 2026-10-04)
    ref_dir = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_prompt_order")
    ref_path = ref_dir / "V1_Original_baseline_krea2_seed3141592_00001_.png"
    
    if not repro_path.exists():
        print(f"FAIL: REPRO image not found at {repro_path}")
        sys.exit(1)
        
    if not ref_path.exists():
        print(f"FAIL: Reference image not found at {ref_path}")
        sys.exit(1)
        
    try:
        img_repro = np.array(Image.open(repro_path).convert("RGB"), dtype=np.int16)
        img_ref = np.array(Image.open(ref_path).convert("RGB"), dtype=np.int16)
    except Exception as e:
        print(f"FAIL: Error loading images: {e}")
        sys.exit(1)
        
    if img_repro.shape != img_ref.shape:
        print(f"FAIL: Shape mismatch! REPRO {img_repro.shape} vs REF {img_ref.shape}")
        sys.exit(1)
        
    diff = np.abs(img_repro - img_ref)
    max_diff = np.max(diff)
    
    if max_diff == 0:
        print(f"PASS: Images are exactly pixel-identical (max diff: {max_diff})")
        sys.exit(0)
    else:
        print(f"FAIL: Images are NOT identical! Max absolute difference: {max_diff}")
        sys.exit(1)

if __name__ == '__main__':
    main()
