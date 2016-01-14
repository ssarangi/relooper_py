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

from basics import *
from validator import *

class RelooperRecursor:
    def __init__(self, parent):
        self.parent = parent

class PreOptimizer(RelooperRecursor):
    def __init__(self, parent):
        RelooperRecursor.__init__(self, parent)
        self.live_blocks = set()

    @verify(curr_block=Block)
    def find_live(self, curr_block):
        if curr_block in self.live_blocks:
            return

        self.live_blocks.add(curr_block)

        for successor in curr_block.branches_out:
            self.find_live(successor)


class Analyzer(RelooperRecursor):
    def __init__(self, parent):
        RelooperRecursor.__init__(self, parent)

    def notice(self, new_shape):
        self.parent.shapes.append(new_shape)

    def get_blocks_out(self, blk_src):
        entries = set()
        for successor in blk_src.branches_out:
            entries.add(successor)

        return entries

    # Converts / processes all branchings to a specific target
    def solipsize(self, target, branch_flow_type, ancestor_shape, from_blocks):
        erase_blks = []
        for pred, branch in target.branches_in.items():
            if pred in from_blocks:
                continue

            target_in = branch
            prior_out = pred.branches_out[target]
            prior_out.ancestor = ancestor_shape
            prior_out.flow_type = branch_flow_type

            erase_blks.append(pred)
            target.processed_branches_in[pred] = target_in
            del pred.branches_out[target]
            pred.processed_branches_out[target] = prior_out

        for blk in erase_blks:
            del target.branches_in[blk]

    def make_simple(self, blocks, inner_blk):
        next_entries = None
        simple_shp = SimpleShape()
        self.notice(simple_shp)
        simple_shp.inner = inner_blk
        inner_blk.parent = simple_shp

        if len(blocks) > 1:
            blocks.remove(inner_blk)
            next_entries = self.get_blocks_out(inner_blk)
            just_inner = {}

            for blk in next_entries:
                self.solipsize(blk, BranchFlowType.DIRECT, simple_shp, just_inner)

        return simple_shp, next_entries

    def make_loop(self, blocks, entries):
        next_entries = None
        inner_blocks = set()
        queue = list(set(entries))

        while len(queue) > 0:
            curr = queue[0]
            queue.remove(curr)

            if curr in inner_blocks:
                inner_blocks.add(curr)
                blocks.remove(curr)

                for pred in curr.branches_in.keys():
                    queue.append(pred)
                    queue = list(set(queue))

        assert len(inner_blocks) > 0

        for curr in inner_blocks:
            for succ in curr.branches_out.keys():
                if succ not in inner_blocks:
                    next_entries.add(succ)

        loop = LoopShape()
        self.notice(loop)

        # Solipsize the loop, replacing with break/continue and marking branches as processed (will not affect later calculations)
        # A. branches to the loop entries become to a continue to this shape.
        for entry in entries:
            self.solipsize(entry, BranchFlowType.CONTINUE, loop, inner_blocks)

        # B. Branches to outside the loop (a next entry) become breaks on this shape
        for next_entry in next_entries:
            self.solipsize(next_entry, BranchFlowType.BREAK, loop, inner_blocks)

        # Finish Up
        inner_shape = self.process(inner_blocks, entries, None)
        loop.inner = inner_shape
        return loop, next_entries

    def process(self, blocks, initial_entries, prev_shape):
        curr_tmp_idx = 0

        entries = initial_entries

        temp_entries = [[], []]
        ret_shp = None

        while True:
            curr_tmp_idx = 1 - curr_tmp_idx
            next_entries = temp_entries[curr_tmp_idx]
            next_entries.clear()

            if len(entries) == 0:
                return None

            if len(entries) == 1:
                curr = entries[0]
                if len(curr.branches_in) == 0:
                    shp, next_entries = self.make_simple(blocks, curr)
                    temp = shp
                    if prev_shape is not None:
                        prev_shape.next_shape = temp
                    if ret_shp is None:
                        ret_shp = temp

                    if len(next_entries) == 0:
                        return ret_shp

                    prev_shape = temp
                    entries = next_entries
                    continue

                # One entry, looping ==> Loop
                loop_shp, next_entries = self.make_loop(blocks, entries)
                temp = loop_shp
                if prev_shape is not None:
                    prev_shape.next_shape = temp
                if ret_shp is not None:
                    ret_shp = temp

                if len(next_entries) == 0:
                    return ret_shp

                prev_shape = temp
                entries = next_entries
                continue


            # One entry, looping ==> Loop
            loop_shp, next_entries = self.make_loop(blocks, entries)
            temp = loop_shp
            if prev_shape is not None:
                prev_shape.next_shape = temp
            if ret_shp is not None:
                ret_shp = temp

            if len(next_entries) == 0:
                return ret_shp

            prev_shape = temp
            entries = next_entries
            continue


class Relooper:
    def __init__(self):
        self.blocks = []
        self.shapes = []
        self.root = None

    def add_block(self, block):
        self.blocks.append(block)

    def render(self):
        self.root.render()

    def calculate(self, entry_block):
        pre_opt = PreOptimizer(self)
        pre_opt.find_live(entry_block)

        # Add incoming branches from live blocks, ignoring dead code
        for curr_blk in self.blocks:
            if curr_blk not in pre_opt.live_blocks:
                continue

            for successor in curr_blk.branches_out:
                successor.branches_in[curr_blk] = Branch(None)

        # Do the split dead ends optimization

        # Recursively process the graph
        all_blocks = set()
        for curr_block in self.blocks:
            all_blocks.add(curr_block)

        entries = set()
        entries.add(entry_block)

        analyzer = Analyzer(self)
        self.root = analyzer.process(all_blocks, list(entries), None)
        a = 10

def main():
    b_a = Block("A", "// Block A\n")
    b_b = Block("B", "// Block B\n")
    b_c = Block("C", "// Block C\n")

    b_a.add_branch_to(b_b, "check == 10", "atob()")
    b_a.add_branch_to(b_c, None, "atoc()")

    b_b.add_branch_to(b_c, None, "btoc()")

    r = Relooper()
    r.add_block(b_a)
    r.add_block(b_b)
    r.add_block(b_c)

    r.calculate(b_a)
    r.render()

if __name__ == "__main__":
    main()