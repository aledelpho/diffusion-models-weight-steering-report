// Diffusion Models Weight Steering - Interactive Viewer
const STATE = {
  model: 'krea2',
  stage: 'stage7', // 'stage7' | 'stage1_5'
  promptId: '0a1c94584d',
  seed: '1337',
  condA: 'baseline',
  condB: 'preset_pos',
  viewMode: 'side', // 'side' | 'toggle' | 'strip'
  stripCond: 'preset_pos',
  toggleActive: 'A'
};

const PROMPTS_STAGE7 = [
  { id: '0a1c94584d', label: 'I09 · Dwarf with Ginger Pigtails' },
  { id: '0aa12a28b0', label: 'I02 · Elf in Obsidian Armor' },
  { id: '0dee1ceb78', label: 'I17 · Undead Human Woman' },
  { id: '2adb8ea1cd', label: 'I01 · Viking in Ice Armor' },
  { id: '2b36c75165', label: 'I11 · Gnome with Wild Blue Curls' },
  { id: '2f3689f658', label: 'I21 · Elemental Fiery Orange' },
  { id: '3d8a617173', label: 'I18 · Celestial Glowing Gold' },
  { id: '402376662d', label: 'I07 · Half-Orc in Granite Armor' },
  { id: '5421ab290b', label: 'I16 · Halfling with Blond Sideburns' },
  { id: '5b67e787c8', label: 'I05 · Tiefling in Chitin Armor' },
  { id: '66faaa372d', label: 'I24 · Construct Brass Faceplate' },
  { id: '8c3325ffd9', label: 'I12 · Human Raven Pixie Cut' },
  { id: '90ec9bbe8c', label: 'I10 · Lizardfolk Spiked Crest' },
  { id: '92b7d2e00d', label: 'I23 · Satyr Chestnut Curls' },
  { id: '952efcc3c6', label: 'I20 · Drow Swept Back Silver' },
  { id: 'a324a148e4', label: 'I06 · Human in Steel Armor' }
];

