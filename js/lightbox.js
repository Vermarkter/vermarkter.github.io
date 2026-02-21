/**
 * VERMARKTER - Portfolio Lightbox
 * Simple, fast, GPU-optimized image viewer
 */

(function() {
    'use strict';

    let lightbox = null;
    let lightboxImg = null;
    let lightboxClose = null;

    /**
     * Create lightbox DOM structure
     */
    function createLightbox() {
        // Container
        lightbox = document.createElement('div');
        lightbox.id = 'portfolio-lightbox';
        lightbox.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(2, 6, 23, 0.95);
            backdrop-filter: blur(20px) saturate(150%);
            -webkit-backdrop-filter: blur(20px) saturate(150%);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
            cursor: zoom-out;
        `;

        // Image
        lightboxImg = document.createElement('img');
        lightboxImg.style.cssText = `
            max-width: 90%;
            max-height: 90%;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            transform: scale(0.95);
            transition: transform 0.3s ease;
            cursor: default;
        `;

        // Close button
        lightboxClose = document.createElement('button');
        lightboxClose.innerHTML = '×';
        lightboxClose.setAttribute('aria-label', 'Close');
        lightboxClose.style.cssText = `
            position: absolute;
            top: 2rem;
            right: 2rem;
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            color: white;
            font-size: 2rem;
            font-weight: 300;
            line-height: 1;
            cursor: pointer;
            transition: all 0.2s ease;
            z-index: 10001;
        `;

        lightboxClose.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255, 255, 255, 0.2)';
            this.style.transform = 'scale(1.1)';
        });

        lightboxClose.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(255, 255, 255, 0.1)';
            this.style.transform = 'scale(1)';
        });

        // Assemble
        lightbox.appendChild(lightboxImg);
        lightbox.appendChild(lightboxClose);
        document.body.appendChild(lightbox);

        // Event listeners
        lightboxClose.addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });

        // ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && lightbox.style.display === 'flex') {
                closeLightbox();
            }
        });
    }

    /**
     * Open lightbox with image
     */
    function openLightbox(imgSrc) {
        if (!lightbox) createLightbox();

        lightboxImg.src = imgSrc;
        lightbox.style.display = 'flex';

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Trigger animation
        requestAnimationFrame(function() {
            lightbox.style.opacity = '1';
            lightboxImg.style.transform = 'scale(1)';
        });
    }

    /**
     * Close lightbox
     */
    function closeLightbox() {
        if (!lightbox) return;

        lightbox.style.opacity = '0';
        lightboxImg.style.transform = 'scale(0.95)';

        setTimeout(function() {
            lightbox.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
    }

    /**
     * Initialize portfolio cards
     */
    function initPortfolioCards() {
        const cards = document.querySelectorAll('.portfolio-card');

        cards.forEach(function(card) {
            const img = card.querySelector('img');
            if (!img || !img.src) return;

            // Make entire card clickable
            card.style.cursor = 'zoom-in';

            card.addEventListener('click', function(e) {
                // Don't trigger if clicking on a link
                if (e.target.tagName === 'A' || e.target.closest('a')) {
                    e.preventDefault();
                }
                openLightbox(img.src);
            });
        });
    }

    /**
     * Auto-init on DOM ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPortfolioCards);
    } else {
        initPortfolioCards();
    }

})();
