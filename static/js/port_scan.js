// ==================== PORT SCANNING SIMULATOR ====================
let currentScan = null;
let scanPackets = [];
let scanIndex = -1;
let scanTimer = null;
let scanPaused = false;

document.addEventListener('DOMContentLoaded', () => {
    if (SCAN_TYPES && SCAN_TYPES.length > 0) {
        selectScanType(SCAN_TYPES[0].id, null, true);
    }
    if (SCAN_SCENARIOS && SCAN_SCENARIOS.length > 0) {
        selectScenario(SCAN_SCENARIOS[0].id, null, true);
    }
});

// ==================== SCAN TYPE SELECTOR ====================
function selectScanType(scanId, event, silent) {
    if (event) {
        event.preventDefault();
        document.querySelectorAll('.scan-tab').forEach(t => t.classList.remove('active'));
        event.currentTarget.classList.add('active');
    }

    const scan = SCAN_TYPES.find(s => s.id === scanId);
    if (!scan) return;

    currentScan = scan;
    scanPackets = scan.packets || [];
    scanIndex = -1;
    scanPaused = false;

    if (scanTimer) { clearInterval(scanTimer); scanTimer = null; }
    updateScanPlayButton('▶ Start Scan');
    renderScanPackets();
    renderScanInfo();

    document.querySelectorAll('.scan-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-scan-id') === scanId);
    });
}

function renderScanPackets() {
    const container = document.getElementById('scanPackets');
    if (!container) return;
    container.innerHTML = '';
    if (scanPackets.length === 0) return;

    scanPackets.forEach((pkt, i) => {
        const div = document.createElement('div');
        div.className = 'scan-packet';
        div.style.opacity = '0.3';
        const dirClass = pkt.from === 'Attacker' ? 'packet-right' : 'packet-left';
        div.innerHTML = `
            <div class="pkt-label">Step ${pkt.seq}</div>
            <div class="pkt-arrow ${dirClass}">
                <div class="pkt-flag" style="background: ${pkt.flag_color}">${pkt.flag}</div>
                <div class="pkt-line"></div>
            </div>
            <div class="pkt-text">${pkt.label}</div>
        `;
        container.appendChild(div);
    });
}

function renderScanInfo() {
    const panel = document.getElementById('scanInfoPanel');
    if (!panel || !currentScan) return;

    const difficultyClass = currentScan.difficulty.toLowerCase();
    panel.innerHTML = `
        <div class="scan-info-header" style="--scan-color: ${currentScan.color}">
            <div class="scan-info-icon">${currentScan.icon}</div>
            <div>
                <h3>${currentScan.name}</h3>
                <p class="scan-info-nickname">${currentScan.nickname}</p>
            </div>
            <div class="scan-info-badges">
                <span class="badge-difficulty diff-${difficultyClass}">${currentScan.difficulty}</span>
                <span class="scan-info-badge">Stealth: ${currentScan.stealth}</span>
                <span class="scan-info-badge">Speed: ${currentScan.speed}</span>
                <span class="scan-info-badge">${currentScan.requires_root ? '🔒 Root' : '👤 User'}</span>
            </div>
        </div>
        <p class="scan-info-desc">${currentScan.description}</p>
        <div class="scan-info-why">
            <strong>Why it's ${currentScan.stealth === 'High' ? 'stealthy' : 'detectable'}:</strong> ${currentScan.why_stealthy}
        </div>
        <div class="scan-terminal-mini">
            <div class="terminal-bar-mini">
                <span class="term-dot red"></span>
                <span class="term-dot yellow"></span>
                <span class="term-dot green"></span>
                <span class="term-title-mini">nmap output</span>
            </div>
            <pre class="terminal-output-mini">$ ${currentScan.command}\n${currentScan.output}</pre>
        </div>
    `;
}

function toggleScanSim() {
    if (scanPackets.length === 0) return;
    if (scanTimer && !scanPaused) { pauseScanSim(); return; }
    if (scanPaused) { resumeScanSim(); return; }
    startScanSim();
}

function startScanSim() {
    if (scanTimer) clearInterval(scanTimer);
    scanIndex = 0;
    scanPaused = false;
    highlightPacket(0);
    updateScanPlayButton('⏸ Pause');
    scanTimer = setInterval(() => {
        scanIndex++;
        if (scanIndex >= scanPackets.length) {
            clearInterval(scanTimer);
            scanTimer = null;
            updateScanPlayButton('▶ Replay');
            return;
        }
        highlightPacket(scanIndex);
    }, 1800);
}

function pauseScanSim() {
    if (!scanTimer) return;
    clearInterval(scanTimer);
    scanTimer = null;
    scanPaused = true;
    updateScanPlayButton('▶ Resume');
}

function resumeScanSim() {
    if (!scanPaused) return;
    scanPaused = false;
    updateScanPlayButton('⏸ Pause');
    scanTimer = setInterval(() => {
        scanIndex++;
        if (scanIndex >= scanPackets.length) {
            clearInterval(scanTimer);
            scanTimer = null;
            updateScanPlayButton('▶ Replay');
            return;
        }
        highlightPacket(scanIndex);
    }, 1800);
}

