import socket
import network
import machine
import uos
import gc
import config
from time import sleep, ticks_ms, ticks_diff, sleep_ms
from camera import Camera
from machine import Pin, SPI, RTC
from webtemplate import HTML_PAGE

# WiFi settings
WIFI_SSID = config.WIFI_SSID 
WIFI_PASSWORD = config.WIFI_PASSWORD

CHUNK_SIZE = 1024
MAX_REQUEST_SIZE = 512
MAX_SAVED_IMAGES = config.MAX_SAVED_IMAGES

class CameraManager:
    def __init__(self):
        self.cam = None
        self.auto_focus_enabled = False
        self.saved_images = []
        self.rtc = RTC()
        self.spi = None
        self.cs = None
        self.initialize_camera()
        
    def get_timestamp(self):
        """Get current timestamp for filename"""
        datetime = self.rtc.datetime()
        return f"{datetime[0]}{datetime[1]:02d}{datetime[2]:02d}_{datetime[4]:02d}{datetime[5]:02d}{datetime[6]:02d}"

    def initialize_camera(self):
        try:
            print("Initializing camera...")
            # Clean up old instances if they exist
            if self.cam:
                del self.cam
            if self.spi:
                self.spi.deinit()
            if self.cs:
                self.cs.value(1)
                
            # Create new instances
            self.spi = SPI(1, sck=Pin(10), mosi=Pin(15), miso=Pin(12), baudrate=8000000)
            self.cs = Pin(13, Pin.OUT)
            self.cs.high()
            
            # Initialize camera
            self.cam = Camera(self.spi, self.cs, skip_sleep=False)
            sleep(2)  # Give camera time to stabilize
            self.cam.resolution = '640x480'
            print("Camera initialized successfully")
            return True
        except Exception as e:
            print(f'Camera init failed: {e}')
            self.cleanup()
            return False

    def cleanup(self):
        """Clean up camera resources"""
        try:
            if self.cam:
                del self.cam
                self.cam = None
            if self.spi:
                self.spi.deinit()
                self.spi = None
            if self.cs:
                self.cs.value(1)
            gc.collect()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def reset_camera(self):
        """Reset camera completely"""
        print("Resetting camera...")
        self.cleanup()
        sleep(2)  # Give more time for reset
        return self.initialize_camera()

    def verify_camera(self):
        """Verify camera is working and reset if needed"""
        try:
            if not self.cam:
                return self.initialize_camera()
            # Try a test capture to verify camera is working
            self.cam.capture_jpg()
            return True
        except:
            print("Camera verification failed, resetting...")
            return self.reset_camera()

    def capture_image(self, save=False):
        if not self.verify_camera():
            raise Exception('Camera not initialized')

        try:
            print('-'*40)
            print('Capturing image...')
            
            retry_count = 0
            while retry_count < 3:
                try:
                    print(f"Capture attempt {retry_count + 1}")
                    self.cam.capture_jpg()
                    print("Image captured, saving to temporary file...")
                    self.cam.saveJPG('temp.jpg')
                    break
                except Exception as e:
                    print(f"Capture attempt failed: {e}")
                    retry_count += 1
                    if retry_count < 3:
                        print("Resetting camera and retrying...")
                        self.reset_camera()
                        sleep(2)
                    else:
                        raise Exception("Failed to capture after 3 attempts")

            # Verify the file exists and has size
            size = uos.stat('temp.jpg')[6]
            print(f'Temporary image saved: {size} bytes')
            
            # If save is requested, copy to a new file with timestamp
            if save:
                timestamp = self.get_timestamp()
                filename = f"img_{timestamp}.jpg"
                print(f"Creating permanent save file: {filename}")
                
                # Copy temp.jpg to new file with progress
                total_bytes = 0
                with open('temp.jpg', 'rb') as src, open(filename, 'wb') as dst:
                    while True:
                        chunk = src.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        dst.write(chunk)
                        total_bytes += len(chunk)
                        progress = (total_bytes / size) * 100
                        print(f"Save progress: {progress:.1f}% ({total_bytes}/{size} bytes)")
                
                print(f"File save completed: {filename}")
                
                # Update saved images list
                self.get_saved_images()  # This will refresh the list
                
                # Keep only last MAX_SAVED_IMAGES images
                while len(self.saved_images) > MAX_SAVED_IMAGES:
                    old_file = self.saved_images.pop(0)
                    try:
                        print(f'Removing old image: {old_file}')
                        uos.remove(old_file)
                        print(f'Successfully removed: {old_file}')
                    except:
                        print(f'Failed to remove: {old_file}')
                
                print(f'Save operation completed: {filename}')
            
            return True
        except Exception as e:
            print(f'Capture error: {e}')
            self.reset_camera()  # Try to recover camera
            return False

    def get_saved_images(self):
        """Return list of saved images with their sizes"""
        try:
            images = []
            # Scan root directory for jpg files
            for filename in uos.listdir('/'):
                if filename.lower().endswith('.jpg') and filename != 'temp.jpg':
                    try:
                        size = uos.stat(filename)[6]
                        images.append({'name': filename, 'size': size})
                    except:
                        continue
            # Update our internal list
            self.saved_images = [img['name'] for img in images]
            return images
        except Exception as e:
            print(f'Error getting saved images: {e}')
            return []
            
    def set_resolution(self, resolution):
        try:
            print(f"Setting resolution to {resolution}")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            self.cam.resolution = resolution
            sleep(2)  # Give camera time to adjust
            
            # Force a reset after resolution change
            self.reset_camera()
            return True
        except Exception as e:
            print(f'Resolution error: {e}')
            self.reset_camera()
            return False

    def set_white_balance(self, mode):
        try:
            print(f"Setting white balance to {mode}")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            self.cam.set_white_balance(mode)
            sleep(2)  # Give camera more time to adjust
            
            # Force a reset after white balance change
            self.reset_camera()
            return True
        except Exception as e:
            print(f'White balance error: {e}')
            self.reset_camera()
            return False
            
    def set_brightness(self, level):
        try:
            print(f"Setting brightness to {level}")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            self.cam.set_brightness_level(int(level))
            sleep(1)  # Give camera time to adjust
            
            # Force a reset after brightness change
            self.reset_camera()
            return True
        except Exception as e:
            print(f'Brightness error: {e}')
            self.reset_camera()
            return False
            
    def set_contrast(self, level):
        try:
            print(f"Setting contrast to {level}")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            self.cam.set_contrast(int(level))
            sleep(1)  # Give camera time to adjust
            
            # Force a reset after contrast change
            self.reset_camera()
            return True
        except Exception as e:
            print(f'Contrast error: {e}')
            self.reset_camera()
            return False
            
    def set_saturation(self, level):
        try:
            print(f"Setting saturation to {level}")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            self.cam.set_saturation_control(int(level))
            sleep(1)  # Give camera time to adjust
            
            # Force a reset after saturation change
            self.reset_camera()
            return True
        except Exception as e:
            print(f'Saturation error: {e}')
            self.reset_camera()
            return False
            
    def set_auto_focus(self, enabled):
        try:
            print(f"Setting auto focus to {enabled}")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            if enabled.lower() == 'true':
                self.auto_focus_enabled = self.cam.auto_focus(True)
            else:
                self.auto_focus_enabled = not self.cam.auto_focus(False)
            sleep(1)  # Give camera time to adjust
            
            # Force a reset after focus change
            self.reset_camera()
            return True
        except Exception as e:
            print(f'Auto focus error: {e}')
            self.reset_camera()
            return False
            
    def trigger_single_focus(self):
        try:
            print("Triggering single focus")
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            result = self.cam.single_focus()
            sleep(1)  # Give camera time to adjust
            
            # Force a reset after focus operation
            self.reset_camera()
            return result
        except Exception as e:
            print(f'Single focus error: {e}')
            self.reset_camera()
            return False

    def set_fixed_focus(self, focus_value):
        try:
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            focus_value = int(focus_value, 16)
            print(f"Setting fixed focus to 0x{focus_value:04X}")
            self.cam._write_reg(0x30, (focus_value >> 8) & 0xFF)
            self.cam._write_reg(0x31, focus_value & 0xFF)
            sleep(0.5)  # Give time for the focus position to change

            # Verify focus register values
            focus_high = self.cam._read_reg(0x30)
            focus_low = self.cam._read_reg(0x31)
            actual_focus = (int.from_bytes(focus_high, 'big') << 8) | int.from_bytes(focus_low, 'big')
            print(f"Focus register values set to 0x{actual_focus:04X}")
            
            return True
        except Exception as e:
            print(f'Fixed focus error: {e}')
            return False

    def set_gain(self, gain_value):
        try:
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            gain_value = int(gain_value, 16)
            print(f"Setting gain to 0x{gain_value:02X}")
            self.cam._write_reg(0x45, gain_value)  # Assuming 0x45 is the gain register
            sleep(0.5)  # Give time for the gain to adjust
            
            # Verify gain register value
            actual_gain = int.from_bytes(self.cam._read_reg(0x45), 'big')
            print(f"Gain register value set to 0x{actual_gain:02X}")
            
            return True
        except Exception as e:
            print(f'Gain error: {e}')
            return False

    def set_exposure(self, exposure_value):
        try:
            if not self.verify_camera():
                raise Exception("Camera not ready")
                
            exposure_value = int(exposure_value, 16)
            print(f"Setting exposure to 0x{exposure_value:02X}")
            self.cam._write_reg(0x55, exposure_value)  # Assuming 0x55 is the exposure register
            sleep(0.5)  # Give time for the exposure to adjust
            
            # Verify exposure register value
            actual_exposure = int.from_bytes(self.cam._read_reg(0x55), 'big')
            print(f"Exposure register value set to 0x{actual_exposure:02X}")
            
            return True
        except Exception as e:
            print(f'Exposure error: {e}')
            return False

    def save_settings(self, preset_name):
        try:
            settings = {
                'resolution': self.cam.resolution,
                'white_balance': self.cam._read_reg(0x42),  # White balance register
                'brightness': self.cam._read_reg(0x43),     # Brightness register
                'contrast': self.cam._read_reg(0x44),       # Contrast register
                'gain': self.cam._read_reg(0x45),          # Gain register
                'exposure': self.cam._read_reg(0x55)        # Exposure register
            }
            
            # Create presets directory if it doesn't exist
            try:
                uos.mkdir('presets')
            except:
                pass
                
            # Save settings to file
            filename = f'presets/{preset_name}.txt'
            with open(filename, 'w') as f:
                for key, value in settings.items():
                    if isinstance(value, bytes):
                        value = int.from_bytes(value, 'big')
                    f.write(f'{key}={value}\n')
            return True
        except Exception as e:
            print(f'Save settings error: {e}')
            return False
            
    def load_settings(self, preset_name):
        try:
            filename = f'presets/{preset_name}.txt'
            settings = {}
            
            # Read settings from file
            with open(filename, 'r') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    settings[key] = value
                    
            # Apply settings
            if 'resolution' in settings:
                self.set_resolution(settings['resolution'])
            if 'brightness' in settings:
                self.set_brightness(settings['brightness'])
            if 'contrast' in settings:
                self.set_contrast(settings['contrast'])
            if 'gain' in settings:
                self.set_gain(settings['gain'])
            if 'exposure' in settings:
                self.set_exposure(settings['exposure'])
                
            return True
        except Exception as e:
            print(f'Load settings error: {e}')
            return False
            
    def get_saved_presets(self):
        try:
            presets = []
            try:
                files = uos.listdir('presets')
            except:
                return []
                
            for file in files:
                if file.endswith('.txt'):
                    presets.append(file[:-4])  # Remove .txt extension
            return presets
        except Exception as e:
            print(f'Get presets error: {e}')
            return []
            
    def get_storage_info(self):
        try:
            # Get filesystem information
            fs_info = uos.statvfs('/')
            block_size = fs_info[0]
            total_blocks = fs_info[2]
            free_blocks = fs_info[3]
            
            # Calculate sizes in bytes
            total_space = block_size * total_blocks
            free_space = block_size * free_blocks
            used_space = total_space - free_space
            
            # Convert to KB since Pico storage is small
            def human_size(size):
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size/1024:.1f} KB"
                else:
                    return f"{size/(1024*1024):.1f} MB"  # Max size will be in MB for Pico
            
            # Get actual count of jpg files (excluding temp.jpg)
            image_count = 0
            try:
                for filename in uos.listdir('/'):
                    if filename.lower().endswith('.jpg') and filename != 'temp.jpg':
                        image_count += 1
            except:
                pass
                
            return {
                'total': human_size(total_space),
                'used': human_size(used_space),
                'free': human_size(free_space),
                'images': image_count
            }
        except Exception as e:
            print(f'Storage info error: {e}')
            return {
                'total': 'Unknown',
                'used': 'Unknown',
                'free': 'Unknown',
                'images': 0
            }

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

        elif path == '/fixedfocus':
            if camera_manager.set_fixed_focus(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')

        elif path == '/gain':
            if camera_manager.set_gain(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')

        elif path == '/exposure':
            if camera_manager.set_exposure(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/save_preset':
            if camera_manager.save_settings(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/load_preset':
            if camera_manager.load_settings(param):
                client.send('HTTP/1.1 200 OK\r\n\r\n')
            else:
                client.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
                
        elif path == '/list_presets':
            presets = camera_manager.get_saved_presets()
            send_json(client, presets)
            
        elif path == '/storage_info':
            info = camera_manager.get_storage_info()
            if info:
                send_json(client, info)
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
    camera_manager = CameraManager()
    start_server()

