import hid
import time
import cairosvg
from PIL import Image
import io

svg_code = """<svg width="130" height="30" viewBox="0 0 151.541 34" fill="none" xmlns="http://www.w3.org/2000/svg" class="transition-colors duration-500"><g fill="black"><path d="M0.34 0H18.5543V5.92571L10.5886 25.84H18.5543V34H0V28.22L7.96571 8.16H0.34V0Z"></path><path d="M33.0771 30.1629H28.4143L27.8314 34H19.1857L24.9657 0H37.2543L43.0829 34H33.66L33.0771 30.1629ZM29.5314 22.4886H31.8629C31.4743 19.4286 31.0857 15.4457 30.7457 11.0743C30.4057 15.4457 29.9686 19.4286 29.5314 22.4886Z"></path><path d="M53.8638 34H44.4895V0H55.4181C60.4695 0 65.8123 1.65143 65.8123 9.86V14.28C65.8123 22.4886 60.4695 24.14 55.4181 24.14H53.8638V34ZM53.8638 8.16V15.98H55.1752C56.0495 15.98 56.4381 15.5914 56.4381 14.62V9.52C56.4381 8.54857 56.0495 8.16 55.1752 8.16H53.8638Z"></path><path d="M101.027 25.84H108.021V34H91.6523V0H107.778V8.16H101.027V12.24H106.467V20.4H101.027V25.84Z"></path><path d="M123.952 0H132.744L125.458 24.0429V34H116.084V24.3829L108.798 0H118.367L120.018 6.55714C120.747 9.52 120.989 11.3171 121.232 13.4543C121.427 11.3171 121.718 9.52 122.398 6.55714L123.952 0Z"></path><path d="M133.327 0H151.541V5.92571L143.575 25.84H151.541V34H132.987V28.22L140.952 8.16H133.327V0Z"></path><path d="M76.8517 8.16L76.8866 8.03566V0H67.5123V34H68.4682L76.8517 8.16Z"></path><path d="M90.3409 0H81.3066L80.1409 3.15714C80.1079 3.24651 80.0749 3.33783 80.0418 3.4272L76.9935 11.9155C76.9585 12.0224 76.9216 12.1331 76.8866 12.24V12.2128L69.0647 34H76.8866V27.0543L77.9552 24.5286L80.7238 34H90.3409L84.3666 15.3L90.3409 0Z"></path></g></svg>"""

# SVG → grayscale → cbuf
png_bytes = cairosvg.svg2png(bytestring=svg_code.encode(), output_width=128, output_height=32)
img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

# Composite onto white background to preserve transparency
background = Image.new("RGBA", img.size, (255, 255, 255, 255))
background.paste(img, mask=img.split()[3])  # alpha channel as mask
img = background.convert("L")

pixels = img.tobytes()
print(f"Pixel min: {min(pixels)}, max: {max(pixels)}, sample: {pixels[:20].hex()}")
cbuf = bytearray(b ^ 0xFF for b in pixels)
# HID send
for d in hid.enumerate():
    if d['usage_page'] == 0xFF00 and d['usage'] == 0x01:
        dev = hid.Device(path=d['path'])
        break
else:
    print("no device")
    exit(1)

for i in range(64):
    pkt = bytes(cbuf[i*64:(i+1)*64])
    dev.write(b'\x00' + pkt)
    print(f"[TX] packet {i}: {pkt.hex()}")
    time.sleep(0.005)

print("[TX] Done — 64 packets sent (4096 bytes)")