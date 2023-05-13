import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import time
import traceback

# Define display properties
display_width = 128
display_height = 64

try:
	# Initialize the display
	disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
	disp.begin()
	disp.clear()
	disp.display()

	# Create a blank image with the mode '1' for monochrome
	image = Image.new('1', (display_width, display_height))

	# Create a drawing object
	draw = ImageDraw.Draw(image)

	#font_large = ImageFont.truetype('arial.ttf', 24)
	font = ImageFont.load_default()

	while True:
		# Clear the image buffer by drawing a black filled box
		draw.rectangle((0, 0, display_width, display_height), outline=0, fill=0)

		try:
			# Get the current time
			current_time = time.strftime('%H:%M:%S')

			text_box = draw.textbbox((0,0), current_time, font=font)


			# Draw the time on the image
			draw.text((0, 1), current_time, font=font, fill=255)

		except Exception:
			# Print the traceback of the error
			traceback.print_exc()
			# Display a fallback message on the image
			draw.text((0, 0), 'Error occurred', fill=255)

		finally:
			# Display the image
			disp.image(image)
			disp.display()

			current_second_fraction = time.time() % 1
			sleep_duration = 1 - current_second_fraction
			time.sleep(sleep_duration)

except KeyboardInterrupt:
	# Clean up resources on keyboard interrupt
	disp.clear()
	disp.display()

finally:
    # Turn off the display
    disp.clear()
    disp.display()



