// ==================== MAIN SCRIPT (ISOLATED SCOPE) ====================
(function () {
    'use strict';

    // ==================== MOBILE MENU TOGGLE ====================
    window.toggleMenu = function () {
        const menu = document.querySelector('.nav-menu');
        if (menu) menu.classList.toggle('open');
    };

    // ==================== NAV DROPDOWN ====================
    window.toggleDropdown = function (event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        const dropdown = event.currentTarget.closest('.nav-dropdown');
        if (!dropdown) return;

        const wasOpen = dropdown.classList.contains('open');

        // Close all dropdowns first
        document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));

        // Toggle the clicked one
        if (!wasOpen) dropdown.classList.add('open');
    };

    // ==================== PORT FILTERING ====================
    window.filterPorts = function () {
        const input = document.getElementById('portSearch');
        if (!input) return;
        const filter = input.value.toLowerCase();
        const rows = document.querySelectorAll('#portsTable tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    };

    window.filterByProto = function (proto, event) {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        if (event) event.target.classList.add('active');

        const rows = document.querySelectorAll('#portsTable tbody tr');
        rows.forEach(row => {
            const rowProto = row.getAttribute('data-proto') || '';
            if (proto === 'all') {
                row.style.display = '';
            } else {
                row.style.display = rowProto.includes(proto) ? '' : 'none';
            }
        });
    };

    // ==================== ON DOM READY ====================
    document.addEventListener('DOMContentLoaded', () => {

        // ---------- Smooth scroll ----------
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#' || href.length < 2) return;
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // ---------- Scroll animation observer ----------
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

        document.querySelectorAll('.content-card, .feature-card, .flag-card, .iot-card, .quick-card, .concept-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });

        // ---------- Active nav link ----------
        document.querySelectorAll('.nav-link').forEach(link => {
            try {
                if (link.href === window.location.href) {
                    link.style.color = 'var(--accent)';
                    link.style.background = 'rgba(0, 212, 255, 0.1)';
                }
            } catch (e) { /* ignore */ }
        });

        // ---------- Keyboard accessibility for device cards ----------
        document.querySelectorAll('.device-card').forEach(card => {
            if (!card.hasAttribute('tabindex')) card.setAttribute('tabindex', '0');
            if (!card.hasAttribute('role')) card.setAttribute('role', 'button');
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    if (typeof window.openDeviceModal === 'function') {
                        window.openDeviceModal(card);
                    }
                }
            });
        });

        // ---------- Keyboard accessibility for port rows ----------
        document.querySelectorAll('.port-row').forEach(row => {
            if (!row.hasAttribute('tabindex')) row.setAttribute('tabindex', '0');
            if (!row.hasAttribute('role')) row.setAttribute('role', 'button');
            row.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') row.click();
            });
        });

        console.log('%c🌐 NetLearnOSI', 'font-size: 18px; font-weight: bold; color: #00d4ff;');
        console.log('%c✅ main.js ready', 'color: #27ae60;');
    });

    // ==================== GLOBAL CLICK HANDLERS ====================
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-dropdown')) {
            document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
        }
    });

    // Close dropdowns on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
        }
    });

})();
// ==================== NAV DROPDOWN ====================
function toggleDropdown(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const dropdown = event.currentTarget.closest('.nav-dropdown');
    if (!dropdown) return;

    const wasOpen = dropdown.classList.contains('open');

    // Close all other dropdowns
    document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));

    if (!wasOpen) dropdown.classList.add('open');
}

// Close dropdown on outside click
document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-dropdown')) {
        document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
    }
});

// Close on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
    }
});
