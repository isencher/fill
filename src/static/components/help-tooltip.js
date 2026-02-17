/**
 * Help Tooltip Component
 * Provides contextual help information throughout the app
 */

class HelpTooltip {
    constructor(options = {}) {
        this.iconText = options.iconText || '?';
        this.content = options.content || '';
        this.position = options.position || 'top'; // top, left, right
        this.wide = options.wide || false;
        this.target = options.target;
    }

    render() {
        const wrapper = document.createElement('span');
        wrapper.className = `help-tooltip ${this.position}`;

        const icon = document.createElement('span');
        icon.className = 'help-tooltip-icon';
        icon.textContent = this.iconText;
        icon.setAttribute('role', 'button');
        icon.setAttribute('tabindex', '0');
        icon.setAttribute('aria-label', 'Show help');

        const content = document.createElement('span');
        content.className = `help-tooltip-content${this.wide ? ' wide' : ''}`;
        content.innerHTML = this.content;

        wrapper.appendChild(icon);
        wrapper.appendChild(content);

        // Keyboard accessibility
        icon.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                content.style.opacity = content.style.opacity === '1' ? '0' : '1';
                content.style.visibility = content.style.visibility === 'visible' ? 'hidden' : 'visible';
            }
        });

        return wrapper;
    }

    static attachTo(selector, options) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const tooltip = new HelpTooltip(options);
            const tooltipElement = tooltip.render();
            element.appendChild(tooltipElement);
        });
    }
}

// Auto-attach tooltips to elements with data-help-tooltip attribute
document.addEventListener('DOMContentLoaded', () => {
    const tooltipElements = document.querySelectorAll('[data-help-tooltip]');
    tooltipElements.forEach(element => {
        const content = element.getAttribute('data-help-tooltip');
        const position = element.getAttribute('data-help-position') || 'top';
        const wide = element.hasAttribute('data-help-wide');

        const tooltip = new HelpTooltip({
            content: content,
            position: position,
            wide: wide
        });

        const tooltipElement = tooltip.render();
        element.appendChild(tooltipElement);
    });
});
