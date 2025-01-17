"""Web template for camera server - Version 0.9"""

HTML_PAGE = """<!DOCTYPE html><html>
<head>
    <title>Camera Capture v0.9</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2196F3;
            --secondary-color: #1976D2;
            --success-color: #4CAF50;
            --error-color: #f44336;
            --warning-color: #ff9800;
            --background-color: #f5f5f5;
            --card-background: #ffffff;
            --text-color: #333333;
            --border-radius: 8px;
            --shadow: 0 2px 4px rgba(0,0,0,0.1);
            --transition: all 0.3s ease;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            background: var(--background-color);
            color: var(--text-color);
            padding: 20px;
        }

        .main-container {
            max-width: 1000px;
            margin: 0 auto;
            background: var(--card-background);
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }

        .header h1 {
            color: var(--primary-color);
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 500;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .controls {
            background: #f8f9fa;
            padding: 25px;
            margin: 20px 0;
            border-radius: var(--border-radius);
            border: 1px solid #e9ecef;
        }

        .control-group {
            background: white;
            padding: 15px;
            margin: 15px 0;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .control-group:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .focus-controls {
            background: #e3f2fd;
            padding: 20px;
            margin: 15px 0;
            border-radius: var(--border-radius);
            border: 1px solid #bbdefb;
        }

        label {
            display: inline-block;
            width: 120px;
            font-weight: 500;
            color: #555;
        }

        select {
            padding: 10px;
            margin: 5px;
            width: 200px;
            border-radius: var(--border-radius);
            border: 1px solid #ddd;
            background: white;
            font-size: 14px;
            transition: var(--transition);
        }

        select:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
        }

        button {
            background: var(--primary-color);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: var(--transition);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        button:hover {
            background: var(--secondary-color);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        button.focus-button {
            background: var(--warning-color);
        }

        button.focus-button:hover {
            background: #f57c00;
        }

        #status {
            padding: 15px;
            margin: 15px 0;
            background: #e8f5e9;
            border-radius: var(--border-radius);
            text-align: center;
            font-weight: 500;
            transition: var(--transition);
        }

        #status.error {
            background: #ffebee;
            color: var(--error-color);
        }

        #status.success {
            background: #e8f5e9;
            color: var(--success-color);
        }

        #status.warning {
            background: #fff3e0;
            color: var(--warning-color);
        }

        img {
            max-width: 100%;
            border: 1px solid #dee2e6;
            border-radius: var(--border-radius);
            margin-top: 20px;
            box-shadow: var(--shadow);
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
            margin-left: 10px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: var(--transition);
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: var(--transition);
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--primary-color);
        }

        input:checked + .slider:before {
            transform: translateX(26px);
        }

        .saved-images {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .saved-images h3 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-weight: 500;
        }

        .saved-image {
            margin: 10px 0;
            padding: 15px;
            background: white;
            border-radius: var(--border-radius);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: var(--transition);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .saved-image:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }

        .saved-image span {
            font-size: 14px;
            color: #666;
        }

        .saved-image button {
            padding: 8px 16px;
            font-size: 14px;
            margin: 0;
        }

        .button-group {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
        }

        .button-group button {
            flex: 1;
            max-width: 200px;
        }

        .debug-log {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: var(--border-radius);
            border: 1px solid #e9ecef;
        }

        .debug-log h3 {
            color: var(--primary-color);
            margin-bottom: 10px;
        }

        #debug-messages {
            font-family: monospace;
            background: #2b2b2b;
            color: #f8f8f8;
            padding: 15px;
            border-radius: var(--border-radius);
            max-height: 200px;
            overflow-y: auto;
        }

        .debug-message {
            margin: 5px 0;
            padding: 5px;
            border-bottom: 1px solid #3d3d3d;
        }

        .debug-message:last-child {
            border-bottom: none;
        }

        .settings-panel {
            background: #fff;
            padding: 20px;
            margin: 20px 0;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .settings-panel h3 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-weight: 500;
        }

        .preset-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .preset-buttons button {
            flex: 1;
            min-width: 120px;
        }

        .storage-info {
            background: #fff;
            padding: 20px;
            margin: 20px 0;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .storage-info h3 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-weight: 500;
        }

        .storage-info p {
            margin: 10px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: var(--border-radius);
        }

        #preset-name {
            padding: 10px;
            margin: 5px;
            border-radius: var(--border-radius);
            border: 1px solid #ddd;
            width: 200px;
        }

        @media (max-width: 768px) {
            .main-container {
                padding: 15px;
            }

            .controls {
                padding: 15px;
            }

            select {
                width: 100%;
                margin: 5px 0;
            }

            .button-group {
                flex-direction: column;
                align-items: stretch;
            }

            .button-group button {
                max-width: none;
            }

            .preset-buttons {
                flex-direction: column;
            }

            .preset-buttons button {
                width: 100%;
            }

            #preset-name {
                width: 100%;
            }
        }
    </style>
    <script>
        let busy = false;
        let retryTimeout = null;

        function clearRetryTimeout() {
            if (retryTimeout) {
                clearTimeout(retryTimeout);
                retryTimeout = null;
            }
        }

        function updateStatus(message, type = 'info') {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = type;
            addDebugMessage(`${type.toUpperCase()}: ${message}`);
        }

        function updateStorageInfo() {
            fetch('/storage_info')
                .then(response => response.json())
                .then(data => {
                    const storageDetails = document.getElementById('storage-details');
                    storageDetails.innerHTML = `
                        <p>Total Space: ${data.total}</p>
                        <p>Used Space: ${data.used}</p>
                        <p>Free Space: ${data.free}</p>
                        <p>Saved Images: ${data.images}</p>
                    `;
                    addDebugMessage('Storage info updated successfully');
                })
                .catch(error => {
                    document.getElementById('storage-details').innerHTML = 'Error loading storage information';
                    addDebugMessage('Error updating storage info: ' + error.message);
                });
        }

        function enableButtons(enable = true) {
            document.querySelectorAll('button').forEach(button => {
                button.disabled = !enable;
            });
        }

        function capture(forceRetry = false) {
            if(busy && !forceRetry) return;
            clearRetryTimeout();
            
            busy = true;
            enableButtons(false);
            updateStatus('Capturing...', 'warning');
            
            const img = document.getElementById('photo');
            
            fetch('/capture?' + Date.now(), {
                cache: 'no-store'
            })
            .then(response => {
                if(!response.ok) throw new Error('Capture failed');
                return response.blob();
            })
            .then(blob => {
                const url = URL.createObjectURL(blob);
                img.onload = () => {
                    URL.revokeObjectURL(img.src);
                    updateStatus('Capture successful', 'success');
                    busy = false;
                    enableButtons(true);
                };
                img.onerror = () => {
                    updateStatus('Image load failed, retrying...', 'error');
                    retryTimeout = setTimeout(() => capture(true), 2000);
                };
                img.src = url;
            })
            .catch(error => {
                updateStatus('Error: ' + error.message, 'error');
                busy = false;
                enableButtons(true);
            });
        }

        function setControl(control, value) {
            if(busy) return;
            clearRetryTimeout();
            
            busy = true;
            enableButtons(false);
            updateStatus('Setting ' + control + ' to ' + value + '...', 'warning');
            
            fetch('/' + control + '?' + value)
                .then(response => {
                    if(!response.ok) throw new Error('Failed to set ' + control);
                    updateStatus(control + ' set to ' + value + ', waiting for camera...', 'warning');
                    return new Promise(resolve => setTimeout(resolve, 3000));
                })
                .then(() => {
                    updateStatus('Taking test capture...', 'warning');
                    return capture(true);
                })
                .catch(error => {
                    updateStatus('Error: ' + error.message, 'error');
                    busy = false;
                    enableButtons(true);
                });
        }

        function toggleAutoFocus() {
            const enabled = document.getElementById('autofocus').checked;
            setControl('autofocus', enabled);
        }

        function singleFocus() {
            if(busy) return;
            clearRetryTimeout();
            
            busy = true;
            enableButtons(false);
            updateStatus('Focusing...', 'warning');
            
            fetch('/singlefocus')
                .then(response => {
                    if(!response.ok) throw new Error('Focus failed');
                    updateStatus('Focus successful, taking test capture...', 'success');
                    setTimeout(() => capture(true), 2000);
                })
                .catch(error => {
                    updateStatus('Error: ' + error.message, 'error');
                    busy = false;
                    enableButtons(true);
                });
        }

        function captureAndSave() {
            if(busy) return;
            clearRetryTimeout();
            
            busy = true;
            enableButtons(false);
            updateStatus('Capturing and saving...', 'warning');
            
            fetch('/capture?save=true', {
                cache: 'no-store'
            })
            .then(response => {
                if(!response.ok) throw new Error('Capture failed');
                return response.blob();
            })
            .then(blob => {
                updateSavedImages();
                updatePresetList();
                updateStorageInfo();
                const url = URL.createObjectURL(blob);
                const img = document.getElementById('photo');
                img.onload = () => {
                    URL.revokeObjectURL(img.src);
                    updateStatus('Image captured and saved', 'success');
                    busy = false;
                    enableButtons(true);
                };
                img.onerror = () => {
                    updateStatus('Image load failed, retrying...', 'error');
                    retryTimeout = setTimeout(() => captureAndSave(), 2000);
                };
                img.src = url;
            })
            .catch(error => {
                updateStatus('Error: ' + error.message, 'error');
                busy = false;
                enableButtons(true);
            });
        }

        function updateSavedImages() {
            if (busy) return;
            
            fetch('/saved_images')
                .then(response => response.json())
                .then(images => {
                    const container = document.getElementById('saved-images');
                    container.innerHTML = '<h3>Saved Images:</h3>';
                    images.forEach(img => {
                        const div = document.createElement('div');
                        div.className = 'saved-image';
                        div.innerHTML = `
                            <span>${img.name} (${formatSize(img.size)})</span>
                            <button onclick="viewImage('${img.name}')">View</button>
                        `;
                        container.appendChild(div);
                    });
                })
                .catch(error => {
                    console.error('Error updating saved images:', error);
                    addDebugMessage('Error updating saved images: ' + error.message);
                });
        }

        function viewImage(filename) {
            if(busy) return;
            clearRetryTimeout();
            
            busy = true;
            enableButtons(false);
            const img = document.getElementById('photo');
            updateStatus('Loading saved image...', 'warning');
            
            img.onload = () => {
                updateStatus('Viewing: ' + filename, 'success');
                busy = false;
                enableButtons(true);
            };
            img.onerror = () => {
                updateStatus('Failed to load image: ' + filename, 'error');
                busy = false;
                enableButtons(true);
            };
            img.src = '/view?' + filename;
        }

        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / 1048576).toFixed(1) + ' MB';
        }

        function addDebugMessage(message) {
            const debugMessages = document.getElementById('debug-messages');
            const messageElement = document.createElement('div');
            messageElement.className = 'debug-message';
            messageElement.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
            debugMessages.insertBefore(messageElement, debugMessages.firstChild);
            
            while (debugMessages.children.length > 50) {
                debugMessages.removeChild(debugMessages.lastChild);
            }
        }

        function savePreset() {
            const name = document.getElementById('preset-name').value.trim();
            if (!name) {
                updateStatus('Please enter a preset name', 'error');
                return;
            }
            
            fetch('/save_preset?' + encodeURIComponent(name))
                .then(response => {
                    if (!response.ok) throw new Error('Failed to save preset');
                    updateStatus('Preset saved: ' + name, 'success');
                    updatePresetList();
                })
                .catch(error => updateStatus('Error: ' + error.message, 'error'));
        }
        
        function loadPreset(name) {
            if (!name) return;
            
            updateStatus('Loading preset: ' + name, 'warning');
            fetch('/load_preset?' + encodeURIComponent(name))
                .then(response => {
                    if (!response.ok) throw new Error('Failed to load preset');
                    updateStatus('Preset loaded: ' + name, 'success');
                    setTimeout(() => capture(true), 1000);
                })
                .catch(error => updateStatus('Error: ' + error.message, 'error'));
        }
        
        function updatePresetList() {
            fetch('/list_presets')
                .then(response => response.json())
                .then(presets => {
                    const select = document.getElementById('preset-select');
                    select.innerHTML = '<option value="">Select a preset...</option>';
                    presets.forEach(preset => {
                        const option = document.createElement('option');
                        option.value = preset;
                        option.textContent = preset;
                        select.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error updating presets:', error);
                    addDebugMessage('Error updating presets: ' + error.message);
                });
        }
        
        function applyPreset(type) {
            const presets = {
                indoor: {
                    wb: 'office',
                    brightness: '0',
                    contrast: '0',
                    exposure: '0x30'
                },
                outdoor: {
                    wb: 'sunny',
                    brightness: '2',
                    contrast: '1',
                    exposure: '0x20'
                },
                lowlight: {
                    wb: 'home',
                    brightness: '1',
                    contrast: '2',
                    exposure: '0x50',
                    gain: '0x40'
                },
                bright: {
                    wb: 'sunny',
                    brightness: '2',
                    contrast: '3',
                    exposure: '0x20',
                    gain: '0x10'
                }
            };
            
            const preset = presets[type];
            if (!preset) return;
            
            updateStatus('Applying ' + type + ' preset...', 'warning');
            
            Promise.all([
                fetch('/whitebalance?' + preset.wb),
                fetch('/brightness?' + preset.brightness),
                fetch('/contrast?' + preset.contrast),
                fetch('/exposure?' + preset.exposure),
                preset.gain ? fetch('/gain?' + preset.gain) : Promise.resolve()
            ])
            .then(() => {
                updateStatus(type + ' preset applied', 'success');
                setTimeout(() => capture(true), 1000);
            })
            .catch(error => updateStatus('Error applying preset: ' + error.message, 'error'));
        }

        document.addEventListener('DOMContentLoaded', function() {
            updateSavedImages();
            updatePresetList();
            updateStorageInfo();
            capture();

            setInterval(() => {
                if (!busy) {
                    updateSavedImages();
                    updatePresetList();
                    updateStorageInfo();
                }
            }, 5000);
        });
    </script>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>Camera Capture v0.9</h1>
            <p>Advanced Camera Control Interface</p>
        </div>

        <div class="controls">
            <div class="focus-controls">
                <div class="control-group">
                    <label>Auto Focus:</label>
                    <label class="switch">
                        <input type="checkbox" id="autofocus" onchange="toggleAutoFocus()">
                        <span class="slider"></span>
                    </label>
                    <button class="focus-button" onclick="singleFocus()">Single Focus</button>
                </div>
                <div class="control-group">
                    <label>Fixed Focus:</label>
                    <select id="focus-length" onchange="setControl('fixedfocus', this.value)">
                        <option value="0x0010">Macro (~5cm)</option>
                        <option value="0x0020">Super Close-up (~10cm)</option>
                        <option value="0x0030">Close-up (~20cm)</option>
                        <option value="0x0040">Desktop Distance (~50cm)</option>
                        <option value="0x0050">Room Distance (~1m)</option>
                        <option value="0x0060">Far Distance (~3m)</option>
                        <option value="0x0070">Very Far (~5m)</option>
                        <option value="0x0080">Infinity (∞)</option>
                    </select>
                </div>
            </div>

            <div class="control-group">
                <label>Resolution:</label>
                <select onchange="setControl('resolution', this.value)">
                    <option value="640x480">640x480</option>
                    <option value="1280x720">720p</option>
                    <option value="1920x1080">1080p</option>
                    <option value="2048x1536">2048x1536</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>White Balance:</label>
                <select onchange="setControl('whitebalance', this.value)">
                    <option value="auto">Auto</option>
                    <option value="sunny">Sunny</option>
                    <option value="cloudy">Cloudy</option>
                    <option value="office">Office</option>
                    <option value="home">Home</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Brightness:</label>
                <select onchange="setControl('brightness', this.value)">
                    <option value="0">Default</option>
                    <option value="1">+1</option>
                    <option value="3">+2</option>
                    <option value="5">+3</option>
                    <option value="7">+4</option>
                    <option value="2">-1</option>
                    <option value="4">-2</option>
                    <option value="6">-3</option>
                    <option value="8">-4</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Contrast:</label>
                <select onchange="setControl('contrast', this.value)">
                    <option value="0">Default</option>
                    <option value="1">+1</option>
                    <option value="3">+2</option>
                    <option value="5">+3</option>
                    <option value="2">-1</option>
                    <option value="4">-2</option>
                    <option value="6">-3</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Saturation:</label>
                <select onchange="setControl('saturation', this.value)">
                    <option value="0">Default</option>
                    <option value="1">+1</option>
                    <option value="3">+2</option>
                    <option value="5">+3</option>
                    <option value="2">-1</option>
                    <option value="4">-2</option>
                    <option value="6">-3</option>
                </select>
            </div>

            <div class="control-group">
                <label>Exposure:</label>
                <select onchange="setControl('exposure', this.value)">
                    <option value="0x10">Very Low</option>
                    <option value="0x20">Low</option>
                    <option value="0x30">Medium Low</option>
                    <option value="0x40">Medium</option>
                    <option value="0x50">Medium High</option>
                    <option value="0x60">High</option>
                    <option value="0x70">Very High</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Gain:</label>
                <select onchange="setControl('gain', this.value)">
                    <option value="0x10">Low</option>
                    <option value="0x20">Medium Low</option>
                    <option value="0x30">Medium</option>
                    <option value="0x40">Medium High</option>
                    <option value="0x50">High</option>
                </select>
            </div>
        </div>

        <div class="button-group">
            <button onclick="capture()">Capture</button>
            <button onclick="captureAndSave()">Capture & Save</button>
        </div>
        
        <div id="status">Ready</div>
        
        <div class="storage-info">
            <h3>Storage Information</h3>
            <div id="storage-details">
                Loading storage information...
            </div>
        </div>

        <div class="settings-panel">
            <h3>Quick Settings</h3>
            <div class="control-group">
                <label>Save Current Settings:</label>
                <input type="text" id="preset-name" placeholder="Preset name">
                <button onclick="savePreset()">Save</button>
            </div>
            <div class="control-group">
                <label>Load Preset:</label>
                <select id="preset-select" onchange="loadPreset(this.value)">
                    <option value="">Select a preset...</option>
                </select>
            </div>
        </div>
        
        <div class="settings-panel">
            <h3>Image Presets</h3>
            <div class="preset-buttons">
                <button onclick="applyPreset('indoor')">Indoor</button>
                <button onclick="applyPreset('outdoor')">Outdoor</button>
                <button onclick="applyPreset('lowlight')">Low Light</button>
                <button onclick="applyPreset('bright')">Bright Day</button>
            </div>
        </div>

        <div class="debug-log">
            <h3>Debug Log</h3>
            <div id="debug-messages"></div>
        </div>

        <div id="saved-images" class="saved-images">
            <h3>Saved Images:</h3>
        </div>

        <img id="photo" alt="Camera Output">
    </div>
</body>
</html>
"""
