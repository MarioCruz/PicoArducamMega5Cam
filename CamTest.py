from machine import Pin, SPI
from camera import Camera
import time
import uos
import gc

# Camera Register Definitions
CAMERA_REGISTERS = {
    # System Control Registers
    'DEVICE_ID': 0x00,      # Device ID (Read only)
    'RESET': 0x01,          # System Reset
    'SENSOR_ID': 0x02,      # Sensor ID (Read only)
    'SYSTEM_STATE': 0x03,   # System State
    
    # Image Format Registers
    'FORMAT': 0x20,         # Image Format Control
    'RESOLUTION': 0x21,     # Resolution Setting
    'COMPRESSION': 0x22,    # Compression Control
    'FORMAT_STATE': 0x23,   # Format State
    
    # Exposure Registers
    'EXPOSURE': 0x24,       # Exposure Control
    'EXPOSURE_GAIN': 0x25,  # Exposure Gain
    'AEC': 0x26,           # Auto Exposure Control
    'LIGHT_MODE': 0x27,    # Light Mode
    
    # Quality Registers
    'QUALITY': 0x28,        # Image Quality Control
    'SHARPNESS': 0x29,      # Sharpness Control
    'CONTRAST': 0x2A,       # Contrast Control
    'BRIGHTNESS': 0x2B,     # Brightness Control
    
    # Focus Registers
    'FOCUS_CONTROL': 0x30,  # Focus Control
    'FOCUS_STATE': 0x31,    # Focus State
    'FOCUS_POSITION': 0x32, # Focus Position
    
    # White Balance Registers
    'WB_MODE': 0x40,        # White Balance Mode
    'WB_STATE': 0x41,       # White Balance State
    'RED_GAIN': 0x42,       # Red Channel Gain
    'GREEN_GAIN': 0x43,     # Green Channel Gain
    'BLUE_GAIN': 0x44,      # Blue Channel Gain
}

# Register Values
RESOLUTION_VALUES = {
    '320x240': 0x00,
    '640x480': 0x01,
    '1280x720': 0x02,
    '1600x1200': 0x03,
    '1920x1080': 0x04,
    '2592x1944': 0x05
}

QUALITY_VALUES = {
    'highest': 0x00,
    'high': 0x01,
    'medium': 0x02,
    'low': 0x03
}

LIGHT_MODE_VALUES = {
    'auto': 0x00,
    'sunny': 0x01,
    'cloudy': 0x02,
    'office': 0x03,
    'home': 0x04
}

def print_debug(message, level=1):
    prefix = "  " * (level - 1)
    print(prefix + "🔍 " + str(message))

def print_section(message):
    separator = "=" * 20
    print("\n" + separator + " " + message + " " + separator)

def get_timestamp():
    """Create timestamp string for MicroPython"""
    t = time.localtime()
    return "{:02d}{:02d}{:02d}".format(t[3], t[4], t[5])

def ensure_folder(folder_name):
    """Create folder if it doesn't exist"""
    try:
        parts = folder_name.split('/')
        path = ''
        for part in parts:
            if not part:
                continue
            path = path + '/' + part if path else part
            try:
                uos.mkdir(path)
            except OSError as e:
                if e.args[0] != 17:  # Ignore "already exists" error
                    raise
        return True
    except Exception as e:
        print_debug(f"Folder error with {folder_name}: {str(e)}")
        return False

def read_register(camera, reg_name):
    """Read and return value from named register"""
    if reg_name in CAMERA_REGISTERS:
        reg_addr = CAMERA_REGISTERS[reg_name]
        return int.from_bytes(camera._read_reg(reg_addr), 1)
    return None

def write_register(camera, reg_name, value):
    """Write value to named register"""
    if reg_name in CAMERA_REGISTERS:
        reg_addr = CAMERA_REGISTERS[reg_name]
        camera._write_reg(reg_addr, value)
        time.sleep_ms(50)  # Allow register to settle
        return True
    return False

def validate_image_quality(size):
    """Validate image quality based on size"""
    if size < 80000:
        return "Low"
    elif size < 100000:
        return "Medium"
    elif size < 120000:
        return "High"
    else:
        return "Excellent"
    
def initialize_camera():
    """Initialize camera with optimized settings"""
    print_debug("Initializing camera")
    
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
    
    # Read initial state
    print_debug("Reading camera state:")
    device_id = read_register(camera, 'DEVICE_ID')
    sensor_id = read_register(camera, 'SENSOR_ID')
    print_debug(f"Device ID: 0x{device_id:02X}", 2)
    print_debug(f"Sensor ID: 0x{sensor_id:02X}", 2)
    
    # Set resolution
    print_debug("Setting resolution to 1600x1200")
    camera.resolution = "1600x1200"
    time.sleep_ms(500)
    
    # Configure image quality
    print_debug("Configuring image parameters")
    write_register(camera, 'QUALITY', QUALITY_VALUES['highest'])
    write_register(camera, 'SHARPNESS', 0x02)  # Enhanced sharpness
    write_register(camera, 'CONTRAST', 0x01)   # Slightly enhanced contrast
    write_register(camera, 'BRIGHTNESS', 0x01)  # Slightly enhanced brightness
    
    # Configure exposure
    print_debug("Setting exposure parameters")
    write_register(camera, 'EXPOSURE', 0x00)    # Auto exposure
    write_register(camera, 'EXPOSURE_GAIN', 0x00)  # Auto gain
    write_register(camera, 'LIGHT_MODE', LIGHT_MODE_VALUES['auto'])
    
    # Verify settings
    print_debug("Verifying settings:")
    format_val = read_register(camera, 'FORMAT')
    res_val = read_register(camera, 'RESOLUTION')
    quality_val = read_register(camera, 'QUALITY')
    exposure_val = read_register(camera, 'EXPOSURE')
    
    print_debug(f"Format: 0x{format_val:02X}", 2)
    print_debug(f"Resolution: 0x{res_val:02X}", 2)
    print_debug(f"Quality: 0x{quality_val:02X}", 2)
    print_debug(f"Exposure: 0x{exposure_val:02X}", 2)
    
    return camera, spi

