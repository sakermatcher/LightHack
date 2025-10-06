# Import necessary modules for indicator rendering
from .texturing import multiply  # Import color multiplication utility
from pygame import surface, SRCALPHA  # Import pygame surface handling

# Generate list of number texture file paths (0.png through 10.png)
numbers= list(f"indicators/{i}.png" for i in range(11))

def indicatorRender(layer):
    """
    Custom renderer for numerical indicators that display values in cell corners.
    Used to show RGB values, potency settings, and other numerical data on cells.
    
    Args:
        layer: Dictionary containing textures, state, and renderer information
               state contains:
                 - corner: Position identifier ("UL", "UR", "DL", "DR")  
                 - color: RGB color tuple for number tinting
                 - number: Integer value to display (0-10)
                 
    Returns:
        40x40 surface with the colored number rendered in the specified corner
    """
    # Extract rendering state information
    state= layer["state"]
    corner= state["corner"]    # Corner position for number placement
    color= state["color"]      # RGB color to tint the number
    number= state["number"]    # Numerical value to display

    # Create transparent surface for rendering the indicator
    final = surface.Surface((40,40), SRCALPHA)

    # Determine pixel coordinates based on corner position
    match corner:
        case "UL":  # Upper Left corner
            blitAt= (6,5)
        case "UR":  # Upper Right corner
            blitAt= (30,5)
        case "DL":  # Down Left corner
            blitAt= (6,30)
        case "DR":  # Down Right corner
            blitAt= (30,30)

    # Render the number with color tinting and blit to the final surface
    # Uses the number as index to select appropriate digit texture (0-10)
    final.blit(multiply(layer["textures"][number], color), blitAt)
    return final