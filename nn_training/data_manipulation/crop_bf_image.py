from PIL import Image
import sys

path = sys.argv[1]

image = Image.open(path)
w, h = image.size
print(w,h)
image = image.crop((280, 120, w, h))
image.thumbnail((150,150))
image.save(path)