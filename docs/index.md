---
hide:
  - toc
---

<style>
/* ── VoxelKit landing page ─────────────────────────────────────────── */

/* Notice banner */
.vk-notice {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: #fffde7;
  border-left: 4px solid #f9a825;
  border-radius: 0 10px 10px 0;
  padding: 0.9rem 1.25rem;
  margin-bottom: 2rem;
  font-size: 0.92rem;
  color: #5a4000;
  line-height: 1.55;
}
[data-md-color-scheme="slate"] .vk-notice {
  background: #1f1a00;
  color: #f9d97f;
  border-left-color: #f9a825;
}
.vk-notice-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 0.05rem; }

/* Hero */
.vk-hero {
  background: linear-gradient(140deg, #0d2137 0%, #0b5e5a 55%, #00897b 100%);
  border-radius: 18px;
  padding: 3.5rem 2rem 2.75rem;
  text-align: center;
  margin-bottom: 2.5rem;
  position: relative;
  overflow: hidden;
}
.vk-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 65% 35%, rgba(255,255,255,0.07) 0%, transparent 65%);
  pointer-events: none;
}
.vk-hero-icon {
  font-size: 4.5rem;
  line-height: 1;
  display: block;
  margin-bottom: 0.4rem;
}
.vk-hero h1 {
  color: #ffffff !important;
  font-size: 3.2rem !important;
  font-weight: 800 !important;
  letter-spacing: -1.5px;
  margin: 0 0 0.1rem !important;
  text-shadow: 0 3px 20px rgba(0,0,0,0.35);
}
.vk-hero .vk-tagline {
  color: rgba(255,255,255,0.82);
  font-size: 1.2rem;
  margin: 0.65rem auto 1.75rem;
  max-width: 580px;
  line-height: 1.65;
}
.vk-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.45rem;
  margin-bottom: 1.9rem;
}
.vk-badges img { height: 23px; vertical-align: middle; }
.vk-cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: center;
}

/* Buttons */
.vk-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  padding: 0.68rem 1.5rem;
  border-radius: 9px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
  border: 2px solid transparent;
  cursor: pointer;
}
.vk-btn-primary {
  background: #ffffff;
  color: #0b5e5a !important;
  border-color: #ffffff;
}
.vk-btn-primary:hover {
  background: #e8f7f6;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.22);
}
.vk-btn-outline {
  background: transparent;
  color: #ffffff !important;
  border-color: rgba(255,255,255,0.55);
}
.vk-btn-outline:hover {
  background: rgba(255,255,255,0.12);
  border-color: #ffffff;
  transform: translateY(-2px);
}

