import os
import glob
import re

def main():
    html_file = r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\index.html"
    base_dir = r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img"
    
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    benchmarks = set(re.findall(r"benchmark_[a-zA-Z0-9_]+", content))
    
    total_images = 0
    dirs_found = 0
    
    for b in benchmarks:
        d1 = os.path.join(base_dir, b)
        d2 = os.path.join(base_dir, b, "renders")
        
        found = False
        for target in [d1, d2]:
            if os.path.exists(target):
                images = glob.glob(os.path.join(target, "*.png"))
                if len(images) > 0:
                    print(f"{b}: {len(images)} images")
                    total_images += len(images)
                    dirs_found += 1
                    found = True
                    break
                    
    print(f"\nFound {dirs_found} benchmark directories with {total_images} total images.")

if __name__ == "__main__":
    main()
