/**
 * File Upload JavaScript
 * Handles drag-and-drop file upload with progress tracking
 */

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const progress = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const message = document.getElementById('message');

let selectedFile = null;

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Validate file type
function validateFileType(file) {
    const validExtensions = ['.xlsx', '.csv', '.XLSX', '.CSV'];
    const fileName = file.name;
    return validExtensions.some(ext => fileName.endsWith(ext));
}

// Show message
function showMessage(text, type) {
    message.textContent = text;
    message.className = `message show ${type}`;
    setTimeout(() => {
        message.className = 'message';
    }, 5000);
}

// Update progress
function updateProgress(percent) {
    progressFill.style.width = percent + '%';
    progressText.textContent = percent + '%';
}

// Handle file selection
function handleFileSelect(file) {
    // Reset UI
    message.className = 'message';
    progress.className = 'progress';
    progressFill.style.width = '0%';
    progressText.textContent = '0%';

    // Validate file type
    if (!validateFileType(file)) {
        showMessage('Invalid file type. Please upload .xlsx or .csv files only.', 'error');
        selectedFile = null;
        fileInfo.className = 'file-info';
        uploadBtn.disabled = true;
        return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showMessage('File too large. Maximum size is 10MB.', 'error');
        selectedFile = null;
        fileInfo.className = 'file-info';
        uploadBtn.disabled = true;
        return;
    }

    // Store file and update UI
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.className = 'file-info show';
    uploadBtn.disabled = false;
}

// Upload file to server
async function uploadFile() {
    if (!selectedFile) {
        showMessage('Please select a file first.', 'error');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);

    // Show progress
    progress.className = 'progress show';
    uploadBtn.disabled = true;

    try {
        // Create XMLHttpRequest for progress tracking
        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                updateProgress(percentComplete);
            }
        });

        // Handle completion
        xhr.addEventListener('load', () => {
            if (xhr.status === 201) {
                const response = JSON.parse(xhr.responseText);
                showMessage(`File uploaded successfully! File ID: ${response.file_id}`, 'success');
                updateProgress(100);

                // Reset form after 2 seconds
                setTimeout(() => {
                    resetForm();
                }, 2000);
            } else if (xhr.status === 413) {
                showMessage('File too large. Maximum size is 10MB.', 'error');
                uploadBtn.disabled = false;
            } else {
                const response = JSON.parse(xhr.responseText);
                showMessage(response.detail || 'Upload failed. Please try again.', 'error');
                uploadBtn.disabled = false;
            }
        });

        // Handle errors
        xhr.addEventListener('error', () => {
            showMessage('Network error. Please check your connection and try again.', 'error');
            uploadBtn.disabled = false;
        });

        // Send request
        xhr.open('POST', '/api/v1/upload');
        xhr.send(formData);

    } catch (error) {
        showMessage('Upload failed: ' + error.message, 'error');
        uploadBtn.disabled = false;
    }
}

// Reset form
function resetForm() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.className = 'file-info';
    progress.className = 'progress';
    progressFill.style.width = '0%';
    progressText.textContent = '0%';
    message.className = 'message';
    uploadBtn.disabled = true;
}

// Event Listeners

// Click on upload area
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop events
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Upload button click
uploadBtn.addEventListener('click', uploadFile);
