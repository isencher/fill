/**
 * Client-Side Validation Utilities
 * Provides real-time validation for file uploads and form inputs
 */

const ValidationUtils = {
    /**
     * Validate file size
     */
    validateFileSize(file, maxSize = 10 * 1024 * 1024) {
        // Default max size: 10MB
        if (!file) {
            return {
                valid: false,
                error: 'No file provided',
                maxSize: maxSize
            };
        }

        if (file.size > maxSize) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            const maxMB = (maxSize / (1024 * 1024)).toFixed(2);
            return {
                valid: false,
                error: `File size (${sizeMB}MB) exceeds maximum (${maxMB}MB)`,
                currentSize: file.size,
                maxSize: maxSize,
                sizeMB: sizeMB,
                maxMB: maxMB
            };
        }

        return {
            valid: true,
            size: file.size,
            sizeMB: (file.size / (1024 * 1024)).toFixed(2)
        };
    },

    /**
     * Validate file type using magic bytes
     */
    async validateFileType(file) {
        if (!file) {
            return {
                valid: false,
                error: 'No file provided'
            };
        }

        const allowedExtensions = ['csv', 'xlsx', 'xls'];
        const extension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) {
            return {
                valid: false,
                error: `File type ".${extension}" is not supported. Allowed types: ${allowedExtensions.join(', ')}`,
                extension: extension
            };
        }

        // Validate with magic bytes
        const magicBytes = await this._readMagicBytes(file);
        const detectedType = this._detectFileTypeFromMagicBytes(magicBytes);

        if (detectedType && detectedType !== extension) {
            return {
                valid: false,
                error: `File extension (${extension}) does not match actual file type (${detectedType})`,
                extension: extension,
                detectedType: detectedType
            };
        }

        return {
            valid: true,
            extension: extension,
            detectedType: detectedType
        };
    },

    /**
     * Read first few bytes of file for magic byte detection
     */
    async _readMagicBytes(file, bytesToRead = 16) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const arrayBuffer = e.target.result;
                const uint8Array = new Uint8Array(arrayBuffer);
                resolve(Array.from(uint8Array.slice(0, bytesToRead)));
            };
            reader.onerror = () => resolve(null);
            reader.readAsArrayBuffer(file.slice(0, bytesToRead));
        });
    },

    /**
     * Detect file type from magic bytes
     */
    _detectFileTypeFromMagicBytes(bytes) {
        if (!bytes || bytes.length < 4) {
            return null;
        }

        // CSV - Check if file starts with text content
        if (this._isTextFile(bytes)) {
            return 'csv';
        }

        // Excel (XLSX) - ZIP signature (xlsx files are ZIP archives)
        if (bytes[0] === 0x50 && bytes[1] === 0x4B && bytes[2] === 0x03 && bytes[3] === 0x04) {
            return 'xlsx';
        }

        // Excel (XLS) - OLE signature
        if (bytes[0] === 0xD0 && bytes[1] === 0xCF && bytes[2] === 0x11 && bytes[3] === 0xE0 && bytes[4] === 0xA1 && bytes[5] === 0xB1 && bytes[6] === 0x1A && bytes[7] === 0xE1) {
            return 'xls';
        }

        return null;
    },

    /**
     * Check if file is text-based
     */
    _isTextFile(bytes) {
        // Check if bytes are printable ASCII or UTF-8
        for (let i = 0; i < Math.min(bytes.length, 1000); i++) {
            const byte = bytes[i];
            // Allow common text characters
            if (byte < 9 || (byte > 13 && byte < 32)) {
                // Control characters except tab (9), newline (10), carriage return (13)
                return false;
            }
            if (byte > 126 && byte < 160) {
                // Extended ASCII - might be UTF-8 multibyte character
                // For simplicity, accept it
            }
        }
        return true;
    },

    /**
     * Validate form field
     */
    validateField(value, rules) {
        const errors = [];
        const warnings = [];

        if (rules.required && (!value || value.trim() === '')) {
            errors.push('This field is required');
        }

        if (value && rules.minLength && value.length < rules.minLength) {
            errors.push(`Minimum length is ${rules.minLength} characters`);
        }

        if (value && rules.maxLength && value.length > rules.maxLength) {
            errors.push(`Maximum length is ${rules.maxLength} characters`);
        }

        if (value && rules.pattern && !rules.pattern.test(value)) {
            errors.push('Invalid format');
        }

        if (value && rules.email && !this._isValidEmail(value)) {
            errors.push('Invalid email address');
        }

        if (value && rules.url && !this._isValidUrl(value)) {
            errors.push('Invalid URL');
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            warnings: warnings
        };
    },

    /**
     * Validate email address
     */
    _isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validate URL
     */
    _isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Show validation feedback
     */
    showFeedback(element, result) {
        if (!element) return;

        // Remove existing feedback
        const existingFeedback = element.querySelector('.validation-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Remove existing classes
        element.classList.remove('valid', 'invalid');

        if (!result.valid) {
            // Show error
            element.classList.add('invalid');
            element.setAttribute('aria-invalid', 'true');

            // Create feedback message
            const feedback = document.createElement('div');
            feedback.className = 'validation-feedback';
            feedback.setAttribute('role', 'alert');
            feedback.setAttribute('aria-live', 'polite');
            feedback.textContent = result.error || result.errors.join(', ');

            element.appendChild(feedback);

            // Announce to screen readers
            if (window.A11yUtils && A11yUtils.announce) {
                A11yUtils.announce(`Validation failed: ${feedback.textContent}`);
            }
        } else {
            // Show success
            element.classList.add('valid');
            element.setAttribute('aria-invalid', 'false');
        }
    },

    /**
     * Real-time file validation with progress
     */
    async validateFileWithProgress(file, onProgress) {
        const maxSize = 10 * 1024 * 1024; // 10MB

        return new Promise((resolve) => {
            // Phase 1: Check file size
            if (onProgress) onProgress({ phase: 'size', progress: 33 });

            const sizeResult = this.validateFileSize(file, maxSize);
            if (!sizeResult.valid) {
                resolve({
                    valid: false,
                    phase: 'size',
                    ...sizeResult
                });
                return;
            }

            // Phase 2: Check file type
            if (onProgress) onProgress({ phase: 'type', progress: 66 });

            setTimeout(async () => {
                const typeResult = await this.validateFileType(file);

                // Phase 3: Complete
                if (onProgress) onProgress({ phase: 'complete', progress: 100 });

                if (!typeResult.valid) {
                    resolve({
                        valid: false,
                        phase: 'type',
                        ...typeResult
                    });
                } else {
                    resolve({
                        valid: true,
                        phase: 'complete',
                        file: file,
                        sizeResult: sizeResult,
                        typeResult: typeResult
                    });
                }
            }, 100); // Small delay to show progress
        });
    },

    /**
     * Batch validate multiple files
     */
    async validateMultipleFiles(files, onProgress) {
        const results = [];
        const total = files.length;

        for (let i = 0; i < total; i++) {
            const result = await this.validateFileWithProgress(files[i]);
            results.push(result);

            if (onProgress) {
                onProgress({
                    current: i + 1,
                    total: total,
                    progress: ((i + 1) / total) * 100
                });
            }
        }

        return results;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ValidationUtils;
}
