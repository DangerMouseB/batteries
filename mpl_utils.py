#*******************************************************************************
#
#    Copyright (c) 2017-2019 David Briant
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#*******************************************************************************


import numpy as np

def AsSteps(xs, ys, align='center', width=None):
    #xMin, xMax = min(xs), max(xs)
    if width is None:
        width = np.diff(xs).min()
    points = []
    lastx = np.nan
    lasty = np.nan
    for x, y in zip(xs, ys):
        if (x - lastx) > 1e-5:
            points.append((lastx, 0))
            points.append((x, 0))
        if not np.isnan(lasty):
            points.append((x, lasty))
        points.append((x, y))
        points.append((x + width, y))
        lastx = x + width
        lasty = y
    points.append((lastx, lasty))
    pxs, pys = zip(*points)
    if align == 'center':
        pxs = np.array(pxs) - width / 2.0
    elif align == 'right':
        pxs = np.array(pxs) - width
    return pxs, np.array(pys)
