// Installation Method Switcher
document.addEventListener('DOMContentLoaded', function() {
    const installCards = document.querySelectorAll('.install-card');
    const installMethods = document.querySelectorAll('.install-method');
    
    installCards.forEach(card => {
        card.addEventListener('click', function() {
            const method = this.getAttribute('data-method');
            
            // Remove active class from all cards and methods
            installCards.forEach(c => c.classList.remove('active'));
            installMethods.forEach(m => m.classList.remove('active'));
            
            // Add active class to clicked card and corresponding method
            this.classList.add('active');
            document.getElementById(`${method}-install`).classList.add('active');
        });
    });
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Terminal Animation System
    function initTerminalAnimations() {
        // 1. Hide all terminal lines except hero section
        document.querySelectorAll('.section:not(.hero) .terminal-line').forEach(line => {
            line.style.opacity = '0';
            line.style.transform = 'translateY(10px)';
            line.style.transition = 'all 0.5s ease';
        });
        
        // 2. Animate hero terminal immediately
        const heroTerminalLines = document.querySelectorAll('.hero .terminal-line');
        heroTerminalLines.forEach((line, index) => {
            line.style.opacity = '0';
            line.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                line.style.transition = 'all 0.5s ease';
                line.style.opacity = '1';
                line.style.transform = 'translateY(0)';
            }, index * 800);
        });
    }
    
    // Function to animate terminal lines in a section
    function animateTerminalLines(section) {
        if (section.dataset.terminalAnimated === 'true') return;
        section.dataset.terminalAnimated = 'true';
        
        const terminalLines = section.querySelectorAll('.terminal-line');
        terminalLines.forEach((line, index) => {
            setTimeout(() => {
                line.style.opacity = '1';
                line.style.transform = 'translateY(0)';
            }, index * 150);
        });
    }
    
    // Initialize terminal animations
    initTerminalAnimations();
    
    // Navbar background on scroll
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(15, 23, 42, 0.98)';
        } else {
            navbar.style.background = 'rgba(15, 23, 42, 0.95)';
        }
    });
    
    // Feature cards hover effect
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Copy code functionality - for both pre code and terminal blocks
    function addCopyButton(element, getText) {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(96, 165, 250, 0.8);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 10;
        `;
        
        element.style.position = 'relative';
        element.appendChild(button);
        
        element.addEventListener('mouseenter', () => {
            button.style.opacity = '1';
        });
        
        element.addEventListener('mouseleave', () => {
            button.style.opacity = '0';
        });
        
        button.addEventListener('click', async () => {
            try {
                const text = getText();
                await navigator.clipboard.writeText(text);
                button.textContent = 'Copied!';
                button.style.background = 'rgba(16, 185, 129, 0.8)';
                
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.style.background = 'rgba(96, 165, 250, 0.8)';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text: ', err);
                button.textContent = 'Failed';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            }
        });
    }
    
    // Add copy buttons to pre code blocks
    document.querySelectorAll('pre code').forEach(codeBlock => {
        const pre = codeBlock.parentNode;
        addCopyButton(pre, () => codeBlock.textContent);
    });
    
    // Add copy buttons to terminal blocks (configuration and installation sections)
    document.querySelectorAll('#configuration .terminal, #installation .terminal').forEach(terminal => {
        const terminalBody = terminal.querySelector('.terminal-body');
        if (terminalBody) {
            addCopyButton(terminal, () => {
                const lines = terminalBody.querySelectorAll('.terminal-line');
                return Array.from(lines).map(line => {
                    const command = line.querySelector('.command');
                    return command ? command.textContent : '';
                }).filter(text => text.trim() !== '').join('\n');
            });
        }
    });
    
    // Intersection Observer for section animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.sectionAnimated) {
                entry.target.dataset.sectionAnimated = 'true';
                
                // Fade in the section
                entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
                
                // Animate terminal lines in this section (exclude hero section)
                if (!entry.target.classList.contains('hero')) {
                    setTimeout(() => {
                        animateTerminalLines(entry.target);
                    }, 400); // Small delay after section appears
                }
            }
        });
    }, observerOptions);
    
    // Setup sections for observation
    document.querySelectorAll('.section').forEach(section => {
        if (!section.classList.contains('hero')) {
            section.style.opacity = '0';
            section.style.transform = 'translateY(30px)';
        }
        observer.observe(section);
    });
    
    // Add CSS for fade in animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .hero {
            animation: fadeInUp 1s ease forwards;
        }
    `;
    document.head.appendChild(style);
});

// Terminal typing effect for demo
function typeText(element, text, speed = 100) {
    return new Promise(resolve => {
        let i = 0;
        element.textContent = '';
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }
        
        type();
    });
}

// Final setup when page is fully loaded
window.addEventListener('load', function() {
    // Ensure all terminal animations are properly initialized
    console.log('🚀 Terminal animations initialized');
    
    // Optional: Add debugging to verify animations are working
    if (window.location.search.includes('debug')) {
        const debugStyle = document.createElement('style');
        debugStyle.textContent = `
            .terminal-line {
                border: 1px dashed rgba(255, 0, 0, 0.3) !important;
            }
            .section[data-section-animated="true"] {
                border: 2px solid rgba(0, 255, 0, 0.3) !important;
            }
        `;
        document.head.appendChild(debugStyle);
        console.log('🐛 Debug mode enabled - red borders show terminal lines, green borders show animated sections');
    }
});