/* Install block */
.vk-install {
  background: linear-gradient(135deg, #f4fdfc 0%, #e5f5f3 100%);
  border: 1.5px solid #b2dfdb;
  border-radius: 14px;
  padding: 2rem 1.75rem;
  text-align: center;
  margin: 2rem 0;
}
[data-md-color-scheme="slate"] .vk-install {
  background: linear-gradient(135deg, #0b1d1c 0%, #0d2b28 100%);
  border-color: #174440;
}
.vk-install-label {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0b5e5a;
  margin: 0 0 1rem;
}
[data-md-color-scheme="slate"] .vk-install-label { color: #4ecdc4; }
.vk-install-box {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  background: #1a2332;
  border-radius: 10px;
  padding: 0.85rem 1.4rem;
  margin-bottom: 0.9rem;
  max-width: 100%;
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
}
.vk-install-box code {
  font-size: 1.1rem !important;
  color: #7ee8a2 !important;
  background: none !important;
  padding: 0 !important;
  font-family: "Fira Code", "JetBrains Mono", "Cascadia Code", monospace !important;
  letter-spacing: 0.4px;
  white-space: nowrap;
}
.vk-copy-btn {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 6px;
  color: rgba(255,255,255,0.75);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.7rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, color 0.15s ease;
  font-family: inherit;
}
.vk-copy-btn:hover {
  background: rgba(255,255,255,0.2);
  color: #ffffff;
}
.vk-install-meta {
  font-size: 0.85rem;
  color: #607d7b;
  margin: 0;
}
[data-md-color-scheme="slate"] .vk-install-meta { color: #90a4ae; }
.vk-install-meta code {
  font-size: 0.83rem !important;
  background: rgba(0,150,136,0.12) !important;
  color: #0b7a75 !important;
  padding: 0.1em 0.4em !important;
  border-radius: 4px !important;
}
[data-md-color-scheme="slate"] .vk-install-meta code {
  background: rgba(0,150,136,0.2) !important;
  color: #4ecdc4 !important;
}

/* Section headings */
.vk-section-heading {
  text-align: center;
  font-size: 1.75rem !important;
  font-weight: 800 !important;
  color: #0b5e5a !important;
  margin: 2.75rem 0 0.4rem !important;
  letter-spacing: -0.5px;
}
[data-md-color-scheme="slate"] .vk-section-heading { color: #4ecdc4 !important; }
.vk-section-sub {
  text-align: center;
  color: #607d7b;
  font-size: 0.98rem;
  margin: 0 0 1.75rem;
}
[data-md-color-scheme="slate"] .vk-section-sub { color: #90a4ae; }

/* Feature cards */
.vk-features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 1.15rem;
  margin-bottom: 1rem;
}
.vk-feat {
  background: #ffffff;
  border: 1.5px solid #e0f0ee;
  border-radius: 13px;
  padding: 1.4rem 1.5rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}
.vk-feat:hover {
  border-color: #0b7a75;
  box-shadow: 0 5px 22px rgba(11,122,117,0.13);
  transform: translateY(-2px);
}
[data-md-color-scheme="slate"] .vk-feat {
  background: #182533;
  border-color: #1a3835;
}
[data-md-color-scheme="slate"] .vk-feat:hover {
  border-color: #0b7a75;
  box-shadow: 0 5px 22px rgba(11,122,117,0.28);
}
.vk-feat-icon { font-size: 1.9rem; line-height: 1; display: block; margin-bottom: 0.7rem; }
.vk-feat h3 {
  font-size: 0.98rem !important;
  font-weight: 700 !important;
  color: #0b5e5a !important;
  margin: 0 0 0.45rem !important;
}
[data-md-color-scheme="slate"] .vk-feat h3 { color: #4ecdc4 !important; }
.vk-feat p {
  font-size: 0.88rem;
  color: #546e7a;
  margin: 0;
  line-height: 1.65;
}
[data-md-color-scheme="slate"] .vk-feat p { color: #90a4ae; }
.vk-feat code {
  font-size: 0.82rem !important;
  background: rgba(0,150,136,0.1) !important;
  color: #0b7a75 !important;
  padding: 0.1em 0.4em !important;
  border-radius: 4px !important;
}
[data-md-color-scheme="slate"] .vk-feat code {
  background: rgba(0,150,136,0.2) !important;
  color: #4ecdc4 !important;
}

/* Format pills */
.vk-formats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  justify-content: center;
  margin: 0 0 2.5rem;
}
.vk-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45em;
  background: #e4f5f3;
  color: #0b5e5a;
  border: 1.5px solid #b2dfdb;
  border-radius: 100px;
  padding: 0.38rem 1.1rem;
  font-size: 0.91rem;
  font-weight: 700;
  font-family: "Fira Code", "JetBrains Mono", monospace;
  transition: background 0.15s, border-color 0.15s, transform 0.15s;
}
.vk-pill:hover {
  background: #c8eae7;
  border-color: #0b7a75;
  transform: translateY(-1px);
}
[data-md-color-scheme="slate"] .vk-pill {
  background: #0c2523;
  color: #4ecdc4;
  border-color: #174440;
}
[data-md-color-scheme="slate"] .vk-pill:hover { background: #163630; }

/* Audience grid */
.vk-audience {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.1rem;
  margin-bottom: 1rem;
}
.vk-aud-card {
  background: #ffffff;
  border: 1.5px solid #eceff1;
  border-radius: 13px;
  padding: 1.25rem 1.4rem;
  display: flex;
  align-items: flex-start;
  gap: 0.95rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}
.vk-aud-card:hover {
  border-color: #0b7a75;
  box-shadow: 0 4px 18px rgba(11,122,117,0.11);
  transform: translateY(-2px);
}
[data-md-color-scheme="slate"] .vk-aud-card {
  background: #182533;
  border-color: #1a3835;
}
[data-md-color-scheme="slate"] .vk-aud-card:hover {
  border-color: #0b7a75;
  box-shadow: 0 4px 18px rgba(11,122,117,0.25);
}
.vk-aud-icon { font-size: 2rem; line-height: 1; flex-shrink: 0; }
.vk-aud-card h4 {
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: #1a2332 !important;
  margin: 0 0 0.3rem !important;
}
[data-md-color-scheme="slate"] .vk-aud-card h4 { color: #dce8ec !important; }
.vk-aud-card p {
  font-size: 0.84rem;
  color: #607d8b;
  margin: 0;
  line-height: 1.55;
}
[data-md-color-scheme="slate"] .vk-aud-card p { color: #90a4ae; }

/* Bottom CTA */
.vk-cta-bottom {
  background: linear-gradient(140deg, #0b5e5a 0%, #00897b 55%, #26a69a 100%);
  border-radius: 18px;
  padding: 3.25rem 2rem;
  text-align: center;
  margin: 2.5rem 0 1rem;
}
.vk-cta-bottom h2 {
  color: #ffffff !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  margin: 0 0 0.7rem !important;
  letter-spacing: -0.5px;
}
.vk-cta-bottom p {
  color: rgba(255,255,255,0.83);
  font-size: 1.05rem;
  margin: 0 auto 1.9rem;
  max-width: 520px;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 600px) {
  .vk-hero h1 { font-size: 2.2rem !important; }
  .vk-hero .vk-tagline { font-size: 1.05rem; }
  .vk-features, .vk-audience { grid-template-columns: 1fr; }
  .vk-cta-bottom h2 { font-size: 1.55rem !important; }
  .vk-install-box { flex-direction: column; gap: 0.65rem; }
}
</style>

<!-- ── Notice ─────────────────────────────────────────────────────── -->
<div class="vk-notice">
  <span class="vk-notice-icon">📋</span>
  <span><strong>Note:</strong> This is the <strong>project landing page</strong>, not the full documentation site. For complete guides, CLI reference, Python API docs, and real-world examples, use the <strong>Full Documentation</strong> button below.</span>
</div>

<!-- ── Hero ───────────────────────────────────────────────────────── -->
<div class="vk-hero">
  <span class="vk-hero-icon">🧊</span>
  <h1>VoxelKit</h1>
  <p class="vk-tagline">Inspect, preview, and QA-check multidimensional imaging data from one unified Python and CLI workflow.</p>

  <div class="vk-badges">
    <a href="https://pypi.org/project/voxelkit/" target="_blank">
      <img src="https://img.shields.io/pypi/v/voxelkit?style=flat-square&color=00c4b4&logo=pypi&logoColor=white&label=PyPI" alt="PyPI version">
    </a>
    <a href="https://pepy.tech/projects/voxelkit" target="_blank">
      <img src="https://static.pepy.tech/badge/voxelkit?style=flat-square" alt="PyPI Downloads">
    </a>
    <a href="https://github.com/ArsalaanAhmad/VoxelKit/stargazers" target="_blank">
      <img src="https://img.shields.io/github/stars/ArsalaanAhmad/VoxelKit?style=flat-square&color=ffd700&logo=github&logoColor=white" alt="GitHub Stars">
    </a>
    <a href="https://pypi.org/project/voxelkit/" target="_blank">
      <img src="https://img.shields.io/pypi/pyversions/voxelkit?style=flat-square&logo=python&logoColor=white&color=3776ab" alt="Python versions">
    </a>
    <a href="https://github.com/ArsalaanAhmad/VoxelKit/blob/main/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/ArsalaanAhmad/VoxelKit?style=flat-square&color=00c4b4" alt="MIT License">
    </a>
    <a href="https://doi.org/10.5281/zenodo.19774569" target="_blank">
      <img src="https://zenodo.org/badge/1210656483.svg?style=flat-square" alt="DOI">
    </a>
  </div>

  <div class="vk-cta-row">
    <a href="getting-started/" class="vk-btn vk-btn-primary">📖 Full Documentation &rarr;</a>
    <a href="https://github.com/ArsalaanAhmad/VoxelKit" class="vk-btn vk-btn-outline" target="_blank">⭐ Star on GitHub</a>
  </div>
</div>

<!-- ── Install ────────────────────────────────────────────────────── -->
<div class="vk-install">
  <p class="vk-install-label">⚡ Get started in seconds</p>
  <div class="vk-install-box">
    <code id="vk-pip-cmd">pip install voxelkit</code>
    <button class="vk-copy-btn" id="vk-copy-btn"
      onclick="navigator.clipboard.writeText('pip install voxelkit').then(()=>{
        var b=document.getElementById('vk-copy-btn');
        b.textContent='✓ Copied!';
        setTimeout(()=>b.textContent='📋 Copy',1600);
      })">📋 Copy</button>
  </div>
  <p class="vk-install-meta">
    Requires <strong>Python ≥ 3.9</strong> &nbsp;&middot;&nbsp; MIT License &nbsp;&middot;&nbsp;
    Extras: <code>pip install voxelkit[gui]</code> for Streamlit GUI &nbsp;&middot;&nbsp;
    100% local — no cloud uploads
  </p>
</div>

<!-- ── Features ──────────────────────────────────────────────────── -->
<h2 class="vk-section-heading">✨ Features</h2>
<p class="vk-section-sub">Everything you need for day-to-day imaging dataset triage</p>

<div class="vk-features">
  <div class="vk-feat">
    <span class="vk-feat-icon">🔍</span>
    <h3>File Inspection</h3>
    <p>Extract shape, dtype, and metadata from any supported format instantly — no format-specific boilerplate required.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">🖼️</span>
    <h3>PNG Slice Previews</h3>
    <p>Generate crisp 2D previews from 3D/4D volumes with configurable plane, slice index, and colormap in a single command.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">📊</span>
    <h3>Per-File QA Reports</h3>
    <p>Compute statistics and auto-detect problems — NaNs, Infs, constant arrays, near-zero volumes — for any single file.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">📁</span>
    <h3>Batch QA Reporting</h3>
    <p>Aggregate QA across an entire directory with <code>report-batch</code>. Surface dataset-level risks before they reach your pipeline.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">🧬</span>
    <h3>Embedding Analysis</h3>
    <p>Specialized QA for 2D embedding matrices — detect dead dimensions, outlier samples, and per-dimension norm statistics.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">🔌</span>
    <h3>Unified Python API</h3>
    <p>Four clean functions — <code>inspect_file</code>, <code>preview_file</code>, <code>report_file</code>, <code>report_batch</code> — work identically across all formats.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">🌐</span>
    <h3>REST API</h3>
    <p>FastAPI-powered HTTP endpoints for remote inspection, preview generation, and QA reporting — drop into any stack.</p>
  </div>
  <div class="vk-feat">
    <span class="vk-feat-icon">🖥️</span>
    <h3>Optional Local GUI</h3>
    <p>Streamlit-based offline interface for point-and-click workflows. Launch in seconds with <code>voxelkit gui</code>.</p>
  </div>
</div>

<!-- ── Format Coverage ───────────────────────────────────────────── -->
<h2 class="vk-section-heading">📂 Supported Formats</h2>
<p class="vk-section-sub">One toolkit, four imaging ecosystems</p>

<div class="vk-formats">
  <span class="vk-pill">🧠 .nii &nbsp;/&nbsp; .nii.gz</span>
  <span class="vk-pill">🗄️ .h5 &nbsp;/&nbsp; .hdf5</span>
  <span class="vk-pill">🔢 .npy &nbsp;/&nbsp; .npz</span>
  <span class="vk-pill">🖼️ .tif &nbsp;/&nbsp; .tiff</span>
</div>

<!-- ── Who Benefits ──────────────────────────────────────────────── -->
<h2 class="vk-section-heading">👥 Who Can Benefit</h2>
<p class="vk-section-sub">VoxelKit fits wherever multidimensional data needs triage</p>

<div class="vk-audience">
  <div class="vk-aud-card">
    <span class="vk-aud-icon">🔬</span>
    <div>
      <h4>Neuroscience Researchers</h4>
      <p>Quickly inspect and QA fMRI, DTI, and structural MRI datasets in NIfTI format — no format-specific boilerplate.</p>
    </div>
  </div>
  <div class="vk-aud-card">
    <span class="vk-aud-icon">🏥</span>
    <div>
      <h4>Medical Imaging Teams</h4>
      <p>Run batch QA across large clinical datasets to catch constant arrays, NaN-contaminated volumes, or zero-dominated scans before analysis.</p>
    </div>
  </div>
  <div class="vk-aud-card">
    <span class="vk-aud-icon">🤖</span>
    <div>
      <h4>ML / AI Practitioners</h4>
      <p>Validate imaging tensors and embedding matrices before training. Catch dead dimensions and outliers early to prevent silent failures.</p>
    </div>
  </div>
  <div class="vk-aud-card">
    <span class="vk-aud-icon">📐</span>
    <div>
      <h4>Data Scientists</h4>
      <p>Rapidly explore unfamiliar multidimensional datasets from collaborators without reading format-specific documentation first.</p>
    </div>
  </div>
  <div class="vk-aud-card">
    <span class="vk-aud-icon">🏗️</span>
    <div>
      <h4>Data Engineers</h4>
      <p>Integrate VoxelKit's REST API or Python interface into automated pipelines to enforce data quality gates at ingestion time.</p>
    </div>
  </div>
  <div class="vk-aud-card">
    <span class="vk-aud-icon">🌍</span>
    <div>
      <h4>Geospatial Engineers</h4>
      <p>Inspect and QA multi-band raster stacks, satellite imagery tiles, and elevation models stored as NumPy, HDF5, or TIFF arrays.</p>
    </div>
  </div>
  <div class="vk-aud-card">
    <span class="vk-aud-icon">🎓</span>
    <div>
      <h4>Educators & Students</h4>
      <p>Use the GUI and CLI to interactively explore neuroimaging and scientific datasets in teaching and research settings.</p>
    </div>
  </div>
</div>

<!-- ── Bottom CTA ────────────────────────────────────────────────── -->
<div class="vk-cta-bottom">
  <h2>Ready to triage your data?</h2>
  <p>The full documentation covers installation, CLI reference, Python API, QA warning types, and real-world examples.</p>
  <div class="vk-cta-row">
    <a href="getting-started/" class="vk-btn vk-btn-primary">📖 Read the Full Docs &rarr;</a>
    <a href="https://pypi.org/project/voxelkit/" class="vk-btn vk-btn-outline" target="_blank">📦 View on PyPI</a>
    <a href="https://github.com/ArsalaanAhmad/VoxelKit" class="vk-btn vk-btn-outline" target="_blank">⭐ GitHub</a>
  </div>
</div>
