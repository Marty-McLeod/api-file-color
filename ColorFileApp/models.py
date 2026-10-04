'''
Contains Pydantic models (data structures) needed for the application
'''
from pydantic import (
    BaseModel, conint, Field, 
    ConfigDict, field_validator
)
from collections import Counter
from typing import Literal, Annotated, Union, get_args
        
        
# Create Pydantic data model for JSON options received in HTTP body

# 29-SEP-2026: Updated models below as "active" key is no longer used (lightdark_XXX &
# colorswap_XXX objects are now consolidated/simplified).
class LightdarkHex(BaseModel):
    lightdark_hex: bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)] # Add 'Annotated' for typechecker acceptance

class LightdarkRgb(BaseModel):
    lightdark_rgb: bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)]

class ColorswapHex(BaseModel):
    colorswap_hex: bool
    order: Literal["r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"]

class ColorswapRgb(BaseModel):
    colorswap_rgb: bool
    order: Literal["r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"]
    
class Options(BaseModel):
    hex_rgb: bool 
    hex_hsl: bool
    
    name_hex: bool
    name_rgb: bool
    
    rgb_hsl: bool
    rgb_hex: bool
    
    hsl_hex: bool
    hsl_rgb: bool
    hsl_hsv: bool
    hsv_hsl: bool
    
    hsv_hex: bool
    hsv_rgb: bool

    lightdark_hex: LightdarkHex
    lightdark_rgb: LightdarkRgb
    colorswap_hex: ColorswapHex
    colorswap_rgb: ColorswapRgb


# TEST CODE BELOW!    
# ==========================================
OptionConvertKeys = Literal[
    "hex_rgb", "hex_hsl", "name_hex", "name_rgb",
    "rgb_hsl", "rgb_hex", "hsl_hex", "hsl_rgb", 
    "hsl_hsv", "hsv_hsl", "hsv_hex", "hsv_rgb"
]

OptionLightDarkKeys = Literal[
    "lightdark_hex", "lightdark_rgb"
]

OptionModeKeys = Literal[
    "lighten", "darken"
]

OptionColorswapKeys = Literal[
    "colorswap_hex", "colorswap_rgb"
]

OptionOrderKeys = Literal[
    "r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"
]

CONVERT_ALLOWED_KEY_NAMES = [
        "hex_rgb",
        "hex_hsl",
        "name_hex",
        "name_rgb",
        "rgb_hsl",
        "rgb_hex",
        "hsl_hex",
        "hsl_rgb",
        "hsl_hsv",
        "hsv_hsl",
        "hsv_hex",
        "hsv_rgb"
]

LIGHTDARK_ALLOWED_KEY_NAMES = [
    "lightdark_hex", "lightdark_rgb"
]

COLORSWAP_ALLOWED_KEY_NAMES = [
    "colorswap_hex", "colorswap_rgb"
]

KEYNAME_LISTS = [
    CONVERT_ALLOWED_KEY_NAMES,
    LIGHTDARK_ALLOWED_KEY_NAMES,
    COLORSWAP_ALLOWED_KEY_NAMES
]
    

# == Validation models for options JSON array, containing an array (list) ==
#   I.e.:
# {
#     "options": [
#         { "hex_rgb": true }, 
#         { "hex_hsl": false },
#           ...        
#         { "lightdark_hex": false, "mode": "lighten", "percent": 10 },
#         { "lightdark_rgb": false, "mode": "lighten", "percent": 10 },
#         { "colorswap_hex": false, "order": "r_to_g" },
#         { "colorswap_rgb": false, "order": "r_to_g" }   
#     ]
#  } 
# Note:
# 1) The models below use strict key names as defined above; these are 
# checked by the validator and a failure will arise if an unknown key is received
# 2) Only requires ONE or more objects that are valid to be received - NOT the entire
# JSON array of objects shown above. I.e., the following is also valid:
# {
#     "options": [
#         { "hex_rgb": true }, 
#         { "lightdark_hex": true, "mode": "lighten", "percent": 10 },
#         { "lightdark_rgb": true, "mode": "lighten", "percent": 10 },
#     ]
# }
# --- Shared base: frozen (hashable, compared by type + values), strict fields --
class ComponentBase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
class OptionConvert(BaseModel):
    hex_rgb: bool 
    # hex_hsl: bool   # <-- these need to be dealt with!!

    # name_hex: bool
    # name_rgb: bool

    # rgb_hsl: bool
    # rgb_hex: bool

    # hsl_hex: bool
    # hsl_rgb: bool
    # hsl_hsv: bool
    # hsv_hsl: bool

    # hsv_hex: bool
    # hsv_rgb: bool

class OptionColorswapHex(BaseModel):
    colorswap_hex: bool
    order: Literal["r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"]

class OptionColorswapRgb(BaseModel):
    colorswap_rgb: bool
    order: Literal["r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"]

class OptionLightdarkHex(BaseModel):
    lightdark_hex: bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)] # Add 'Annotated' for typechecker acceptance

class OptionLightdarkRgb(BaseModel):
    lightdark_rgb: bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)]


# Custom parent model: builds a top level list which can contain all 3 types of
# option objects. If one or more exists/is validated, the whole model is validated
# (Union[] validates one or more child classes)
# class ItemList(RootModel):
#     root: list[ OptionConvert ]
AnyOption = Union[
    OptionConvert, OptionColorswapHex,
    OptionColorswapRgb, OptionLightdarkHex,
    OptionLightdarkRgb
]

MAX_OPTIONS = len(get_args(AnyOption))

# Parent wrapper: assigns key "options" to the parent model and creates a list
# containing one or more child models. An enmpty input list from the API endpoint
# is not validated.
#
# I.e.: "options": [... ]
class PayloadWrapper(BaseModel):
    # Uses annotation declarations to require a min. of 1 member object of any type
    options: Annotated[list[AnyOption], Field(min_length=1)]
    
    @field_validator("options")
    @classmethod
    def no_identical_components(cls, items: list) -> list:
        counts = Counter(items)
        duplicates = [repr(item) for item, n in counts.items() if n > 1]
        if duplicates:
            raise ValueError(f"Duplicate components not allowed: {duplicates}")
        return items