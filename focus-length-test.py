import uos
from camera import Camera
from machine import Pin, SPI
import time

def print_debug(message):
    print(f"🔍 {message}")

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
            print_debug(f"Directory '{directory}' created")
    except OSError as e:
        print_debug(f"Error creating directory '{directory}': {e}")

def read_register(camera, addr):
    """Read and return the value from the specified register"""
    return int.from_bytes(camera._read_reg(addr), 'big')

def write_register(camera, addr, value):
    """Write a value to the specified register"""
    camera._write_reg(addr, value)
    time.sleep_ms(50)  # Allow time for the register to update

def capture_and_save_image(camera, filename):
    """Capture and save an image with the specified filename, showing progress with dots"""
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
        
        # Save the image with progress dots
        print(f"Saving image as {filename}...", end="")
        camera.saveJPG(filename)
        print("")  # New line after dots
        
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

        # Adjust additional settings
        print("Adjusting additional settings...")
        # Example settings - these might need to be adjusted based on the camera's documentation and desired effect
        exposure_value = 0x20  # Example exposure value
        gain_value = 0x10      # Example gain value
        white_balance_value = camera.WB_MODE_AUTO  # Example white balance mode
        
        write_register(camera, camera.CAM_REG_BRIGHTNESS_CONTROL, camera.BRIGHTNESS_DEFAULT)
        write_register(camera, camera.CAM_REG_CONTRAST_CONTROL, camera.CONTRAST_DEFAULT)
        write_register(camera, camera.CAM_REG_SATURATION_CONTROL, camera.SATURATION_DEFAULT)
        write_register(camera, camera.CAM_REG_WB_MODE_CONTROL, white_balance_value)
        write_register(camera, camera.CAM_REG_SENSOR_RESET, exposure_value)
        write_register(camera, camera.CAM_REG_SENSOR_ID, gain_value)

        # No focus adjustment
        print("Capturing image with no focus adjustment...")
        capture_and_save_image(camera, f"{test_directory}/{resolution}_no_focus.jpg")
        
        # Auto focus
        print("Setting autofocus...")
        camera.auto_focus(True)
        capture_and_save_image(camera, f"{test_directory}/{resolution}_autofocus.jpg")
        camera.auto_focus(False)  # Turn off autofocus for subsequent tests

        # Fixed focus at various lengths
        fixed_focus_lengths = [0x0010, 0x0020, 0x0030, 0x0040, 0x0050, 0x0060, 0x0070, 0x0080]
        for length in fixed_focus_lengths:
            print(f"Setting fixed focus to 0x{length:04X}...")
            camera._write_reg(0x30, (length >> 8) & 0xFF)
            camera._write_reg(0x31, length & 0xFF)
            time.sleep(0.5)  # Give time for the focus position to change
            
            # Verify focus register values
            focus_high = read_register(camera, 0x30)
            focus_low = read_register(camera, 0x31)
            actual_focus = (focus_high << 8) | focus_low
            print(f"Focus register values after setting to 0x{length:04X}: 0x{actual_focus:04X}")
            
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
