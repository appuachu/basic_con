// ==================== BRUTE FORCE MODULE (ISOLATED SCOPE) ====================
(function () {
    'use strict';

    // ==================== STATE ====================
    let currentTool = null;
    let currentSimSteps = [];
    let currentSimIndex = 0;
    let bfSimTimer = null;
    let isSimPaused = false;
    let currentToolColor = '#00d4ff';

    // ==================== HELPERS ====================
    function escapeHtml(str) {
        if (str === undefined || str === null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // ==================== OPEN TOOL MODAL ====================
    function openToolModal(card) {
        let tool;
        try {
            tool = JSON.parse(card.getAttribute('data-tool'));
        } catch (e) {
            console.error('Failed to parse tool JSON:', e);
            return;
        }

        currentTool = tool;
        currentToolColor = tool.color || '#00d4ff';

        const modal = document.getElementById('toolModal');
        if (!modal) {
            console.error('Modal element #toolModal not found!');
            return;
        }

        // ----- Header -----
        const header = document.getElementById('toolModalHeader');
        if (header) header.style.setProperty('--modal-color', tool.color || '#00d4ff');

        const icon = document.getElementById('toolModalIcon');
        if (icon) {
            icon.textContent = tool.icon || '🔧';
            icon.style.background = tool.color || '#00d4ff';
        }

        const title = document.getElementById('toolModalTitle');
        if (title) title.textContent = tool.name || 'Tool';

        const subtitle = document.getElementById('toolModalSubtitle');
        if (subtitle) subtitle.textContent = tool.tagline || '';

        // ----- About -----
        const desc = document.getElementById('toolModalDesc');
        if (desc) desc.textContent = tool.description || 'No description available.';

        // ----- Install -----
        const install = document.getElementById('toolModalInstall');
        if (install) install.textContent = '$ ' + (tool.install || 'N/A');

        // ----- Flags -----
        const flagsContainer = document.getElementById('toolModalFlags');
        if (flagsContainer) {
            flagsContainer.innerHTML = '';
            (tool.common_flags || []).forEach(f => {
                const div = document.createElement('div');
                div.className = 'flag-mini';
                div.innerHTML = `<code>${escapeHtml(f.flag)}</code><span>${escapeHtml(f.desc)}</span>`;
                flagsContainer.appendChild(div);
            });
        }

        // ----- Success Examples -----
        renderExamples('toolModalExamples', tool.examples, false);

        // ----- Failure Examples -----
        renderExamples('toolModalFailures', tool.failures, true);

        // ----- Reset Tabs to Success -----
        document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
        const successBtn = document.getElementById('tabSuccessBtn');
        if (successBtn) successBtn.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        const successContent = document.getElementById('tab-content-success');
        if (successContent) successContent.classList.add('active');

        // ----- Simulation -----
        currentSimSteps = tool.simulation || [];
        currentSimIndex = 0;
        isSimPaused = false;
        if (bfSimTimer) { clearInterval(bfSimTimer); bfSimTimer = null; }

        const simSection = document.getElementById('modalSim');
        const simControls = modal.querySelector('.sim-controls');

        if (currentSimSteps.length > 0) {
            if (simControls) simControls.style.display = 'flex';
            updatePlayButton('▶ Play');
            renderSimScene();
        } else {
            if (simSection) {
                simSection.innerHTML = '<p style="color: var(--text-dim); text-align:center; padding: 1rem;">No simulation available for this tool</p>';
            }
            if (simControls) simControls.style.display = 'none';
        }

        // ----- Show Modal -----
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // ==================== RENDER EXAMPLES ====================
    function renderExamples(containerId, examples, isFailure) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

        if (!examples || examples.length === 0) {
            container.innerHTML = `<p style="color: var(--text-dim); text-align:center; padding: 1rem;">No ${isFailure ? 'failure' : 'success'} examples available</p>`;
            return;
        }

        examples.forEach(ex => {
            const div = document.createElement('div');
            div.className = 'example-block' + (isFailure ? ' example-failure' : '');

            // Handle multi-line commands nicely
            const formattedCmd = escapeHtml(ex.command || '').replace(/\n/g, '<br>$ ');

            div.innerHTML = `
                <h4>${isFailure ? '❌ ' : '✅ '}${escapeHtml(ex.title || '')}</h4>
                <div class="modal-command-display">$ ${formattedCmd}</div>
                <p class="example-explain">${escapeHtml(ex.explanation || '')}</p>
                <div class="scan-terminal-mini ${isFailure ? 'terminal-failure' : ''}">
                    <div class="terminal-bar-mini">
                        <span class="term-dot red"></span>
                        <span class="term-dot yellow"></span>
                        <span class="term-dot green"></span>
                        <span class="term-title-mini">${isFailure ? 'error output' : 'output'}</span>
                    </div>
                    <pre class="terminal-output-mini">${escapeHtml(ex.output || '')}</pre>
                </div>
            `;
            container.appendChild(div);
        });
    }

    // ==================== TAB SWITCHING ====================
    function switchOutputTab(tab, event) {
        document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
        if (event) event.currentTarget.classList.add('active');

        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        const target = document.getElementById('tab-content-' + tab);
        if (target) target.classList.add('active');
    }

    // ==================== CLOSE MODAL ====================
    function closeToolModal(event) {
        if (event && event.target !== event.currentTarget) return;
        const modal = document.getElementById('toolModal');
        if (modal) modal.classList.remove('active');
        document.body.style.overflow = '';
        if (bfSimTimer) clearInterval(bfSimTimer);
        bfSimTimer = null;
        isSimPaused = false;
    }

    // ==================== SIMULATION ====================
    function renderSimScene() {
        const player = document.getElementById('modalSim');
        if (!player) return;
        player.innerHTML = '';

        if (currentSimSteps.length === 0) {
            player.innerHTML = '<p style="color: var(--text-dim); text-align:center;">No simulation available</p>';
            return;
        }

        const step = currentSimSteps[currentSimIndex];
        const scene = document.createElement('div');
        scene.className = 'sim-scene active';
        scene.innerHTML = `
            <div class="sim-endpoint">
                <span class="sim-endpoint-icon">📤</span>
                <span>${escapeHtml(step.from)}</span>
            </div>
            <div class="sim-arrow-middle">
                <div class="sim-packet" style="background: ${currentToolColor}">${escapeHtml(step.data)}</div>
                <div class="sim-action-label">${escapeHtml(step.desc)}</div>
                <div style="font-size: 0.7rem; color: var(--text-dim);">Step ${currentSimIndex + 1} / ${currentSimSteps.length}</div>
            </div>
            <div class="sim-endpoint">
                <span class="sim-endpoint-icon">📥</span>
                <span>${escapeHtml(step.to)}</span>
            </div>
        `;
        player.appendChild(scene);

        // Progress dots
        const dots = document.createElement('div');
        dots.style.cssText = 'display:flex;justify-content:center;gap:0.4rem;margin-top:0.5rem;';
        currentSimSteps.forEach((_, i) => {
            const dot = document.createElement('span');
            dot.style.cssText = `width:8px;height:8px;border-radius:50%;background:${i <= currentSimIndex ? 'var(--accent)' : 'var(--border)'};transition:all 0.3s;`;
            dots.appendChild(dot);
        });
        player.appendChild(dots);
    }

    function toggleSim() {
        if (currentSimSteps.length === 0) return;
        if (bfSimTimer && !isSimPaused) { pauseSim(); return; }
        if (isSimPaused) { resumeSim(); return; }
        startSim();
    }

    function startSim() {
        if (bfSimTimer) clearInterval(bfSimTimer);
        currentSimIndex = 0;
        isSimPaused = false;
        renderSimScene();
        updatePlayButton('⏸ Pause');
        bfSimTimer = setInterval(() => {
            currentSimIndex++;
            if (currentSimIndex >= currentSimSteps.length) {
                clearInterval(bfSimTimer);
                bfSimTimer = null;
                currentSimIndex = currentSimSteps.length - 1;
                renderSimScene();
                updatePlayButton('▶ Replay');
                return;
            }
            renderSimScene();
        }, 1800);
    }

    function pauseSim() {
        if (!bfSimTimer) return;
        clearInterval(bfSimTimer);
        bfSimTimer = null;
        isSimPaused = true;
        updatePlayButton('▶ Resume');
    }

    function resumeSim() {
        if (!isSimPaused) return;
        isSimPaused = false;
        updatePlayButton('⏸ Pause');
        bfSimTimer = setInterval(() => {
            currentSimIndex++;
            if (currentSimIndex >= currentSimSteps.length) {
                clearInterval(bfSimTimer);
                bfSimTimer = null;
                currentSimIndex = currentSimSteps.length - 1;
                renderSimScene();
                updatePlayButton('▶ Replay');
                return;
            }
            renderSimScene();
        }, 1800);
    }

    function updatePlayButton(label) {
        const btn = document.getElementById('simPlayBtn');
        if (!btn) return;
        btn.textContent = label;
        btn.classList.remove('is-paused', 'is-playing');
        if (label.includes('Pause')) btn.classList.add('is-playing');
        if (label.includes('Resume')) btn.classList.add('is-paused');
    }

    function resetSim() {
        if (bfSimTimer) clearInterval(bfSimTimer);
        bfSimTimer = null;
        isSimPaused = false;
        currentSimIndex = 0;
        updatePlayButton('▶ Play');
        renderSimScene();
    }

    // ==================== EXPOSE GLOBALLY ====================
    window.openToolModal = openToolModal;
    window.closeToolModal = closeToolModal;
    window.toggleSim = toggleSim;
    window.resetSim = resetSim;
    window.switchOutputTab = switchOutputTab;
    window.playSim = toggleSim; // alias for older template calls

    // ==================== EVENT LISTENERS ====================
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeToolModal();
    });

    document.addEventListener('DOMContentLoaded', () => {
        // Keyboard accessibility for tool cards
        document.querySelectorAll('.tool-card').forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openToolModal(card);
                }
            });
        });

        console.log('%c🔐 Brute Force module loaded', 'color: #e74c3c; font-weight: bold;');
        console.log('%c  Tool cards found: ' + document.querySelectorAll('.tool-card').length, 'color: #8b95b8;');
    });
})();
