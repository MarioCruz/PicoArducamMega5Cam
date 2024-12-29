from machine import Pin, SPI
from camera import Camera
import time

def test_camera_autofocus():
    try:
        # Initialize SPI
        print("Initializing SPI...")
        spi = SPI(1, 
                  baudrate=4000000,
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
        
        print("\nCreating camera instance...")
        camera = Camera(spi, cs)
        
        # Wait for camera to stabilize
        print("Waiting for camera to stabilize...")
        time.sleep(2)
        
        # Set resolution
        print("\nSetting resolution to 640x480...")
        camera.resolution = '640x480'
        
        # Enable auto focus
        print("\nEnabling auto focus...")
        result = camera.auto_focus(True)
        print(f"Auto focus enable result: {result}")
        
        # Wait for auto focus to adjust
        print("Waiting for auto focus adjustment...")
        time.sleep(2)
        
        # Take picture
        print("\nCapturing image...")
        camera.capture_jpg()
        
        # Save the image
        print("Saving image...")
        camera.saveJPG('autofocus_test.jpg')
        print("Image saved as 'autofocus_test.jpg'")
        
        # Disable auto focus
        print("\nDisabling auto focus...")
        camera.auto_focus(False)
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if 'spi' in locals():
            spi.deinit()
        print("\nTest completed")

if __name__ == '__main__':
    print("Starting camera autofocus test...")
    test_camera_autofocus()
