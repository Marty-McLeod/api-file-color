## Design Goals and Notes

#### Color functionality

_(Done)_
- [x] Validation / error handling function

- [x] Shift (swap) colors from R to G / G to R, G to B/B to G, R to B/B to R

- [x] Darken/lighten hex (except blacklisted/only whitelist)
- [x] Darken/lighten RGB (except blacklisted/only whitelist)

- [x] Change named colors / convert to HEX or RGB

- [x] Convert HEX to RGB, returns string or tuple
- [x] Convert HEX to HSL, returns tuple or string

- [x] Convert RGB to HSL, returns tuple or string
- [x] Convert RGB to HEX, returns string or tuple

- [x] Convert HSL to HEX, returns string or tuple
- [x] Convert HSL to RGB, returns tuple or string
- [x] Convert HSL to HSV

- [x] Convert HSV to HSL
- [x] Convert HSV to RGB
- [x] Convert HSV to HEX

### Structure for the JSON options data object 
```
{
    "options": 
    { 
        "hex_rgb": true, 
        "hex_hsl": false,

        "rgb_hsl": false,
        "rgb_hex": false,

        "hsl_hex": false,
        "hsl_rgb": false,
        "hsl_hsv": false,

        "hsv_hsl": false,
        "hsv_hex": false,
        "hsv_rgb": false,

        "name_hex": true,
        "name_rgb": false,

        "lightdark_hex": { "active": false, "mode": "lighten", "percent": 10 },
        "lightdark_rgb": { "active": false, "mode": "lighten", "percent": 10 },
        
        "colorswap_hex": { "active": false, "order": "r_to_g" },
        "colorswap_rgb": { "active": false, "order": "r_to_g" }
    }
}
```