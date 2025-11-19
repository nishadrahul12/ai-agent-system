// ============================================================================
// AI MULTI-AGENT SYSTEM - DASHBOARD JAVASCRIPT
// ============================================================================

const API_URL = 'http://localhost:8000';
let currentFileId = null;
let currentTaskId = null;
let currentColumnMapping = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    loadColumnTypes();  // ← ADD THIS LINE
    setupFileUpload();
    setupTabs();
    checkAPIStatus();
    
    // Check API status every 5 seconds
    setInterval(checkAPIStatus, 5000);
});


// ============================================================================
// API STATUS CHECK
// ============================================================================

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            document.getElementById('api-status').textContent = '● Connected';
            document.getElementById('api-status').classList.add('online');
            document.getElementById('api-status').classList.remove('offline');
        } else {
            setOfflineStatus();
        }
    } catch (error) {
        setOfflineStatus();
    }
}

function setOfflineStatus() {
    document.getElementById('api-status').textContent = '● Offline';
    document.getElementById('api-status').classList.remove('online');
    document.getElementById('api-status').classList.add('offline');
}

// ============================================================================
// FILE UPLOAD SETUP
// ============================================================================

function setupFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');

    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
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
            handleFileUpload(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// ============================================================================
// HANDLE FILE UPLOAD
// ============================================================================

async function handleFileUpload(file) {
    try {
        // Validate file type
        if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
            alert('Please upload a CSV or Excel file');
            return;
        }

        // Validate file size (5GB)
        const fileSizeGB = file.size / (1024 ** 3);
        if (fileSizeGB > 5) {
            alert('File too large! Maximum 5GB allowed');
            return;
        }

        // Show loading
        showMessage('Uploading file...');

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);

        // Upload to API
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Upload response:', data);

        // Store file ID
        currentFileId = data.file_id;
        currentColumnMapping = data.auto_column_mapping;

        // Display file info
        document.getElementById('fileInfo').style.display = 'block';
        document.getElementById('fileName').textContent = data.filename;
        document.getElementById('fileSize').textContent = `${data.file_size_mb} MB`;
        document.getElementById('fileEncoding').textContent = data.encoding;

        // Show column mapping
        displayColumnMapping(data.columns, data.auto_column_mapping);

        // Enable analyze button
        document.getElementById('analyzeBtn').disabled = false;

        // Check which tab is active and load columns
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        if (activeTab === 'correlation') {
            loadNumericColumnsForCorrelation(currentFileId);
        } else if (activeTab === 'prediction') {
            loadNumericColumnsForPrediction(currentFileId);
        }
        
        // Enable correlation and prediction buttons
        document.getElementById('correlationBtn').disabled = false;
        document.getElementById('predictionBtn').disabled = false;
        document.getElementById('analyzeBtn').disabled = false;

    } catch (error) {
        console.error('Upload error:', error);
        showMessage(`Error: ${error.message}`, 'error');
    }
}

// ============================================================================
// COLUMN MAPPING WITH MEMORY
// ============================================================================

let availableColumnTypes = {};

// Load column types on startup
async function loadColumnTypes() {
    try {
        const response = await fetch(`${API_URL}/column-types`);
        if (response.ok) {
            const data = await response.json();
            availableColumnTypes = data.column_types.common_column_types;
            console.log('Column types loaded:', availableColumnTypes);
        }
    } catch (error) {
        console.error('Error loading column types:', error);
    }
}

