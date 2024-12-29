from machine import Pin, SPI
from camera import Camera
import time
import uos

def test_camera_capture():
    try:
        # Initialize SPI with debug info
        print("\n=== Camera Test Sequence ===")
        print("1. Initializing SPI...")
        spi = SPI(1, 
                  baudrate=8000000,
                  polarity=0, 
                  phase=0, 
                  bits=8, 
                  firstbit=SPI.MSB,
                  sck=Pin(10),
                  mosi=Pin(15),
                  miso=Pin(12))
        
        # Initialize CS pin
        cs = Pin(13, Pin.OUT)
        cs.value(1)
        
        print("2. Creating camera instance...")
        camera = Camera(spi, cs)
        
        # Wait for camera to stabilize
        print("3. Waiting for camera to stabilize...")
        time.sleep(2)
        
        # Take picture without autofocus
        print("\n=== Testing Normal Capture ===")
        print("4. Capturing image without autofocus...")
        camera.capture_jpg()
        print("5. Saving image without autofocus...")
        camera.saveJPG('no_autofocus.jpg')
        size1 = uos.stat('no_autofocus.jpg')[6]
        print(f"Success! File size: {size1} bytes")
        
        # Enable autofocus and take second picture
        print("\n=== Testing Autofocus Capture ===")
        print("6. Enabling autofocus...")
        result = camera.auto_focus(True)
        print(f"Autofocus enable result: {result}")
        
        time.sleep(2)  # Give time for autofocus to adjust
        
        print("7. Capturing image with autofocus...")
        camera.capture_jpg()
        print("8. Saving image with autofocus...")
        camera.saveJPG('with_autofocus.jpg')
        size2 = uos.stat('with_autofocus.jpg')[6]
        print(f"Success! File size: {size2} bytes")
        
        print("\n=== Test Complete ===")
        print(f"No Autofocus image size: {size1} bytes")
        print(f"With Autofocus image size: {size2} bytes")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if 'spi' in locals():
            spi.deinit()

if __name__ == '__main__':
    test_camera_capture()
