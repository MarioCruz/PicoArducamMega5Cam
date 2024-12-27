# Raspberry Pi Pico W Camera Web Server

A web-based camera control interface for the Raspberry Pi Pico W with Arducam.

## Features

- Live camera preview
- Camera controls:
  - Auto focus (toggle and single-focus)
  - Resolution settings
  - White balance
  - Brightness
  - Contrast
  - Saturation
- Image storage:
  - Save last 3 images
  - View saved images
  - Automatic cleanup
- Clean web interface
- Status feedback
- Error handling

## Hardware Requirements

- Raspberry Pi Pico W
- Arducam Camera (5MP or 3MP model)
- MicroUSB cable for power

## Pin Connections

| Pico W | Arducam |
|--------|---------|
| GP10   | SCK     |
| GP11   | MOSI    |
| GP12   | MISO    |
| GP13   | CS      |
| VBUS   | VCC     |
| GND    | GND     |

## Software Setup

1. Install the latest MicroPython firmware on your Pico W
2. Copy all project files to your Pico W:
   - webserver.py (main web server)
   - camera.py (camera driver)
   - config.py (configuration)
   - boot.py (startup script)

3. Update WiFi settings in config.py:
   ```python
   WIFI_SSID = "YourSSID"
   WIFI_PASSWORD = "YourPassword"
   ```

## Usage

1. Power up your Pico W
2. The server will start automatically
3. Connect to the IP address shown on the Pico W console
4. Use the web interface to:
   - View live camera feed
   - Adjust camera settings
   - Capture and save images
   - View saved images

## Files

- `webserver.py`: Main web server and camera control interface
- `camera.py`: Arducam camera driver
- `config.py`: Configuration settings
- `boot.py`: Boot configuration
- `test_camera.py`: Simple Test

## Notes

- Camera initialization takes a few seconds
- Auto focus is only available on 5MP camera models
- Images are stored in RAM, power loss will clear saved images
- Maximum of 3 saved images to preserve memory

## Troubleshooting

1. If camera fails to initialize:
   - Check physical connections
   - Reset the Pico W
   - Ensure proper power supply

2. If web interface is not accessible:
   - Check WiFi settings
   - Verify IP address from console
   - Reset the Pico W

3. If images fail to save:
   - Check available memory
   - Reduce image resolution
   - Clear saved images