function displayColumnMapping(columns, mapping) {
    const section = document.getElementById('columnMappingSection');
    const container = document.getElementById('columnMappingContainer');

    container.innerHTML = '';

    columns.forEach(col => {
        const detectedType = mapping[col] || 'unknown';

        const row = document.createElement('div');
        row.className = 'column-mapping-row';
        row.style.marginBottom = '1rem';
        row.style.padding = '1rem';
        row.style.background = 'rgba(51, 65, 85, 0.3)';
        row.style.borderRadius = '6px';
        row.style.borderLeft = '3px solid var(--primary-color)';

        const columnLabel = document.createElement('div');
        columnLabel.style.marginBottom = '0.5rem';
        columnLabel.innerHTML = `<strong>Column: ${col}</strong><br><small style="color: var(--text-secondary);">Sample values: [auto-detected]</small>`;

        // Tab buttons to switch between Standard, Telecom, User Saved
        const tabContainer = document.createElement('div');
        tabContainer.style.display = 'flex';
        tabContainer.style.gap = '0.5rem';
        tabContainer.style.marginBottom = '0.5rem';
        tabContainer.style.borderBottom = '1px solid var(--border-color)';
        tabContainer.style.paddingBottom = '0.5rem';

        const tabs = ['Standard', 'Telecom', 'user_saved'];
        tabs.forEach(tab => {
            const btn = document.createElement('button');
            btn.textContent = tab === 'user_saved' ? 'Custom Saved' : tab;
            btn.style.padding = '0.4rem 0.8rem';
            btn.style.background = 'transparent';
            btn.style.border = '1px solid var(--border-color)';
            btn.style.color = 'var(--text-primary)';
            btn.style.borderRadius = '4px';
            btn.style.cursor = 'pointer';
            btn.style.fontSize = '0.85rem';
            btn.onclick = () => switchTab(col, tab);
            tabContainer.appendChild(btn);
        });

        // Dropdown for standard types
        const select = document.createElement('select');
        select.id = `col_${col}`;
        select.style.width = '100%';
        select.style.padding = '0.75rem';
        select.style.background = 'var(--bg-tertiary)';
        select.style.color = 'var(--text-primary)';
        select.style.border = '1px solid var(--border-color)';
        select.style.borderRadius = '6px';
        select.style.fontSize = '0.9rem';
        select.style.marginBottom = '0.5rem';
        select.style.cursor = 'pointer';
        select.value = detectedType;
        select.onchange = () => updateColumnMapping(col, select.value);

        // Add Standard options
        const standardGroup = document.createElement('optgroup');
        standardGroup.label = '📋 Standard Types';
        (availableColumnTypes.Standard || []).forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.label;
            standardGroup.appendChild(option);
        });
        select.appendChild(standardGroup);

        // Add Telecom options
        const telecomGroup = document.createElement('optgroup');
        telecomGroup.label = '📡 Telecom Types';
        (availableColumnTypes.Telecom || []).forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.label;
            telecomGroup.appendChild(option);
        });
        select.appendChild(telecomGroup);

        // Add Custom option
        const customOption = document.createElement('option');
        customOption.value = 'custom_text';
        customOption.textContent = '✏️ Custom Description';
        select.appendChild(customOption);

        // Custom text input (hidden by default)
        const customInput = document.createElement('input');
        customInput.type = 'text';
        customInput.id = `custom_${col}`;
        customInput.placeholder = 'Describe this column type...';
        customInput.style.width = '100%';
        customInput.style.padding = '0.75rem';
        customInput.style.background = 'var(--bg-tertiary)';
        customInput.style.color = 'var(--text-primary)';
        customInput.style.border = '1px solid var(--secondary-color)';
        customInput.style.borderRadius = '6px';
        customInput.style.fontSize = '0.9rem';
        customInput.style.display = 'none';
        customInput.style.marginTop = '0.5rem';
        customInput.placeholder = `Example: "Radio Access Channel Setup Attempts" or "Date in M/D/YYYY format"`;
        customInput.onchange = () => {
            if (customInput.value) {
                updateColumnMapping(col, `custom: ${customInput.value}`);
            }
        };

        // Show/hide custom input based on selection
        select.onchange = function() {
            if (this.value === 'custom_text') {
                customInput.style.display = 'block';
                customInput.focus();
            } else {
                customInput.style.display = 'none';
                updateColumnMapping(col, this.value);
            }
        };

        row.appendChild(columnLabel);
        row.appendChild(tabContainer);
        row.appendChild(select);
        row.appendChild(customInput);

        container.appendChild(row);
    });

    section.style.display = 'block';
}

function switchTab(columnName, tabName) {
    // For future enhancement: switch between tab categories
    console.log(`Switching ${columnName} to ${tabName}`);
}

