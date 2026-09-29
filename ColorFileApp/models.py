'''
Contains Pydantic models (data structures) needed for the application
'''
from pydantic import BaseModel, conint, RootModel
from typing import Literal, Annotated, List, Dict, Any
        
        
# Create Pydantic data model for JSON options received in HTTP body

# 29-SEP-2026: Updated models below as "active" key is no longer used (lightdark_XXX &
# colorswap_XXX objects are now consolidated/simplified).
class LightdarkHex(BaseModel):
    bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)] # Add 'Annotated' for typechecker acceptance

class LightdarkRgb(BaseModel):
    bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)]

class ColorswapHex(BaseModel):
    bool
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

    # lightdark_hex: LightdarkHex
    # lightdark_rgb: LightdarkRgb
    # colorswap_hex: ColorswapHex
    # colorswap_rgb: ColorswapRgb
    
# Define a model for each individual object containing a single key-value pair
class PayloadWrapper(BaseModel):
    options: list[dict[str, bool]]
    
