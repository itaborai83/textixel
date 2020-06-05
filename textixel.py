import os
import random
import argparse
import statistics as stats
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat, ImageFilter

class Tile():
    
    def __init__(self, char, width, height, font, use_alternates, inverse):
        self.char = char
        self.width = width
        self.height = height
        self.font = font
        self.use_alternates = use_alternates
        self.inverse = inverse
        self.img = None
        self.black_count = 0
        self.min_color = None
        self.max_color = None
        self.alternates = [self]
        
    def init(self):
        if not self.inverse:
            self.img = Image.new(mode="1", size=(self.width, self.height), color=1)
        else:
            self.img = Image.new(mode="1", size=(self.width, self.height), color=0)
        d = ImageDraw.Draw(self.img)
        if not self.inverse:
            d.text((0,0), self.char, font=self.font, fill=0)
        else:
            d.text((0,0), self.char, font=self.font, fill=1)
        for x in range(self.width):
            for y in range(self.height):
                pixel = self.img.getpixel((x, y))
                if pixel == 0:
                    self.black_count += 1
    
    def __lt__(self, other):
        if self.black_count < other.black_count:
            return True
        elif self.black_count == other.black_count:
            return self.inverse < other.inverse
        else:
            return False
            
    def pick(self):
        if self.use_alternates:
            return random.sample(self.alternates, 1)[ 0 ]
        else:
            return self
        
class TileSet():
    
    CHARS = r""" '1234567890-="!@#$%&*()_+qwertyuiop[QWERTYUIOP`{asdfghjkl~]ASDFGHJKL^}\zxcvbnm,.;/|ZXCVBNM<>:?"""
    FONT_NAME = "FreeMono.ttf" # https://github.com/python-pillow/Pillow/blob/master/Tests/fonts/FreeMono.ttf
    
    def __init__(self, fontsize, use_alternates):
        self.fontsize = fontsize
        self.use_alternates = use_alternates
        self.tiles = []
        self.color_indexes = []
        self.colors = [ None ] * 256
        
    def init(self):
        font = ImageFont.truetype(self.FONT_NAME, size=self.fontsize)
        width, height = self._get_char_dimensions(font)
        self._build_tiles(font, width, height)
        self._build_color_map()
        #for tile in self.tiles:
        #    print(tile.char, tile.black_count, tile.min_color, tile.max_color)
        return width, height
    
    def _get_char_dimensions(self, font):
        ws = []
        hs = []
        for c in self.CHARS:
            w, h = font.getsize(c)
            ws.append(w)
            hs.append(h)
        width = max(ws)
        height = max(hs)
        return width, height
    
    def _build_tiles(self, font, width, height):   
        self.tiles = []
        tmp_tiles = []
        for ch in self.CHARS:
            t = Tile(ch, width, height, font, self.use_alternates, inverse=False)
            t.init()
            tmp_tiles.append(t)
            t = Tile(ch, width, height, font, self.use_alternates, inverse=True)
            t.init()
            tmp_tiles.append(t)
        # cull tiles
        tmp_tiles.sort()
        last_black_count = -1
        new_tiles = []
        for tile in tmp_tiles:
            if tile.black_count != last_black_count:
                self.tiles.append(tile)
            else:
                self.tiles[ -1 ].alternates.append(tile)
            last_black_count = tile.black_count
    
    def _build_color_map(self):
        tile_count = len(self.tiles)
        for color in range(256):
            idx = int((color / 256) * tile_count)
            tile = self.tiles[ idx ]
            if tile.min_color is None:
                tile.min_color = color
                tile.max_color = color
            else:
                tile.max_color = color
            self.colors[ color ] = tile
    
    def color_count(self):
        return len(self.tiles)
    
    def translate_tile(self, input_tile):
        color = round(ImageStat.Stat(input_tile).median[ 0 ])
        #color = round(ImageStat.Stat(input_tile).mean[ 0 ])
        
        return self.colors[ 255 - color ].pick()
    
class App():
    
    CHAR_ASPECT_RATIO = 0.5 # width / height
    
    def __init__(self, alternates, show, fontsize, input_, output):
        self.show = show
        self.fontsize = fontsize
        self.input = input_
        self.output = output
        self.tile_set = TileSet(fontsize, alternates)
        
    def process_image(self, img, tile_width, tile_height):
        # crop image
        img_width, img_height = img.size
        new_width = (img_width // tile_width) * tile_width
        new_height = (img_height // tile_height) * tile_height
        crop_box = (0, 0, new_width, new_height)
        img = img.crop(crop_box)
        img = img.convert(mode="L")
        #img.show()
        img = img.filter(ImageFilter.UnsharpMask())
        #img.show()
        #img = ImageOps.equalize(img)
        #img.show()        
        return img
            
    def build_new_image(self, img):
        return Image.new("L", img.size, 255)
    
    def run(self):
        tile_width, tile_height = self.tile_set.init()
        img = Image.open(self.input)
        processed_img = self.process_image(img, tile_width, tile_height)
        output_image = self.build_new_image(processed_img)
       
        num_lines = output_image.size[ 0 ] // tile_width
        num_columns = output_image.size[ 1 ] // tile_height
        for j in range(num_columns):
            for i in range(num_lines):
                x1 = i * tile_width
                y1 = j * tile_height
                x2 = (i * tile_width) + tile_width
                y2 = (j * tile_height) + tile_height
                crop_box = (x1, y1, x2, y2)
                input_tile = processed_img.crop(crop_box)
                output_tile = self.tile_set.translate_tile(input_tile)
                output_image.paste(output_tile.img, crop_box)
        output_image.save(self.output)
        if self.show:
            output_image.show()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alternates', action="store_true", help='use alternate tiles for the same gray value')
    parser.add_argument('--show', action="store_true", help='show image')
    parser.add_argument('--fontsize', type=int, default=12, help='font size to use')
    parser.add_argument('input', type=str, help='input image file name')
    parser.add_argument('output', type=str, help='output image file name')
    args = parser.parse_args()
    app = App(args.alternates, args.show, args.fontsize, args.input, args.output)
    app.run()
    
