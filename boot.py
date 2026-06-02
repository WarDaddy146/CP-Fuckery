"""
boot.py — runs once at reset, before code.py.

This file MUST live in the CIRCUITPY drive's root (next to code.py).
It registers a custom raw-HID interface in addition to the standard
keyboard, so the PC can talk to the board over a vendor-defined HID
channel without any driver install.

After saving this file, fully power-cycle the board (unplug + replug)
so the host re-enumerates the new USB descriptor.
"""

import usb_hid

# 64-byte IN and 64-byte OUT reports on a vendor-defined usage page.
# Usage Page 0xFF00 is the conventional "vendor-defined" range; the OS
# treats it as raw and won't try to interpret the bytes.
RAW_HID_REPORT_DESCRIPTOR = bytes((
    0x06, 0x00, 0xFF,  # Usage Page (Vendor Defined 0xFF00)
    0x09, 0x01,        # Usage (Vendor Usage 1)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x02,        #   Usage (Vendor Usage 2) -- IN report (device -> host)
    0x15, 0x00,        #   Logical Minimum (0)
    0x26, 0xFF, 0x00,  #   Logical Maximum (255)
    0x75, 0x08,        #   Report Size (8 bits)
    0x95, 0x40,        #   Report Count (64 bytes)
    0x81, 0x02,        #   Input (Data, Var, Abs)
    0x09, 0x03,        #   Usage (Vendor Usage 3) -- OUT report (host -> device)
    0x15, 0x00,        #   Logical Minimum (0)
    0x26, 0xFF, 0x00,  #   Logical Maximum (255)
    0x75, 0x08,        #   Report Size (8 bits)
    0x95, 0x40,        #   Report Count (64 bytes)
    0x91, 0x02,        #   Output (Data, Var, Abs)
    0xC0,              # End Collection
))

raw_hid = usb_hid.Device(
    report_descriptor=RAW_HID_REPORT_DESCRIPTOR,
    usage_page=0xFF00,
    usage=0x01,
    report_ids=(0,),         # report ID 0 = no report-ID prefix
    in_report_lengths=(64,),
    out_report_lengths=(64,),
)

usb_hid.enable((usb_hid.Device.KEYBOARD, raw_hid))
