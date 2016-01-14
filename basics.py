"""
The MIT License (MIT)

Copyright (c) 2015 <Satyajit Sarangi>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from enum import Enum

class BranchFlowType(Enum):
    DIRECT = 0
    BREAK = 1
    CONTINUE = 2

class Branch:
    def __init__(self, condition, code=None):
        self.ancestor = None
        self.flow_type = None
        self.labeled = False
        self.condition = condition
        self.code = code

    def render(self, target, set_label):
        pass

class Block:
    id_counter = 0

    def __init__(self, name, code):
        self.branches_out = {}
        self.branches_in = {}
        self.processed_branches_out = {}
        self.processed_branches_in = {}
        self.name = name
        self.parent = None

        self.id = Block.id_counter
        Block.id_counter += 1

        self.code = code
        self.default_target = None

        self.is_checked_multiple_entry = False

    def add_branch_to(self, target, condition, code):
        assert target not in self.branches_out
        self.branches_out[target] = Branch(condition, code)

    def render(self, in_loop):
        pass

    def __str__(self):
        return "Block: <%s>" % self.name


class ShapeType(Enum):
    SIMPLE = 1
    MULTIPLE = 2
    LOOP = 3

class Shape:
    id_counter = 0

    def __init__(self, shp_type):
        self.id = Shape.id_counter
        Shape.id_counter += 1

        self.next_shape = None
        self.shape_type = shp_type

    def render(self, in_loop):
        pass


class SimpleShape(Shape):
    def __init__(self):
        Shape.__init__(self, ShapeType.SIMPLE)
        self.inner = None

    def render(self, in_loop):
        self.inner.render(in_loop)
        if self.next_shape:
            self.next_shape.render(in_loop)

class LabeledShape(Shape):
    def __init__(self, shp_type):
        Shape.__init__(self, shp_type)
        self.labeled = False

    def render(self, in_loop):
        pass


class LoopShape(LabeledShape):
    def __init__(self, shp_type):
        LabeledShape.__init__(self, ShapeType.LOOP)
        self.inner = None

    def render(self, in_loop):
        pass