const PROMPTS_STAGE1_5 = [
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

const CONDITIONS_STAGE7 = [
  { id: 'baseline', label: 'Baseline (Unmodified base)' },
  { id: 'preset_pos', label: 'Preset (+, Targeted Configuration)' },
  { id: 'preset_neg', label: 'Preset (-, Inverted Signs)' },
  { id: 'blockshuf_pos', label: 'BLOCKSHUFFLE (+, Permuted Blocks)' },
  { id: 'blockshuf_neg', label: 'BLOCKSHUFFLE (-, Inverted Signs)' },
  { id: 'rand_pos', label: 'RANDSIGN (+, Random Signs)' },
  { id: 'rand_neg', label: 'RANDSIGN (-, Inverted Signs)' }
];

const CONDITIONS_STAGE1_5 = [
  { id: 'baseline', label: 'Baseline (Unmodified base)' },
  { id: 'preset', label: 'Preset (+, Targeted Configuration)' },
  { id: 'preset_neg', label: 'Preset (-, Inverted Signs)' },
  { id: 'preset_half', label: 'Preset (Half, eps = 0.5)' },
  { id: 'blockshuffle', label: 'BLOCKSHUFFLE (+, Permuted Blocks)' },
  { id: 'blockshuffle_neg', label: 'BLOCKSHUFFLE (-, Inverted Signs)' },
  { id: 'randsign', label: 'RANDSIGN (+, Random Signs)' },
  { id: 'randsign_neg', label: 'RANDSIGN (-, Inverted Signs)' }
];

const SEEDS = ['1337', '42', '4242145', '777', '9999'];

const PROMPT_FOLDERS_STAGE7 = {'2adb8ea1cd': 'I01_a_viking_woman_with_blonde_long_braided_hair_2adb8ea1cd', '0aa12a28b0': 'I02_an_elf_man_with_long_white_straight_hair_0aa12a28b0', 'c31d285321': 'I03_an_orc_woman_with_dark_green_dreadlocks_c31d285321', 'bb8edafd35': 'I04_a_goblin_man_with_huge_pointed_ears_bb8edafd35', '5b67e787c8': 'I05_a_tiefling_woman_with_curled_ram_horns_and_purple_hair_5b67e787c8', 'a324a148e4': 'I06_a_human_man_with_cropped_brown_hair_and_stubble_a324a148e4', '402376662d': 'I07_a_half_orc_man_with_a_shaved_head_and_facial_scars_402376662d', 'c00acc77d9': 'I08_a_high_elf_woman_with_a_tight_red_ponytail_c00acc77d9', '0a1c94584d': 'I09_a_dwarf_woman_with_twin_braided_ginger_pigtails_0a1c94584d', '90ec9bbe8c': 'I10_a_lizardfolk_man_with_spiked_crest_and_yellow_eyes_90ec9bbe8c', '2b36c75165': 'I11_a_gnome_woman_with_wild_blue_curls_2b36c75165', '8c3325ffd9': 'I12_a_human_woman_with_short_raven_pixie_cut_8c3325ffd9', 'fb96d83893': 'I13_a_minotaur_man_with_heavy_iron_nose_ring_fb96d83893', 'c478c2b3f1': 'I14_a_wood_elf_woman_with_messy_brown_braided_crown_c478c2b3f1', 'ef69aba3ba': 'I15_a_dragonborn_man_with_dark_red_scaled_face_ef69aba3ba', '5421ab290b': 'I16_a_halfling_man_with_curly_blond_sideburns_5421ab290b', '0dee1ceb78': 'I17_an_undead_human_woman_with_hollow_cheeks_and_ragged_dark_hair_0dee1ceb78', '3d8a617173': 'I18_a_celestial_woman_with_glowing_metallic_gold_skin_3d8a617173', 'f1f616b0ac': 'I19_a_deep_gnome_man_with_chalky_gray_bald_head_f1f616b0ac', '952efcc3c6': 'I20_a_drow_man_with_swept_back_silver_hair_952efcc3c6', '2f3689f658': 'I21_an_elemental_woman_with_fiery_orange_glowing_hair_2f3689f658', 'c412444d34': 'I22_a_barbarian_man_with_messy_long_black_hair_c412444d34', '92b7d2e00d': 'I23_a_satyr_woman_with_small_curled_horns_and_unruly_chestnut_curls_92b7d2e00d', '66faaa372d': 'I24_a_construct_man_with_blank_brass_faceplate_66faaa372d'};

const PROMPT_FOLDERS_STAGE1_5 = {
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

const PROMPT_TEXT = {};
function loadPrompts() {
  return fetch('../data/prompts.json')
    .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
    .then(d => { (d.prompts || []).forEach(p => { PROMPT_TEXT[p.sha1] = p; }); })
    .catch(() => { /* fallback locale */ });
}

function getActivePrompts() {
  return (STATE.stage === 'stage7') ? PROMPTS_STAGE7 : PROMPTS_STAGE1_5;
}

function getActiveConditions() {
  return (STATE.stage === 'stage7') ? CONDITIONS_STAGE7 : CONDITIONS_STAGE1_5;
}

function updatePromptPanel() {
  const meta = document.getElementById('prompt-meta');
  const text = document.getElementById('prompt-text');
  if (!meta || !text) return;
  const p = PROMPT_TEXT[STATE.promptId];
  const list = getActivePrompts();
  const entry = list.find(x => x.id === STATE.promptId);
  const label = entry ? entry.label : STATE.promptId;
  if (p) {
    meta.textContent = `${p.id} · ${p.tag} · prompt_sha1 ${p.sha1} · ${p.family}`;
    text.textContent = p.text;
  } else {
    meta.textContent = `${label} · prompt_sha1 ${STATE.promptId}`;
    text.textContent = 'Full prompt text lives in data/prompts.json.';
  }
}

function getImagePath(model, condition, promptId, seed) {
  if (STATE.stage === 'stage7') {
    const folder = PROMPT_FOLDERS_STAGE7[promptId] || promptId;
    return `../assets/01_steering_stage7/${condition}/${folder}/${seed}.webp`;
  }
  const folder = PROMPT_FOLDERS_STAGE1_5[promptId] || promptId;
  return `../assets/01_steering/${condition}/${folder}/${seed}.webp`;
}

function populateSelectors() {
  const promptSelect = document.getElementById('select-prompt');
  promptSelect.innerHTML = '';
  const prompts = getActivePrompts();
  prompts.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.label} [${p.id.slice(0, 6)}]`;
    promptSelect.appendChild(opt);
  });
  STATE.promptId = prompts[0].id;
  promptSelect.value = STATE.promptId;

  const conds = getActiveConditions();
  const condASelect = document.getElementById('select-cond-a');
  const condBSelect = document.getElementById('select-cond-b');
  condASelect.innerHTML = '';
  condBSelect.innerHTML = '';
  conds.forEach(c => {
    const optA = document.createElement('option');
    optA.value = c.id;
    optA.textContent = c.label;
    condASelect.appendChild(optA);

    const optB = document.createElement('option');
    optB.value = c.id;
    optB.textContent = c.label;
    condBSelect.appendChild(optB);
  });

  STATE.condA = conds[0].id;
  STATE.condB = conds.length > 1 ? conds[1].id : conds[0].id;
  condASelect.value = STATE.condA;
  condBSelect.value = STATE.condB;

  const stripCondSelect = document.getElementById('select-strip-cond');
  if (stripCondSelect) {
    stripCondSelect.innerHTML = '';
    conds.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.label;
      stripCondSelect.appendChild(opt);
    });
    STATE.stripCond = STATE.condB;
    stripCondSelect.value = STATE.stripCond;
  }
}

function initDOM() {
  const stageSelect = document.getElementById('select-stage');
  if (stageSelect) {
    stageSelect.value = STATE.stage;
    stageSelect.addEventListener('change', (e) => {
      STATE.stage = e.target.value;
      populateSelectors();
      updateRender();
    });
  }

  populateSelectors();

  const seedSelect = document.getElementById('select-seed');
  seedSelect.innerHTML = '';
  SEEDS.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = `Seed ${s}`;
    seedSelect.appendChild(opt);
  });
  seedSelect.value = STATE.seed;

  document.getElementById('select-prompt').addEventListener('change', (e) => {
    STATE.promptId = e.target.value;
    updateRender();
  });

  seedSelect.addEventListener('change', (e) => {
    STATE.seed = e.target.value;
    updateRender();
  });

  document.getElementById('select-cond-a').addEventListener('change', (e) => {
    STATE.condA = e.target.value;
    updateRender();
  });

  document.getElementById('select-cond-b').addEventListener('change', (e) => {
    STATE.condB = e.target.value;
    updateRender();
  });

  const stripCondSelect = document.getElementById('select-strip-cond');
  if (stripCondSelect) {
    stripCondSelect.addEventListener('change', (e) => {
      STATE.stripCond = e.target.value;
      updateRender();
    });
  }

  document.getElementById('btn-mode-strip').addEventListener('click', () => setMode('strip'));
  document.getElementById('btn-mode-side').addEventListener('click', () => setMode('side'));
  document.getElementById('btn-mode-toggle').addEventListener('click', () => setMode('toggle'));
  document.getElementById('btn-toggle-switch').addEventListener('click', () => toggleAB());
  document.getElementById('img-toggle').addEventListener('click', () => toggleAB());

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
  loadPrompts().then(updatePromptPanel);
});
