/**
 * Template Selection Page JavaScript
 * Handles template listing, selection, and upload
 */

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const fileId = urlParams.get('file_id');

// DOM elements
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const contentArea = document.getElementById('contentArea');
const templateGrid = document.getElementById('templateGrid');
const fileName = document.getElementById('fileName');
const fileIdEl = document.getElementById('fileId');
const uploadArea = document.getElementById('uploadArea');
const templateFileInput = document.getElementById('templateFileInput');

// State
let selectedTemplate = null;
let fileInfo = null;

// Initialize page
async function init() {
    // Check if file_id is provided
    if (!fileId) {
        showError();
        return;
    }
    
    showLoading();
    
    // Load file info and templates in parallel
    const [fileResult, templatesResult] = await Promise.all([
        loadFileInfo(),
        loadTemplates()
    ]);
    
    if (!fileResult) {
        showError();
        return;
    }
    
    renderTemplates(templatesResult);
    showContent();
}

// Show/hide sections
function showLoading() {
    loadingState.style.display = 'block';
    errorState.style.display = 'none';
    contentArea.style.display = 'none';

    // Show skeleton loader for template list
    if (typeof showSkeleton === 'function') {
        showSkeleton('templateGrid', {
            type: 'card',
            count: 6,
            animate: true
        });
    }
}

function showError() {
    loadingState.style.display = 'none';
    errorState.style.display = 'block';
    contentArea.style.display = 'none';

    // Use the standardized empty state component
    createEmptyState('errorState', {
        icon: '⚠️',
        title: '缺少数据文件',
        message: '请先上传数据文件，再选择模板',
        variant: 'warning',
        actions: [
            {
                label: '← 返回上传数据',
                primary: true,
                onClick: () => {
                    window.location.href = '/';
                }
            }
        ]
    });
}

function showContent() {
    loadingState.style.display = 'none';
    errorState.style.display = 'none';
    contentArea.style.display = 'grid';
}

// Load file info
async function loadFileInfo() {
    try {
        const response = await fetch('/api/v1/files?limit=1000');
        if (!response.ok) {
            throw new Error('Failed to load files');
        }
        
        const data = await response.json();
        fileInfo = data.files.find(f => f.file_id === fileId);
        
        if (fileInfo) {
            fileName.textContent = fileInfo.filename;
            fileIdEl.textContent = fileId.substring(0, 8) + '...';
            return true;
        }
        
        // If not found in list, still proceed (might be in memory)
        fileName.textContent = '已上传文件';
        fileIdEl.textContent = fileId.substring(0, 8) + '...';
        return true;
    } catch (error) {
        console.error('Error loading file info:', error);
        // Don't fail - we can still proceed with template selection
        fileName.textContent = '已上传文件';
        fileIdEl.textContent = fileId.substring(0, 8) + '...';
        return true;
    }
}

// Built-in example templates
const BUILT_IN_TEMPLATES = [
    {
        id: "builtin-invoice",
        name: "🧾 发票模板",
        description: "标准发票模板，适用于开具各类发票",
        placeholders: ["客户名称", "金额", "日期", "发票号码"],
        file_path: "/templates/invoice.docx",
        created_at: new Date().toISOString()
    },
    {
        id: "builtin-contract",
        name: "📋 合同模板", 
        description: "标准合同模板，包含甲乙双方信息",
        placeholders: ["甲方", "乙方", "金额", "日期", "合同编号"],
        file_path: "/templates/contract.docx",
        created_at: new Date().toISOString()
    },
    {
        id: "builtin-letter",
        name: "✉️ 信函模板",
        description: "正式信函模板，适用于商务函件",
        placeholders: ["收件人", "主题", "日期", "发件人"],
        file_path: "/templates/letter.docx",
        created_at: new Date().toISOString()
    }
];

// Load templates
async function loadTemplates() {
    try {
        const response = await fetch('/api/v1/templates?limit=100');
        if (!response.ok) {
            throw new Error('Failed to load templates');
        }
        
        const data = await response.json();
        const serverTemplates = data.templates || [];
        
        // If no server templates, use built-in examples
        if (serverTemplates.length === 0) {
            console.log('No server templates, using built-in examples');
            return BUILT_IN_TEMPLATES;
        }
        
        return serverTemplates;
    } catch (error) {
        console.error('Error loading templates:', error);
        // Return built-in templates on error
        return BUILT_IN_TEMPLATES;
    }
}

// Convert placeholder names to readable business language
function getPlaceholderDescription(placeholders) {
    if (!placeholders || placeholders.length === 0) {
        return 'Basic template';
    }

    // Map of common placeholder keywords to business terms
    const keywordMap = {
        'name': '名称',
        'customer': '客户',
        'client': '客户',
        'amount': '金额',
        'money': '金额',
        'price': '价格',
        'date': '日期',
        'time': '时间',
        'number': '编号',
        'id': '编号',
        'invoice': '发票',
        'contract': '合同',
        'address': '地址',
        'email': '邮箱',
        'phone': '电话',
        'company': '公司',
        'product': '产品',
        'quantity': '数量'
    };

    // Extract keywords from placeholders
    const keywords = new Set();
    placeholders.forEach(p => {
        const lower = p.toLowerCase();
        for (const [key, value] of Object.entries(keywordMap)) {
            if (lower.includes(key)) {
                keywords.add(value);
            }
        }
    });

    // If no keywords found, use placeholder names directly
    if (keywords.size === 0) {
        const count = placeholders.length;
        const firstFew = placeholders.slice(0, 3).join('、');
        return count > 3
            ? `Includes: ${firstFew} 等 ${count} 项`
            : `Includes: ${firstFew}`;
    }

    // Convert to readable format
    const readable = Array.from(keywords).slice(0, 4).join('、');
    const count = keywords.size;
    return count > 4 ? `Includes: ${readable} 等 ${count} 项` : `Includes: ${readable}`;
}

