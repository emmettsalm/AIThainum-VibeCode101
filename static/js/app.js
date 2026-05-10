/* ── Toast ───────────────────────────────────────────────────────────────── */
let _toastTimer = null;
function showToast(msg, type = '') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = 'show ' + type;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { el.className = ''; }, 3500);
}

/* ══════════════════════════════════════════════════════════════════════════
   USER PAGE
   ══════════════════════════════════════════════════════════════════════════ */
(function initUserPage() {
  const canvas = document.getElementById('draw-canvas');
  if (!canvas) return;

  const ctx      = canvas.getContext('2d');
  const hint     = document.getElementById('canvas-hint');
  const penSlider = document.getElementById('pen-size');
  const penDot   = document.getElementById('pen-preview');
  let drawing    = false;
  let hasDrawn   = false;
  let lastX = 0, lastY = 0;
  let penSize = 28;

  /* ── Canvas init ──────────────────────────────────────────────────────── */
  function initCanvas() {
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  initCanvas();

  /* ── Pen preview dot ─────────────────────────────────────────────────── */
  function updatePenPreview() {
    const sz = Math.round(penSize / 2.5);
    penDot.innerHTML = `<div class="pen-preview-dot" style="width:${sz}px;height:${sz}px"></div>`;
  }
  updatePenPreview();
  penSlider.addEventListener('input', () => {
    penSize = parseInt(penSlider.value);
    updatePenPreview();
  });

  /* ── Draw helpers ────────────────────────────────────────────────────── */
  function getPos(e) {
    const rect  = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect.width;
    const scaleY = canvas.height / rect.height;
    const src = e.touches ? e.touches[0] : e;
    return [(src.clientX - rect.left) * scaleX,
            (src.clientY - rect.top)  * scaleY];
  }

  function startDraw(e) {
    e.preventDefault();
    drawing = true;
    if (!hasDrawn) { hasDrawn = true; hint.classList.add('hidden'); }
    [lastX, lastY] = getPos(e);
    ctx.beginPath();
    ctx.arc(lastX, lastY, penSize / 2, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
  }
  function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    const [x, y] = getPos(e);
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.lineWidth   = penSize;
    ctx.lineCap     = 'round';
    ctx.lineJoin    = 'round';
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
    [lastX, lastY] = [x, y];
  }
  function stopDraw() { drawing = false; }

  canvas.addEventListener('mousedown',  startDraw);
  canvas.addEventListener('mousemove',  draw);
  canvas.addEventListener('mouseup',    stopDraw);
  canvas.addEventListener('mouseleave', stopDraw);
  canvas.addEventListener('touchstart', startDraw, { passive: false });
  canvas.addEventListener('touchmove',  draw,       { passive: false });
  canvas.addEventListener('touchend',   stopDraw);

  /* ── Clear ───────────────────────────────────────────────────────────── */
  document.getElementById('btn-clear').addEventListener('click', () => {
    initCanvas();
    hasDrawn = false;
    hint.classList.remove('hidden');
    document.getElementById('result-panel').style.display      = 'none';
    document.getElementById('result-placeholder').style.display = '';
  });

  /* ── Predict ─────────────────────────────────────────────────────────── */
  document.getElementById('btn-predict').addEventListener('click', async () => {
    if (!hasDrawn) { showToast('วาดตัวเลขก่อนนะ', 'error'); return; }

    document.getElementById('result-placeholder').style.display = 'none';
    document.getElementById('result-panel').style.display       = 'none';
    document.getElementById('loading-overlay').style.display    = '';
    document.getElementById('btn-predict').disabled             = true;

    try {
      const res  = await fetch('/api/predict', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ image: canvas.toDataURL('image/png') }),
      });
      const data = await res.json();
      document.getElementById('loading-overlay').style.display = 'none';
      document.getElementById('btn-predict').disabled          = false;

      if (data.error) {
        showToast('Error: ' + data.error, 'error');
        document.getElementById('result-placeholder').style.display = '';
        return;
      }
      renderResult(data);
    } catch (err) {
      document.getElementById('loading-overlay').style.display      = 'none';
      document.getElementById('btn-predict').disabled               = false;
      document.getElementById('result-placeholder').style.display   = '';
      showToast('Network error: ' + err.message, 'error');
    }
  });

  function renderResult(data) {
    /* 28x28 preview */
    if (data.preview) {
      const prev = document.getElementById('preview-img');
      if (prev) prev.src = data.preview;
    }
    /* digit */
    const digit = document.getElementById('result-digit');
    digit.textContent = data.predicted_label;
    digit.style.animation = 'none';
    requestAnimationFrame(() => { digit.style.animation = ''; });

    document.getElementById('result-numeric').textContent = '(' + data.predicted_numeric + ')';
    document.getElementById('result-conf').textContent    = (data.confidence * 100).toFixed(1) + '% confidence';

    /* bars */
    const container = document.getElementById('bars-container');
    container.innerHTML = '';
    data.all_predictions.forEach(p => {
      const isTop = p.label === data.predicted_label;
      const row = document.createElement('div');
      row.className = 'bar-row' + (isTop ? ' winner' : '');
      row.innerHTML = `
        <span class="bar-label">${p.label}</span>
        <div class="bar-track"><div class="bar-fill${isTop ? ' top' : ''}" data-pct="${(p.confidence*100).toFixed(1)}"></div></div>
        <span class="bar-pct">${(p.confidence*100).toFixed(1)}%</span>`;
      container.appendChild(row);
    });
    requestAnimationFrame(() => {
      container.querySelectorAll('.bar-fill').forEach(b => { b.style.width = b.dataset.pct + '%'; });
    });

    document.getElementById('result-panel').style.display = '';
  }
})();

