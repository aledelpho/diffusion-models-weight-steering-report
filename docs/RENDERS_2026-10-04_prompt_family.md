# Renders: Prompt Family Experiment (2026-10-04)

## Commands Run
`ash
python experiments/prompt_family.py --queue --first 1
python experiments/prompt_family.py --repro
python experiments/prompt_family.py --queue
python experiments/prompt_family.py --count
python experiments/build_prompt_family_eye_page.py
`

## Output of Step 2 (Reproducibility check)
`	ext
REPRO PASS max abs diff 0
`

## Output of Step 4 (File count verification)
`	ext
expected 433 missing 0 [] duplicates 0
`

## Output of Step 5 (Eye page generation)
`	ext
written 33
`
