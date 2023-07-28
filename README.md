# 4MaxProTouchscreenMount
Parametric and modular touchscreen mount for Anycubic 4Max Pro (2.0)

## Background

I switched to using the Klipper firmware on my 4Max Pro 2.0 a while back, and if you've ever used Klipper, I'm sure you understand why I can never go back to Marlin. The one feature of this printer that doesn't work with Klipper is the touchscreen, which is some proprietary thing with very limited functionality, and I never liked it even when it did work. Fortunately, at the same time I started using Klipper, I learned of the existence of [KlipperScreen](https://klipperscreen.readthedocs.io/en/latest/), which provides much more functionality and a prettier UI.

However, KlipperScreen requires a custom touchscreen directly connected to the Klipper host, which means I had to do some extra work. In KlipperScreen's [list of supported hardware](https://klipperscreen.readthedocs.io/en/latest/Hardware/), there is a 3.5" Raspberry Pi touchscreen, which happens to be the same size as the stock touchscreen in the 4Max Pro. These are very inexpensive and easy to obtain from AliExpress or Amazon, and are a convenient solution if you already use a Pi as your Klipper host. After procrastinating for a year, I started by opening up the printer and taking some measurements and designing a replica of the stock touchscreen mount. I then printed it out, verified it against the original, and proceeded to create a modified design for the mounting plate to accomodate this Raspberry Pi touchscreen. As for the wiring, to keep it relatively simple, I used a 2x13 pin ribbon cable (2.54mm pitch of course).

I recommend at least 1 metre length, if you plan on installing your Pi inside the bottom of the printer, or longer if you want to keep it separate. I also had to clip off some of the casing of the female end of the connector to get it to fit, and bend some of the GPIO pins on the Raspberry Pi in order to get the male connector to fit, but those were very minor inconveniences to me.

## Off-the-shelf hardware

| Part | Link | Price | Quantity |
| ---- | ---- | ----- | -------- |
| Ribbon cable (length 1M, A-02, 2x13 26P) | https://www.aliexpress.com/item/1005003733065114.html | £6 | 1 |
| Raspberry Pi 3.5" touchscreen | https://www.aliexpress.com/item/32229578580.html | £7 | 1 |
| M2 self-tapping screws (around 4-8mm length) | You can find them anywhere | Cheap | 4 |

## 3D printed hardware

| Part | Quantity |
| ---- | -------- |
| 4Max_Pro_RPi_Touchscreen_Mount_Plate | 1 |
| 4Max_Pro_RPi_Touchscreen_Mount_Spacer | 4 |

The plate and spacers are separate to enable easy FDM printing without supports. These parts are all best printed in their default orientation (flat side down).