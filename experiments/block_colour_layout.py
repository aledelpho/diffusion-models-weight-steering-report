"""Colour change, layout kept and total change for every single-block arm.

Benches: single_blocks_styles, _v3, _v4 (23 prompts). For each arm against the
baseline of the same prompt and seed, in CIELAB at 64x80 (lab() of
block_effect_overlap.py):
  d_chroma  mean chroma (sqrt(a^2+b^2)) of the arm minus the baseline's
  layout_r  Pearson r of the L channel with the baseline's (1 = same layout)
  dE        mean colour distance to the baseline
Written for the question "is blk23 a clean saturation knob?" (2026-10-04),
after the blk23 renders were opened.
Writes data/block_colour_layout.csv.
"""
import glob,os,re,sys,numpy as np
sys.path.insert(0,os.path.expanduser('~/mnt/diffusion-models-weight-steering-report/experiments'))
from block_effect_overlap import lab
R=os.path.expanduser('~/mnt')
out=[]
for b in ['benchmark_single_blocks_styles','benchmark_single_blocks_v3','benchmark_single_blocks_v4']:
  d=f'{R}/{b}/renders'
  for bf in glob.glob(d+'/*_baseline_*.png'):
    pid=os.path.basename(bf).split('_baseline')[0]; seed=re.search(r'seed(\d+)',bf)[1]
    B=lab(bf); cB=np.hypot(B[...,1],B[...,2]).mean()
    rows={}
    for f in glob.glob(f'{d}/{pid}_blk*_seed{seed}_*.png'):
      m=re.search(r'_(blk\d\d)_(pos|neg)_d([\d.]+)_',f); X=lab(f)
      dose=float(m[3])*(1 if m[2]=='pos' else -1)
      c=np.hypot(X[...,1],X[...,2]).mean()
      lay=np.corrcoef(X[...,0].ravel(),B[...,0].ravel())[0,1]
      out.append((b[24:],pid,m[1],dose,round(c-cB,2),round(lay,3),round(float(np.linalg.norm(X-B,axis=-1).mean()),2)))
import csv
w=csv.writer(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','block_colour_layout.csv'),'w',newline='')); w.writerow(['bench','prompt','block','dose','d_chroma','layout_r','dE']); w.writerows(out)
print(len(out))
