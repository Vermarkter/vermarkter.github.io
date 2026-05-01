/*!
 * DIGITAL RAIN  —  matrix.js  v2.1  "Luxury Tech"
 * Small 11px chars · dense 12px columns · dimmed cyan/steel-blue palette
 * Canvas opacity + blur controlled in CSS for max flexibility
 */
(function () {
    'use strict';

    /* ═══════════════════════════════════════════
       CONFIG — tweak here, no DOM changes needed
    ═══════════════════════════════════════════ */
    var isMobile = window.innerWidth < 768;

    var C = {
        FONT_SIZE    : 11,
        COL_WIDTH    : isMobile ? 36 : 12,  // 3x wider on mobile = 3x fewer columns
        TRAIL_MIN    : 28,
        TRAIL_MAX    : 60,
        SPEED_MIN    : 0.20,
        SPEED_MAX    : 0.78,
        SCROLL_BOOST : 2.2,
        SCROLL_DECAY : 0.032,
        MUTATE_PROB  : 0.014,
        CHARS: '0123456789ABCDEFabcdef€$%₿↗▲∞πΩβαΔ|!?'
    };

    /* ═══════════════════════════════════════════
       STATE
    ═══════════════════════════════════════════ */
    var cvs, ctx, W, H;
    var cols  = [];
    var boost = 0;
    var lastY = 0;
    var raf;

    /* ═══════════════════════════════════════════
       BOOTSTRAP
    ═══════════════════════════════════════════ */
    function init() {
        var old = document.getElementById('matrix-canvas');
        if (old) old.remove();

        cvs    = document.createElement('canvas');
        cvs.id = 'matrix-canvas';
        document.body.prepend(cvs);

        ctx = cvs.getContext('2d');

        resize();
        window.addEventListener('resize', debounce(resize, 180));
        window.addEventListener('scroll', onScroll, { passive: true });

        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(tick);
    }

    /* ═══════════════════════════════════════════
       RESIZE
    ═══════════════════════════════════════════ */
    function resize() {
        W = cvs.width  = window.innerWidth;
        H = cvs.height = window.innerHeight;
        buildCols();
    }

    function buildCols() {
        var n = Math.ceil(W / C.COL_WIDTH) + 2;
        cols = [];
        for (var i = 0; i < n; i++) cols.push(makeCol(i, true));
    }

    function makeCol(idx, scatter) {
        var trail = (C.TRAIL_MIN + Math.random() * (C.TRAIL_MAX - C.TRAIL_MIN)) | 0;
        var speed = C.SPEED_MIN + Math.random() * (C.SPEED_MAX - C.SPEED_MIN);
        var chars = [];
        for (var j = 0; j < trail; j++) chars.push(rc());
        return {
            x    : idx * C.COL_WIDTH,
            y    : scatter ? Math.random() * H : -trail * C.FONT_SIZE * 1.5,
            speed: speed,
            trail: trail,
            chars: chars
        };
    }

    function rc() {
        return C.CHARS[Math.random() * C.CHARS.length | 0];
    }

    /* ═══════════════════════════════════════════
       SCROLL BOOST
    ═══════════════════════════════════════════ */
    function onScroll() {
        var dy = Math.abs(window.scrollY - lastY);
        lastY  = window.scrollY;
        boost  = Math.min(C.SCROLL_BOOST, boost + dy * 0.014);
    }

    /* ═══════════════════════════════════════════
       RENDER LOOP
    ═══════════════════════════════════════════ */
    function tick() {
        boost = Math.max(0, boost - C.SCROLL_DECAY);
        var spd = 1 + boost;
        var rH  = C.FONT_SIZE * 1.5;

        ctx.clearRect(0, 0, W, H);
        ctx.font         = C.FONT_SIZE + 'px "Courier New",Courier,monospace';
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'alphabetic';

        for (var i = 0; i < cols.length; i++) {
            var col = cols[i];

            col.y += col.speed * spd * rH;

            if (Math.random() < C.MUTATE_PROB) {
                col.chars[Math.random() * col.trail | 0] = rc();
            }

            if (col.y - col.trail * rH > H) {
                col.y     = -rH * 2;
                col.speed = C.SPEED_MIN + Math.random() * (C.SPEED_MAX - C.SPEED_MIN);
                col.trail = (C.TRAIL_MIN + Math.random() * (C.TRAIL_MAX - C.TRAIL_MIN)) | 0;
                for (var k = 0; k < col.trail; k++) {
                    if (Math.random() > 0.6) col.chars[k] = rc();
                }
            }

            var cx = col.x + C.COL_WIDTH * 0.5;
            for (var j = 0; j < col.trail; j++) {
                var cy = col.y - j * rH;
                if (cy < -rH || cy > H + rH) continue;

                var t = 1 - j / col.trail;
                ctx.fillStyle = color(j, t, col.trail);
                ctx.fillText(col.chars[j], cx, cy);
            }
        }

        raf = requestAnimationFrame(tick);
    }

    /* ═══════════════════════════════════════════
       COLOR FUNCTION  —  Deep Void palette
       Background: #0a0a20 (deep navy) → #1a0033 (dark violet)
       Gradient direction: HEAD = electric violet-blue, TAIL = deep purple void

       j = 0      HEAD      electric blue-violet  #7b6cff
       j = 1..3   SHOULDER  indigo                #5b4de0
       j = 4..14  MID TRAIL indigo → violet       #3b1a8c range
       j = 15+    DEEP TAIL violet → #1a0033 void fade
    ═══════════════════════════════════════════ */
    function color(j, t, trail) {
        var r, g, b, a;

        if (j === 0) {
            /* HEAD — electric blue-violet #7b6cff */
            r = 123; g = 108; b = 255;
            a = 0.95;

        } else if (j <= 3) {
            /* SHOULDER — indigo #5b4de0 */
            r = 91;  g = 77;  b = 224;
            a = 0.80 - (j - 1) * 0.12;

        } else if (j <= 14) {
            /* MID TRAIL — indigo → deep violet #3b1a8c */
            var p1 = (j - 3) / 11;
            r = (91  - p1 * 32) | 0;   /* 91  → 59  */
            g = (77  - p1 * 51) | 0;   /* 77  → 26  */
            b = (224 - p1 * 84) | 0;   /* 224 → 140 */
            a = t * 0.65;

        } else {
            /* DEEP TAIL — deep violet → #1a0033 void */
            var p2 = Math.min((j - 14) / Math.max(trail - 14, 1), 1);
            r = (59  - p2 * 33) | 0;   /* 59  → 26  */
            g = (26  - p2 * 26) | 0;   /* 26  → 0   */
            b = (140 - p2 * 89) | 0;   /* 140 → 51  */
            a = t * 0.28;
        }

        return 'rgba(' + r + ',' + g + ',' + b + ',' + Math.min(a, 1).toFixed(2) + ')';
    }

    /* ═══════════════════════════════════════════
       UTILITY
    ═══════════════════════════════════════════ */
    function debounce(fn, ms) {
        var t;
        return function () {
            clearTimeout(t);
            t = setTimeout(fn, ms);
        };
    }

    /* ═══════════════════════════════════════════
       START
    ═══════════════════════════════════════════ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
