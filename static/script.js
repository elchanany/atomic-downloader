// --- DOM Refs ---
const dom = {
    input: document.getElementById('url-input'),
    pasteBtn: document.getElementById('paste-btn'),
    siteBadge: document.getElementById('site-badge'),
    siteName: document.getElementById('site-name'),
    siteIcon: document.getElementById('site-icon'),
    smartLogin: document.getElementById('smart-login'),
    loginBtn: document.getElementById('login-btn'),
    downloadBtn: document.getElementById('download-btn'),
    addQueueBtn: document.getElementById('add-queue-btn'),
    urlQueue: document.getElementById('url-queue'),
    queueList: document.getElementById('queue-list'),
    queueCount: document.getElementById('queue-count'),
    dashboard: document.getElementById('dashboard'),
    progressWrap: document.getElementById('progress-wrap'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),
    logsToggle: document.getElementById('logs-toggle'),
    logsContainer: document.getElementById('logs-container'),
    logsContent: document.getElementById('logs-content'),
    errorMsg: document.getElementById('error-msg'),
    historySection: document.getElementById('history-section'),
    sidebar: document.getElementById('sidebar'),
    sidebarOverlay: document.getElementById('sidebar-overlay'),
    qualityRow: document.getElementById('quality-row'),
    qualityPills: document.getElementById('quality-pills'),
    qualityLoading: document.getElementById('quality-loading'),
    stats: {
        speed: document.getElementById('stat-speed'),
        eta: document.getElementById('stat-eta'),
        total: document.getElementById('stat-total')
    }
};

// --- Localization Manager ---
class LocalizationManager {
    constructor() {
        this.currentLang = localStorage.getItem('preferred_language') || 'en';
        this.translations = {};
        this.supportedLangs = [
            { "code": "en", "name": "English", "dir": "ltr" },
            { "code": "he", "name": "עברית", "dir": "rtl" },
            { "code": "es", "name": "Español", "dir": "ltr" },
            { "code": "fr", "name": "Français", "dir": "ltr" },
            { "code": "de", "name": "Deutsch", "dir": "ltr" },
            { "code": "ru", "name": "Русский", "dir": "ltr" },
            { "code": "ar", "name": "العربية", "dir": "rtl" },
            { "code": "zh-CN", "name": "简体中文", "dir": "ltr" },
            { "code": "zh-TW", "name": "繁體中文", "dir": "ltr" },
            { "code": "ja", "name": "日本語", "dir": "ltr" },
            { "code": "ko", "name": "한국어", "dir": "ltr" },
            { "code": "pt", "name": "Português", "dir": "ltr" },
            { "code": "it", "name": "Italiano", "dir": "ltr" },
            { "code": "nl", "name": "Nederlands", "dir": "ltr" },
            { "code": "tr", "name": "Türkçe", "dir": "ltr" },
            { "code": "pl", "name": "Polski", "dir": "ltr" },
            { "code": "id", "name": "Bahasa Indonesia", "dir": "ltr" },
            { "code": "hi", "name": "हिन्दी", "dir": "ltr" },
            { "code": "vi", "name": "Tiếng Việt", "dir": "ltr" },
            { "code": "th", "name": "ไทย", "dir": "ltr" },
            { "code": "sv", "name": "Svenska", "dir": "ltr" },
            { "code": "da", "name": "Dansk", "dir": "ltr" },
            { "code": "no", "name": "Norsk", "dir": "ltr" },
            { "code": "fi", "name": "Suomi", "dir": "ltr" },
            { "code": "el", "name": "Ελληνικά", "dir": "ltr" },
            { "code": "cs", "name": "Čeština", "dir": "ltr" },
            { "code": "hu", "name": "Magyar", "dir": "ltr" },
            { "code": "ro", "name": "Română", "dir": "ltr" },
            { "code": "uk", "name": "Українська", "dir": "ltr" },
            { "code": "bg", "name": "Български", "dir": "ltr" },
            { "code": "hr", "name": "Hrvatski", "dir": "ltr" },
            { "code": "sr", "name": "Српски", "dir": "ltr" },
            { "code": "sk", "name": "Slovenčina", "dir": "ltr" },
            { "code": "ca", "name": "Català", "dir": "ltr" },
            { "code": "tl", "name": "Filipino", "dir": "ltr" },
            { "code": "ms", "name": "Bahasa Melayu", "dir": "ltr" },
            { "code": "fa", "name": "فارسی", "dir": "rtl" },
            { "code": "sw", "name": "Kiswahili", "dir": "ltr" },
            { "code": "ta", "name": "தமிழ்", "dir": "ltr" },
            { "code": "te", "name": "తెలుగు", "dir": "ltr" },
            { "code": "ur", "name": "اردو", "dir": "rtl" },
            { "code": "bn", "name": "বাংলা", "dir": "ltr" },
            { "code": "mr", "name": "मराठी", "dir": "ltr" },
            { "code": "gu", "name": "ગુજરાતી", "dir": "ltr" },
            { "code": "pa", "name": "ਪੰਜਾਬੀ", "dir": "ltr" },
            { "code": "kn", "name": "ಕನ್ನಡ", "dir": "ltr" },
            { "code": "ml", "name": "മലയാളം", "dir": "ltr" }
        ];
    }

