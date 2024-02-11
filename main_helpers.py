"""
Function: list2string
@param ls: list
@param sep: separator(inserted between values)

@Return(str): string representation of the list
"""

def list2string(ls, sep=" "):
    out = ""
    for i in range(len(ls)):
        out += str(ls[i])
        if i < len(ls) - 1:
            out += sep
    return out
