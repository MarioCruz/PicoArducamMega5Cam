import socket
import network
import machine
import uos
import gc
from time import sleep, ticks_ms, ticks_diff, sleep_ms
from camera import Camera
from machine import Pin, SPI, RTC

from config import WIFI_SSID, WIFI_PASSWORD, MAX_SAVED_IMAGES, ENABLE_WATCHDOG, WATCHDOG_TIMEOUT

CHUNK_SIZE = 1024
MAX_REQUEST_SIZE = 512
MAX_SAVED_IMAGES = 3

class CameraManager:
    def __init__(self):
        self.cam = None
        self.auto_focus_enabled = False
        self.saved_images = []
        self.rtc = RTC()
        self.initialize_camera()
        
    def get_timestamp(self):
        """Get current timestamp for filename"""
        datetime = self.rtc.datetime()
        return f"{datetime[0]}{datetime[1]:02d}{datetime[2]:02d}_{datetime[4]:02d}{datetime[5]:02d}{datetime[6]:02d}"

    def initialize_camera(self):
        try:
            camSPI = SPI(1, sck=Pin(10), mosi=Pin(15), miso=Pin(12), baudrate=8000000)
            camCS = Pin(13, Pin.OUT)
            camCS.high()
            self.cam = Camera(camSPI, camCS, skip_sleep=False)
            self.cam.resolution = '640x480'
            return True
        except Exception as e:
            print(f'Camera init failed: {e}')
            return False

    def capture_image(self, save=False):
        if not self.cam:
            if not self.initialize_camera():
                raise Exception('Camera not initialized')

        try:
            print('-'*40)
            print('Capturing image...')
            
            # Capture and save to temp.jpg
            self.cam.capture_jpg()
            self.cam.saveJPG('temp.jpg')
            
            # Verify the file exists and has size
            size = uos.stat('temp.jpg')[6]
            print(f'Image saved to temp.jpg: {size} bytes')
            
            # If save is requested, copy to a new file with timestamp
            if save:
                timestamp = self.get_timestamp()
                filename = f"img_{timestamp}.jpg"
                
                # Copy temp.jpg to new file
                with open('temp.jpg', 'rb') as src, open(filename, 'wb') as dst:
                    while True:
                        chunk = src.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        dst.write(chunk)
                
                # Add to saved images list
                self.saved_images.append(filename)
                
                # Keep only last 3 images
                while len(self.saved_images) > MAX_SAVED_IMAGES:
                    old_file = self.saved_images.pop(0)
                    try:
                        uos.remove(old_file)
                        print(f'Removed old image: {old_file}')
                    except:
                        print(f'Failed to remove: {old_file}')
                
                print(f'Saved as: {filename}')
            
            return True
        except Exception as e:
            print(f'Capture error: {e}')
            return False
    
    def get_saved_images(self):
        """Return list of saved images with their sizes"""
        images = []
        for filename in self.saved_images:
            try:
                size = uos.stat(filename)[6]
                images.append({'name': filename, 'size': size})
            except:
                continue
        return images
            
    def set_resolution(self, resolution):
        try:
            self.cam.resolution = resolution
            return True
        except Exception as e:
            print(f'Resolution error: {e}')
            return False
            
    def set_white_balance(self, mode):
        try:
            self.cam.set_white_balance(mode)
            return True
        except Exception as e:
            print(f'White balance error: {e}')
            return False
            
    def set_brightness(self, level):
        try:
            self.cam.set_brightness_level(int(level))
            return True
        except Exception as e:
            print(f'Brightness error: {e}')
            return False
            
    def set_contrast(self, level):
        try:
            self.cam.set_contrast(int(level))
            return True
        except Exception as e:
            print(f'Contrast error: {e}')
            return False
            
    def set_saturation(self, level):
        try:
            self.cam.set_saturation_control(int(level))
            return True
        except Exception as e:
            print(f'Saturation error: {e}')
            return False
            
    def set_auto_focus(self, enabled):
        try:
            if enabled.lower() == 'true':
                self.auto_focus_enabled = self.cam.auto_focus(True)
            else:
                self.auto_focus_enabled = not self.cam.auto_focus(False)
            return True
        except Exception as e:
            print(f'Auto focus error: {e}')
            return False
            
    def trigger_single_focus(self):
        try:
            return self.cam.single_focus()
        except Exception as e:
            print(f'Single focus error: {e}')
            return False

