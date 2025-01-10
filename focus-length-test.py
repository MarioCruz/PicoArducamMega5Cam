from machine import Pin, SPI
from camera import Camera
import time
import uos

def print_debug(message, level=1):
    prefix = "  " * (level - 1)
    print(prefix + "🔍 " + str(message))

def initialize_camera():
    """Initialize and return camera instance"""
    spi = SPI(1,
              sck=Pin(10),
              mosi=Pin(15),
              miso=Pin(12),
              baudrate=8000000,
              polarity=0,
              phase=0)
    
    cs = Pin(13, Pin.OUT)
    cs.value(1)
    time.sleep_ms(100)
    
    camera = Camera(spi, cs)
    time.sleep_ms(500)
    
    return camera, spi

def read_focus_position(camera):
    """Read and return the focus position from the specified registers"""
    pos_high = int.from_bytes(camera._read_reg(0x30), 'big')
    pos_low = int.from_bytes(camera._read_reg(0x31), 'big')
    return (pos_high << 8) | pos_low

def change_focus_position(camera, position):
    """Change the focus position to the specified value"""
    pos_high = (position >> 8) & 0xFF
    pos_low = position & 0xFF
    camera._write_reg(0x30, pos_high)
    print_debug(f"Wrote to 0x30: 0x{pos_high:02X}")
    time.sleep_ms(100)
    camera._write_reg(0x31, pos_low)
    print_debug(f"Wrote to 0x31: 0x{pos_low:02X}")
    time.sleep(0.5)  # Give time for the focus position to change

def read_register(camera, addr):
    """Read and return the value from the specified register"""
    return int.from_bytes(camera._read_reg(addr), 'big')

def write_register(camera, addr, value):
    """Write a value to the specified register"""
    camera._write_reg(addr, value)
    print_debug(f"Wrote to register 0x{addr:02X}: 0x{value:02X}")
    time.sleep_ms(100)  # Give time for the register to be written

def verify_register(camera, addr, expected_value):
    """Verify that the register holds the expected value"""
    actual_value = read_register(camera, addr)
    if actual_value == expected_value:
        print_debug(f"Register 0x{addr:02X} verification passed: 0x{actual_value:02X}")
    else:
        print_debug(f"Register 0x{addr:02X} verification failed: expected 0x{expected_value:02X}, got 0x{actual_value:02X}")

def ensure_directory(directory):
    """Ensure that the directory exists"""
    if directory not in uos.listdir():
        uos.mkdir(directory)
        print_debug(f"Directory '{directory}' created")

def save_image(camera, directory, name):
    """Capture and save an image with the specified name, showing progress with dots"""
    camera.capture_jpg()
    filename = f"{directory}/{name}.jpg"

    try:
        jpg_file = open(filename, 'wb')
        buffer_size = 1024  # Define buffer size for reading and writing
        total_bytes_written = 0
        remaining_bytes = camera.total_length

        print(f"Saving {filename}: ", end='')
        while remaining_bytes > 0:
            bytes_to_read = min(buffer_size, remaining_bytes)
            data = camera._read_byte()[:bytes_to_read]
            jpg_file.write(data)
            total_bytes_written += bytes_to_read
            remaining_bytes -= bytes_to_read
            print(".", end='')

        jpg_file.close()
        print(f" {total_bytes_written} bytes")
    except Exception as e:
        print_debug(f"Error saving image {filename}: {e}")

def main():
    print_debug("Initializing camera...")
    camera, spi = initialize_camera()
    
    try:
        print_debug("Camera initialized. Waiting for 1 second...")
        time.sleep(1)
        
        # Ensure 'test' directory exists
        test_directory = "test"
        ensure_directory(test_directory)
        
        # Supported resolutions
        resolutions = {
            '320x240': camera.RESOLUTION_320X240,
            '640x480': camera.RESOLUTION_640X480,
            '1280x720': camera.RESOLUTION_1280X720,
            '1600x1200': camera.RESOLUTION_1600X1200,
            '1920x1080': camera.RESOLUTION_1920X1080,
            '2592x1944': camera.RESOLUTION_2592X1944  # Highest resolution for 5MP
        }

        for resolution, res_value in resolutions.items():
            print_debug(f"Testing resolution: {resolution}")
            camera.resolution = resolution
            
            # Read initial focus position
            initial_focus = read_focus_position(camera)
            print_debug(f"Initial focus position: 0x{initial_focus:04X}")
            save_image(camera, test_directory, f"{resolution}_initial_focus_0x{initial_focus:04X}")
            
            # Set new focus position
            new_focus = 0x0050  # Example value, change as needed
            print_debug(f"Changing focus position to: 0x{new_focus:04X}")
            change_focus_position(camera, new_focus)
            
            # Read new focus position
            updated_focus = read_focus_position(camera)
            print_debug(f"Updated focus position: 0x{updated_focus:04X}")
            save_image(camera, test_directory, f"{resolution}_updated_focus_0x{updated_focus:04X}")
            
            # Verify if the focus position changed
            if new_focus == updated_focus:
                print_debug("Focus position successfully changed!")
            else:
                print_debug("Failed to change focus position.")
            
            # Additional register verification
            print_debug("Verifying other registers...")
            test_registers = {
                0x20: 0x01,  # Example value, you can change it as needed
                0x21: 0x02,  # Example value, you can change it as needed
                0x22: 0x00   # Example value, you can change it as needed
            }
            
            # Write to registers and save images
            for addr, value in test_registers.items():
                write_register(camera, addr, value)
                save_image(camera, test_directory, f"{resolution}_reg_{addr:02X}_set_to_{value:02X}")
            
            # Verify registers
            for addr, expected_value in test_registers.items():
                verify_register(camera, addr, expected_value)
            
            # Additional focus on register 0x21
            print_debug("Additional verification for register 0x21:")
            expected_value = 0x02
            write_register(camera, 0x21, expected_value)
            save_image(camera, test_directory, f"{resolution}_reg_21_after_write")
            actual_value = read_register(camera, 0x21)
            print_debug(f"After writing, register 0x21: expected 0x{expected_value:02X}, got 0x{actual_value:02X}")
            if actual_value == expected_value:
                print_debug("Register 0x21 verification passed!")
            else:
                print_debug("Register 0x21 verification failed!")
        
    finally:
        print_debug("Deinitializing SPI...")
        spi.deinit()

if __name__ == '__main__':
    main()
