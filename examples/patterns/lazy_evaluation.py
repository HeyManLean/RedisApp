# -*- coding: utf-8 -*-
"""
懒加载模式
- property 默认是都会执行被装饰的方法, 返回值
- 这个模式是, 当使用这个属性, 才执行被装饰的方法, 并缓存(只执行一次)
"""
import functools


functools.update_wrapper()