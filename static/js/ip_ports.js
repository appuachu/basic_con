// IP Simulation
let ipSimIndex = -1;
let ipSimTimer = null;

function playIPSim() {
    const steps = document.querySelectorAll('.ip-sim-step');
    if (!steps.length) return;

    if (ipSimTimer) clearInterval(ipSimTimer);
    ipSimIndex = -1;
    steps.forEach(s => s.classList.remove('active'));

    ipSimTimer = setInterval(() => {
        ipSimIndex++;
        if (ipSimIndex >= steps.length) {
            clearInterval(ipSimTimer);
            ipSimTimer = null;
            return;
        }
        steps[ipSimIndex].classList.add('active');
        steps[ipSimIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 2200);
}

function resetIPSim() {
    if (ipSimTimer) clearInterval(ipSimTimer);
    ipSimTimer = null;
    ipSimIndex = -1;
    document.querySelectorAll('.ip-sim-step').forEach(s => s.classList.remove('active'));
}

// IP Tabs
function showIPTab(tabId, event) {
    document.querySelectorAll('.ip-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.ip-tab-content').forEach(c => c.classList.remove('active'));
    if (event) event.target.classList.add('active');
    document.getElementById('tab-' + tabId)?.classList.add('active');
}

// Port Category Expand
function toggleCategory(card) {
    card.classList.toggle('open');
}

console.log('%c🎯 IP & Ports module loaded', 'color: #27ae60; font-weight: bold;');
