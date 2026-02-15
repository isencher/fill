/**
 * Mapping Page JavaScript
 * Handles column-to-placeholder mapping interface
 */

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const fileId = urlParams.get('file_id');
const templateId = urlParams.get('template_id');

// DOM elements
const loadingState = document.getElementById('loadingState');
const contentArea = document.getElementById('contentArea');
const emptyState = document.getElementById('emptyState');
const emptyStateMessage = document.getElementById('emptyStateMessage');
const fileName = document.getElementById('fileName');
const fileIdEl = document.getElementById('fileId');
const templateName = document.getElementById('templateName');
const templateIdEl = document.getElementById('templateId');
const tableHead = document.getElementById('tableHead');
const tableBody = document.getElementById('tableBody');
const placeholdersList = document.getElementById('placeholdersList');
const saveMappingBtn = document.getElementById('saveMappingBtn');
const cancelBtn = document.getElementById('cancelBtn');
const message = document.getElementById('message');

// Built-in templates (same as templates.js)
const BUILT_IN_TEMPLATES = {
    "builtin-invoice": {
        id: "builtin-invoice",
        name: "🧾 发票模板",
        description: "标准发票模板",
        placeholders: ["客户名称", "金额", "日期", "发票号码"]
    },
    "builtin-contract": {
        id: "builtin-contract",
        name: "📋 合同模板",
        description: "标准合同模板",
        placeholders: ["甲方", "乙方", "金额", "日期", "合同编号"]
    },
    "builtin-letter": {
        id: "builtin-letter",
        name: "✉️ 信函模板",
        description: "正式信函模板",
        placeholders: ["收件人", "主题", "日期", "发件人"]
    }
};

// Data storage
let fileData = null;
let templateData = null;
let columns = [];

// Show message
function showMessage(text, type) {
    message.textContent = text;
    message.className = `message show ${type}`;
    setTimeout(() => {
        message.className = 'message';
    }, 5000);
}

// Show/hide sections
function showSection(section) {
    loadingState.style.display = 'none';
    contentArea.style.display = 'none';
    emptyState.style.display = 'none';

    if (section === 'loading') {
        loadingState.style.display = 'block';
    } else if (section === 'content') {
        contentArea.style.display = 'block';
    } else if (section === 'empty') {
        emptyState.style.display = 'block';
    }
}

// Parse file to get data preview
async function loadFileData() {
    try {
        const response = await fetch(`/api/v1/parse/${fileId}`);
        if (!response.ok) {
            throw new Error('Failed to parse file');
        }
        const data = await response.json();

        // Store data
        fileData = data;

        // Get columns from first row
        if (data.rows && data.rows.length > 0) {
            columns = Object.keys(data.rows[0]);
        }

        // Update file info
        const fileResponse = await fetch(`/api/v1/files?limit=1000`);
        const fileDataList = await fileResponse.json();
        const fileInfo = fileDataList.files.find(f => f.file_id === fileId);
        if (fileInfo) {
            fileName.textContent = fileInfo.filename;
            fileIdEl.textContent = fileId;
        }

        return data;
    } catch (error) {
        console.error('Error loading file data:', error);
        showMessage('Failed to load file data: ' + error.message, 'error');
        return null;
    }
}

// Load template data
async function loadTemplateData() {
    try {
        // Check if it's a built-in template first
        if (BUILT_IN_TEMPLATES[templateId]) {
            templateData = BUILT_IN_TEMPLATES[templateId];
            templateName.textContent = templateData.name;
            templateIdEl.textContent = templateId;
            return templateData;
        }
        
        // Otherwise fetch from server
        const response = await fetch(`/api/v1/templates/${templateId}`);
        if (!response.ok) {
            throw new Error('Failed to load template');
        }
        const data = await response.json();

        templateData = data;

        // Update template info
        templateName.textContent = data.name;
        templateIdEl.textContent = templateId;

        return data;
    } catch (error) {
        console.error('Error loading template data:', error);
        showMessage('Failed to load template data: ' + error.message, 'error');
        return null;
    }
}

