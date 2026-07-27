'''
Contains Pydantic models (data structures) needed for the application
'''
from pydantic import BaseModel, conint
from typing import Literal, Annotated
        
        
# Create Pydantic data model for JSON options received in HTTP body
class LightdarkHex(BaseModel):
    active: bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)] # Add 'Annotated' for typechecker acceptance

class LightdarkRgb(BaseModel):
    active: bool
    mode: Literal["lighten", "darken"]
    percent: Annotated[int, conint(ge=0, le=100)]

class ColorswapHex(BaseModel):
    active: bool
    order: Literal["r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"]

class ColorswapRgb(BaseModel):
    active: bool
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