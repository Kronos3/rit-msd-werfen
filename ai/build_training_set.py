#!/usr/bin/env python3

from optparse import OptionParser
from typing import Set
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from pathlib import Path


def permute(characters: Set[str], length: int, count: int, seed=0):
    """
    :param characters: set of characters to generate permutations for
    :param length: length of each permutation instance
    :param count: number of permutations to generate (randomly selected from set)
    :param seed: seed for randomly selected permutations
    """

    characters_np = np.array(list(characters))

    np.random.seed(seed)
    out_set: Set[str] = set()
    for i in range(count):
        while True:
            t = np.random.choice(characters_np, size=length, replace=True)
            text = "".join(t)
            if text not in out_set:
                out_set.add(text)
                yield i, text
                break


def main():
    parser = OptionParser()
    parser.add_option("-n", "--count", dest="count", type="int",
                      default=2000,
                      help="Number of training points")
    parser.add_option("-l", "--length", dest="length", type="int",
                      default=5,
                      help="Number of characters per image")
    parser.add_option("-o", "--output", dest="output",
                      help="Output directory of training set", default=".")
    parser.add_option("-c", "--characters", dest="characters",
                      help="Character set to permute through",
                      default="0123456789")
    parser.add_option("-s", "--font-size", dest="font_size", type="int",
                      default=20, help="Font size in pixels")
    parser.add_option("-f", "--font", dest="font", type="str",
                      help="Font size in pixels")
    parser.add_option("--prefix", dest="prefix", default="training",
                      help="Filename prefix for training data")
    parser.add_option("--type", type="choice", choices=("png", "tif"),
                      default="tif",
                      help="Generate either 'tif' or 'png' (Default: tif)")

    (options, args) = parser.parse_args()

    font = ImageFont.truetype(options.font, size=options.font_size)

    output_path = Path(options.output)
    output_path.mkdir(parents=True, exist_ok=True)

    width = options.font_size * options.length + 20
    height = options.font_size + 4

    for i, text in permute(set(options.characters), options.length, options.count):
        img_file = output_path / f'{options.prefix}_{i}.{options.type}'
        txt_file = output_path / f'{options.prefix}_{i}.gt.txt'
        img = Image.new('L', (width, height), color='white')
        img_draw = ImageDraw.Draw(img)
        img_draw.text((0, 0), text, font=font)

        img.save(str(img_file))
        with txt_file.open('w+') as f:
            f.write(text)

    return 0


if __name__ == "__main__":
    exit(main())
