#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Philipp Rudiger.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..example import ExampleWidget


def test_bokeh_widget_creation_blank():
    w = BokehWidget()
    assert w.render_bundle == {}
