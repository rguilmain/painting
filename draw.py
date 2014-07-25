"""http://codegolf.stackexchange.com/questions/22144/images-with-all-colors.
"""

from __future__ import division
from PIL import Image

import argparse
import math
import multiprocessing
import random
import sys
import time


class Color(object):

  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b


class Point(object):

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.color = None


class Picture(object):

  def __init__(self, x_size, y_size):
    self.x_size = x_size
    self.y_size = y_size
    self.image = Image.new("RGB", (self.x_size, self.y_size))
    self.pixels = self.image.load()
    self.points = []
    for x in range(self.x_size):
      column = []
      for y in range(self.y_size):
        column.append(Point(x, y))
      self.points.append(column)

  def get_point(self, x, y):
    return self.points[x][y]

  def paint(self, point, color):
    self.pixels[point.x, point.y] = (color.r, color.g, color.b)
    point.color = color

  def save(self):
    self.image.save(time.strftime("%Y%m%d%H%M%S") + ".png")

  def show(self):
    self.image.show()


def get_neighbors(point, picture):
  for x in (point.x - 1, point.x, point.x + 1):
    for y in (point.y - 1, point.y, point.y + 1):
      if x == point.x and y == point.y:
        continue
      if x < 0 or x >= picture.x_size or y < 0 or y >= picture.y_size:
        continue
      yield picture.get_point(x, y)


def get_colors(num_colors):
  colors = []
  num_partitions = int(num_colors**(1 / 3)) + 1
  for r in range(num_partitions):
    for g in range(num_partitions):
      for b in range(num_partitions):
        colors.append(Color(int(r * 255 / (num_partitions - 1)),
                            int(g * 255 / (num_partitions - 1)),
                            int(b * 255 / (num_partitions - 1))))
  random.shuffle(colors)
  return colors


def error(color1, color2):
  dr = color1.r - color2.r
  dg = color1.g - color2.g
  db = color1.b - color2.b
  return dr * dr + dg * dg + db * db


def get_best_point(points, color, picture):
  best_point = None
  min_difference = sys.maxint
  for point in points:
    for neighbor in get_neighbors(point, picture):
      if not neighbor.color:
        continue
      difference = error(color, neighbor.color)
      if difference < min_difference:
        best_point = point
        min_difference = difference
  return best_point


def main(argv=None):
  if argv is not None:
    sys.argv = argv

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("-x", "--x-size", default=100, type=int,
                      help="x dimension")
  parser.add_argument("-y", "--y-size", default=50, type=int,
                      help="y dimension")
  parser.add_argument("-n", "--num-starbursts", default=1, type=int,
                      help="number of starbursts to grow")
  args = parser.parse_args()

  start_time = time.time()
  picture = Picture(args.x_size, args.y_size)
  num_pixels = picture.x_size * picture.y_size
  colors = get_colors(num_pixels)

  starting_points = set()
  for starburst in range(args.num_starbursts):
    starting_points.add(picture.get_point(
      random.randint(0, picture.x_size - 1),
      random.randint(0, picture.y_size - 1)))

  available_points = set()
  for starting_point in starting_points:
    picture.paint(starting_point, colors.pop())
    for neighbor in get_neighbors(starting_point, picture):
      available_points.add(neighbor)

  num_pixels_drawn = len(starting_points)
  while available_points:
    color = colors.pop()
    best_point = get_best_point(available_points, color, picture)
    picture.paint(best_point, color)
    num_pixels_drawn += 1
    sys.stdout.flush()
    sys.stdout.write("\r%.2f%% complete" %
                     (100 * num_pixels_drawn / num_pixels))
    available_points.remove(best_point)
    for neighbor in get_neighbors(best_point, picture):
      if not neighbor.color:
        available_points.add(neighbor)

  print "\nTotal running time: {} seconds.".format(time.time() - start_time)
  if num_pixels >= 100000:
    picture.save()
  picture.show()


if __name__ == "__main__":
  sys.exit(main())
