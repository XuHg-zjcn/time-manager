#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2020 Xu Ruijun

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import time
from iv2 import Iv2
from ivtree2 import IvTree2

ivt = IvTree2([Iv2(1,4)])
ivt2 = IvTree2([Iv2(-1,2), Iv2(3,7)])
print(ivt & ivt2)
print(ivt | ivt2)
print(ivt + 2)

n = 10000
tree = IvTree2()
for i in range(n):
    tree.addi(i, i+0.5)
t0 = time.perf_counter()
_ = tree - IvTree2([Iv2(2, 100), Iv2(200, 300), Iv2(103, 130)])
t1 = time.perf_counter()
print((t1-t0)/n*1e6, 'us')
