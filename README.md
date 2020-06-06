# textixel - an image to ASCII tile converter



## Examples:

![Example](/examples/koudelka_txt.jpg)

![Example](/examples/rain_txt.jpg)

## About

This program creates a new image from an existing one
mapping small tiles from the original image to dinamically
generated tiles built from ascii letters.

The dynamic tiles work like an ad hoc dithering algorithm,
allowing a coarser representation of gray values.

The size of the tiles (and the "textyness" of the output image)
is controlled by the font size parameter. I recommend trying
font sizes 8 or 12 on relatively large image for good results.

I was inspired to use this approach after seeing some
implementations using pixel by pixel translation which
deforms the aspect ratio 

The examples directory have some interesting before and after images.

## Instalation 

First clone this repository locally.

Then install the requirements with the following command;

`pip install -r requirements.txt`

It is recommended to use a virtual environment.

## Running

This program runs as a command line script.

To run it, use the following command.

`python textixel.py [--show] [--fontsize FONTSIZE] <input image file> <output image file>`
