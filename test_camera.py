
def test_capture():
    import uos
    from camera import Camera
    from machine import Pin, SPI
    
    try:
        # Initialize camera
        print("Initializing camera...")
        camSPI = SPI(1, sck=Pin(10), mosi=Pin(15), miso=Pin(12), baudrate=8000000)
        camCS = Pin(13, Pin.OUT)
        camCS.high()
        cam = Camera(camSPI, camCS, skip_sleep=False)
        
        # Try to capture
        print("Capturing image...")
        cam.capture_jpg()
        print("Saving test image...")
        cam.saveJPG('test.jpg')
        
        # Check result
        size = uos.stat('test.jpg')[6]
        print(f"Success! File size: {size} bytes")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    test_capture()
