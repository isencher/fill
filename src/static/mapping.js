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

// Show message with animation
function showMessage(text, type) {
    // Use the animation helper if available
    if (typeof animateMessage === 'function') {
        animateMessage(message, type);
        message.textContent = text;
    } else {
        // Fallback to original behavior
        message.textContent = text;
        message.className = `message show ${type}`;
        setTimeout(() => {
            message.className = 'message';
        }, 5000);
    }
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

// Show empty state with standardized component
function showEmptyState(type, customMessage = null) {
    const states = {
        NO_FILE_OR_TEMPLATE: {
            icon: '🔗',
            title: 'Setup required',
            message: '请先上传数据文件并选择模板',
            variant: 'warning',
            actions: [
                {
                    label: '← 返回上传数据',
                    primary: true,
                    onClick: () => { window.location.href = '/'; }
                }
            ]
        },
        NO_FILE: {
            icon: '📁',
            title: 'No data file',
            message: '缺少数据文件。请先上传数据文件。',
            variant: 'warning',
            actions: [
                {
                    label: '← 返回上传数据',
                    primary: true,
                    onClick: () => { window.location.href = '/'; }
                }
            ]
        },
        NO_TEMPLATE: {
            icon: '📄',
            title: 'No template selected',
            message: '缺少模板。请先选择模板。',
            variant: 'warning',
            actions: [
                {
                    label: '← 返回选择模板',
                    primary: true,
                    onClick: () => {
                        const url = fileId ? `/templates.html?file_id=${encodeURIComponent(fileId)}` : '/templates.html';
                        window.location.href = url;
                    }
                }
            ]
        },
        ERROR_LOADING_FILE: {
            icon: '❌',
            title: 'Failed to load file',
            message: 'Failed to load file data. Please try again or select a different file.',
            variant: 'error',
            actions: [
                {
                    label: '← 返回上传数据',
                    primary: true,
                    onClick: () => { window.location.href = '/'; }
                }
            ]
        },
        ERROR_LOADING_TEMPLATE: {
            icon: '❌',
            title: 'Failed to load template',
            message: 'Failed to load template data. Please try again or select a different template.',
            variant: 'error',
            actions: [
                {
                    label: '← 返回选择模板',
                    primary: true,
                    onClick: () => {
                        const url = fileId ? `/templates.html?file_id=${encodeURIComponent(fileId)}` : '/templates.html';
                        window.location.href = url;
                    }
                }
            ]
        }
    };

    const state = states[type];
    if (state) {
        createEmptyState('emptyState', {
            ...state,
            message: customMessage || state.message
        });
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

        // Add change event listener for animation
        select.addEventListener('change', () => {
            if (typeof animateSelectChange === 'function') {
                animateSelectChange(select);
            }
        });

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

        // Set button to loading state
        if (typeof setButtonLoading === 'function') {
            setButtonLoading(saveMappingBtn, true);
        } else {
            saveMappingBtn.disabled = true;
        }

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

        // Show button success animation
        if (typeof setButtonLoading === 'function') {
            setButtonLoading(saveMappingBtn, false);
        }
        if (typeof setButtonSuccess === 'function') {
            setButtonSuccess(saveMappingBtn);
        }

        // Redirect after 2 seconds
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);

    } catch (error) {
        console.error('Error saving mapping:', error);
        showMessage('Failed to save mapping: ' + error.message, 'error');
        if (typeof setButtonLoading === 'function') {
            setButtonLoading(saveMappingBtn, false);
        } else {
            saveMappingBtn.disabled = false;
        }
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
        showEmptyState('NO_FILE_OR_TEMPLATE');
        showSection('empty');
        return;
    }
    
    if (!fileId) {
        showEmptyState('NO_FILE');
        showSection('empty');
        return;
    }
    
    if (!templateId) {
        showEmptyState('NO_TEMPLATE');
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
        showEmptyState('ERROR_LOADING_FILE');
        showSection('empty');
        return;
    }

    if (!templateResult) {
        showEmptyState('ERROR_LOADING_TEMPLATE');
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