// Render data preview table
function renderDataTable(data) {
    // Clear existing content
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';

    if (!data.rows || data.rows.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="100%">No data available</td></tr>';
        return;
    }

    // Create header row with column names
    const headerRow = document.createElement('tr');
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);

    // Create data rows (first 5 only)
    const previewRows = data.rows.slice(0, 5);
    previewRows.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(column => {
            const td = document.createElement('td');
            const value = row[column];
            td.textContent = value !== null && value !== undefined ? value : '';
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

// Render placeholders list with mapping dropdowns
function renderPlaceholdersList(template) {
    placeholdersList.innerHTML = '';

    if (!template.placeholders || template.placeholders.length === 0) {
        placeholdersList.innerHTML = '<div class="empty-state">No placeholders found in template</div>';
        return;
    }

    template.placeholders.forEach(placeholder => {
        const item = document.createElement('div');
        item.className = 'placeholder-item';

        const label = document.createElement('div');
        label.className = 'placeholder-name';
        label.textContent = `{{${placeholder}}}`;

        const select = document.createElement('select');
        select.className = 'placeholder-select';
        select.dataset.placeholder = placeholder;

        // Add empty option
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '-- Select column --';
        select.appendChild(emptyOption);

        // Add column options
        columns.forEach(column => {
            const option = document.createElement('option');
            option.value = column;
            option.textContent = column;
            select.appendChild(option);
        });

        item.appendChild(label);
        item.appendChild(select);
        placeholdersList.appendChild(item);
    });
}

// Save mapping
async function saveMapping() {
    try {
        // Collect mappings
        const columnMappings = {};
        const selectElements = placeholdersList.querySelectorAll('.placeholder-select');

        selectElements.forEach(select => {
            const placeholder = select.dataset.placeholder;
            const column = select.value;

            if (column) {
                columnMappings[placeholder] = column;
            }
        });

        // Validate all placeholders are mapped
        const templatePlaceholders = templateData.placeholders || [];
        const unmapped = templatePlaceholders.filter(p => !columnMappings[p]);

        if (unmapped.length > 0) {
            showMessage(`Please map all placeholders. Unmapped: ${unmapped.join(', ')}`, 'error');
            return;
        }

        // Create mapping
        const mappingData = {
            file_id: fileId,
            template_id: templateId,
            column_mappings: columnMappings
        };

        saveMappingBtn.disabled = true;

        const response = await fetch('/api/v1/mappings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(mappingData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save mapping');
        }

        const result = await response.json();
        showMessage(`Mapping saved successfully! Mapping ID: ${result.id}`, 'success');

        // Redirect after 2 seconds
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);

    } catch (error) {
        console.error('Error saving mapping:', error);
        showMessage('Failed to save mapping: ' + error.message, 'error');
        saveMappingBtn.disabled = false;
    }
}

// Cancel and go back
function cancel() {
    if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
        window.location.href = '/';
    }
}

// Initialize page
async function init() {
    // Validate parameters with helpful error messages
    if (!fileId && !templateId) {
        emptyStateMessage.textContent = '请先上传数据文件并选择模板';
        document.getElementById('uploadLink').style.display = 'inline-block';
        showSection('empty');
        return;
    }
    
    if (!fileId) {
        emptyStateMessage.textContent = '缺少数据文件。请先上传数据文件。';
        document.getElementById('uploadLink').style.display = 'inline-block';
        showSection('empty');
        return;
    }
    
    if (!templateId) {
        emptyStateMessage.textContent = '缺少模板。请先选择模板。';
        // If we have file_id, link to template selection with file_id
        const templateLink = document.getElementById('templateLink');
        templateLink.href = '/templates.html?file_id=' + encodeURIComponent(fileId);
        templateLink.style.display = 'inline-block';
        showSection('empty');
        return;
    }

    showSection('loading');

    // Load data in parallel
    const [fileResult, templateResult] = await Promise.all([
        loadFileData(),
        loadTemplateData()
    ]);

    // Check if data loaded successfully
    if (!fileResult) {
        emptyStateMessage.textContent = 'Failed to load file data. Please try again or select a different file.';
        showSection('empty');
        return;
    }

    if (!templateResult) {
        emptyStateMessage.textContent = 'Failed to load template data. Please try again or select a different template.';
        showSection('empty');
        return;
    }

    // Render UI
    renderDataTable(fileResult);
    renderPlaceholdersList(templateResult);

    showSection('content');
}

// Event listeners
saveMappingBtn.addEventListener('click', saveMapping);
cancelBtn.addEventListener('click', cancel);

// Start initialization
init();
