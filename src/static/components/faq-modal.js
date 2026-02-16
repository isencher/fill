/**
 * FAQ Modal Component
 * Provides frequently asked questions and answers
 */

const FAQ_DATA = [
    {
        question: "How do I format my data file?",
        answer: `<p>Your data file should be either a CSV or Excel (.xlsx) file with:</p>
        <ul>
            <li>Column headers in the first row</li>
            <li>Data rows starting from the second row</li>
            <li>No empty columns or rows</li>
            <li>Consistent data format in each column</li>
        </ul>
        <p>Example: A customer list might have columns like "Name", "Email", "Phone", "Date".</p>`
    },
    {
        question: "What file formats are supported?",
        answer: `<p>We support the following file formats:</p>
        <ul>
            <li><strong>CSV</strong> - Comma-separated values (.csv)</li>
            <li><strong>Excel</strong> - Microsoft Excel files (.xlsx, .xlsm)</li>
            <li><strong>TSV</strong> - Tab-separated values (.tsv)</li>
        </ul>
        <p>Maximum file size is 10MB.</p>`
    },
    {
        question: "How do I create a custom template?",
        answer: `<p>To create a custom template:</p>
        <ol>
            <li>Prepare your document (DOCX, TXT, HTML, or CSV)</li>
            <li>Insert placeholders using double curly braces: <code>{{field_name}}</code></li>
            <li>Use descriptive field names that match your data columns</li>
            <li>Upload the template in the Templates section</li>
        </ol>
        <p><strong>Example:</strong> "Dear {{name}}, your invoice #{{invoice_number}} is due on {{due_date}}."</p>`
    },
    {
        question: "Why didn't auto-match work for my data?",
        answer: `<p>Auto-match may not work perfectly if:</p>
        <ul>
            <li>Your column names are very different from placeholder names</li>
            <li>Column names contain abbreviations or codes</li>
            <li>Data is in a different language</li>
        </ul>
        <p><strong>Solution:</strong> You can manually adjust mappings by selecting the correct column for each placeholder from the dropdown menus.</p>`
    },
    {
        question: "How do I download sample data?",
        answer: `<p>You can download sample data files from the upload page:</p>
        <ul>
            <li>Click "Download Sample CSV" for a CSV template</li>
            <li>Click "Download Sample Excel" for an Excel template</li>
        </ul>
        <p>These samples include common field names and examples to help you get started.</p>`
    },
    {
        question: "Can I save my mappings for future use?",
        answer: `<p>Yes! When you create a mapping:</p>
        <ul>
            <li>The mapping is saved with your template</li>
            <li>Next time you use the same template with similar data</li>
            <li>The system will remember your previous mappings</li>
        </ul>
        <p>This saves time when processing similar files repeatedly.</p>`
    },
    {
        question: "What happens to my uploaded files?",
        answer: `<p>Your files are processed as follows:</p>
        <ul>
            <li>Files are temporarily stored during processing</li>
            <li>Generated documents are available for download</li>
            <li>Temporary files are automatically cleaned up</li>
        </ul>
        <p>Your data is not shared with third parties and is only used for document generation.</p>`
    },
    {
        question: "How do I download generated documents?",
        answer: `<p>After processing completes:</p>
        <ul>
            <li>You'll see a download link for all generated documents</li>
            <li>Documents are bundled in a ZIP file</li>
            <li>Click the download button to save to your computer</li>
        </ul>
        <p>Individual documents can also be downloaded if needed.</p>`
    }
];

class FAQModal {
    constructor() {
        this.modal = null;
        this.isOpen = false;
        this.searchInput = null;
    }

    create() {
        // Create FAQ button
        const button = document.createElement('button');
        button.className = 'faq-button';
        button.innerHTML = '?';
        button.setAttribute('aria-label', 'Open FAQ');
        button.addEventListener('click', () => this.open());

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'faq-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-label', 'Frequently Asked Questions');

        modal.innerHTML = `
            <div class="faq-modal-content">
                <div class="faq-modal-header">
                    <h2 class="faq-modal-title">❓ Help & FAQ</h2>
                    <button class="faq-modal-close" aria-label="Close">&times;</button>
                </div>
                <div class="faq-modal-body">
                    <input type="text" class="faq-search" placeholder="Search questions...">
                    <div class="faq-items"></div>
                    <div class="faq-no-results">No matching questions found</div>
                </div>
            </div>
        `;

        // Close button
        const closeBtn = modal.querySelector('.faq-modal-close');
        closeBtn.addEventListener('click', () => this.close());

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.close();
            }
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Search functionality
        this.searchInput = modal.querySelector('.faq-search');
        this.searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));

        // Render FAQ items
        this.renderFAQItems(modal);

        this.modal = modal;

        return { button, modal };
    }

    renderFAQItems(modal) {
        const container = modal.querySelector('.faq-items');

        FAQ_DATA.forEach((item, index) => {
            const faqItem = document.createElement('div');
            faqItem.className = 'faq-item';
            faqItem.setAttribute('data-question', item.question.toLowerCase());
            faqItem.setAttribute('data-answer', item.answer.toLowerCase());

            faqItem.innerHTML = `
                <div class="faq-question">${item.question}</div>
                <div class="faq-answer">${item.answer}</div>
            `;

            faqItem.querySelector('.faq-question').addEventListener('click', () => {
                faqItem.classList.toggle('open');
            });

            container.appendChild(faqItem);
        });
    }

    handleSearch(query) {
        const normalizedQuery = query.toLowerCase().trim();
        const items = this.modal.querySelectorAll('.faq-item');
        const noResults = this.modal.querySelector('.faq-no-results');
        let visibleCount = 0;

        items.forEach(item => {
            const question = item.getAttribute('data-question');
            const answer = item.getAttribute('data-answer');

            if (!normalizedQuery || question.includes(normalizedQuery) || answer.includes(normalizedQuery)) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        noResults.classList.toggle('show', visibleCount === 0);
    }

    open() {
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        this.isOpen = true;
        this.searchInput.value = '';
        this.handleSearch('');
        this.searchInput.focus();
    }

    close() {
        this.modal.classList.remove('show');
        document.body.style.overflow = '';
        this.isOpen = false;
    }
}

// Auto-initialize FAQ button
document.addEventListener('DOMContentLoaded', () => {
    const faq = new FAQModal();
    const { button, modal } = faq.create();

    document.body.appendChild(button);
    document.body.appendChild(modal);
});