    async init() {
        await this.loadLanguage(this.currentLang);
        this.renderLanguageGrid();
        window.changeLanguage = (code) => this.setLanguage(code);
    }

    async loadLanguage(langCode) {
        try {
            const res = await fetch(`/static/locales/${langCode}.json`);
            if (!res.ok) throw new Error(`Language file not found: ${langCode}`);
            this.translations = await res.json();
            this.currentLang = langCode;
            this.applyTranslations();
            this.updateDirection();
            localStorage.setItem('preferred_language', langCode);
        } catch (e) {
            console.error('Failed to load language:', e);
            if (langCode !== 'en') await this.loadLanguage('en');
        }
    }

    async setLanguage(langCode) {
        await this.loadLanguage(langCode);
        window.closeModal(null, 'language-modal');
    }

    t(key) {
        const keys = key.split('.');
        let val = this.translations;
        for (const k of keys) {
            val = val ? val[k] : null;
        }
        return val || key;
    }

    applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (!key) return;
            const translated = this.t(key);
            if (translated === key) return; // No translation found

            // For elements with no children (plain text), use textContent directly
            if (el.children.length === 0) {
                el.textContent = translated;
                return;
            }

            // For elements with children (icons, spans inside), update only the text node
            // Find the first direct text node that has content
            let found = false;
            for (const node of el.childNodes) {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                    node.textContent = ` ${translated} `;
                    found = true;
                    break;
                }
            }
            // If no text node found, try to find a child span with no data-i18n of its own
            if (!found) {
                const span = el.querySelector('span:not([data-i18n])');
                if (span && span.children.length === 0) {
                    span.textContent = translated;
                }
            }
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (key) el.placeholder = this.t(key);
        });
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            if (key) el.title = this.t(key);
        });
    }

    updateDirection() {
        const langInfo = this.supportedLangs.find(l => l.code === this.currentLang);
        const dir = langInfo ? langInfo.dir : 'ltr';
        document.documentElement.dir = dir;
        document.documentElement.lang = this.currentLang;
        if (dir === 'rtl') document.body.classList.add('rtl');
        else document.body.classList.remove('rtl');
    }

    renderLanguageGrid() {
        const grid = document.getElementById('lang-grid');
        if (!grid) return;
        grid.innerHTML = this.supportedLangs.map(l => `
            <button class="lang-card ${l.code === this.currentLang ? 'active' : ''}" 
                    onclick="changeLanguage('${l.code}')">
                <div class="lang-name">${l.name}</div>
                <div class="lang-code">${l.code.toUpperCase()}</div>
            </button>
        `).join('');
    }

    filterLanguages(query) {
        const lower = query.toLowerCase();
        const cards = document.getElementById('lang-grid').children;
        Array.from(cards).forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(lower) ? '' : 'none';
        });
    }
}

const i18n = new LocalizationManager();
window.filterLanguages = () => i18n.filterLanguages(document.getElementById('lang-search').value);

// Check for language query param from launcher
const urlParams = new URLSearchParams(window.location.search);
const langParam = urlParams.get('lang');
if (langParam) {
    localStorage.setItem('preferred_language', langParam);
    // Clean URL
    const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({ path: newUrl }, '', newUrl);
}

// Global error handler for debugging
window.addEventListener('error', (event) => {
    console.error('Script Error:', event.error);
    showToast(`Script Error: ${event.message}`, 'error');
});

try {
    i18n.init();
} catch (e) {
    console.error('i18n init error:', e);
}

// --- Connectivity Check ---
async function checkConnectivity() {
    try {
        const res = await fetch('/api/connectivity', { signal: AbortSignal.timeout(5000) });
        const data = await res.json();
        const banner = document.getElementById('no-internet-banner');
        if (banner) {
            if (data.online) {
                banner.classList.add('hidden');
            } else {
                banner.classList.remove('hidden');
            }
        }
    } catch {
        // If fetch itself fails, server is running but can't check — show banner
        const banner = document.getElementById('no-internet-banner');
        if (banner) banner.classList.remove('hidden');
    }
}
checkConnectivity();
setInterval(checkConnectivity, 30000);

const ADV_DEFAULTS = {
    concurrent: 1,
    ratelimit: 0,
    retries: 10,
    chunksize: 0,
    audioFormat: 'mp3',
    audioQuality: '192',
    container: 'mp4',
    subtitles: false,
    subLangs: 'he,en',
    embedThumb: false,
    embedMetadata: false,
    sponsorblock: false,
    sbAction: 'mark',
    proxy: '',
    impersonate: false,
    sleep: 0,
    noCheckCert: false,
    archive: false,
    restrictFn: false,
    noOverwrites: false,
    noPlaylist: false,
    outtmpl: '',
    cookiesBrowser: ''
};

let pollInterval = null;
let urlQueue = [];
let renderedHistory = new Set();
let formatProbeTimer = null;
let selectedQuality = localStorage.getItem('preferred_quality') || 'best';
let currentProgress = 0; // For smooth animation