function highlightPacket(index) {
    const packets = document.querySelectorAll('.scan-packet');
    packets.forEach((p, i) => {
        p.style.opacity = i <= index ? '1' : '0.3';
        p.classList.toggle('active', i === index);
    });
    if (packets[index]) packets[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function resetScanSim() {
    if (scanTimer) clearInterval(scanTimer);
    scanTimer = null;
    scanPaused = false;
    scanIndex = -1;
    updateScanPlayButton('▶ Start Scan');
    document.querySelectorAll('.scan-packet').forEach(p => {
        p.style.opacity = '0.3';
        p.classList.remove('active');
    });
}

function updateScanPlayButton(label) {
    const btn = document.getElementById('scanPlayBtn');
    if (!btn) return;
    btn.textContent = label;
    btn.classList.remove('is-playing', 'is-paused');
    if (label.includes('Pause')) btn.classList.add('is-playing');
    if (label.includes('Resume')) btn.classList.add('is-paused');
}

// ==================== SCAN SCENARIO SELECTOR ====================
function selectScenario(scenarioId, event, silent) {
    if (event) {
        event.preventDefault();
        document.querySelectorAll('.scenario-tab').forEach(t => t.classList.remove('active'));
        event.currentTarget.classList.add('active');
    }

    const scen = SCAN_SCENARIOS.find(s => s.id === scenarioId);
    if (!scen) return;

    const display = document.getElementById('scenarioDisplay');
    if (!display) return;

    // Build packet flow HTML
    const packetFlowHtml = scen.packet_flow.map(pkt => `
        <div class="scenario-packet">
            <div class="sp-from">${pkt.from}</div>
            <div class="sp-arrow">
                <span class="sp-flag" style="background: ${pkt.flag_color}">${pkt.flag}</span>
                <span class="sp-line"></span>
            </div>
            <div class="sp-to">${pkt.to}</div>
            <div class="sp-label">${pkt.label}</div>
        </div>
    `).join('');

    display.innerHTML = `
        <div class="scenario-card" style="--scen-color: ${scen.color}">
            <div class="scenario-header">
                <div class="scenario-icon">${scen.icon}</div>
                <div>
                    <h3>${scen.title}</h3>
                    <p class="scenario-situation">${scen.situation}</p>
                </div>
            </div>

            <p class="scenario-desc">${scen.description}</p>

            <div class="scenario-grid">
                <div class="scenario-block">
                    <h4>📄 Example Output</h4>
                    <div class="scan-terminal-mini">
                        <pre class="terminal-output-mini">${scen.example_output}</pre>
                    </div>
                </div>

                <div class="scenario-block">
                    <h4>🎬 Packet Flow</h4>
                    <div class="scenario-flow">${packetFlowHtml}</div>
                </div>
            </div>

            <div class="scenario-info">
                <div class="scenario-info-item">
                    <strong>💡 Meaning:</strong> ${scen.meaning}
                </div>
                <div class="scenario-info-item highlight">
                    <strong>➡️ Next Step:</strong> ${scen.next_action}
                </div>
            </div>
        </div>
    `;

    document.querySelectorAll('.scenario-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-scenario-id') === scenarioId);
    });
}

// ==================== NMAP COMMAND MODAL ====================
let currentNmapCmd = null;

function openNmapModal(card) {
    const cmd = JSON.parse(card.getAttribute('data-command'));
    currentNmapCmd = cmd;

    const modal = document.getElementById('nmapModal');
    if (!modal) return;

    document.getElementById('nmapModalHeader').style.setProperty('--modal-color', cmd.color);
    document.getElementById('nmapModalIcon').style.background = cmd.color;
    document.getElementById('nmapModalIcon').textContent = '$';
    document.getElementById('nmapModalTitle').textContent = cmd.command;
    document.getElementById('nmapModalSubtitle').textContent = cmd.description;
    document.getElementById('nmapModalCommand').textContent = '$ ' + cmd.command;
    document.getElementById('nmapModalCommand').style.borderColor = cmd.color;
    document.getElementById('nmapModalExplanation').textContent = cmd.explanation;
    document.getElementById('nmapModalOutput').textContent = '$ ' + cmd.command + '\n\n' + cmd.output;
    document.getElementById('nmapModalScenario').textContent = cmd.scenario;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeNmapModal(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('nmapModal');
    if (modal) modal.classList.remove('active');
    document.body.style.overflow = '';
}

function copyCurrentCommand() {
    if (!currentNmapCmd) return;
    navigator.clipboard.writeText(currentNmapCmd.command).then(() => {
        const btn = event.target;
        const original = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = original; }, 1500);
    });
}

// Keyboard accessibility for command cards
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nmap-command-card').forEach(card => {
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openNmapModal(card);
            }
        });
    });
});

// Escape closes modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeNmapModal();
    }
});
