#  Copyright (c) 2019 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Digital filter objects

class AvgFilter(object):
    """ This is a simple averaging low pass filter.  'depth' is how large
        the buffer list is"""
    def __init__(self, depth):
        self.depth = depth
        self.buffer = [0.0] * depth
        self.bptr = 0

    def setValue(self, x):
        self.buffer[self.bptr] = x
        self.bptr += 1
        if self.bptr == self.depth: self.bptr = 0
        return sum(self.buffer) / self.depth
