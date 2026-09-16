# The ComfyUI graphs behind every image

Every PNG in [`assets/images/`](../../assets/images/) was written by ComfyUI with its
generation graph embedded in a PNG `tEXt` chunk named `prompt` (the API-format graph).
Dragging any of those PNGs onto a ComfyUI canvas reloads the exact graph that produced it.

Two things are published here so that the graph is readable **without** downloading a
1.8 MB PNG first:

* **[`../../data/comfy_graphs.json`](../../data/comfy_graphs.json)** — the complete
  per-image record: `assets/images/.../<seed>.png` → its full graph, for all 370
  committed renders. This is the byte-for-byte content of the embedded chunk, so it
  carries the seed, the sampler settings, the checkpoint, the preset file and the
  prompt text actually sent to the text encoder for each individual image.
* **`graph_*.json`** — the three distinct topologies, pretty-printed. Across all 370
  renders there are only three:

| File | Nodes | What it is |
|---|---|---|
| `graph_1_10nodes.json` | 10 | Baseline — `ArthemyKrea2ResetPatcher` restores the stock checkpoint; no preset is loaded. |
| `graph_2_12nodes.json` | 12 | Baseline with `ArthemyKrea2ModelVisualizer` attached (used to dump per-tensor norms). |
| `graph_3_11nodes.json` | 11 | Treatment — `ArthemyKrea2PresetLoader` applies one of the six preset files before sampling. |

The custom nodes are from
[`aledelpho/comfyui-arthemy-krea2-tuner`](https://github.com/aledelpho/comfyui-arthemy-krea2-tuner).

## Why this matters for verification

The claim "the prompt was never modified between conditions" is checkable twice over,
from two independent records:

1. `prompt_sha1` in [`../../data/prompts.json`](../../data/prompts.json) and in the
   stage manifests, and
2. the `CLIPTextEncode` node inside each image's own graph here.

If those two ever disagreed for any image, the experiment would be invalid — and both
are published, so the disagreement would be findable by anyone.
