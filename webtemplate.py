"""
Web template for camera server - Version 0.9
"""

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
                .catch(error => console.error('Error updating saved images:', error));
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

        // Initial load with event handlers
        document.addEventListener('DOMContentLoaded', function() {
            updateSavedImages();
            capture();

            // Update saved images list every 5 seconds if not busy
            setInterval(() => {
                if (!busy) {
                    updateSavedImages();
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
    </div>

    <div class="button-group">
        <button onclick="capture()">Capture</button>
        <button onclick="captureAndSave()">Capture & Save</button>
    </div>
    
    <div id="status">Ready</div>
    <div id="saved-images" class="saved-images"></div>
    <img id="photo" alt="Camera Output">
</div>
</body>
</html>"""