let logsUserScrolled = false;

// Detect manual scroll in logs
document.addEventListener('DOMContentLoaded', () => {
    const logsEl = document.getElementById('logs-content');
    if (logsEl) {
        logsEl.addEventListener('scroll', () => {
            const atBottom = logsEl.scrollHeight - logsEl.scrollTop - logsEl.clientHeight < 30;
            logsUserScrolled = !atBottom;
        });
    }
});

// Cancel download
// Cancel download
async function cancelDownload() {
    try {
        await fetch('/api/cancel', { method: 'POST' });
    } catch (e) { }
    if (pollInterval) clearInterval(pollInterval);
    stopEtaCountdown();
    resetDownloadBtn();
    showToast(i18n ? (i18n.t('toasts.download_cancelled') || 'Download cancelled') : 'Download cancelled', 'error');
};

// --- Quality Pills ---
function initQualityPills() {
    const pills = dom.qualityPills.querySelectorAll('.quality-pill');
    pills.forEach(pill => {
        if (pill.dataset.value === selectedQuality) {
            pill.classList.add('active');
        } else {
            pill.classList.remove('active');
        }
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            selectedQuality = pill.dataset.value;
            localStorage.setItem('preferred_quality', selectedQuality);
        });
    });
}
try {
    initQualityPills();
} catch (e) {
    console.error('initQualityPills error:', e);
}

// Also set settings modal dropdown
const settingsDQ = document.getElementById('default-quality-setting');
if (settingsDQ) settingsDQ.value = selectedQuality;

// --- Sidebar ---
// --- Sidebar ---
function toggleSidebar() {
    dom.sidebar.classList.toggle('open');
    dom.sidebarOverlay.classList.toggle('open');
};

async function openFolder() {
    await fetch('/api/open_folder', { method: 'POST' });
};

async function chooseFolder() {
    try {
        const res = await fetch('/api/choose_folder', { method: 'POST' });
        const data = await res.json();
        if (data.path) {
            document.getElementById('adv-save-path').value = data.path;
        }
    } catch (e) {
        console.error('Error choosing folder:', e);
    }
};

// --- Modals ---
// --- Modals ---
function openSettingsModal() {
    toggleSidebar();
    document.getElementById('settings-modal').classList.remove('hidden');
};
window.openAboutModal = function () {
    toggleSidebar();
    document.getElementById('about-modal').classList.remove('hidden');
};
window.openLanguageModal = function () {
    toggleSidebar();
    document.getElementById('language-modal').classList.remove('hidden');
};
function closeModal(e, id) {
    document.getElementById(id).classList.add('hidden');
}
function selectLang(btn) {
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
};

// --- Paste Button ---
dom.pasteBtn.addEventListener('click', async () => {
    try {
        const text = await navigator.clipboard.readText();
        dom.input.value = text.trim();
        dom.input.dispatchEvent(new Event('input'));
    } catch (e) {
        showToast(i18n.t('toasts.clipboard_error'), 'error');
    }
});

// --- Site Detection ---
dom.input.addEventListener('input', debounce(detectSite, 500));