function updateColumnMapping(column, type) {
    if (currentColumnMapping) {
        currentColumnMapping[column] = type;
        console.log('Updated mapping:', currentColumnMapping);
    }
}

function resetColumnMapping() {
    location.reload();
}

async function saveColumnMappings() {
    try {
        if (!currentFileId || !currentColumnMapping) {
            alert('No mappings to save');
            return;
        }

        const response = await fetch(`${API_URL}/save-column-mapping`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: currentFileId,
                mapping: currentColumnMapping
            })
        });

        if (response.ok) {
            showMessage('Column mappings saved! Will use for future uploads.', 'success');
        } else {
            throw new Error('Failed to save');
        }
    } catch (error) {
        console.error('Save error:', error);
        showMessage(`Error saving mappings: ${error.message}`, 'error');
    }
}


// ============================================================================
// TASK TYPE HANDLING
// ============================================================================

function selectPredefinedTask() {
    const select = document.getElementById('predefinedTasks');
    const customDiv = document.getElementById('customTaskDiv');
    const selected = select.value;

    if (selected === 'custom') {
        customDiv.style.display = 'block';
        document.getElementById('customTaskInput').focus();
    } else if (selected) {
        customDiv.style.display = 'none';
        // Auto-select the radio button
        const radio = document.querySelector(`input[value="${selected}"]`);
        if (radio) {
            radio.checked = true;
        }
    } else {
        customDiv.style.display = 'none';
    }
}

// ============================================================================
// CORRELATION ANALYSIS
// ============================================================================

async function loadNumericColumns(fileId) {
    try {
        const response = await fetch(`${API_URL}/get-numeric-columns/${fileId}`);
        if (response.ok) {
            const data = await response.json();
            populateCorrelationUI(data.numeric_columns);
        }
    } catch (error) {
        console.error('Error loading numeric columns:', error);
        showMessage('Error loading columns for correlation', 'error');
    }
}

function populateCorrelationUI(columns) {
    // Populate target column dropdown
    const targetSelect = document.getElementById('targetColumn');
    targetSelect.innerHTML = '<option value="">-- Select target column --</option>';
    
    columns.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = col;
        targetSelect.appendChild(option);
    });

    // Populate source columns checkboxes
    const container = document.getElementById('sourceColumnsContainer');
    container.innerHTML = '';
    
    columns.forEach(col => {
        const label = document.createElement('label');
        label.style.display = 'flex';
        label.style.alignItems = 'center';
        label.style.gap = '0.5rem';
        label.style.cursor = 'pointer';
        label.style.padding = '0.5rem';
        label.style.borderRadius = '4px';
        label.style.transition = 'background 0.2s';
        
        label.onmouseover = () => label.style.background = 'rgba(37, 99, 235, 0.1)';
        label.onmouseout = () => label.style.background = 'transparent';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = col;
        checkbox.className = 'source-column-checkbox';
        checkbox.style.cursor = 'pointer';
        checkbox.style.width = '1.2rem';
        checkbox.style.height = '1.2rem';
        checkbox.style.accentColor = 'var(--primary-color)';
        
        const span = document.createElement('span');
        span.textContent = col;
        span.style.flex = '1';
        
        label.appendChild(checkbox);
        label.appendChild(span);
        container.appendChild(label);
    });
}

