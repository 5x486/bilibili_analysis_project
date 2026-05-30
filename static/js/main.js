// BiliAnalytics - Main JS
// Particles.js + GSAP entrance animations

document.addEventListener('DOMContentLoaded', function () {
    // Particles.js background
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            particles: {
                number: { value: 50, density: { enable: true, value_area: 1000 } },
                color: { value: ['#FB7299', '#00d4ff', '#FF6B9D', '#a78bfa'] },
                shape: { type: 'circle' },
                opacity: { value: 0.4, random: true, anim: { enable: true, speed: 0.4, opacity_min: 0.08, sync: false } },
                size: { value: 2.5, random: true, anim: { enable: true, speed: 0.8, size_min: 0.3, sync: false } },
                line_linked: { enable: true, distance: 150, color: '#FB7299', opacity: 0.12, width: 1 },
                move: { enable: true, speed: 1.2, direction: 'none', random: true, straight: false,
                    out_mode: 'out', bounce: false,
                    attract: { enable: true, rotateX: 600, rotateY: 1200 } }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: { enable: true, mode: 'grab' },
                    onclick: { enable: true, mode: 'push' },
                    resize: true
                },
                modes: {
                    grab: { distance: 140, line_linked: { opacity: 0.35 } },
                    push: { particles_nb: 3 }
                }
            },
            retina_detect: true
        });
    }

    // GSAP page entrance: staggered card fade-up
    gsap.fromTo('.glass-card', {
        opacity: 0,
        y: 28,
    }, {
        opacity: 1,
        y: 0,
        duration: 0.65,
        stagger: 0.08,
        ease: 'power3.out',
    });

    // GSAP sidebar nav link entrance
    gsap.fromTo('.nav-link', {
        opacity: 0,
        x: -16,
    }, {
        opacity: 1,
        x: 0,
        duration: 0.5,
        stagger: 0.04,
        delay: 0.15,
        ease: 'power2.out',
    });
});
