// Diffusion Models Weight Steering - Interactive Viewer
const STATE = {
  model: 'krea2',
  promptId: '30de058455',
  seed: '4242145',
  condA: 'baseline',
  condB: 'preset',
  viewMode: 'side', // 'side' | 'toggle' | 'strip'
  stripCond: 'preset',
  toggleActive: 'A'
};

const PROMPTS = [
    { id: '30de058455', label: 'Sea-touched Siren (Teal)' },
    { id: 'c6a4015aae', label: 'Goblin with Sly Grin (Yellow)' },
    { id: '7e8536f9bb', label: 'Barbarian Half-Orc in Rage (Red)' },
    { id: '95acba3b41', label: 'Ancient Hag Manic (Chartreuse)' },
    { id: '4d43750a91', label: 'Dwarf with Booming Shout (Teal)' },
    { id: '5a0d2949e1', label: 'Sneezing Dwarf (Blue)' },
    { id: '0496d2dadf', label: 'Tiefling in Icy Contempt (Purple)' },
    { id: 'ecdd49e618', label: 'Dark Elf in Simmering Fury (Teal)' },
    { id: '83301f8591', label: 'Tiefling in Dazed Shock (Orange)' },
    { id: 'd96b69d21c', label: 'Elf Screaming in Terror (Blue)' }
  ];

const SEEDS = ['4242145', '42', '1337', '777', '9999'];

// Testo completo dei prompt, per sha1. Caricato da data/prompts.json cosi' che il
// viewer e i CSV non possano divergere: la stessa sorgente che nomina le cartelle
// di assets/ e' quella che scrive il testo a schermo.
const PROMPT_TEXT = {};
function loadPrompts() {
  return fetch('../data/prompts.json')
    .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
    .then(d => { (d.prompts || []).forEach(p => { PROMPT_TEXT[p.sha1] = p; }); })
    .catch(() => { /* aperto da file://, il pannello resta con il solo hash */ });
}

function updatePromptPanel() {
  const meta = document.getElementById('prompt-meta');
  const text = document.getElementById('prompt-text');
  if (!meta || !text) return;
  const p = PROMPT_TEXT[STATE.promptId];
  const entry = PROMPTS.find(x => x.id === STATE.promptId);
  const label = entry ? entry.label : STATE.promptId;
  if (p) {
    meta.textContent = `${p.id} · ${p.tag} · prompt_sha1 ${p.sha1} · ${p.family}`;
    text.textContent = p.text;
  } else {
    meta.textContent = `${label} · prompt_sha1 ${STATE.promptId}`;
    text.textContent = 'Full prompt text lives in data/prompts.json. Serve this folder over HTTP '
      + '(for example: python -m http.server) to read it here — a page opened straight from '
      + 'the filesystem cannot fetch it.';
  }
}

const CONDITIONS = [
  { id: 'baseline', label: 'Baseline (Unmodified base)' },
  { id: 'preset', label: 'Preset (+, Targeted Configuration)' },
  { id: 'preset_neg', label: 'Preset (-, Inverted Signs)' },
  { id: 'preset_half', label: 'Preset (Half, eps = 0.5)' },
  { id: 'blockshuffle', label: 'BLOCKSHUFFLE (+, Permuted Blocks)' },
  { id: 'blockshuffle_neg', label: 'BLOCKSHUFFLE (-, Inverted Signs)' },
  { id: 'randsign', label: 'RANDSIGN (+, Random Signs)' },
  { id: 'randsign_neg', label: 'RANDSIGN (-, Inverted Signs)' }
];

const PROMPT_FOLDERS = {
  '30de058455': 'G1_seatouched_teal_30de058455',
  'c6a4015aae': 'G2_goblin_yellow_c6a4015aae',
  '7e8536f9bb': 'F1_halforc_red_7e8536f9bb',
  '95acba3b41': 'G4_hag_chartreuse_95acba3b41',
  '4d43750a91': 'G3_dwarf_teal_4d43750a91',
  '5a0d2949e1': 'G5_dwarf_sneeze_blue_5a0d2949e1',
  '0496d2dadf': 'G6_tiefling_purple_0496d2dadf',
  'ecdd49e618': 'F2_darkelf_teal_ecdd49e618',
  '83301f8591': 'F3_tiefling_orange_83301f8591',
  'd96b69d21c': 'F4_elf_blue_d96b69d21c'
};

function getImagePath(model, condition, promptId, seed) {
  const folder = PROMPT_FOLDERS[promptId] || promptId;
  return `../assets/01_steering/${condition}/${folder}/${seed}.webp`;
}

