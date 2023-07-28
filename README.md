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

## Installation

1. Prepare the new touchscreen mount by securing the 3D printed spacers to the 3D printed mounting plate using the M2 self-tapping screws, connecting the ribbon cable to the Raspberry Pi touchscreen in the orientation shown below, and placing the touchscreen onto the spacers. It should friction fit and be held securely, but not be bent by excessive pressure. Ignore the chopped off bits of the 3D printed plate - I have improved the design since installing it for myself. You will probably need to clip the plastic on the female end of the ribbon cable to get it to fit around the plate. It's very soft plastic and easy to do this without any negative effects.
![image](https://github.com/JonnyHaystack/4MaxProTouchscreenMount/assets/1266473/de4e3410-8937-48bd-bc74-35dfc1bfe0ef)
![image](https://github.com/JonnyHaystack/4MaxProTouchscreenMount/assets/1266473/220738a8-461b-4f7b-940a-cd2a0e64a32f)

2. Remove all panels from the printer. You must remove the bottom panel first, then the rear panel, followed by the side panels, and then the top panel. You should disconnect the cable from the stock touchscreen before removing the top panel. The final panel is the front panel, which you only need to remove if you want to route your wiring through the front, which is what I found to be the cleanest way. Removing the side panels is the most difficult part, because there are multiple plastic latches you need to move out of the way with some kind of prying tool while applying constant outward pressure to the panel so the latches don't slide back into place.
3. Unfasten the 4 screws that secure the stock touchscreen mounting plate to the top panel. This allows you to remove the stock touchscreen from the printer frame.
4. Use the screws from the stock touchscreen mount to secure the new touchscreen mount to the frame. Refer to the image in step 1 for orientation.
5. Route your ribbon cable to your Raspberry Pi somehow. Below are photos of how I achieved this by routing the cable down the side of the front panel. It required cutting off a little bit of the bottom of the front panel to fit the cable through into the underside of the printer's frame.
![image](https://github.com/JonnyHaystack/4MaxProTouchscreenMount/assets/1266473/69a85b1c-687f-4373-a018-6fdd42ad6d5d)
![image](https://github.com/JonnyHaystack/4MaxProTouchscreenMount/assets/1266473/a3998c13-aff2-469c-8efb-b87886b68ecc)

The wiring and the cut parts of the front panel are completely hidden once the bottom panel is secured, so don't worry too much about it looking ugly!

6. Put the printer back together. For convenience, I have catalogued which screws are used for which panels below.

- 8x M3x6 cap head for front panel
- 9x M3x6 cap head for top panel
- 8x M3x4 countersunk for side panels
- 8x M3x10 countersunk for back panel
- 4x M3x10 cap head for bottom panel
- 4x M4x8 cap head for bottom panel
- 4x M3x12 pan head wood screws for touchscreen

## Software Configuration

See the [KlipperScreen documentation](https://klipperscreen.readthedocs.io) for setting up KlipperScreen itself, and see the [LCD Wiki page](http://www.lcdwiki.com/3.5inch_RPi_Display) for the 3.5" Raspberry Pi touchscreen for driver setup and calibration.

For the orientation in which I installed the touchscreen, I had to first apply the rotation of the display as instructed on the LCD Wiki page, and then create the following file in `/etc/X11/xorg.conf.d/99-calibration.conf`, in order to transform the touchscreen inputs to match the display rotation.
```
Section "InputClass"
        Identifier      "calibration"
        MatchProduct    "ADS7846 Touchscreen"
        Option "TransformationMatrix" "-1 0 1 0 1 0 0 0 1"
        #Option  "Calibration"   "3936 227 268 3880"
        #Option  "SwapAxes"      "1"
EndSection
```

In order for this config to be applied you must restart the Raspberry Pi or at least restart Xorg.

## Final result

Have fun!

![image](https://github.com/JonnyHaystack/4MaxProTouchscreenMount/assets/1266473/036dd368-6a78-4666-9197-a0dc985ccb92)
