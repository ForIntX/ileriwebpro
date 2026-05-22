/**
 * kiosk.js — Hasta Kiosk Sistemi JavaScript
 * Check-in validasyon, polling, anamnez chat logic
 */

/* ======================================================
   1. ORTAK YARDIMCILAR
   ====================================================== */

/** Saat göstergesi */
function updateClock() {
  const el = document.getElementById('kiosk-clock');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

  const dateEl = document.getElementById('kiosk-date');
  if (dateEl) {
    dateEl.textContent = now.toLocaleDateString('tr-TR', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
  }
}
setInterval(updateClock, 1000);
updateClock();

/* ======================================================
   2. CHECK-IN FORMU
   ====================================================== */

(function initCheckinForm() {
  const form = document.getElementById('checkin-form');
  if (!form) return;

  const tcInput       = document.getElementById('tc_no');
  const nameInput     = document.getElementById('full_name');
  const polyclinicSel = document.getElementById('polyclinic_id');
  const submitBtn     = document.getElementById('submit-btn');
  const tcError       = document.getElementById('tc-error');
  const nameError     = document.getElementById('name-error');
  const polyError     = document.getElementById('poly-error');
  const formError     = document.getElementById('form-error');

  function showError(el, msg) {
    if (!el) return;
    el.textContent = msg ? '⚠ ' + msg : '';
    el.style.display = msg ? 'flex' : 'none';
  }

  function validateTc(val) {
    if (!val) return 'TC kimlik numarası zorunludur.';
    if (!/^\d+$/.test(val)) return 'Yalnızca rakam giriniz.';
    if (val.length !== 11) return `${val.length}/11 hane — 11 hane olmalıdır.`;
    return '';
  }

  // Sadece rakam girişi
  tcInput.addEventListener('input', () => {
    tcInput.value = tcInput.value.replace(/\D/g, '').slice(0, 11);
    const err = validateTc(tcInput.value);
    showError(tcError, err);
    if (err) {
      tcInput.classList.add('is-error');
      tcInput.classList.remove('is-valid');
    } else {
      tcInput.classList.remove('is-error');
      tcInput.classList.add('is-valid');
    }
    updateSubmitState();
  });

  nameInput.addEventListener('input', () => {
    const err = nameInput.value.trim() ? '' : 'Ad soyad zorunludur.';
    showError(nameError, err);
    nameInput.classList.toggle('is-error', !!err);
    nameInput.classList.toggle('is-valid', !err);
    updateSubmitState();
  });

  polyclinicSel.addEventListener('change', () => {
    const err = polyclinicSel.value ? '' : 'Poliklinik seçimi zorunludur.';
    showError(polyError, err);
    polyclinicSel.classList.toggle('is-error', !!err);
    polyclinicSel.classList.toggle('is-valid', !err);
    updateSubmitState();
  });

  function updateSubmitState() {
    const tcOk   = !validateTc(tcInput.value);
    const nameOk = !!nameInput.value.trim();
    const polyOk = !!polyclinicSel.value;
    submitBtn.disabled = !(tcOk && nameOk && polyOk);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showError(formError, '');

    const payload = {
      tc_no:         tcInput.value.trim(),
      full_name:     nameInput.value.trim(),
      polyclinic_id: parseInt(polyclinicSel.value),
      doctor_id:     document.getElementById('doctor_id')?.value
                     ? parseInt(document.getElementById('doctor_id').value) : null,
    };

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner" style="width:28px;height:28px;border-width:3px;display:inline-block;"></div> İşleniyor…';

    try {
      const res  = await fetch('/api/checkin/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success) {
        window.location.href = `/kiosk/success/?token=${data.data.queue_token}`;
      } else {
        showError(formError, data.error || 'Bir hata oluştu.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-icon">✓</span> Sıra Numarası Al';
      }
    } catch {
      showError(formError, 'Sunucuya bağlanılamadı. Lütfen tekrar deneyin.');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="btn-icon">✓</span> Sıra Numarası Al';
    }
  });

  // Poliklinik değişince doktorları yükle
  polyclinicSel.addEventListener('change', loadDoctors);

  async function loadDoctors() {
    const doctorContainer = document.getElementById('doctor-container');
    const doctorSel       = document.getElementById('doctor_id');
    if (!doctorContainer || !doctorSel) return;

    const pid = polyclinicSel.value;
    if (!pid) {
      doctorContainer.classList.add('hidden');
      return;
    }
    doctorSel.innerHTML = '<option value="">— Otomatik Atama —</option>';
    doctorContainer.classList.remove('hidden');
    // Basit: doktorları admin'den veya fixtures'dan çekemedik, bu yüzden dinamik değil.
    // Gerçek projede /api/doctors/?polyclinic=<id> endpoint eklenebilir.
  }
})();

/* ======================================================
   3. SIRA TAKİP (POLLING) — queue.html
   ====================================================== */

(function initQueuePolling() {
  const queueDisplay = document.getElementById('queue-display');
  if (!queueDisplay) return;

  const token           = queueDisplay.dataset.token;
  const queueNumEl      = document.getElementById('queue-number');
  const remainingEl     = document.getElementById('remaining-count');
  const statusEl        = document.getElementById('status-badge');
  const doctorEl        = document.getElementById('doctor-name');
  const roomEl          = document.getElementById('room-number');
  const polyclinicEl    = document.getElementById('polyclinic-name');
  const calledOverlay   = document.getElementById('called-overlay');
  const waitingSection  = document.getElementById('waiting-section');

  let lastStatus = '';
  let beepPlayed = false;

  async function pollQueue() {
    try {
      const res  = await fetch(`/api/queue/${token}/`);
      const data = await res.json();
      if (!data.success) return;

      const d = data.data;

      // Sıra numarası
      if (queueNumEl) queueNumEl.textContent = d.queue_number;

      // Kalan kişi
      if (remainingEl) {
        remainingEl.textContent = d.remaining_count;
        remainingEl.className = 'remaining-count ' +
          (d.remaining_count === 0 ? 'none' : d.remaining_count <= 3 ? 'few' : 'many');
      }

      // Doktor / oda / poliklinik
      if (doctorEl)     doctorEl.textContent     = d.doctor_name   || '—';
      if (roomEl)       roomEl.textContent       = d.room          || '—';
      if (polyclinicEl) polyclinicEl.textContent = d.polyclinic    || '—';

      // Durum
      updateStatus(d.status);

    } catch { /* sessizce geç */ }
  }

  function updateStatus(status) {
    if (status === lastStatus) return;
    lastStatus = status;

    const labels = {
      waiting:   '🟡 Bekliyor',
      called:    '🟢 ÇAĞRILDI',
      completed: '✅ Tamamlandı',
      cancelled: '❌ İptal',
    };

    if (statusEl) {
      statusEl.textContent  = labels[status] || status;
      statusEl.className    = `status-badge ${status}`;
    }

    if (status === 'called') {
      // Yeşil ekran efekti
      document.body.classList.add('state-called');
      if (waitingSection)  waitingSection.classList.add('hidden');
      if (calledOverlay)   calledOverlay.classList.remove('hidden');

      // Sesli uyarı (1 kez)
      if (!beepPlayed) {
        beepPlayed = true;
        playBeep();
        // Browser bildirimi (izin varsa)
        if (Notification.permission === 'granted') {
          new Notification('🏥 Sıranız Geldi!', {
            body: 'Lütfen belirlenen odaya geçiniz.',
            icon: '/static/img/hospital-icon.png',
          });
        }
      }
    }
  }

  function playBeep() {
    try {
      const ctx  = new (window.AudioContext || window.webkitAudioContext)();
      const play = (freq, start, dur) => {
        const osc  = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = freq;
        osc.type = 'sine';
        gain.gain.setValueAtTime(.6, ctx.currentTime + start);
        gain.gain.exponentialRampToValueAtTime(.001, ctx.currentTime + start + dur);
        osc.start(ctx.currentTime + start);
        osc.stop(ctx.currentTime + start + dur + .1);
      };
      play(880, 0, .25);
      play(1046, .35, .25);
      play(1318, .70, .5);
    } catch {}
  }

  // İzin iste
  if (Notification && Notification.permission === 'default') {
    Notification.requestPermission();
  }

  pollQueue(); // İlk yükleme
  setInterval(pollQueue, 5000);
})();

/* ======================================================
   4. ANAMNEz CHAT — anamnez.html
   ====================================================== */

(function initAnamnezChat() {
  const chatContainer = document.getElementById('chat-container');
  if (!chatContainer) return;

  const token       = chatContainer.dataset.token;
  const messages    = document.getElementById('chat-messages');
  const input       = document.getElementById('chat-input');
  const sendBtn     = document.getElementById('btn-send');
  const finishBtn   = document.getElementById('btn-finish');
  const dangerBanner= document.getElementById('danger-banner');
  const summaryArea = document.getElementById('summary-area');
  const inputArea   = document.getElementById('chat-input-area');

  let sessionActive = false;
  let riskDetected  = false;

  function addBubble(text, role) {
    const div = document.createElement('div');
    div.className = `bubble bubble-${role}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'bubble bubble-typing';
    div.id = 'typing-indicator';
    div.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function hideTyping() {
    const t = document.getElementById('typing-indicator');
    if (t) t.remove();
  }

  async function startSession() {
    showTyping();
    try {
      const res  = await fetch('/api/anamnez/start/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ queue_token: token }),
      });
      const data = await res.json();
      hideTyping();

      if (data.success && data.data.question) {
        addBubble(data.data.question, 'assistant');
        sessionActive = true;
        sendBtn.disabled  = false;
        input.disabled    = false;
        input.focus();
      } else {
        addBubble('Anamnez başlatılırken bir sorun oluştu. Lütfen personeli çağırın.', 'assistant');
      }
    } catch {
      hideTyping();
      addBubble('Sunucuya bağlanılamadı.', 'assistant');
    }
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text || !sessionActive) return;

    addBubble(text, 'user');
    input.value   = '';
    sendBtn.disabled = true;
    input.disabled   = true;
    showTyping();

    try {
      const res  = await fetch('/api/anamnez/message/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ queue_token: token, message: text }),
      });
      const data = await res.json();
      hideTyping();

      if (data.success) {
        if (data.data.reply) addBubble(data.data.reply, 'assistant');

        if (data.data.risk_detected && !riskDetected) {
          riskDetected = true;
          if (dangerBanner) dangerBanner.classList.remove('hidden');
        }

        if (data.data.finished) {
          sessionActive = false;
          await finishSession();
          return;
        }
      } else {
        addBubble('Bir hata oluştu: ' + (data.error || ''), 'assistant');
      }
    } catch {
      hideTyping();
      addBubble('Sunucuya bağlanılamadı.', 'assistant');
    } finally {
      sendBtn.disabled = false;
      input.disabled   = false;
      input.focus();
    }
  }

  async function finishSession() {
    sendBtn.disabled  = true;
    input.disabled    = true;
    if (finishBtn) finishBtn.disabled = true;

    showTyping();
    try {
      const res  = await fetch('/api/anamnez/finish/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ queue_token: token }),
      });
      const data = await res.json();
      hideTyping();

      if (data.success) {
        // Input alanını gizle
        if (inputArea) inputArea.classList.add('hidden');

        // Özet göster
        if (summaryArea) {
          summaryArea.classList.remove('hidden');
          const summaryText = document.getElementById('summary-text');
          if (summaryText) summaryText.textContent = data.data.summary || '—';
        }
        addBubble('✅ Anamneziniz tamamlandı ve doktor panelinize iletildi. Teşekkür ederiz.', 'assistant');
      }
    } catch {
      hideTyping();
      addBubble('Tamamlama sırasında hata oluştu.', 'assistant');
    }
  }

  // Gönder butonu
  sendBtn.addEventListener('click', sendMessage);

  // Enter (shift+enter yeni satır)
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Bitir butonu
  if (finishBtn) {
    finishBtn.addEventListener('click', () => {
      if (confirm('Anamnezi bitirmek istediğinize emin misiniz?')) {
        sessionActive = false;
        finishSession();
      }
    });
  }

  // Oturumu başlat
  startSession();
})();