function initDOM() {
  const promptSelect = document.getElementById('select-prompt');
  PROMPTS.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.label} [${p.id}]`;
    promptSelect.appendChild(opt);
  });
  promptSelect.value = STATE.promptId;

  const seedSelect = document.getElementById('select-seed');
  SEEDS.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = `Seed ${s}`;
    seedSelect.appendChild(opt);
  });
  seedSelect.value = STATE.seed;

  const condASelect = document.getElementById('select-cond-a');
  const condBSelect = document.getElementById('select-cond-b');
  CONDITIONS.forEach(c => {
    const optA = document.createElement('option');
    optA.value = c.id;
    optA.textContent = c.label;
    condASelect.appendChild(optA);

    const optB = document.createElement('option');
    optB.value = c.id;
    optB.textContent = c.label;
    condBSelect.appendChild(optB);
  });
  condASelect.value = STATE.condA;
  condBSelect.value = STATE.condB;

  // Event Listeners
  promptSelect.addEventListener('change', (e) => {
    STATE.promptId = e.target.value;
    updateRender();
  });

  seedSelect.addEventListener('change', (e) => {
    STATE.seed = e.target.value;
    updateRender();
  });

  condASelect.addEventListener('change', (e) => {
    STATE.condA = e.target.value;
    updateRender();
  });

  condBSelect.addEventListener('change', (e) => {
    STATE.condB = e.target.value;
    updateRender();
  });

  
  const stripCondSelect = document.getElementById('select-strip-cond');
  if (stripCondSelect) {
    CONDITIONS.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.label;
      stripCondSelect.appendChild(opt);
    });
    stripCondSelect.value = STATE.stripCond;
    stripCondSelect.addEventListener('change', (e) => {
      STATE.stripCond = e.target.value;
      updateRender();
    });
  }

  document.getElementById('btn-mode-strip').addEventListener('click', () => {
    setMode('strip');
  });

  document.getElementById('btn-mode-side').addEventListener('click', () => {
    setMode('side');
  });

  document.getElementById('btn-mode-toggle').addEventListener('click', () => {
    setMode('toggle');
  });

  document.getElementById('btn-toggle-switch').addEventListener('click', () => {
    toggleAB();
  });

  const toggleImg = document.getElementById('img-toggle');
  toggleImg.addEventListener('click', () => {
    toggleAB();
  });

  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && STATE.viewMode === 'toggle') {
      e.preventDefault();
      toggleAB();
    }
  });

  updateRender();
}

function setMode(mode) {
  STATE.viewMode = mode;
  document.getElementById('btn-mode-side').classList.toggle('active', mode === 'side');
  document.getElementById('btn-mode-toggle').classList.toggle('active', mode === 'toggle');
  document.getElementById('btn-mode-strip').classList.toggle('active', mode === 'strip');

  document.getElementById('side-by-side-view').style.display = (mode === 'side') ? 'grid' : 'none';
  document.getElementById('toggle-view').style.display = (mode === 'toggle') ? 'flex' : 'none';
  document.getElementById('strip-view').style.display = (mode === 'strip') ? 'flex' : 'none';
  updateRender();
}

function toggleAB() {
  STATE.toggleActive = (STATE.toggleActive === 'A') ? 'B' : 'A';
  updateToggleDisplay();
}

function updateToggleDisplay() {
  const isA = (STATE.toggleActive === 'A');
  const cond = isA ? STATE.condA : STATE.condB;
  const path = getImagePath(STATE.model, cond, STATE.promptId, STATE.seed);

  const img = document.getElementById('img-toggle');
  img.src = path;

  const badge = document.getElementById('toggle-status-badge');
  badge.className = `toggle-badge ${isA ? 'a' : 'b'}`;
  badge.textContent = `Viewing: [${STATE.toggleActive}] ${cond.toUpperCase()}`;

  document.getElementById('toggle-meta-path').textContent = path;
}

function updateRender() {
  updatePromptPanel();
  if (STATE.viewMode === 'side') {
    const pathA = getImagePath(STATE.model, STATE.condA, STATE.promptId, STATE.seed);
    const pathB = getImagePath(STATE.model, STATE.condB, STATE.promptId, STATE.seed);

    document.getElementById('img-a').src = pathA;
    document.getElementById('img-b').src = pathB;

    document.getElementById('meta-path-a').textContent = pathA;
    document.getElementById('meta-path-b').textContent = pathB;
  } else if (STATE.viewMode === 'toggle') {
    updateToggleDisplay();
  } else if (STATE.viewMode === 'strip') {
    SEEDS.forEach((seed, idx) => {
      const el = document.getElementById('strip-img-' + idx);
      if (el) {
        el.src = getImagePath(STATE.model, STATE.stripCond, STATE.promptId, seed);
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initDOM();
  // i prompt arrivano in modo asincrono: il pannello si riempie appena ci sono,
  // e nel frattempo l'interfaccia e' gia' utilizzabile
  loadPrompts().then(updatePromptPanel);
});