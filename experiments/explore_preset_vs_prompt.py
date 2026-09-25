# -*- coding: utf-8 -*-
"""experiments/explore_preset_vs_prompt.py — POST-HOC, DESCRIPTIVE.
Decided after the pre-registered results were seen, in answer to two questions from the
observer. Reports no p-value and supports no claim: with three seeds per cell every recall is
one of 0, 1/3, 2/3, 1, and single cells are noisy. Writes data/recall_by_preset_prompt.csv."""
import os,sys,csv,numpy as np,collections
sys.path.insert(0,os.path.expanduser("~/mnt/diffusion-models-weight-steering-report/experiments"))
import style_capacity_multiprompt as M
presets,prompts,seeds,cells,D=M.load(M.FEATURES_23)
P,Q,S,F=len(presets),len(prompts),len(seeds),len(M.FEATURES_23)
sd=M.scale(D,Q,S); X=(D/sd).reshape(P,Q,S,F)
C=X.mean(axis=2)                      # (P,Q,F) centroide per preset per prompt
# --- 1) distanze: fra preset a parita' di prompt  vs  stesso preset fra prompt diversi
wp=[];  # within prompt, fra preset
for q in range(Q):
    for i in range(P):
        for j in range(i+1,P): wp.append(np.linalg.norm(C[i,q]-C[j,q]))
sp=[]   # stesso preset, fra prompt
for i in range(P):
    for q in range(Q):
        for r in range(q+1,Q): sp.append(np.linalg.norm(C[i,q]-C[i,r]))
xp=[]   # preset diversi E prompt diversi
for i in range(P):
    for j in range(P):
        if i==j: continue
        for q in range(Q):
            for r in range(Q):
                if q<r: xp.append(np.linalg.norm(C[i,q]-C[j,r]))
print("=== 1) quanto pesa il preset e quanto il prompt (unita': rumore di seed) ===")
print(f"  preset diversi, STESSO prompt      n={len(wp):5d}  media {np.mean(wp):7.3f}  mediana {np.median(wp):7.3f}")
print(f"  STESSO preset, prompt diversi      n={len(sp):5d}  media {np.mean(sp):7.3f}  mediana {np.median(sp):7.3f}")
print(f"  preset diversi E prompt diversi    n={len(xp):5d}  media {np.mean(xp):7.3f}  mediana {np.median(xp):7.3f}")
print(f"  rapporto prompt/preset: {np.mean(sp)/np.mean(wp):.2f}x")
# coseno: la direzione di uno stesso preset sopravvive al cambio di prompt?
def cos(a,b):
    na,nb=np.linalg.norm(a),np.linalg.norm(b)
    return float(a@b/(na*nb)) if na and nb else np.nan
same=[cos(C[i,q],C[i,r]) for i in range(P) for q in range(Q) for r in range(q+1,Q)]
diff=[cos(C[i,q],C[j,r]) for i in range(P) for j in range(P) if i!=j for q in range(Q) for r in range(Q) if q<r]
print(f"  coseno stesso preset fra prompt   media {np.nanmean(same):+.4f}")
print(f"  coseno preset diversi fra prompt  media {np.nanmean(diff):+.4f}")
# --- 2) riconoscibilita' per (preset, prompt)
Kidx=np.arange(S)[None,:,None]
inv=np.repeat(np.arange(P)[None,None,:],Q,axis=0).repeat(S,axis=1)
rec=np.zeros((P,Q))
for q in range(Q):
    tr=np.array([j for j in range(Q) if j!=q]); J=tr[:,None,None]
    cen=X[inv[tr],J,Kidx].mean(axis=(0,1))
    cn=cen/np.where(np.linalg.norm(cen,axis=1,keepdims=True)>0,np.linalg.norm(cen,axis=1,keepdims=True),1.0)
    Xq=X[:,q]; nx=np.linalg.norm(Xq,axis=2,keepdims=True); Un=Xq/np.where(nx>0,nx,1.0)
    pred=np.argmax(Un@cn.T,axis=2)
    for i in range(P): rec[i,q]=(pred[i]==i).mean()
names=[f"{p[0]}_d{p[1]}" for p in presets]
order=np.argsort(-rec.mean(axis=1))
print()
print("=== 2) riconoscimento per (preset, prompt) — % su 3 seed ===")
print(f"{'preset':22s}{'media':>7s}  "+"".join(f"{q.replace('S','').split('_')[1][:6]:>7s}" for q in prompts))
for i in order:
    print(f"{names[i]:22s}{rec[i].mean()*100:6.1f}%  "+"".join(f"{rec[i,q]*100:6.0f}%" for q in range(Q)))
print()
print("=== preset con media <20% ma almeno un prompt >=67% ===")
for i in order:
    if rec[i].mean()<0.20 and rec[i].max()>=0.66:
        best=[prompts[q] for q in range(Q) if rec[i,q]==rec[i].max()]
        print(f"   {names[i]:22s} media {rec[i].mean()*100:5.1f}%  ->  {rec[i].max()*100:.0f}% su {best}")
print()
print("=== per prompt: riconoscimento medio su tutti i preset ===")
for q in range(Q): print(f"   {prompts[q]:16s} {rec[:,q].mean()*100:5.1f}%")
with open(os.path.expanduser("~/mnt/diffusion-models-weight-steering-report/data/recall_by_preset_prompt.csv"),"w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["preset","region","draw"]+prompts+["mean"])
    for i in range(P): w.writerow([names[i],presets[i][0],presets[i][1]]+[f"{rec[i,q]:.4f}" for q in range(Q)]+[f"{rec[i].mean():.4f}"])
print("\nscritto data/recall_by_preset_prompt.csv")
