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
                
                # Add to saved images list
                self.saved_images.append(filename)
                
                # Keep only last 3 images
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
    start_server()