def enhanced_warmup(camera):
    """Enhanced warmup sequence"""
    print_debug("Performing enhanced warmup sequence")
    
    for i in range(3):
        print_debug(f"Warmup shot {i+1}/3")
        # Double focus
        camera.auto_focus()
        time.sleep_ms(300)
        camera.auto_focus()
        time.sleep_ms(400)
        
        # Capture
        camera.capture_jpg()
        time.sleep_ms(500 + i * 200)  # Progressive delays
    
    print_debug("Warmup complete")
    time.sleep_ms(1000)

def take_best_picture(camera, folder, base_filename, attempts=4):
    """Take multiple pictures with bracketing and keep the best one"""
    ensure_folder(folder)
    best_size = 0
    best_file = None
    
    print_debug(f"Taking {attempts} sets of bracketed pictures...")
    
    for i in range(attempts):
        print_debug(f"\nAttempt {i+1}/{attempts}")
        
        # Memory cleanup
        gc.collect()
        
        # Progressive focus sequence
        print_debug("Focus sequence...")
        for _ in range(2):
            camera.auto_focus()
            time.sleep_ms(300)
        
        # Pre-capture delay
        time.sleep_ms(500)
        
        # Capture with bracketing
        print_debug("Capturing bracketed pair...")
        sizes = []
        for j in range(2):
            camera.capture_jpg()
            time.sleep_ms(400)
            
            temp_filename = f"{base_filename}_temp_{i}_{j}.jpg"
            full_path = f"{folder}/{temp_filename}"
            
            camera.saveJPG(full_path)
            time.sleep_ms(400)
            
            if temp_filename in uos.listdir(folder):
                size = uos.stat(full_path)[6]
                sizes.append((size, temp_filename))
                print_debug(f"Shot {j+1} size: {size} bytes", 2)
        
        # Process bracketed shots
        if sizes:
            size, filename = max(sizes, key=lambda x: x[0])
            print_debug(f"Best bracketed size: {size} bytes")
            
            # Delete the smaller bracketed shot
            for s, f in sizes:
                if f != filename:
                    uos.remove(f"{folder}/{f}")
            
            if size > best_size:
                if best_file and best_file in uos.listdir(folder):
                    uos.remove(f"{folder}/{best_file}")
                best_size = size
                best_file = filename
                print_debug("★ New best image!")
                quality = validate_image_quality(size)
                print_debug(f"Quality: {quality}", 2)
            else:
                print_debug(f"No improvement (-{best_size - size} bytes)")
                uos.remove(f"{folder}/{filename}")
        
        time.sleep_ms(1000)
    
    # Rename best file to final name
    if best_file:
        final_name = f"{base_filename}.jpg"
        uos.rename(f"{folder}/{best_file}", f"{folder}/{final_name}")
        print_debug(f"\nBest image saved as: {final_name}")
        print_debug(f"Final size: {best_size} bytes")
        print_debug(f"Final quality: {validate_image_quality(best_size)}")
        return best_size
    
    return 0

def optimal_capture():
    """Take high quality 1600x1200 pictures with optimization"""
    print_section("OPTIMIZED CAPTURE - 1600x1200")
    
    try:
        timestamp = get_timestamp()
        folder = f"capture_{timestamp}"
        
        camera, spi = initialize_camera()
        
        # Perform enhanced warmup
        enhanced_warmup(camera)
        time.sleep_ms(2000)
        
        # Take series of best pictures
        sizes = []
        qualities = []
        
        for i in range(3):
            print_section(f"CAPTURE {i+1}/3")
            size = take_best_picture(camera, folder, f"photo_{i+1}", attempts=4)
            sizes.append(size)
            qualities.append(validate_image_quality(size))
            time.sleep_ms(2000)
        
        # Print summary
        print_section("CAPTURE SUMMARY")
        for i, (size, quality) in enumerate(zip(sizes, qualities), 1):
            print_debug(f"Photo {i}:")
            print_debug(f"Size: {size} bytes", 2)
            print_debug(f"Quality: {quality}", 2)
            if i > 1:
                diff = size - sizes[i-2]
                print_debug(f"Change from previous: {diff:+d} bytes", 2)
        
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            print_debug(f"\nAverage size: {avg_size:.0f} bytes")
            print_debug(f"Size range: {min(sizes)} - {max(sizes)} bytes")
            
            # Calculate consistency
            variance = max(sizes) - min(sizes)
            print_debug(f"Size variance: {variance} bytes")
            consistency = "High" if variance < 10000 else "Medium" if variance < 20000 else "Low"
            print_debug(f"Capture consistency: {consistency}")
            
            # Quality summary
            quality_counts = {}
            for q in qualities:
                quality_counts[q] = quality_counts.get(q, 0) + 1
            print_debug("\nQuality distribution:")
            for q, count in quality_counts.items():
                print_debug(f"{q}: {count} photos", 2)
        
    except Exception as e:
        print_section("ERROR")
        print_debug("Test failed: " + str(e))
        import sys
        sys.print_exception(e)
        
    finally:
        if spi:
            spi.deinit()
        print_debug("\nCapture completed")

if __name__ == '__main__':
    optimal_capture()
