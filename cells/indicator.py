from .texturing import multiply
from pygame import surface, SRCALPHA

numbers= list(f"indicators/{i}.png" for i in range(11))

def indicatorRender(layer):
    """
    corner= "UR"
    color= (int, int, int)
    number= int
    """
    state= layer["state"]
    corner= state["corner"]
    color= state["color"]
    number= state["number"]

    final = surface.Surface((40,40), SRCALPHA)

    match corner:
        case "UL":
            blitAt= (6,5)
        case "UR":
            blitAt= (30,5)
        case "DL":
            blitAt= (6,30)
        case "DR":
            blitAt= (30,30)

    final.blit(multiply(layer["textures"][number], color), blitAt)
    return final