async function detectSite() {
    const url = dom.input.value.trim();
    if (!url) {
        dom.siteBadge.classList.add('hidden');
        dom.smartLogin.classList.add('hidden');
        dom.qualityRow.classList.add('hidden');
        return;
    }

    try {
        const res = await fetch('/api/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const info = await res.json();

        if (info.site) {
            dom.siteBadge.classList.remove('hidden');
            dom.siteName.innerText = info.site;
            dom.siteIcon.innerText = info.icon;

            dom.siteBadge.className = 'site-badge-row';
            const classMap = {
                'Pornhub': 'ph', 'YouTube': 'yt', 'TikTok': 'tt',
                'Instagram': 'ig', 'Facebook': 'fb', 'General': 'gen'
            };
            if (classMap[info.site]) dom.siteBadge.classList.add(classMap[info.site]);

            if (info.protected && !info.has_cookies) {
                dom.smartLogin.classList.remove('hidden');
            } else {
                dom.smartLogin.classList.add('hidden');
            }

            dom.qualityRow.classList.remove('hidden');
            probeFormats(url);
        } else {
            dom.siteBadge.classList.add('hidden');
            if (url.startsWith('http')) {
                dom.qualityRow.classList.remove('hidden');
                probeFormats(url);
            }
        }
    } catch (e) { }
}

// --- Format Probing ---
async function probeFormats(url) {
    if (formatProbeTimer) clearTimeout(formatProbeTimer);
    formatProbeTimer = setTimeout(async () => {
        dom.qualityLoading.classList.remove('hidden');
        try {
            const res = await fetch('/api/formats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await res.json();

            if (data.formats && data.formats.length > 0) {
                // Rebuild pills dynamically
                dom.qualityPills.innerHTML = '<button class="quality-pill" data-value="best">MAX</button>';
                data.formats.forEach(f => {
                    const btn = document.createElement('button');
                    btn.className = 'quality-pill';
                    btn.dataset.value = f.value;
                    btn.textContent = f.label.split(' (')[0]; // Short label
                    dom.qualityPills.appendChild(btn);
                });

                // Re-init click handlers and restore selection
                const pills = dom.qualityPills.querySelectorAll('.quality-pill');
                let foundSaved = false;
                pills.forEach(pill => {
                    if (pill.dataset.value === selectedQuality) {
                        pill.classList.add('active');
                        foundSaved = true;
                    }
                    pill.addEventListener('click', () => {
                        pills.forEach(p => p.classList.remove('active'));
                        pill.classList.add('active');
                        selectedQuality = pill.dataset.value;
                        localStorage.setItem('preferred_quality', selectedQuality);
                    });
                });
                if (!foundSaved) {
                    pills[0].classList.add('active');
                    selectedQuality = 'best';
                }
            }
        } catch (e) { }
        finally { dom.qualityLoading.classList.add('hidden'); }
    }, 800);
}

// --- Add to Queue ---
dom.addQueueBtn.addEventListener('click', () => {
    const url = dom.input.value.trim();
    if (!url) return;
    urlQueue.push(url);
    dom.input.value = '';
    dom.siteBadge.classList.add('hidden');
    renderQueue();
});

function renderQueue() {
    dom.queueCount.innerText = urlQueue.length;
    if (urlQueue.length === 0) {
        dom.urlQueue.classList.add('hidden');
        return;
    }
    dom.urlQueue.classList.remove('hidden');
    dom.queueList.innerHTML = urlQueue.map((url, i) => `
        <div class="queue-item">
            <button class="queue-remove" onclick="removeFromQueue(${i})">
                <i class="ph-bold ph-x"></i>
            </button>
            <span>${url}</span>
        </div>
    `).join('');
}

function removeFromQueue(index) {
    urlQueue.splice(index, 1);
    renderQueue();
};

// --- Login ---
dom.loginBtn.addEventListener('click', async () => {
    dom.loginBtn.disabled = true;
    dom.loginBtn.innerHTML = `<i class="ph-bold ph-spinner ph-spin"></i> ${i18n.t('dashboard.login_connecting')}`;
    await fetch('/api/login', { method: 'POST' });
    startPollingLogins();
});

// --- Download ---
dom.downloadBtn.addEventListener('click', async () => {
    const currentUrl = dom.input.value.trim();
    let allUrls = [...urlQueue];
    if (currentUrl) allUrls.push(currentUrl);
    if (allUrls.length === 0) return;

    const quality = selectedQuality;
    const urlText = allUrls.join('\n');

    urlQueue = [];
    renderQueue();
    dom.input.value = '';
    dom.siteBadge.classList.add('hidden');
    dom.qualityRow.classList.add('hidden');

    dom.downloadBtn.disabled = true;
    dom.downloadBtn.innerHTML = `<i class="ph-bold ph-spinner ph-spin"></i> ${i18n.t('dashboard.initializing') || 'Initializing...'}`;
    dom.downloadBtn.classList.add('downloading');
    dom.downloadBtn.classList.remove('complete');
    document.getElementById('cancel-btn').classList.remove('hidden');
    dom.errorMsg.classList.add('hidden');
    dom.progressWrap.classList.remove('hidden');
    dom.dashboard.classList.remove('hidden');

    currentProgress = 0;
    dom.progressBar.style.width = '0%';
    dom.progressText.innerText = '0%';
    logsUserScrolled = false;

    try {
        const res = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlText, quality, advanced: getAdvancedSettings() })
        });
        const data = await res.json();
        if (data.error) throw data.error;

        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(updateStatus, 500);
    } catch (e) {
        showError(e);
        resetDownloadBtn();
    }
});

// --- Smooth Progress Animation ---
function smoothProgress(targetPercent) {
    const diff = targetPercent - currentProgress;
    if (Math.abs(diff) < 0.001) return;

    // Smooth interpolation
    currentProgress += diff * 0.15;
    if (currentProgress > targetPercent) currentProgress = targetPercent;

    const displayPercent = Math.round(currentProgress * 100);
    dom.progressBar.style.width = displayPercent + '%';
    dom.progressText.innerText = displayPercent + '%';

    if (Math.abs(targetPercent - currentProgress) > 0.001) {
        requestAnimationFrame(() => smoothProgress(targetPercent));
    }
}

// --- ETA / Status Globals ---
let etaSeconds = null;
let etaCountdownInterval = null;
let etaLastSyncTime = 0;
const ETA_SYNC_INTERVAL = 10; // Only resync from server every 10 seconds

