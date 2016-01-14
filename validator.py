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

__author__ = 'sarangis'

# Code from http://typeandflow.blogspot.com/2011/06/python-decorator-with-optional-keyword.html
# Very well explained
class U:
    def __init__(self, *args):
        self.types = args

    def __str__(self):
        return ",".join(self.types)

    __repr__ = __str__

def verify(func=None, **options):
    if func is not None:
        # We received the function on this call, so we can define
        # and return the inner function
        def inner(*args, **kwargs):
            if len(options) == 0:
                raise Exception("Expected verification arguments")

            func_code = func.__code__
            arg_names = func_code.co_varnames

            for k, v in options.items():
                # Find the key in the original function
                idx = arg_names.index(k)

                if (len(args) > idx):
                    # get the idx'th arg
                    arg = args[idx]
                else:
                    # Find in the keyword args
                    if k in kwargs:
                        arg = kwargs.get(k)

                if isinstance(v, U):
                    # Unroll the types to check for multiple types
                    types_match = False
                    for dtype in v.types:
                        if isinstance(arg, dtype):
                            types_match = True

                    if types_match == False:
                        raise Exception("Expected " + str(k) + " to be of type: " + str(v) + " but received type: " + str(type(arg)))
                elif not isinstance(arg, v):
                    raise Exception("Expected " + str(k) + " to be of type: " + v.__name__ + " but received type: " + str(type(arg)))

            output = func(*args, **kwargs)
            return output

        return inner
    else:
        # We didn't receive the function on this call, so the return value
        # of this call will receive it, and we're getting the options now.
        def partial_inner(func):
            return verify(func, **options)
        return partial_inner


class Validator:
    def validate(self):
        raise NotImplementedError("Validation method has to be implemented")