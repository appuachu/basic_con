// ==================== SIMULATIONS HELPER (ISOLATED) ====================
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        // Observe simulation scenes for animation triggers
        const simObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                }
            });
        }, { threshold: 0.3 });

        document.querySelectorAll('.sim-scene, .flow-step, .hs-step').forEach(el => {
            simObserver.observe(el);
        });

        console.log('%c🎬 simulations.js loaded', 'color: #00d4ff;');
    });
})();
