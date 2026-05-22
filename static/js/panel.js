/**
 * panel.js — Doktor Paneli & Numaratör JS
 */

/* ======================================================
   1. ORTAK
   ====================================================== */
function updateClock() {
  const el = document.getElementById('display-clock');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('tr-TR', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
}
setInterval(updateClock, 1000);
updateClock();

/* ======================================================
   2. DOKTOR PANELİ
   ====================================================== */

(function initDoctorPanel() {
  const panelEl = document.getElementById('doctor-panel');
  if (!panelEl) return;

  const doctorId        = parseInt(panelEl.dataset.doctorId);
  const callNextBtn     = document.getElementById('btn-call-next');
  const completeBtn     = document.getElementById('btn-complete');
  const cancelBtn       = document.getElementById('btn-cancel');
  const calledSection   = document.getElementById('called-section');
  const waitingTableBody= document.getElementById('waiting-table-body');
  const noPatientsMsg   = document.getElementById('no-patients-msg');
  const calledPatientEl = document.getElementById('called-patient-info');
  const statWaiting     = document.getElementById('stat-waiting');
  const statCalled      = document.getElementById('stat-called');
  const statCompleted   = document.getElementById('stat-completed');

  let currentToken = null;

  /* ── Sonraki Hastayı Çağır ── */
  if (callNextBtn) {
    callNextBtn.addEventListener('click', async () => {
      callNextBtn.disabled = true;
      callNextBtn.textContent = '⏳ Çağrılıyor…';

      try {
        const res  = await fetch('/api/queue/call-next/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ doctor_id: doctorId }),
        });
        const data = await res.json();

        if (data.success) {
          showCalledPatient(data.data);
          await refreshPanel();
        } else {
          alert(data.error || 'Bekleyen hasta bulunamadı.');
        }
      } catch {
        alert('Sunucuya bağlanılamadı.');
      } finally {
        callNextBtn.disabled = false;
        callNextBtn.innerHTML = '📢 Sonraki Hastayı Çağır';
      }
    });
  }

  /* ── Tamamlandı ── */
  if (completeBtn) {
    completeBtn.addEventListener('click', async () => {
      if (!currentToken) return;
      await updateQueueStatus(currentToken, 'complete');
    });
  }

  /* ── İptal ── */
  if (cancelBtn) {
    cancelBtn.addEventListener('click', async () => {
      if (!currentToken) return;
      if (!confirm('Bu hastayı iptal etmek istediğinize emin misiniz?')) return;
      await updateQueueStatus(currentToken, 'cancel');
    });
  }

  async function updateQueueStatus(token, action) {
    try {
      const res  = await fetch(`/api/queue/${action}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ queue_token: token }),
      });
      const data = await res.json();
      if (data.success) {
        hideCalledSection();
        await refreshPanel();
      } else {
        alert(data.error || 'İşlem başarısız.');
      }
    } catch {
      alert('Sunucu hatası.');
    }
  }

  function showCalledPatient(d) {
    currentToken = d.queue_token;
    if (calledSection)   calledSection.classList.remove('hidden');
    if (calledPatientEl) {
      document.getElementById('called-queue-num').textContent   = d.queue_number;
      document.getElementById('called-patient-name').textContent = d.patient_name;
      document.getElementById('called-room').textContent        = d.room || '—';
      const summaryEl = document.getElementById('called-anamnez');
      if (summaryEl) {
        summaryEl.textContent = d.anamnez_summary || 'Anamnez bulunmuyor.';
        summaryEl.parentElement.classList.toggle('risk', d.risk_detected || false);
      }
    }
  }

  function hideCalledSection() {
    currentToken = null;
    if (calledSection) calledSection.classList.add('hidden');
  }

  async function refreshPanel() {
    try {
      const res  = await fetch(`/api/panel/doctor/${doctorId}/`);
      const data = await res.json();
      if (!data.success) return;
      renderWaitingTable(data.data.waiting_patients || []);
      if (statWaiting)   statWaiting.textContent   = data.data.stats?.waiting   ?? 0;
      if (statCalled)    statCalled.textContent     = data.data.stats?.called    ?? 0;
      if (statCompleted) statCompleted.textContent  = data.data.stats?.completed ?? 0;
    } catch {}
  }

  function renderWaitingTable(patients) {
    if (!waitingTableBody) return;
    waitingTableBody.innerHTML = '';

    if (!patients.length) {
      if (noPatientsMsg) noPatientsMsg.classList.remove('hidden');
      return;
    }
    if (noPatientsMsg) noPatientsMsg.classList.add('hidden');

    patients.forEach(p => {
      const tr = document.createElement('tr');
      if (p.risk_detected) tr.classList.add('risk-row');
      tr.innerHTML = `
        <td><strong>#${p.queue_number}</strong></td>
        <td>${escHtml(p.patient_name)}</td>
        <td style="color:var(--text-secondary);font-size:13px">${formatTime(p.created_at)}</td>
        <td style="font-size:13px;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
          ${p.anamnez_summary
            ? `<span title="${escHtml(p.anamnez_summary)}">${escHtml(p.anamnez_summary.slice(0, 60))}${p.anamnez_summary.length > 60 ? '…' : ''}</span>`
            : '<span style="color:var(--text-muted)">—</span>'}
          ${p.risk_detected ? '<span class="risk-badge">⚠ Risk</span>' : ''}
        </td>
        <td>
          <button class="btn btn-primary btn-sm" onclick="callSpecific(${p.id})">📢 Çağır</button>
        </td>
      `;
      waitingTableBody.appendChild(tr);
    });
  }

  window.callSpecific = async function(entryId) {
    try {
      const res  = await fetch('/api/queue/call-specific/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entry_id: entryId, doctor_id: doctorId }),
      });
      const data = await res.json();
      if (data.success) {
        showCalledPatient(data.data);
        await refreshPanel();
      } else {
        alert(data.error || 'Hata.');
      }
    } catch { alert('Sunucu hatası.'); }
  };

  function escHtml(str) {
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function formatTime(isoStr) {
    if (!isoStr) return '—';
    const d = new Date(isoStr);
    return d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  }

  // İlk yükleme
  refreshPanel();
  setInterval(refreshPanel, 10000); // 10 saniyede bir güncelle
})();

/* ======================================================
   3. NUMARATÖR EKRANI — queue_display.html
   ====================================================== */

(function initDisplay() {
  const displayEl = document.getElementById('queue-display-screen');
  if (!displayEl) return;

  const rowsContainer = document.getElementById('display-rows');
  let lastIds = [];

  function playBeep() {
    try {
      const ctx  = new (window.AudioContext || window.webkitAudioContext)();
      [523, 659, 784].forEach((freq, i) => {
        const osc  = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = freq;
        osc.type = 'triangle';
        gain.gain.setValueAtTime(.5, ctx.currentTime + i * .22);
        gain.gain.exponentialRampToValueAtTime(.001, ctx.currentTime + i * .22 + .35);
        osc.start(ctx.currentTime + i * .22);
        osc.stop(ctx.currentTime + i * .22 + .4);
      });
    } catch {}
  }

  async function fetchDisplay() {
    try {
      const res  = await fetch('/api/panel/display/');
      const data = await res.json();
      if (!data.success) return;
      renderRows(data.data.recent_calls || []);
    } catch {}
  }

  function renderRows(calls) {
    if (!rowsContainer) return;

    const newIds = calls.map(c => c.id);
    const hasNew  = newIds.some(id => !lastIds.includes(id));

    if (hasNew && lastIds.length > 0) {
      playBeep();
    }
    lastIds = newIds;

    rowsContainer.innerHTML = '';
    if (!calls.length) {
      rowsContainer.innerHTML = `
        <div style="text-align:center;padding:80px;color:rgba(255,255,255,.3);font-size:20px;">
          Henüz çağrı yapılmadı.
        </div>`;
      return;
    }

    calls.forEach((c, idx) => {
      const isNew = hasNew && idx === 0;
      const row   = document.createElement('div');
      row.className = `display-row${isNew ? ' flash' : ''}`;
      row.innerHTML = `
        <div class="display-col">
          <div class="display-col-label">Sıra No</div>
          <div class="display-col-value queue-num${isNew ? ' new-call' : ''}">${c.queue_number}</div>
        </div>
        <div class="display-col">
          <div class="display-col-label">Hasta</div>
          <div class="display-col-value" style="font-size:20px;">${escHtml(c.patient_name)}</div>
        </div>
        <div class="display-col">
          <div class="display-col-label">Poliklinik</div>
          <div class="display-col-value" style="font-size:18px;">${escHtml(c.polyclinic)}</div>
        </div>
        <div class="display-col">
          <div class="display-col-label">Doktor</div>
          <div class="display-col-value" style="font-size:18px;">${escHtml(c.doctor_name || '—')}</div>
        </div>
        <div class="display-col">
          <div class="display-col-label">Oda</div>
          <div class="display-col-value" style="font-size:24px;">${escHtml(c.room || '—')}</div>
          <div class="display-time">${formatTime(c.called_at)}</div>
        </div>
      `;
      rowsContainer.appendChild(row);
    });
  }

  function escHtml(str) {
    return String(str || '')
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function formatTime(isoStr) {
    if (!isoStr) return '';
    const d = new Date(isoStr);
    return d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  }

  fetchDisplay();
  setInterval(fetchDisplay, 5000);
})();