function formatEtaDisplay(totalSec) {
    if (totalSec == null || totalSec <= 0) return '--';
    totalSec = Math.round(totalSec);
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function startEtaCountdown() {
    if (etaCountdownInterval) return; // Already running
    etaCountdownInterval = setInterval(() => {
        if (etaSeconds !== null && etaSeconds > 0) {
            etaSeconds--;
            dom.stats.eta.innerText = formatEtaDisplay(etaSeconds);
        } else if (etaSeconds !== null && etaSeconds <= 0) {
            dom.stats.eta.innerText = '--';
        }
    }, 1000);
}

function stopEtaCountdown() {
    if (etaCountdownInterval) {
        clearInterval(etaCountdownInterval);
        etaCountdownInterval = null;
    }
    etaSeconds = null;
    etaLastSyncTime = 0;
}

// --- Status Polling ---
async function updateStatus() {
    try {
        const res = await fetch('/api/status');
        const state = await res.json();

        // Smooth progress
        smoothProgress(state.percent);

        // Stats - clean display
        dom.stats.speed.innerText = cleanStat(state.speed);
        dom.stats.total.innerText = cleanStat(state.total);

        // ETA — stable countdown, resync from server every 10 seconds
        const now = Date.now() / 1000;
        const etaStr = cleanStat(state.eta);

        // Parse ETA string to seconds (inline — no external function dependency)
        let serverEta = null;
        if (etaStr && etaStr !== '--') {
            // Try "HH:MM:SS" or "MM:SS" format
            const colonMatch = etaStr.match(/(\d+):(\d+)(?::(\d+))?/);
            if (colonMatch) {
                if (colonMatch[3]) {
                    serverEta = parseInt(colonMatch[1]) * 3600 + parseInt(colonMatch[2]) * 60 + parseInt(colonMatch[3]);
                } else {
                    serverEta = parseInt(colonMatch[1]) * 60 + parseInt(colonMatch[2]);
                }
            } else {
                // Try "Xs" format
                const secMatch = etaStr.match(/(\d+)\s*s/);
                if (secMatch) serverEta = parseInt(secMatch[1]);
            }
        }

        if (serverEta !== null && serverEta > 0) {
            // Only resync if enough time passed or first value
            if (etaSeconds === null || (now - etaLastSyncTime) >= ETA_SYNC_INTERVAL) {
                etaSeconds = serverEta;
                etaLastSyncTime = now;
                dom.stats.eta.innerText = formatEtaDisplay(etaSeconds);
                startEtaCountdown();
            }
        } else if (etaSeconds === null) {
            // No ETA available and no countdown running
            dom.stats.eta.innerText = '--';
        }

        // Update button text while downloading
        if (state.status === 'downloading' && state.percent > 0) {
            const pct = Math.round(state.percent * 100);
            let text = `${i18n.t('dashboard.downloading_pct').replace('{pct}', pct)}`;

            // Playlist info
            if (state.playlist_count && state.playlist_count > 1) {
                text += ` <span class="playlist-info">(${state.playlist_index}/${state.playlist_count})</span>`;
            }

            // 99% Stuck Fix: Show "Processing..." if > 98%
            if (state.percent >= 0.99) {
                dom.downloadBtn.innerHTML = `<i class="ph-bold ph-gear ph-spin"></i> ${i18n.t('dashboard.processing')}`;
                dom.stats.eta.innerText = '--';
            } else {
                dom.downloadBtn.innerHTML = `<i class="ph-bold ph-spinner ph-spin"></i> ${text}`;
            }
        } else if (state.status === 'processing') {
            stopEtaCountdown();
            dom.downloadBtn.innerHTML = `<i class="ph-bold ph-gear ph-spin"></i> ${i18n.t('dashboard.processing')}`;
            dom.stats.eta.innerText = '--';
            dom.stats.speed.innerText = '--';
        }

        // Logs (smart scroll: only auto-scroll if user hasn't manually scrolled up)
        dom.logsContent.innerText = state.logs.join('\n');
        if (!logsUserScrolled) {
            dom.logsContent.scrollTop = dom.logsContent.scrollHeight;
        }

        // History
        if (state.history) {
            state.history.forEach(item => {
                const key = item.filename || item.title;
                if (!renderedHistory.has(key)) {
                    renderedHistory.add(key);
                    renderHistoryCard(item);
                }
            });
        }

        if (state.status === 'finished') {
            clearInterval(pollInterval);
            stopEtaCountdown();
            currentProgress = 1.0;
            dom.progressBar.style.width = '100%';
            dom.progressText.innerText = '100%';
            dom.stats.eta.innerText = '--';
            dom.downloadBtn.disabled = false;
            dom.downloadBtn.innerHTML = `<i class="ph-bold ph-check-circle"></i> ${i18n.t('dashboard.download_complete_btn')}`;
            dom.downloadBtn.classList.remove('downloading');
            dom.downloadBtn.classList.add('complete');
            document.getElementById('cancel-btn').classList.add('hidden');
            showToast(i18n.t('toasts.download_complete'), 'success');
            setTimeout(() => resetDownloadBtn(), 4000);
        }

        if (state.status === 'error') {
            clearInterval(pollInterval);
            stopEtaCountdown();
            showError(state.error_msg);
            resetDownloadBtn();
        }

        // Handle cancelled state (status goes back to idle during download)
        if (state.status === 'idle' && dom.downloadBtn.classList.contains('downloading')) {
            clearInterval(pollInterval);
            stopEtaCountdown();
            resetDownloadBtn();
            showToast(i18n.t('toasts.download_cancelled') || 'Download cancelled', 'error');
        }

        if (state.logs.join('').includes('Login Successful')) {
            dom.smartLogin.classList.add('hidden');
        }
    } catch (e) { }
}

// --- ETA Countdown Timer ---
function parseEtaToSeconds(etaStr) {
    if (!etaStr || etaStr === '--') return null;
    // Handle formats: "1:23", "01:23", "1:02:34", "45s", "2m 30s"
    etaStr = etaStr.trim();

    // HH:MM:SS or MM:SS
    const colonMatch = etaStr.match(/(\d+):(\d+)(?::(\d+))?/);
    if (colonMatch) {
        if (colonMatch[3]) {
            return parseInt(colonMatch[1]) * 3600 + parseInt(colonMatch[2]) * 60 + parseInt(colonMatch[3]);
        }
        return parseInt(colonMatch[1]) * 60 + parseInt(colonMatch[2]);
    }

    // Pure seconds
    const secMatch = etaStr.match(/(\d+)\s*s/);
    if (secMatch) return parseInt(secMatch[1]);

    return null;
}

function formatEtaSeconds(totalSec) {
    if (totalSec <= 0) return '00:00';
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function startEtaCountdown() {
    stopEtaCountdown();
    dom.stats.eta.innerText = formatEtaSeconds(etaSeconds);
    etaCountdownInterval = setInterval(() => {
        if (etaSeconds > 0) {
            etaSeconds--;
            dom.stats.eta.innerText = formatEtaSeconds(etaSeconds);
        } else {
            dom.stats.eta.innerText = '00:00';
            stopEtaCountdown();
        }
    }, 1000);
}

function stopEtaCountdown() {
    if (etaCountdownInterval) {
        clearInterval(etaCountdownInterval);
        etaCountdownInterval = null;
    }
    etaSeconds = null;
}

function cleanStat(val) {
    if (!val || val === 'N/A' || val === 'None') return '--';
    // Remove ANSI codes
    return val.replace(/\x1B\[[0-9;]*m/g, '').trim();
}

// --- Auto-paste URL on focus ---
dom.input.addEventListener('focus', async () => {
    if (dom.input.value.trim()) return; // Don't overwrite existing text
    try {
        const text = await navigator.clipboard.readText();
        if (text && (text.startsWith('http://') || text.startsWith('https://'))) {
            dom.input.value = text;
            dom.input.dispatchEvent(new Event('input'));
        }
    } catch (e) { } // Clipboard permission denied — ignore silently
});

function resetDownloadBtn() {
    dom.downloadBtn.disabled = false;
    dom.downloadBtn.innerHTML = `<span class="btn-text">${i18n.t('dashboard.download_btn')}</span><span class="btn-icon"><i class="ph-bold ph-download-simple"></i></span>`;
    dom.downloadBtn.style.background = '';
    dom.downloadBtn.classList.remove('downloading', 'complete');
    document.getElementById('cancel-btn').classList.add('hidden');
}

// --- History Cards ---
function renderHistoryCard(item) {
    const card = document.createElement('div');
    card.className = 'history-card';

    // Detect if this is an audio file
    const audioExts = ['.mp3', '.m4a', '.opus', '.wav', '.aac', '.flac', '.ogg', '.wma'];
    const fname = (item.filename || '').toLowerCase();
    const isAudio = audioExts.some(ext => fname.endsWith(ext));

    const thumbStyle = item.thumbnail && !isAudio ? `background-image: url('${item.thumbnail}')` : '';
    const thumbClass = isAudio ? 'thumb-preview audio-thumb' : 'thumb-preview';
    const thumbIcon = isAudio
        ? '<i class="ph-bold ph-music-notes" style="font-size:1.5rem;color:var(--neon-cyan)"></i>'
        : (item.thumbnail ? '' : '<i class="ph-bold ph-film-strip" style="font-size:1.5rem;color:var(--text-dim)"></i>');

    const safeFilename = (item.filename || '').replace(/\\/g, '/').replace(/'/g, "\\'");

    const playIcon = isAudio ? 'ph-play' : 'ph-play';
    const playLabel = isAudio ? (i18n.t('history.open_file') || 'Play') : i18n.t('history.open_file');

    card.innerHTML = `
        <div class="${thumbClass}" style="${thumbStyle}" onclick="playFile(decodeURIComponent('${encodeURIComponent(safeFilename)}'))">
            ${thumbIcon}
            <div class="play-overlay"><i class="ph-fill ph-play"></i></div>
        </div>
        <div class="history-info">
            <div class="history-title">${item.title || 'Unknown'}</div>
            <div class="history-meta">${item.index + 1}/${item.total} - ${i18n.t('history.download_complete')}</div>
        </div>
        <div class="history-actions">
            <button class="mini-btn play" onclick="playFile(decodeURIComponent('${encodeURIComponent(safeFilename)}'))" title="${playLabel}">
                <i class="ph-bold ${isAudio ? 'ph-play' : 'ph-play'}"></i>
            </button>
            <button class="mini-btn folder" onclick="openFolder()" title="${i18n.t('history.open_folder')}">
                <i class="ph-bold ph-folder-open"></i>
            </button>
        </div>
    `;

    dom.historySection.prepend(card);
}

async function playFile(filename) {
    if (!filename) return;
    try {
        const res = await fetch('/api/play_file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        const data = await res.json();
        if (!data.success) {
            showToast(i18n.t('toasts.play_error'), 'error');
        }
    } catch (e) {
        showToast(i18n.t('toasts.play_error_generic'), 'error');
    }
};

// --- Login Polling ---
function startPollingLogins() {
    const int = setInterval(async () => {
        const res = await fetch('/api/status');
        const state = await res.json();
        const logs = state.logs.join('\n');

        if (logs.includes('Login Successful')) {
            clearInterval(int);
            dom.smartLogin.classList.add('hidden');
            dom.loginBtn.disabled = false;
            dom.loginBtn.innerHTML = `<i class="ph-bold ph-key"></i> ${i18n.t('dashboard.login_btn')}`;
            showToast(i18n.t('toasts.login_success'), 'success');
        }
    }, 1000);
}

// --- Toast ---
function showToast(msg, type = 'error') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="ph-bold ${type === 'success' ? 'ph-check-circle' : 'ph-warning-circle'}"></i>
        <span>${msg}</span>
    `;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function showError(msg) {
    dom.errorMsg.classList.add('hidden');
    showToast(msg, 'error');
}

// --- Utils ---
function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

// --- Copy Logs ---
// --- Copy Logs ---
async function copyLogs() {
    try {
        const text = dom.logsContent.innerText;
        await navigator.clipboard.writeText(text);
        showToast(i18n.t('toasts.copy_logs'), 'success');
    } catch (e) {
        showToast(i18n.t('toasts.copy_error'), 'error');
    }
};

// --- Logs Modal ---
function openLogsModal() {
    const modal = document.getElementById('logs-modal');
    if (modal) {
        modal.classList.remove('hidden');
        // Scroll logs to bottom
        const logsEl = document.getElementById('logs-content');
        if (logsEl) setTimeout(() => logsEl.scrollTop = logsEl.scrollHeight, 100);
    }
};

// ============== ADVANCED SETTINGS ==============

// ADV_DEFAULTS moved to top to fix initialization error

function getAdvancedSettings() {
    try {
        const saved = localStorage.getItem('adv_settings');
        return saved ? { ...ADV_DEFAULTS, ...JSON.parse(saved) } : { ...ADV_DEFAULTS };
    } catch (e) { return { ...ADV_DEFAULTS }; }
}

function loadAdvancedSettingsToUI() {
    const s = getAdvancedSettings();
    document.getElementById('adv-concurrent').value = s.concurrent;
    document.getElementById('adv-concurrent').nextElementSibling.textContent = s.concurrent;
    document.getElementById('adv-ratelimit').value = s.ratelimit;
    document.getElementById('adv-retries').value = s.retries;
    document.getElementById('adv-chunksize').value = s.chunksize;
    document.getElementById('adv-audio-format').value = s.audioFormat;
    document.getElementById('adv-audio-quality').value = s.audioQuality;
    document.getElementById('adv-container').value = s.container;
    document.getElementById('adv-subtitles').checked = s.subtitles;
    document.getElementById('adv-sub-langs').value = s.subLangs;
    document.getElementById('adv-sub-langs-row').style.display = s.subtitles ? '' : 'none';
    document.getElementById('adv-embed-thumb').checked = s.embedThumb;
    document.getElementById('adv-embed-metadata').checked = s.embedMetadata;
    document.getElementById('adv-sponsorblock').checked = s.sponsorblock;
    document.getElementById('adv-sb-action').value = s.sbAction;
    document.getElementById('adv-sb-action-row').style.display = s.sponsorblock ? '' : 'none';
    document.getElementById('adv-proxy').value = s.proxy;
    document.getElementById('adv-impersonate').checked = s.impersonate;
    document.getElementById('adv-sleep').value = s.sleep;
    document.getElementById('adv-no-check-cert').checked = s.noCheckCert;
    document.getElementById('adv-archive').checked = s.archive;
    document.getElementById('adv-restrict-fn').checked = s.restrictFn;
    document.getElementById('adv-no-overwrites').checked = s.noOverwrites;
    document.getElementById('adv-no-playlist').checked = s.noPlaylist;
    document.getElementById('adv-outtmpl').value = s.outtmpl;
    document.getElementById('adv-cookies-browser').value = s.cookiesBrowser;
    document.getElementById('adv-save-path').value = s.savePath || '';
}

function readAdvancedSettingsFromUI() {
    return {
        concurrent: parseInt(document.getElementById('adv-concurrent').value) || 1,
        ratelimit: parseInt(document.getElementById('adv-ratelimit').value) || 0,
        retries: parseInt(document.getElementById('adv-retries').value) || 10,
        chunksize: parseInt(document.getElementById('adv-chunksize').value) || 0,
        audioFormat: document.getElementById('adv-audio-format').value,
        audioQuality: document.getElementById('adv-audio-quality').value,
        container: document.getElementById('adv-container').value,
        subtitles: document.getElementById('adv-subtitles').checked,
        subLangs: document.getElementById('adv-sub-langs').value,
        embedThumb: document.getElementById('adv-embed-thumb').checked,
        embedMetadata: document.getElementById('adv-embed-metadata').checked,
        sponsorblock: document.getElementById('adv-sponsorblock').checked,
        sbAction: document.getElementById('adv-sb-action').value,
        proxy: document.getElementById('adv-proxy').value.trim(),
        impersonate: document.getElementById('adv-impersonate').checked,
        sleep: parseInt(document.getElementById('adv-sleep').value) || 0,
        noCheckCert: document.getElementById('adv-no-check-cert').checked,
        archive: document.getElementById('adv-archive').checked,
        restrictFn: document.getElementById('adv-restrict-fn').checked,
        noOverwrites: document.getElementById('adv-no-overwrites').checked,
        noPlaylist: document.getElementById('adv-no-playlist').checked,
        outtmpl: document.getElementById('adv-outtmpl').value.trim(),
        outtmpl: document.getElementById('adv-outtmpl').value.trim(),
        cookiesBrowser: document.getElementById('adv-cookies-browser').value,
        savePath: document.getElementById('adv-save-path').value.trim()
    };
}

function openAdvancedSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
    loadAdvancedSettingsToUI();
    document.getElementById('advanced-modal').classList.remove('hidden');
};

function toggleAdvGroup(header) {
    header.parentElement.classList.toggle('open');
};

function saveAdvancedSettings() {
    const settings = readAdvancedSettingsFromUI();
    localStorage.setItem('adv_settings', JSON.stringify(settings));
    showToast(i18n.t('toasts.advanced_saved'), 'success');
    document.getElementById('advanced-modal').classList.add('hidden');
};

function resetAdvancedSettings() {
    localStorage.removeItem('adv_settings');
    loadAdvancedSettingsToUI();
    showToast(i18n.t('toasts.advanced_reset'), 'success');
};

// Conditional fields: toggle subtitles langs row
const advSubs = document.getElementById('adv-subtitles');
if (advSubs) {
    advSubs.addEventListener('change', function () {
        const row = document.getElementById('adv-sub-langs-row');
        if (row) row.style.display = this.checked ? '' : 'none';
    });
}

// Conditional fields: toggle SponsorBlock action row
const advSB = document.getElementById('adv-sponsorblock');
if (advSB) {
    advSB.addEventListener('change', function () {
        const row = document.getElementById('adv-sb-action-row');
        if (row) row.style.display = this.checked ? '' : 'none';
    });
}

// ============== UPDATE SYSTEM ==============

async function checkForUpdates() {
    const btn = document.getElementById('update-btn');
    const origHTML = btn.innerHTML;
    btn.innerHTML = `<i class="ph-bold ph-spinner ph-spin"></i><span>${i18n.t('updates.checking')}</span>`;
    btn.disabled = true;

    try {
        const res = await fetch('/api/check_updates');
        const data = await res.json();

        if (data.ytdlp_update) {
            const badge = document.getElementById('update-badge');
            badge.classList.remove('hidden');
            badge.textContent = '1';

            btn.innerHTML = `<i class="ph-bold ph-arrow-clockwise"></i><span>${i18n.t('updates.available').replace('{version}', data.ytdlp_latest)}</span>`;
            btn.onclick = () => runYtdlpUpdate();
            btn.classList.add('update-available');
        } else {
            showToast(i18n.t('updates.uptodate'), 'success');
            btn.innerHTML = origHTML;
        }
    } catch (e) {
        showToast(i18n.t('updates.error_check'), 'error');
        btn.innerHTML = origHTML;
    }
    btn.disabled = false;
};

async function runYtdlpUpdate() {
    const btn = document.getElementById('update-btn');
    btn.innerHTML = `<i class="ph-bold ph-spinner ph-spin"></i><span>${i18n.t('updates.updating')}</span>`;
    btn.disabled = true;

    try {
        const res = await fetch('/api/update_ytdlp', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast(i18n.t('updates.success'), 'success');
            const badge = document.getElementById('update-badge');
            badge.classList.add('hidden');
            btn.classList.remove('update-available');
            btn.innerHTML = `<i class="ph-bold ph-arrow-clockwise"></i><span>${i18n.t('sidebar.check_updates')}</span>`;
            btn.onclick = () => checkForUpdates();
        } else {
            showToast(i18n.t('updates.error_update_detail').replace('{msg}', data.error || ''), 'error');
        }
    } catch (e) {
        showToast(i18n.t('updates.error'), 'error');
    }
    btn.disabled = false;
}

// Auto-check for updates on page load (silent)
setTimeout(async () => {
    try {
        const res = await fetch('/api/check_updates');
        const data = await res.json();
        if (data.ytdlp_update) {
            const badge = document.getElementById('update-badge');
            badge.classList.remove('hidden');
            badge.textContent = '1';
            const btn = document.getElementById('update-btn');
            btn.innerHTML = `<i class="ph-bold ph-arrow-clockwise"></i><span>${i18n.t('updates.available_badge')}</span><span id="update-badge" class="update-badge">1</span>`;
        }
    } catch (e) { }
}, 3000);
