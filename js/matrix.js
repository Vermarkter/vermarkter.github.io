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
    var C = {
        FONT_SIZE    : 11,      // px — small, delicate
        COL_WIDTH    : 12,      // px — dense column pitch
        TRAIL_MIN    : 28,      // chars
        TRAIL_MAX    : 60,      // chars
        SPEED_MIN    : 0.20,    // cells/frame  (slower = calmer)
        SPEED_MAX    : 0.78,    // cells/frame
        SCROLL_BOOST : 2.2,     // max multiplier on scroll
        SCROLL_DECAY : 0.032,   // boost decay per frame
        MUTATE_PROB  : 0.014,   // probability of char mutation per frame
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
       COLOR FUNCTION  —  Luxury Tech palette
       Canvas element has CSS opacity:0.22 + filter:blur(0.8px)
       so individual alpha values can be generous for visible gradient.

       j = 0      HEAD      bright cyan   #00d4f0
       j = 1..3   SHOULDER  mid cyan      #00b8d4
       j = 4..14  MID TRAIL cyan → steel  #64748b range
       j = 15+    DEEP TAIL steel → purple-slate, fast fade
    ═══════════════════════════════════════════ */
    function color(j, t, trail) {
        var r, g, b, a;

        if (j === 0) {
            /* HEAD — bright cyan, canvas opacity brings it down to ~0.20 */
            r = 0; g = 212; b = 240;
            a = 0.92;

        } else if (j <= 3) {
            /* SHOULDER — mid cyan */
            r = 0; g = 185; b = 220;
            a = 0.78 - (j - 1) * 0.13;

        } else if (j <= 14) {
            /* MID TRAIL — cyan → steel blue (#64748b) */
            var p1 = (j - 3) / 11;
            r = (0   + p1 * 100) | 0;  /* 0   → 100 */
            g = (185 - p1 * 69)  | 0;  /* 185 → 116 */
            b = (220 - p1 * 81)  | 0;  /* 220 → 139 */
            a = t * 0.70;

        } else {
            /* DEEP TAIL — steel blue → purple-slate fade */
            var p2 = Math.min((j - 14) / Math.max(trail - 14, 1), 1);
            r = (100 + p2 * 39)  | 0;  /* 100 → 139 */
            g = (116 - p2 * 24)  | 0;  /* 116 → 92  */
            b = (139 + p2 * 107) | 0;  /* 139 → 246 */
            a = t * 0.32;
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
