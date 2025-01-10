import uos
from camera import Camera
from machine import Pin, SPI
import time

def initialize_camera():
    """Initialize and return camera instance"""
    spi = SPI(1, sck=Pin(10), mosi=Pin(15), miso=Pin(12), baudrate=8000000)
    cs = Pin(13, Pin.OUT)
    cs.high()
    return Camera(spi, cs, skip_sleep=False), spi, cs

def ensure_directory(directory):
    """Ensure that the directory exists"""
    try:
        if directory not in uos.listdir():
            uos.mkdir(directory)
            print(f"Directory '{directory}' created")
    except OSError as e:
        print(f"Error creating directory '{directory}': {e}")

def capture_and_save_image(camera, filename):
    """Capture and save an image with the specified filename"""
    try:
        # Ensure directory path
        dir_path = '/'.join(filename.split('/')[:-1])
        ensure_directory(dir_path)
        
        print("Capturing image...")
        camera.capture_jpg()
        
        # Verify if capture was successful
        if camera.received_length == 0:
            print("Error: No data captured.")
            return
        
        print(f"Captured data length: {camera.received_length} bytes")
        
        # Save the image
        print(f"Saving image as {filename}...")
        camera.saveJPG(filename)
        size = uos.stat(filename)[6]
        print(f"Image saved as {filename} ({size} bytes)")
    except Exception as e:
        print(f"Error saving image {filename}: {e}")

def main():
    try:
        # Initialize camera
        print("Initializing camera...")
        camera, spi, cs = initialize_camera()
        
        # Ensure 'test' directory exists
        test_directory = "test"
        ensure_directory(test_directory)

        # Set resolution to 1280x720
        resolution = '1280x720'
        print(f"Setting resolution to: {resolution}")
        camera.resolution = resolution

        # No focus
        print("Capturing image with no focus adjustment...")
        capture_and_save_image(camera, f"{test_directory}/{resolution}_no_focus.jpg")
        
        # Auto focus
        print("Setting autofocus...")
        camera.auto_focus(True)
        capture_and_save_image(camera, f"{test_directory}/{resolution}_autofocus.jpg")
        camera.auto_focus(False)  # Turn off autofocus for subsequent tests

        # Fixed focus at two different lengths
        fixed_focus_lengths = [0x0020, 0x0050]
        for length in fixed_focus_lengths:
            print(f"Setting fixed focus to 0x{length:04X}...")
            camera._write_reg(0x30, (length >> 8) & 0xFF)
            camera._write_reg(0x31, length & 0xFF)
            time.sleep(0.5)  # Give time for the focus position to change
            
            filename = f"{test_directory}/{resolution}_fixed_focus_0x{length:04X}.jpg"
            capture_and_save_image(camera, filename)
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        # Deinitialize SPI
        print("Deinitializing SPI...")
        spi.deinit()

if __name__ == '__main__':
    main()
