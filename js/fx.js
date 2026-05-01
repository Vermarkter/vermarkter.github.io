/*!
 * fx.js — Luxury Visual Effects
 * 1. Mouse parallax — subtle depth shift on hero/card layers
 * 2. Blur-reveal — Intersection Observer with blur→sharp transition
 * All transforms use will-change + translateZ(0) for GPU compositing.
 * No external deps. ~2KB minified.
 */
(function () {
    'use strict';

    /* ── 1. MOUSE PARALLAX ─────────────────────────────────────────
       Elements with [data-depth="0.3"] shift by ±depth * maxShift px.
       Canvas #matrix-canvas gets its own subtle counter-shift.
       Uses requestAnimationFrame lerp — never janky.
    ─────────────────────────────────────────────────────────────── */
    var MAX_SHIFT = 18;       // px at depth=1.0
    var LERP      = 0.072;    // interpolation speed (0=frozen, 1=instant)

    var mouse  = { x: 0, y: 0 };   // normalized -1…+1
    var target = { x: 0, y: 0 };   // lerp target
    var cur    = { x: 0, y: 0 };   // current (smoothed)
    var rafPx;

    function onMouseMove(e) {
        target.x = (e.clientX / window.innerWidth  - 0.5) * 2;
        target.y = (e.clientY / window.innerHeight - 0.5) * 2;
    }

    function tickParallax() {
        cur.x += (target.x - cur.x) * LERP;
        cur.y += (target.y - cur.y) * LERP;

        // Parallax layers: anything with [data-depth]
        var layers = document.querySelectorAll('[data-depth]');
        for (var i = 0; i < layers.length; i++) {
            var d  = parseFloat(layers[i].getAttribute('data-depth')) || 0;
            var tx = -cur.x * MAX_SHIFT * d;
            var ty = -cur.y * MAX_SHIFT * d;
            layers[i].style.transform = 'translate3d(' + tx.toFixed(2) + 'px,' +
                                                         ty.toFixed(2) + 'px,0)';
        }

        // Matrix canvas — very subtle counter-movement for depth illusion
        var cvs = document.getElementById('matrix-canvas');
        if (cvs) {
            cvs.style.transform = 'translate3d(' +
                (cur.x * 6).toFixed(2) + 'px,' +
                (cur.y * 6).toFixed(2) + 'px,0) scale(1.02)';
        }

        // Hero badge / pill elements — drift a bit
        var pills = document.querySelectorAll('.hero [style*="border-radius:50px"]:not(a), .hero-badge');
        for (var j = 0; j < pills.length; j++) {
            pills[j].style.transform = 'translate3d(' +
                (cur.x * MAX_SHIFT * 0.45).toFixed(2) + 'px,' +
                (cur.y * MAX_SHIFT * 0.45).toFixed(2) + 'px,0)';
        }

        rafPx = requestAnimationFrame(tickParallax);
    }

    function initParallax() {
        // Only on non-touch devices — touch has its own scroll parallax feel
        if ('ontouchstart' in window) return;

        window.addEventListener('mousemove', onMouseMove, { passive: true });

        // Reset on mouse leave
        document.addEventListener('mouseleave', function () {
            target.x = 0;
            target.y = 0;
        });

        cancelAnimationFrame(rafPx);
        rafPx = requestAnimationFrame(tickParallax);
    }


    /* ── 2. BLUR-REVEAL (Intersection Observer) ────────────────────
       Watches .reveal elements.
       Hidden state:  opacity:0, translateY(32px), blur(12px)
       Visible state: opacity:1, translateY(0),    blur(0)
       Staggered delay for siblings inside the same parent.
       Respects prefers-reduced-motion.
    ─────────────────────────────────────────────────────────────── */
    var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initBlurReveal() {
        // Collect targets — add .reveal to anything we want animated
        // Also auto-tag common semantic blocks that don't have it yet
        var AUTO_SELECTORS = [
            '.card', '.glass', '.service-card', '.pricing-card',
            '.faq-item', '.stat-item', '.stat-card',
            '.testimonial-card', '.portfolio-card',
            '.pain-card', '.step-card', '.feature-item',
            'section > .container > *:not(h1):not(h2)',
        ].join(',');

        var existing = document.querySelectorAll('.reveal');
        var auto     = document.querySelectorAll(AUTO_SELECTORS);

        // Merge into a Set to avoid duplicates
        var all = new Set();
        existing.forEach(function (el) { all.add(el); });
        auto.forEach(function (el) {
            // Skip elements already inside a .reveal ancestor
            if (!el.closest('.hero') && !el.closest('header') && !el.closest('nav')) {
                all.add(el);
            }
        });

        all.forEach(function (el) {
            // Mark element index within its parent for stagger
            var siblings = el.parentElement
                ? Array.from(el.parentElement.children).filter(function (c) {
                      return c.classList.contains(el.classList[0]);
                  })
                : [];
            var idx = siblings.indexOf(el);

            el.classList.add('blur-hidden');
            if (idx > 0) {
                el.style.transitionDelay = Math.min(idx * 0.08, 0.4) + 's';
            }
        });

        if (REDUCED) {
            // Skip animation — just show everything
            all.forEach(function (el) {
                el.classList.remove('blur-hidden');
                el.classList.add('blur-visible');
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    // rAF ensures paint happens before class toggle (no FOUC)
                    requestAnimationFrame(function () {
                        el.classList.remove('blur-hidden');
                        el.classList.add('blur-visible');
                    });
                    observer.unobserve(el);
                }
            });
        }, {
            threshold:  0.07,
            rootMargin: '0px 0px -48px 0px',
        });

        all.forEach(function (el) { observer.observe(el); });
    }


    /* ── BOOT ───────────────────────────────────────────────────── */
    function boot() {
        initParallax();
        initBlurReveal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

})();
