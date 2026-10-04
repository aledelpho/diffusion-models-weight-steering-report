import csv
import urllib.parse
from pathlib import Path

def main():
    data_dir = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\data")
    docs_dir = Path(r"C:\Users\aless\Desktop\diffusion-models-weight-steering-report\docs")
    target_dir = Path(r"C:\StabilityMatrix-win-x64\Data\Images\Text2Img\benchmark_prompt_writing")
    
    plan = []
    with open(data_dir / 'prompt_writing_plan.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['type'] != 'repro':
                plan.append(row)
                
    arms = set()
    for row in plan:
        if row['cond_id'] != 'baseline':
            arms.add(row['cond_id'])
    
    arms = sorted(list(arms))
    subjects = ['S1', 'S2']
    writings = ['W1', 'W2', 'W3', 'W4', 'C1']
    
    html = []
    html.append("<html><head><style>")
    html.append("body { font-family: sans-serif; background: #111; color: #eee; margin: 20px; }")
    html.append("img { width: 100%; max-width: 256px; height: auto; }")
    html.append("table { border-collapse: collapse; margin-bottom: 40px; }")
    html.append("th, td { border: 1px solid #444; padding: 10px; text-align: center; }")
    html.append("th { background: #222; }")
    html.append(".baseline { color: #888; }")
    html.append(".arm { color: #fff; font-weight: bold; }")
    html.append("</style></head><body>")
    html.append("<h1>Prompt Writing Eye Sheets</h1>")
    
    for arm in arms:
        html.append(f"<hr><h2>Arm: {arm}</h2>")
        
        for subj in subjects:
            html.append(f"<h3>Subject: {subj}</h3>")
            html.append("<table>")
            html.append("<tr><th>Writing</th><th>Baseline (Seed 1)</th><th>Arm (Seed 1)</th><th>Baseline (Seed 2)</th><th>Arm (Seed 2)</th></tr>")
            
            for w in writings:
                pid_prefix = f"{subj}_{w}"
                
                b1, a1, b2, a2 = None, None, None, None
                for row in plan:
                    if row['prompt_id'].startswith(pid_prefix):
                        if row['cond_id'] == 'baseline':
                            if row['base_seed'] == '3141592':
                                b1 = row['expected_filename']
                            elif row['base_seed'] == '1234567':
                                b2 = row['expected_filename']
                        elif row['cond_id'] == arm:
                            if row['base_seed'] == '3141592':
                                a1 = row['expected_filename']
                            elif row['base_seed'] == '1234567':
                                a2 = row['expected_filename']
                                
                def make_img(fname):
                    if fname:
                        raw_path = str(target_dir / fname).replace('\\', '/')
                        p = urllib.parse.quote(f"file:///{raw_path}", safe=':/')
                        return f"<a href='{p}' target='_blank'><img src='{p}'></a><br><small>{fname}</small>"
                    return "N/A"
                    
                html.append("<tr>")
                html.append(f"<td><strong>{w}</strong></td>")
                html.append(f"<td>{make_img(b1)}</td>")
                html.append(f"<td>{make_img(a1)}</td>")
                html.append(f"<td>{make_img(b2)}</td>")
                html.append(f"<td>{make_img(a2)}</td>")
                html.append("</tr>")
            html.append("</table>")
            
    html.append("</body></html>")
    
    out_html = target_dir / "eye_sheets.html"
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))
        
    print(f"Generated {out_html}")
    
if __name__ == '__main__':
    main()
