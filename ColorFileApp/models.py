'''
Contains Pydantic models (data structures) used for data validation for
endpoing option data objects received
'''
from pydantic import (
    BaseModel, conint, Field, 
    ConfigDict, field_validator
)
from collections import Counter
from typing import Literal, Annotated, Union, get_args, Any
import re

# RegEx expresion for capturing key-value parameters in model member error message
# strings
REGEX_INNER_OBJECT= r"\w+\((.*)\)"

# Create Pydantic data model for JSON options received in HTTP body
#
# Pydantic model-friendly array lists for keynames
# == For color conversion options ==
CONVERT_KEYS_LITERAL = Literal[
    "hex_rgb", "hex_hsl", "name_hex", "name_rgb",
    "rgb_hsl", "rgb_hex", "hsl_hex", "hsl_rgb", 
    "hsl_hsv", "hsv_hsl", "hsv_hex", "hsv_rgb"
]

# == For color light/dark effect options ==
LIGHTDARK_KEYS_LITERAL = Literal[
    "lightdark_hex", "lightdark_rgb"
]

LIGHTDARK_PARAM_KEYS_LITERAL = Literal[ "mode", "percent" ]

LIGHTDARK_MODE_VALS_LITERAL = Literal[
    "lighten", "darken"
]

# == For color swap R/G/B options ==
COLORSWAP_KEYS_LITERAL = Literal[
    "colorswap_hex", "colorswap_rgb"
]

COLORSWAP_PARAM_KEYS_LITERAL = Literal["order"]

COLORSWAP_ORDER_VALS_LITERAL = Literal[
    "r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"
]

# Standard string lists (definitions) for use in non-model purposes
CONVERT_ALLOWED_KEY_NAMES = [
    "hex_rgb", "hex_hsl", "name_hex", "name_rgb",
    "rgb_hsl", "rgb_hex", "hsl_hex", "hsl_rgb",
    "hsl_hsv", "hsv_hsl", "hsv_hex", "hsv_rgb"
]

LIGHTDARK_ALLOWED_KEY_NAMES = [ "lightdark_hex", "lightdark_rgb" ]
LIGHTDARK_ALLOWED_PARAM_KEY_NAMES = [ "mode", "percent" ]
LIGHTDARK_ALLOWED_MODE_VALS = [ "lighten", "darken" ]

COLORSWAP_ALLOWED_KEY_NAMES = [ "colorswap_hex", "colorswap_rgb" ]
COLORSWAP_ALLOWED_PARAM_KEY_NAMES = [ "order" ]
COLORSWAP_ALLOWED_ORDER_VALS = [ "r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r" ]

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
# JSON array of objects shown above. I.e., the following is valid:
# {
#     "options": [
#         { "hex_rgb": true }, 
#         { "lightdark_hex": true, "mode": "lighten", "percent": 10 },
#         { "lightdark_rgb": true, "mode": "lighten", "percent": 10 },
#     ]
# }
# --- Shared base: frozen (hashable, compared by type + values), strict fields --
class ComponentBase(BaseModel):
    # Makes values non-mutable
    model_config = ConfigDict(frozen=True)
    
class OptionConvertHexRgb(ComponentBase):
    hex_rgb: bool   # hex to rgb conversion

class OptionConvertHexHsl(ComponentBase):
    hex_hsl: bool   # hex to hue, saturation, lightness conv.

class OptionConvertNameHex(ComponentBase):
    name_hex: bool  # name to hex conv.
    
class OptionConvertNameRgb(ComponentBase):
    name_rgb: bool  # name to rgb conv.

class OptionConvertRgbHsl(ComponentBase):
    rgb_hsl: bool   # rgb to HSL
    
class OptionConvertRgbHex(ComponentBase):
    rgb_hex: bool   # rgb to hex

class OptionConvertHslHex(ComponentBase):
    hsl_hex: bool   # hsl to hex
    
class OptionConvertHslRgb(ComponentBase):
    hsl_rgb: bool   # hsl to rgb
    
class OptionConvertHslHsv(ComponentBase):
    hsl_hsv: bool   # hsl to hue, saturation, value
    
class OptionConvertHsvHsl(ComponentBase):
    hsv_hsl: bool   # hsv to hsl

class OptionConvertHsvHex(ComponentBase):
    hsv_hex: bool   # hsv to hex
    
class OptionConvertHsvRgb(ComponentBase):
    hsv_rgb: bool   # hsv to rgb

class OptionColorswapHex(ComponentBase):
    colorswap_hex: bool # R/G/B colorswapping conv.
    order: COLORSWAP_ORDER_VALS_LITERAL # Defines list of acceptable strings/order values


class OptionColorswapRgb(ComponentBase):
    colorswap_rgb: bool
    order: COLORSWAP_ORDER_VALS_LITERAL

class OptionLightdarkHex(ComponentBase):
    lightdark_hex: bool # Lightness increase/decrease option
    mode: LIGHTDARK_MODE_VALS_LITERAL   # defines list of accept. modes
    percent: Annotated[int, conint(ge=0, le=100)] # Restricts to 0-100 integer range