def connect_wifi():
    print('Connecting to WiFi...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        attempts = 0
        while not wlan.isconnected() and attempts < 10:
            sleep(1)
            attempts += 1
        if not wlan.isconnected():
            raise Exception('WiFi connection failed')
    print(f'Connected: {wlan.ifconfig()[0]}')
    return wlan.ifconfig()[0]

def send_file(client, filename):
    try:
        file_size = uos.stat(filename)[6]
        print(f'Sending {filename}: {file_size} bytes')
        
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: image/jpeg\r\n')
        client.send(f'Content-Length: {file_size}\r\n')
        client.send('Cache-Control: no-cache\r\n')
        client.send('\r\n')
        
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                client.write(chunk)
                gc.collect()
    except Exception as e:
        print(f'Send error: {e}')
        raise

def send_json(client, data):
    import json
    json_str = json.dumps(data)
    
    client.send('HTTP/1.1 200 OK\r\n')
    client.send('Content-Type: application/json\r\n')
    client.send(f'Content-Length: {len(json_str)}\r\n')
    client.send('\r\n')
    client.write(json_str)

HTML_PAGE = """<!DOCTYPE html><html>
<head><title>Camera Control</title>
<style>
body {
    font-family: sans-serif;
    margin: 20px;
    padding: 20px;
    background: #f0f0f0;
}
.main-container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.controls {
    background: #e9ecef;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
    border: 1px solid #dee2e6;
}
.control-group {
    margin: 15px 0;
    padding: 10px;
    background: white;
    border-radius: 5px;
}
.focus-controls {
    background: #d1ecf1;
    padding: 15px;
    margin: 15px 0;
    border-radius: 5px;
    border: 1px solid #bee5eb;
}
label {
    display: inline-block;
    width: 120px;
    font-weight: bold;
}
select {
    padding: 8px;
    margin: 5px;
    width: 200px;
    border-radius: 4px;
}
button {
    background: #007bff;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    margin: 10px;
}
button:hover {
    background: #0056b3;
}
button.focus-button {
    background: #17a2b8;
}
button.focus-button:hover {
    background: #138496;
}
#status {
    padding: 10px;
    margin: 10px 0;
    background: #e9ecef;
    border-radius: 5px;
}
img {
    max-width: 100%;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    margin-top: 20px;
}
h1 {
    color: #333;
    text-align: center;
    margin-bottom: 20px;
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
    transition: .4s;
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
    transition: .4s;
    border-radius: 50%;
}
input:checked + .slider {
    background-color: #2196F3;
}
input:checked + .slider:before {
    transform: translateX(26px);
}
.saved-images {
    margin: 20px 0;
    padding: 15px;
    background: #e9ecef;
    border-radius: 5px;
}
.saved-image {
    margin: 10px 0;
    padding: 10px;
    background: white;
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.saved-image button {
    margin: 0 5px;
    padding: 8px 16px;
}
</style>
<script>
let busy = false;

function capture() {
    if(busy) return;
    busy = true;
    const status = document.getElementById('status');
    const img = document.getElementById('photo');
    status.textContent = 'Capturing...';
    
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
            status.textContent = 'Capture successful';
            busy = false;
        };
        img.src = url;
    })
    .catch(error => {
        status.textContent = 'Error: ' + error.message;
        busy = false;
    });
}

function setControl(control, value) {
    if(busy) return;
    busy = true;
    const status = document.getElementById('status');
    status.textContent = 'Setting ' + control + ' to ' + value + '...';
    
    fetch('/' + control + '?' + value)
        .then(response => {
            if(!response.ok) throw new Error('Failed to set ' + control);
            status.textContent = control + ' set to ' + value;
            setTimeout(capture, 500);
        })
        .catch(error => {
            status.textContent = 'Error: ' + error.message;
            busy = false;
        });
}

function toggleAutoFocus() {
    const enabled = document.getElementById('autofocus').checked;
    setControl('autofocus', enabled);
}

function singleFocus() {
    if(busy) return;
    busy = true;
    const status = document.getElementById('status');
    status.textContent = 'Focusing...';
    
    fetch('/singlefocus')
        .then(response => {
            if(!response.ok) throw new Error('Focus failed');
            status.textContent = 'Focus successful';
            setTimeout(capture, 500);
        })
        .catch(error => {
            status.textContent = 'Error: ' + error.message;
            busy = false;
        });
}

function captureAndSave() {
    if(busy) return;
    busy = true;
    const status = document.getElementById('status');
    status.textContent = 'Capturing and saving...';
    
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
            status.textContent = 'Image captured and saved';
            busy = false;
        };
        img.src = url;
    })
    .catch(error => {
        status.textContent = 'Error: ' + error.message;
        busy = false;
    });
}

function updateSavedImages() {
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
    const img = document.getElementById('photo');
    const status = document.getElementById('status');
    status.textContent = 'Loading saved image...';
    
    img.src = '/view?' + filename;
    img.onload = () => {
        status.textContent = 'Viewing: ' + filename;
    };
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

// Update saved images list periodically
setInterval(updateSavedImages, 5000);

// Initial load
document.addEventListener('DOMContentLoaded', function() {
    updateSavedImages();
    capture();
});
</script>
</head>
<body>
<div class="main-container">
    <h1>Camera Control</h1>

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

    <div class="control-group">
        <button onclick="capture()">Capture</button>
        <button onclick="captureAndSave()">Capture & Save</button>
    </div>
    
    <div id="status">Ready</div>
    <div id="saved-images" class="saved-images"></div>
    <img id="photo" alt="Camera Output">
</div>
</body>
</html>"""

camera_manager = CameraManager()

def handle_request(client):
    try:
        request = client.recv(MAX_REQUEST_SIZE).decode()
        request_line = request.split('\r\n')[0]
        method, path = request_line.split(' ')[:2]
        
        print(f'Request: {method} {path}')
        
        if '?' in path:
            path, param = path.split('?')
        else:
            param = ''
        
        if path == '/':
            client.send('HTTP/1.1 200 OK\r\n')
            client.send('Content-Type: text/html\r\n')
            client.send('\r\n')
            client.write(HTML_PAGE)
        
        elif path == '/capture':
            should_save = param == 'save=true'
            if camera_manager.capture_image(save=should_save):
                send_file(client, 'temp.jpg')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
        
        elif path == '/saved_images':
            send_json(client, camera_manager.get_saved_images())
        
        elif path == '/view':
            if param:
                send_file(client, param)
            else:
                client.send('HTTP/1.1 400 Bad Request\r\n\r\n')
        
        elif path == '/resolution':
            if camera_manager.set_resolution(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/whitebalance':
            if camera_manager.set_white_balance(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/brightness':
            if camera_manager.set_brightness(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/contrast':
            if camera_manager.set_contrast(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/saturation':
            if camera_manager.set_saturation(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/autofocus':
            if camera_manager.set_auto_focus(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/singlefocus':
            if camera_manager.trigger_single_focus():
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
        
        else:
            client.send('HTTP/1.1 404 Not Found\r\n\r\n')
            
    except Exception as e:
        print(f'Request error: {e}')
        try:
            client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
        except:
            pass
    finally:
        try:
            client.close()
        except:
            pass
        gc.collect()

def start_server():
    ip = connect_wifi()
    s = socket.socket()
    s.bind(('', 80))
    s.listen(5)
    print(f'Server running at http://{ip}')
    
    while True:
        try:
            client, addr = s.accept()
            handle_request(client)
        except Exception as e:
            print(f'Server error: {e}')
            try:
                client.close()
            except:
                pass

if __name__ == '__main__':
    start_server()
