from PIL import Image
from StringIO import StringIO


class PngSerializer(object):
    @classmethod
    def load(cls, file_obj):
        return file_obj.read()

    @classmethod
    def dump(cls, obj, file_obj):
        img = Image.open(StringIO(obj))
        newImg = Image.new("RGBA", (img.width, img.width), (255, 255, 255, 0))
        offset = (img.width - img.height) / 2
        newImg.paste(img, (0, offset, img.width, img.height + offset))
        newImg.thumbnail((256, 256))
        newImg.save(file_obj, format="PNG")
        return True


class JpgSerializer(object):
    @classmethod
    def load(cls, file_obj):
        return file_obj.read()

    @classmethod
    def dump(cls, obj, file_obj):
        img = Image.open(StringIO(obj))
        img.thumbnail((256, 256))
        img.save(file_obj, format="JPG")
        return True