async function runCorrelationAnalysis() {
    try {
        console.log('=== Running Correlation Analysis ===');
        
        if (!currentFileId) {
            alert('Please upload a file first');
            return;
        }

        const targetColumn = document.getElementById('targetColumn').value;
        console.log('Target Column:', targetColumn);
        
        if (!targetColumn) {
            alert('Please select a target column');
            return;
        }

        // Get checked source columns
        const checkboxes = document.querySelectorAll('.source-column-checkbox:checked');
        console.log('Selected checkboxes:', checkboxes.length);
        
        if (checkboxes.length < 2) {
            alert('Please select at least 2 source columns');
            return;
        }

        const sourceColumns = Array.from(checkboxes).map(cb => {
            console.log('Selected source:', cb.value);
            return cb.value;
        });

        console.log('Final payload:', {
            file_id: currentFileId,
            target_column: targetColumn,
            source_columns: sourceColumns
        });

        // Show loading state
        showMessage('Analyzing correlations... this may take 1-2 minutes', 'info');
        document.getElementById('statusSection').style.display = 'block';
        document.getElementById('statusMessage').textContent = 'Processing your data...';
        document.getElementById('resultsSection').style.display = 'none';
        
        // Make API call
        const response = await fetch(`${API_URL}/correlation-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: currentFileId,
                target_column: targetColumn,
                source_columns: sourceColumns
            })
        });

        console.log('API Response Status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error:', errorData);
            throw new Error(errorData.detail || `HTTP ${response.status}: Analysis failed`);
        }

        const data = await response.json();
        console.log('Analysis Results:', data);
        
        // Hide loading, show results
        document.getElementById('statusSection').style.display = 'none';
        displayCorrelationResults(data.analysis);
        document.getElementById('resultsSection').style.display = 'block';
        
        showMessage('✅ Correlation analysis complete!', 'success');

    } catch (error) {
        console.error('❌ Analysis Error:', error);
        document.getElementById('statusSection').style.display = 'none';
        showMessage(`Error: ${error.message}`, 'error');
    }
}

function displayCorrelationResults(analysis) {
    try {
        console.log('Displaying correlation results...');
        console.log('Analysis data:', analysis);
        
        // Hide other sections
        document.getElementById('statusSection').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

        // Summary
        // Create outlier warning if outliers detected
        const outlierWarning = analysis.outlier_detection?.warning_message 
            ? `<div style="padding: 1rem; margin-bottom: 1rem; background: ${
                analysis.outlier_detection.severity === 'high' ? 'rgba(239, 68, 68, 0.15)' :
                analysis.outlier_detection.severity === 'medium' ? 'rgba(245, 158, 11, 0.15)' :
                'rgba(34, 197, 94, 0.15)'
            }; border-left: 4px solid ${
                analysis.outlier_detection.severity === 'high' ? '#ef4444' :
                analysis.outlier_detection.severity === 'medium' ? '#f59e0b' :
                '#22c55e'
            }; border-radius: 6px;">
                <strong>${analysis.outlier_detection.warning_message}</strong>
                ${analysis.outlier_detection.outlier_columns?.length > 0 ? 
                `<div style="font-size: 0.85rem; margin-top: 0.5rem; color: var(--text-secondary);">
                    <strong>Affected Columns:</strong> ${analysis.outlier_detection.outlier_columns.join(', ')}<br>
                    <strong>Outlier Percentages:</strong> ${Object.entries(analysis.outlier_detection.outlier_percentages || {})
                    .map(([col, pct]) => `${col.substring(0, 30)}: ${pct}%`)
                    .join(' | ')}
                </div>` : ''
            }
        </div>` : '';

        const summaryHtml = `
            <div style="margin-bottom: 1rem;">
                ${outlierWarning}
                <h4>📊 Analysis Summary</h4>
                <p><strong>Best Model:</strong> ${analysis.best_model}</p>
                <p><strong>Accuracy (R² Score):</strong> ${(analysis.score_percentage).toFixed(2)}%</p>
                <p><strong>Target Variable:</strong> ${analysis.target}</p>
            </div>
        `;

        document.getElementById('resultsSummary').innerHTML = summaryHtml;

        // Features ranked by correlation
        const findingsHtml = analysis.features_ranked.map((item, idx) => `
            <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(37, 99, 235, 0.1); border-radius: 6px; border-left: 3px solid var(--primary-color);">
                <strong>#${item.rank}: ${item.feature}</strong><br>
                <span style="color: var(--secondary-color);">Correlation Score: ${(item.correlation_score * 100).toFixed(2)}%</span><br>
                <small style="color: var(--text-secondary);">💡 ${item.explanation}</small>
            </div>
        `).join('');
        document.getElementById('resultsFindings').innerHTML = findingsHtml;

        // All models comparison
        const modelsHtml = `
            <ul style="list-style: none; padding: 0;">
                ${analysis.all_models.map(m => `
                    <li style="padding: 0.5rem; margin-bottom: 0.5rem; background: rgba(51, 65, 85, 0.3); border-radius: 4px;">
                        <strong>${m.model_name}:</strong> ${m.score_percentage.toFixed(2)}%
                        ${m.model_name === analysis.best_model ? ' ⭐ BEST FIT' : ''}
                    </li>
                `).join('')}
            </ul>
        `;
        document.getElementById('resultsRisks').innerHTML = modelsHtml;

        // Recommendations
        document.getElementById('resultsRecommendations').innerHTML = `
            <p><strong>How to Interpret:</strong></p>
            <ul>
                <li>Features are ranked by their correlation strength with the target</li>
                <li>Top features (#1-3) have the strongest influence on ${analysis.target}</li>
                <li>${analysis.best_model} provided the best fit for this data</li>
                <li>R² Score of ${analysis.score_percentage.toFixed(2)}% indicates model quality</li>
            </ul>
        `;
        
        console.log('✅ Results displayed successfully');
        
    } catch (error) {
        console.error('❌ Error displaying results:', error);
        showMessage('Error displaying results: ' + error.message, 'error');
    }
}

// ============================================================================
// START ANALYSIS
// ============================================================================

async function startAnalysis() {
    try {
        if (!currentFileId) {
            alert('Please upload a file first');
            return;
        }

        // Get task type
        let taskType = document.querySelector('input[name="taskType"]:checked').value;
        
        // If custom task, use custom input
        if (taskType === 'custom') {
            const customTask = document.getElementById('customTaskInput').value;
            if (!customTask.trim()) {
                alert('Please describe your custom task');
                return;
            }
            // For custom tasks, send as description
            taskType = `custom_${Date.now()}`;
        }


        // Show status
        document.getElementById('statusSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';

        showMessage('Starting analysis...');

        // Call API
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: currentFileId,
                task_type: taskType,
                custom_column_mapping: currentColumnMapping
            })
        });

        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Analysis response:', data);

        currentTaskId = data.task_id;

        // Display results
        displayResults(data.results);

    } catch (error) {
        console.error('Analysis error:', error);
        showMessage(`Error: ${error.message}`, 'error');
        document.getElementById('statusSection').style.display = 'none';
    }
}

// Show/hide correlation section based on task type
function updateTaskTypeUI() {
    const taskType = document.querySelector('input[name="taskType"]:checked').value;
    const correlationSection = document.getElementById('correlationSection');
    const predictionSection = document.getElementById('predictionSection');
    
    if (taskType === 'correlation' && currentFileId) {
        correlationSection.style.display = 'block';
        loadNumericColumns(currentFileId);
    } else {
        correlationSection.style.display = 'none';
    }
    
    if (taskType === 'prediction' && currentFileId) {
        predictionSection.style.display = 'block';
        loadNumericColumns(currentFileId);
    } else {
        predictionSection.style.display = 'none';
    }
}


// ============================================================================
// DISPLAY RESULTS
// ============================================================================

function displayResults(results) {
    try {
        // Hide status
        document.getElementById('statusSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

        // Parse results
        const result = Array.isArray(results) ? results[0] : results;

        // Display summary
        const summary = result.analysis?.summary || 'Analysis completed successfully';
        document.getElementById('resultsSummary').innerHTML = `<p>${summary}</p>`;

        // Display findings
        const findings = result.analysis?.key_findings || [];
        const findingsHTML = findings.length > 0
            ? `<ul>${findings.map(f => `<li><strong>${f.finding}</strong> - Confidence: ${(f.confidence * 100).toFixed(0)}%</li>`).join('')}</ul>`
            : '<p>No specific findings.</p>';
        document.getElementById('resultsFindings').innerHTML = findingsHTML;

        // Display risks
        const risks = result.risks_identified || [];
        const risksHTML = risks.length > 0
            ? `<ul>${risks.map(r => `<li><strong>${r.risk_type}</strong> - Probability: ${(r.probability * 100).toFixed(0)}%</li>`).join('')}</ul>`
            : '<p>No risks identified.</p>';
        document.getElementById('resultsRisks').innerHTML = risksHTML;

        // Display recommendations
        const recommendations = result.recommendations || [];
        const recsHTML = recommendations.length > 0
            ? `<ol>${recommendations.map((r, i) => `<li><strong>${r.action}</strong> (Timeline: ${r.timeline})</li>`).join('')}</ol>`
            : '<p>No recommendations.</p>';
        document.getElementById('resultsRecommendations').innerHTML = recsHTML;

        showMessage('Analysis complete!', 'success');

    } catch (error) {
        console.error('Display error:', error);
        showMessage(`Error displaying results: ${error.message}`, 'error');
    }
}

// ============================================================================
// DOWNLOAD RESULTS
// ============================================================================

async function downloadResults(format) {
    try {
        if (!currentTaskId) {
            alert('No results to download');
            return;
        }

        showMessage(`Downloading ${format.toUpperCase()}...`);

        const url = `${API_URL}/download/${currentTaskId}?format=${format}`;
        
        // Create link and download
        const link = document.createElement('a');
        link.href = url;
        link.download = `analysis_results_${currentTaskId}.${format === 'excel' ? 'xlsx' : format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showMessage(`Downloaded as ${format.toUpperCase()}!`, 'success');

    } catch (error) {
        console.error('Download error:', error);
        showMessage(`Download failed: ${error.message}`, 'error');
    }
}

// ============================================================================
// CLEAR ALL
// ============================================================================

function clearAll() {
    if (confirm('Clear all data and start over?')) {
        currentFileId = null;
        currentTaskId = null;
        currentColumnMapping = null;

        document.getElementById('fileInput').value = '';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('columnMappingSection').style.display = 'none';
        document.getElementById('statusSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('emptyState').style.display = 'block';
        document.getElementById('analyzeBtn').disabled = true;

        showMessage('All cleared!', 'success');
    }
}

// ============================================================================
// MESSAGE DISPLAY
// ============================================================================

function showMessage(msg, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${msg}`);
    // Can be extended to show toast notifications
}

// Redirect API root to dashboard
if (window.location.pathname === '/' || window.location.pathname === '') {
    console.log('Dashboard loaded');
}

// ============================================================================
// TAB MANAGEMENT
// ============================================================================

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
}

function switchTab(tabName) {
    console.log('Switching to tab:', tabName);
    
    // Hide all tab configs
    document.querySelectorAll('.tab-config').forEach(el => {
        el.classList.remove('active');
    });
    
    // Remove active from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab config
    const tabConfig = document.getElementById(`tab-${tabName}-config`);
    if (tabConfig) {
        tabConfig.classList.add('active');
    }
    
    // Mark button as active
    const btn = document.querySelector(`[data-tab="${tabName}"]`);
    if (btn) {
        btn.classList.add('active');
    }
    
    // Update results title
    const titles = {
        'analysis': '📊 Task Analysis Results',
        'correlation': '📈 Correlation Analysis Results',
        'prediction': '🔮 Time-Series Forecast'
    };
    document.getElementById('resultsTitle').textContent = titles[tabName] || '📊 Results';
    
    // If file already uploaded, load numeric columns for new tab
    if (currentFileId && (tabName === 'correlation' || tabName === 'prediction')) {
        if (tabName === 'correlation') {
            loadNumericColumnsForCorrelation(currentFileId);
        } else if (tabName === 'prediction') {
            loadNumericColumnsForPrediction(currentFileId);
        }
    }

    // Scroll to step 3 configuration section
    const scrollTarget = document.getElementById(`tab-${tabName}-config`);
    if (scrollTarget) {
        setTimeout(() => {
            scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 200);
}

}

// ============================================================================
// CORRELATION - Load Numeric Columns
// ============================================================================

async function loadNumericColumnsForCorrelation(fileId) {
    try {
        const response = await fetch(`${API_URL}/get-numeric-columns/${fileId}`);
        if (response.ok) {
            const data = await response.json();
            populateCorrelationColumns(data.numeric_columns);
            document.getElementById('correlationBtn').disabled = false;
        }
    } catch (error) {
        console.error('Error loading numeric columns:', error);
    }
}

function populateCorrelationColumns(columns) {
    // Populate target column dropdown
    const targetSelect = document.getElementById('targetColumn');
    targetSelect.innerHTML = '<option value="">-- Select target column --</option>';
    
    columns.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = col;
        targetSelect.appendChild(option);
    });

    // Populate source columns checkboxes
    const container = document.getElementById('sourceColumnsContainer');
    container.innerHTML = '';
    
    columns.forEach(col => {
        const label = document.createElement('label');
        label.style.display = 'flex';
        label.style.alignItems = 'center';
        label.style.gap = '0.5rem';
        label.style.cursor = 'pointer';
        label.style.padding = '0.5rem';
        label.style.borderRadius = '4px';
        label.style.transition = 'background 0.2s';
        
        label.onmouseover = () => label.style.background = 'rgba(37, 99, 235, 0.1)';
        label.onmouseout = () => label.style.background = 'transparent';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = col;
        checkbox.className = 'source-column-checkbox';
        checkbox.style.cursor = 'pointer';
        checkbox.style.width = '1.2rem';
        checkbox.style.height = '1.2rem';
        checkbox.style.accentColor = 'var(--primary-color)';
        
        const span = document.createElement('span');
        span.textContent = col;
        span.style.flex = '1';
        
        label.appendChild(checkbox);
        label.appendChild(span);
        container.appendChild(label);
    });
}

// ============================================================================
// PREDICTION - Load Numeric Columns
// ============================================================================

async function loadNumericColumnsForPrediction(fileId) {
    try {
        const response = await fetch(`${API_URL}/get-numeric-columns/${fileId}`);
        if (response.ok) {
            const data = await response.json();
            populatePredictionColumns(data.numeric_columns);
            document.getElementById('predictionBtn').disabled = false;
        }
    } catch (error) {
        console.error('Error loading numeric columns:', error);
    }
}

function populatePredictionColumns(columns) {
    // Populate target column dropdown
    const targetSelect = document.getElementById('predictionTarget');
    targetSelect.innerHTML = '<option value="">-- Select target column --</option>';
    
    columns.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = col;
        targetSelect.appendChild(option);
    });

    // Populate feature columns checkboxes
    const container = document.getElementById('predictionFeaturesContainer');
    container.innerHTML = '';
    
    columns.forEach(col => {
        const label = document.createElement('label');
        label.style.display = 'flex';
        label.style.alignItems = 'center';
        label.style.gap = '0.5rem';
        label.style.cursor = 'pointer';
        label.style.padding = '0.5rem';
        label.style.borderRadius = '4px';
        label.style.transition = 'background 0.2s';
        
        label.onmouseover = () => label.style.background = 'rgba(37, 99, 235, 0.1)';
        label.onmouseout = () => label.style.background = 'transparent';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = col;
        checkbox.className = 'prediction-feature-checkbox';
        checkbox.style.cursor = 'pointer';
        checkbox.style.width = '1.2rem';
        checkbox.style.height = '1.2rem';
        checkbox.style.accentColor = 'var(--primary-color)';
        
        const span = document.createElement('span');
        span.textContent = col;
        span.style.flex = '1';
        
        label.appendChild(checkbox);
        label.appendChild(span);
        container.appendChild(label);
    });
}

// ============================================================================
// PLACEHOLDER - Prediction Function
// ============================================================================

async function runPrediction() {
    alert('🔮 Time-Series Prediction coming in Phase 6C!\n\nThis will forecast future values based on historical trends.');
}

// ============================================================================
// PLACEHOLDER - Task Type Selection
// ============================================================================

function selectTaskType() {
    const taskType = document.getElementById('predefinedTasks').value;
    const customDiv = document.getElementById('customTaskDiv');
    
    if (taskType === 'custom') {
        customDiv.style.display = 'block';
        document.getElementById('customTaskInput').focus();
    } else {
        customDiv.style.display = 'none';
    }
    
    document.getElementById('analyzeBtn').disabled = !taskType;
}