/* ══════════════════════════════════════════════════════════════════════════
   ADMIN PAGE
   ══════════════════════════════════════════════════════════════════════════ */
(function initAdminPage() {
  if (!document.getElementById('dropzone')) return;

  /* Fetch model info from API on load — avoids timing issues */
  fetch('/api/model_info')
    .then(r => r.json())
    .then(renderModelInfo)
    .catch(() => {});

  const fileInput = document.getElementById('model-file-input');
  const dropzone  = document.getElementById('dropzone');
  const btnUpload = document.getElementById('btn-upload');
  let selectedFile = null;

  /* drag & drop */
  dropzone.addEventListener('dragover',  e => { e.preventDefault(); dropzone.classList.add('drag-over'); });
  dropzone.addEventListener('dragleave', ()   => dropzone.classList.remove('drag-over'));
  dropzone.addEventListener('drop', e => {
    e.preventDefault(); dropzone.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f) selectFile(f);
  });
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) selectFile(fileInput.files[0]); });

  function selectFile(f) {
    if (!f.name.endsWith('.h5') && !f.name.endsWith('.keras')) {
      showToast('รองรับเฉพาะไฟล์ .h5 หรือ .keras', 'error'); return;
    }
    selectedFile = f;
    document.getElementById('selected-file-name').textContent = `📎 ${f.name}  (${(f.size/1024).toFixed(1)} KB)`;
    document.getElementById('selected-file-info').style.display = '';
    btnUpload.disabled = false;
  }

  /* upload */
  btnUpload.addEventListener('click', async () => {
    if (!selectedFile) return;
    btnUpload.disabled = true;
    const progress     = document.getElementById('upload-progress');
    const progressFill = document.getElementById('upload-progress-fill');
    progress.classList.add('active');
    progressFill.style.width = '30%';

    const form = new FormData();
    form.append('model', selectedFile);
    try {
      progressFill.style.width = '65%';
      const res  = await fetch('/api/upload_model', { method: 'POST', body: form });
      progressFill.style.width = '95%';
      const data = await res.json();
      setTimeout(() => { progress.classList.remove('active'); progressFill.style.width = '0%'; }, 500);

      if (data.error) { showToast(data.error, 'error'); btnUpload.disabled = false; return; }

      showToast('✓ ' + data.message, 'ok');
      renderModelInfo(data.model_info);
      selectedFile = null;
      fileInput.value = '';
      document.getElementById('selected-file-info').style.display = 'none';

    } catch (err) {
      progress.classList.remove('active'); progressFill.style.width = '0%';
      btnUpload.disabled = false;
      showToast('Network error: ' + err.message, 'error');
    }
  });

  /* reset */
  document.getElementById('btn-reset').addEventListener('click', async () => {
    if (!confirm('รีเซ็ตกลับเป็น original model?')) return;
    try {
      const res  = await fetch('/api/reset_model', { method: 'POST' });
      const data = await res.json();
      if (data.success) { showToast('✓ กลับเป็น original model แล้ว', 'ok'); renderModelInfo(data.model_info); }
    } catch (err) { showToast('Error: ' + err.message, 'error'); }
  });

  function renderModelInfo(info) {
    const isOrig = info.is_original;
    document.getElementById('status-dot').className   = 'status-dot ' + (isOrig ? 'original' : 'custom');
    document.getElementById('status-badge').className = 'status-badge ' + (isOrig ? 'original' : 'custom');
    document.getElementById('status-badge').textContent = isOrig ? 'ORIGINAL' : 'UPLOADED';
    document.getElementById('status-name').textContent  = info.name || '—';
    document.getElementById('status-meta').textContent  = isOrig
      ? 'โมเดลเริ่มต้น — ถาวรตลอดการทำงานของ server'
      : '⚠️ Uploaded — อยู่ในหน่วยความจำเท่านั้น ไม่ถาวร';
    document.getElementById('model-info-body').innerHTML = `
      <tr><td>Input shape</td><td>${info.input_shape || '—'}</td></tr>
      <tr><td>Output classes</td><td>${info.output_classes || '—'}</td></tr>
      <tr><td>Status</td><td>${isOrig ? '✅ Original' : '🔄 Temporary upload'}</td></tr>`;
  }
})();
