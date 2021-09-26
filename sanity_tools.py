
# https://blender.stackexchange.com/questions/95304/get-hex-triplet-for-color-and-real-256-rgb-from-diffuse-color-using-python
def to_hex(c):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * pow(c, 1.0 / 2.4) - 0.055

    return hex(max(min(int(srgb * 255 + 0.5), 255), 0))

def toHex(r, g, b):
    rgb = [r, g, b]
    result = ""
    i = 0
    while i < 3:
        val = str(to_hex(rgb[i]))
        val = val[2:]
        if len(val) == 1:
            val += val
        result += val
        i += 1
    return result


num = 4280885528
c_bytes = num.to_bytes(4, 'little')

color_type = 'CImVector'

if color_type == 'CImVector':
    red = c_bytes[2]
    green = c_bytes[1]
    blue = c_bytes[0]
    alpha = c_bytes[3]

elif color_type == 'CArgb':
    red = c_bytes[0]
    green = c_bytes[1]
    blue = c_bytes[2]
    alpha = c_bytes[3]

print(num)
print(red, green, blue, alpha)
cvec = (float(red) / 255, float(green) / 255, float(blue) / 255, float(alpha) / 255)
hexcolor = toHex(cvec[0], cvec[1], cvec[2])

print(cvec)
print(hexcolor)
