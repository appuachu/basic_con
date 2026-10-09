// ==================== DEVICE + PORT MODALS (ISOLATED SCOPE) ====================
(function () {
    'use strict';

    let currentSimSteps = [];
    let currentSimIndex = 0;
    let simTimer = null;
    let isSimPaused = false;

    let portSimSteps = [];
    let portSimIndex = 0;
    let portSimTimer = null;

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

    // ==================== DEVICE MODAL ====================
    function openDeviceModal(card) {
        let device;
        try {
            device = JSON.parse(card.getAttribute('data-device'));
        } catch (e) {
            console.error('Failed to parse device JSON:', e);
            return;
        }

        const modal = document.getElementById('deviceModal');
        if (!modal) {
            console.error('Modal #deviceModal not found');
            return;
        }

        // Header
        const header = document.getElementById('modalHeader');
        if (header) header.style.setProperty('--modal-color', device.color || '#00d4ff');

        const icon = document.getElementById('modalIcon');
        if (icon) {
            icon.textContent = device.icon || '📦';
            icon.style.background = device.color || '#00d4ff';
        }

        const title = document.getElementById('modalTitle');
        if (title) title.textContent = device.name || 'Device';

        const subtitle = document.getElementById('modalSubtitle');
        if (subtitle) subtitle.textContent = device.short || '';

        // Image
        const img = document.getElementById('modalImage');
        const credit = document.getElementById('modalImageCredit');
        if (img) {
            if (device.image) {
                img.src = device.image;
                img.alt = device.name || '';
                img.style.display = 'block';
                if (credit) credit.textContent = device.image_credit || '';
            } else {
                img.style.display = 'none';
                if (credit) credit.textContent = '';
            }
        }

        // Use case
        const useCase = document.getElementById('modalUseCase');
        if (useCase) useCase.textContent = device.use_case || '';

        // How it works
        const howList = document.getElementById('modalHow');
        if (howList) {
            howList.innerHTML = '';
            (device.how_it_works || []).forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                howList.appendChild(li);
            });
        }

        // Real world
        const realWorld = document.getElementById('modalExample');
        if (realWorld) realWorld.textContent = device.real_example || '';

        // Layers
        const layersDiv = document.getElementById('modalLayers');
        if (layersDiv) {
            layersDiv.innerHTML = '';
            const layerColors = {
                1: '#1abc9c', 2: '#9b59b6', 3: '#3498db',
                4: '#27ae60', 5: '#f39c12', 6: '#e67e22', 7: '#e74c3c'
            };
            (device.layers || []).forEach(l => {
                const badge = document.createElement('span');
                badge.className = 'modal-layer-badge';
                badge.style.background = layerColors[l] || '#00d4ff';
                badge.textContent = 'Layer ' + l;
                layersDiv.appendChild(badge);
            });
        }

        // Reset simulation
        currentSimSteps = device.simulation_steps || [];
        currentSimIndex = 0;
        isSimPaused = false;
        if (simTimer) { clearInterval(simTimer); simTimer = null; }
        updatePlayButton('▶ Play');
        renderSimScene();

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function renderSimScene() {
        const player = document.getElementById('modalSim');
        if (!player) return;
        player.innerHTML = '';

        if (currentSimSteps.length === 0) {
            player.innerHTML = '<p style="color: var(--text-dim); text-align:center; padding: 1rem;">No simulation available</p>';
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
                <div class="sim-packet">${escapeHtml(step.data)}</div>
                <div class="sim-action-label">${escapeHtml(step.action)}</div>
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
        if (simTimer && !isSimPaused) { pauseSim(); return; }
        if (isSimPaused) { resumeSim(); return; }
        startSim();
    }

    function startSim() {
        if (simTimer) clearInterval(simTimer);
        currentSimIndex = 0;
        isSimPaused = false;
        renderSimScene();
        updatePlayButton('⏸ Pause');

        simTimer = setInterval(() => {
            currentSimIndex++;
            if (currentSimIndex >= currentSimSteps.length) {
                clearInterval(simTimer);
                simTimer = null;
                currentSimIndex = currentSimSteps.length - 1;
                renderSimScene();
                updatePlayButton('▶ Replay');
                return;
            }
            renderSimScene();
        }, 1800);
    }

    function pauseSim() {
        if (!simTimer) return;
        clearInterval(simTimer);
        simTimer = null;
        isSimPaused = true;
        updatePlayButton('▶ Resume');
    }

    function resumeSim() {
        if (!isSimPaused) return;
        isSimPaused = false;
        updatePlayButton('⏸ Pause');

        simTimer = setInterval(() => {
            currentSimIndex++;
            if (currentSimIndex >= currentSimSteps.length) {
                clearInterval(simTimer);
                simTimer = null;
                currentSimIndex = currentSimSteps.length - 1;
                renderSimScene();
                updatePlayButton('▶ Replay');
                return;
            }
            renderSimScene();
        }, 1800);
    }

    function resetSim() {
        if (simTimer) clearInterval(simTimer);
        simTimer = null;
        isSimPaused = false;
        currentSimIndex = 0;
        updatePlayButton('▶ Play');
        renderSimScene();
    }

    function updatePlayButton(label) {
        const btn = document.getElementById('simPlayBtn');
        if (!btn) return;
        btn.textContent = label;
        btn.classList.remove('is-paused', 'is-playing');
        if (label.indexOf('Pause') !== -1) btn.classList.add('is-playing');
        if (label.indexOf('Resume') !== -1) btn.classList.add('is-paused');
    }

    function closeModal(event) {
        if (event && event.target !== event.currentTarget) return;
        const modal = document.getElementById('deviceModal');
        if (modal) modal.classList.remove('active');
        document.body.style.overflow = '';
        if (simTimer) clearInterval(simTimer);
        simTimer = null;
        isSimPaused = false;
    }

    // ==================== PORT MODAL ====================
    function openPortModal(portNum, service, protocol, description) {
        const modal = document.getElementById('portModal');
        if (!modal) return;

        fetch('/api/port/' + portNum)
            .then(res => res.ok ? res.json() : null)
            .then(simData => {
                const color = (simData && simData.color) || '#00d4ff';

                const header = document.getElementById('portModalHeader');
                if (header) header.style.setProperty('--modal-color', color);

                const iconEl = document.getElementById('portModalIcon');
                if (iconEl) {
                    iconEl.textContent = portNum;
                    iconEl.style.background = color;
                }

                const titleEl = document.getElementById('portModalTitle');
                if (titleEl) titleEl.textContent = service;

                const subEl = document.getElementById('portModalSubtitle');
                if (subEl) subEl.textContent = 'Port ' + portNum + ' • ' + protocol + ' • ' + description;

                portSimSteps = (simData && simData.sim) || [
                    { step: 1, title: 'Connection', desc: 'Client connects to port ' + portNum },
                    { step: 2, title: 'Protocol', desc: service + ' handles communication' },
                    { step: 3, title: 'Data Exchange', desc: 'Data transferred' },
                    { step: 4, title: 'Complete', desc: 'Connection closed' }
                ];
                portSimIndex = 0;
                renderPortSim();
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            })
            .catch(err => console.error('Port fetch failed:', err));
    }

    function renderPortSim() {
        const player = document.getElementById('portSimPlayer');
        if (!player) return;
        player.innerHTML = '';

        const header = document.getElementById('portModalHeader');
        if (header) {
            player.style.setProperty('--port-color', header.style.getPropertyValue('--modal-color') || '#00d4ff');
        }

        portSimSteps.forEach((step, i) => {
            const div = document.createElement('div');
            div.className = 'port-sim-step' + (i <= portSimIndex ? ' active' : '');
            div.innerHTML = `
                <div class="port-sim-step-num">${step.step}</div>
                <div class="port-sim-step-content">
                    <h4>${escapeHtml(step.title)}</h4>
                    <p>${escapeHtml(step.desc)}</p>
                </div>
            `;
            player.appendChild(div);
        });
    }

    function playPortSim() {
        if (portSimSteps.length === 0) return;
        if (portSimTimer) clearInterval(portSimTimer);
        portSimIndex = 0;
        renderPortSim();
        portSimTimer = setInterval(() => {
            portSimIndex++;
            renderPortSim();
            if (portSimIndex >= portSimSteps.length - 1) {
                clearInterval(portSimTimer);
                portSimTimer = null;
            }
        }, 1500);
    }

    function resetPortSim() {
        if (portSimTimer) clearInterval(portSimTimer);
        portSimTimer = null;
        portSimIndex = 0;
        renderPortSim();
    }

    function closePortModal(event) {
        if (event && event.target !== event.currentTarget) return;
        const modal = document.getElementById('portModal');
        if (modal) modal.classList.remove('active');
        document.body.style.overflow = '';
        if (portSimTimer) clearInterval(portSimTimer);
        portSimTimer = null;
    }

    // ==================== KEYBOARD SHORTCUTS ====================
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closePortModal();
        }
        if (e.key === ' ') {
            const modal = document.getElementById('deviceModal');
            if (modal && modal.classList.contains('active')) {
                const tag = e.target.tagName;
                if (tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'BUTTON') {
                    e.preventDefault();
                    toggleSim();
                }
            }
        }
    });

    // ==================== EXPOSE GLOBALLY ====================
    window.openDeviceModal = openDeviceModal;
    window.closeModal = closeModal;
    window.toggleSim = toggleSim;
    window.resetSim = resetSim;
    window.playSim = toggleSim;
    window.openPortModal = openPortModal;
    window.closePortModal = closePortModal;
    window.playPortSim = playPortSim;
    window.resetPortSim = resetPortSim;

    console.log('%c✅ modals.js loaded', 'color: #27ae60; font-weight: bold;');
})();