class OptionLightdarkRgb(ComponentBase):
    lightdark_rgb: bool
    mode: LIGHTDARK_MODE_VALS_LITERAL
    percent: Annotated[int, conint(ge=0, le=100)]


# Custom parent model: builds a top level list which can contain all types of
# option objects. If one or more exists/is validated, the whole model is validated
# (Union[] validates one or more child classes)
AnyOption = Union[
    OptionConvertHexRgb, OptionConvertHexHsl, OptionConvertNameHex, OptionConvertNameRgb,
    OptionConvertRgbHsl, OptionConvertRgbHex, OptionConvertHslHex, OptionConvertHslRgb,
    OptionConvertHslHsv, OptionConvertHsvHsl, OptionConvertHsvHex, OptionConvertHsvRgb,
    OptionColorswapHex, OptionColorswapRgb, 
    OptionLightdarkHex, OptionLightdarkRgb
]

ALLOWED_KEYS: frozenset[str] = frozenset({
    *CONVERT_ALLOWED_KEY_NAMES,
    *LIGHTDARK_ALLOWED_KEY_NAMES,
    *LIGHTDARK_ALLOWED_PARAM_KEY_NAMES,
    *COLORSWAP_ALLOWED_KEY_NAMES,
    *COLORSWAP_ALLOWED_PARAM_KEY_NAMES
})


# Parent wrapper "list type": assigns key "options" to the parent model and creates a list
# containing one or more child models. An enmpty input list from the API endpoint
# is not validated.
#
# I.e.: "options": [... ]
class PayloadWrapperListType(BaseModel):
    # Uses annotation declarations to require a min. of 1 member object of any type
    options: Annotated[list[AnyOption], Field(min_length=1)]
    
    # 1) BEFORE parsing: validate raw input key names against the predefined list
    @field_validator("options", mode="before")
    @classmethod
    # Gather all keys across all data members received; for 1 or more bad key names,
    # raise a single error and build the error response messaging
    def validate_key_names(cls, raw: Any) -> Any:
        # Ensure the raw data is a list; if not, return it
        if not isinstance(raw, list):
            return raw # let Pydantic report the wrong type        

        problems = []
        # Enumerate supplies the pos. of each item; iterate and for ech item 
        # which is raw data (dict) and not a model instance, verify the keys are
        # a member of allowed keys
        for index, item in enumerate(raw):
            if isinstance(item, dict):
                # For raw object, use keys (from set() "-" operator
                # to find any remaining unknown keys in item
                unknown = sorted(set(item) - ALLOWED_KEYS)
                if unknown: # If true (containes bad key(s) ), save it
                    problems.append(f"item {index}: {unknown}")
                    
        # If problems list is non-empty, raise error with all bad keys contained
        if problems:
            raise ValueError(
                f"unknown key names {'; '.join(problems)}"
                # f"Allowed: {sorted(ALLOWED_KEYS)}"
            )
        return raw
    
    # 2) AFTER parsing: reject identical member objects 
    @field_validator("options", mode="after")
    @classmethod
    def no_duplicate_keys(cls, items: list) -> list:
        counts = Counter(items)
        duplicates = [repr(item) for item, n in counts.items() if n > 1]
        if duplicates:
            obj_members = []
            for each in duplicates:
                # RegEx use to capture all inside the '()' chars.
                match = re.search(REGEX_INNER_OBJECT, each)
                obj_members.append('{' + f'{match.group(1)}' + '}')
            raise ValueError(f'duplicate key-value objects not allowed: {obj_members}')
        return items


# Parent wrapper "object type": replicates the original legacy incoming data structure
# I.e.: "options": { {"hex_rgb": true }, {"lightdark_hex": true, "mode": "lighten",
#   "percent": 50 }
# ...etc..
# }
# Does not validated if any member is missing
# I.e.: "options": [... ]
# class PayloadWrapperObjectType(BaseModel):
#     # Uses annotation declarations to require a min. of 1 member object of any type
#     options: AnyOption
    
#     # 1) BEFORE parsing: validate raw input key names against the predefined list
#     @field_validator("options", mode="before")
#     @classmethod
#     # Gather all keys across all data members received; for 1 or more bad key names,
#     # raise a single error and build the error response messaging
#     def validate_key_names(cls, raw: Any) -> Any:
#         # Ensure the raw data is a list; if not, return it
#         if not isinstance(raw, list):
#             return raw # let Pydantic report the wrong type        

#         problems = []
#         # Enumerate supplies the pos. of each item; iterate and for ech item 
#         # which is raw data (dict) and not a model instance, verify the keys are
#         # a member of allowed keys
#         for index, item in enumerate(raw):
#             if isinstance(item, dict):
#                 # For raw object, use keys (from set() "-" operator
#                 # to find any remaining unknown keys in item
#                 unknown = sorted(set(item) - ALLOWED_KEYS)
#                 if unknown: # If true (containes bad key(s) ), save it
#                     problems.append(f"item {index}: {unknown}")
                    
#         # If problems list is non-empty, raise error with all bad keys contained
#         if problems:
#             raise ValueError(
#                 f"unknown key names {'; '.join(problems)}"
#                 # f"Allowed: {sorted(ALLOWED_KEYS)}"
#             )
#         return raw