// Render template cards
function renderTemplates(templates) {
    templateGrid.innerHTML = '';

    // If no templates, show message
    if (templates.length === 0) {
        templateGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #666;">
                <div style="font-size: 48px; margin-bottom: 15px;">📭</div>
                <div>暂无模板，请上传自定义模板</div>
            </div>
        `;
        return;
    }

    templates.forEach(template => {
        const card = document.createElement('div');
        card.className = 'template-card';
        card.setAttribute('data-testid', 'template-card');
        card.dataset.templateId = template.id;

        // Icon based on template name
        let icon = '📄';
        if (template.name.includes('发票')) icon = '🧾';
        else if (template.name.includes('合同')) icon = '📋';
        else if (template.name.includes('信')) icon = '✉️';

        // Get readable placeholder description
        const placeholderDescription = getPlaceholderDescription(template.placeholders);

        // Check if template has many placeholders (for "View Details" feature)
        const hasManyPlaceholders = (template.placeholders || []).length > 4;
        const placeholderCount = (template.placeholders || []).length;

        card.innerHTML = `
            <div class="template-icon">${icon}</div>
            <div class="template-name">${escapeHtml(template.name)}</div>
            <div class="template-description">${escapeHtml(template.description || '')}</div>
            <div class="template-summary">
                <span class="template-summary-icon">📋</span>
                <span class="template-summary-text">${placeholderDescription}</span>
                ${hasManyPlaceholders ? `<span class="template-summary-count">(${placeholderCount} 项)</span>` : ''}
            </div>
            ${hasManyPlaceholders ? `
                <button class="view-details-btn" data-template-id="${template.id}" data-testid="view-details-btn">
                    查看详情 ▼
                </button>
                <div class="template-details" data-details-for="${template.id}" style="display: none;">
                    <div class="template-details-title">数据字段：</div>
                    <div class="template-details-list">
                        ${(template.placeholders || []).map(p =>
                            `<code class="placeholder-code">{{${escapeHtml(p)}}}</code>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
            <button class="use-template-btn btn-primary" data-testid="use-template-btn">
                选择此模板 →
            </button>
        `;

        // Click to select
        card.addEventListener('click', (e) => {
            // Handle "View Details" button
            if (e.target.classList.contains('view-details-btn')) {
                e.stopPropagation();
                const detailsDiv = card.querySelector(`.template-details[data-details-for="${template.id}"]`);
                const btn = e.target;

                if (detailsDiv.style.display === 'none') {
                    detailsDiv.style.display = 'block';
                    btn.textContent = '收起详情 ▲';
                } else {
                    detailsDiv.style.display = 'none';
                    btn.textContent = '查看详情 ▼';
                }
                return;
            }

            // Handle "Use Template" button or card click
            if (e.target.classList.contains('use-template-btn') || !e.target.classList.contains('view-details-btn')) {
                // Remove selected class from all cards
                document.querySelectorAll('.template-card').forEach(c => c.classList.remove('selected'));

                // Add selected class to this card
                card.classList.add('selected');
                selectedTemplate = template.id;

                // Navigate to mapping page
                selectTemplate(template.id);
            }
        });

        templateGrid.appendChild(card);
    });
}

// Select template and navigate to mapping
function selectTemplate(templateId) {
    if (!templateId && !selectedTemplate) {
        alert('请先选择一个模板');
        return;
    }
    
    const finalTemplateId = templateId || selectedTemplate;
    
    // Navigate to mapping page with BOTH file_id and template_id
    const mappingUrl = `/mapping.html?file_id=${encodeURIComponent(fileId)}&template_id=${encodeURIComponent(finalTemplateId)}`;
    window.location.href = mappingUrl;
}

// Handle template file upload
uploadArea.addEventListener('click', () => {
    templateFileInput.click();
});

templateFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validTypes = ['.docx', '.txt', '.xlsx', '.DOCX', '.TXT', '.XLSX'];
    const isValid = validTypes.some(ext => file.name.endsWith(ext));
    
    if (!isValid) {
        alert('请上传 .docx, .xlsx 或 .txt 格式的模板文件');
        return;
    }
    
    // Upload template
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name.replace(/\.[^/.]+$/, ''));
    
    try {
        const response = await fetch('/api/v1/templates/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        
        // Navigate to mapping with new template
        selectTemplate(result.template.id);
        
    } catch (error) {
        console.error('Error uploading template:', error);
        alert('模板上传失败，请重试');
    }
});

// Utility: Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Start
init();
