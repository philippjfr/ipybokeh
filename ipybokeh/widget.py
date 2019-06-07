#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Philipp Rudiger.
# Distributed under the terms of the Modified BSD License.

"""
Defines a BokehWidget which renders bokeh models and performs
bi-directional syncing just like bokeh server.
"""

import json

from ipywidgets import DOMWidget

from bokeh.core.json_encoder import BokehJSONEncoder
from bokeh.embed.elements import div_for_render_item
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.models import LayoutDOM
from bokeh.plotting import Document
from bokeh.protocol import Protocol

from traitlets import Unicode, Dict
from ._frontend import module_name, module_version


def diff(doc, binary=True, events=None):
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    events = list(doc._held_events) if events is None else events
    if not events:
        return None
    msg = Protocol("1.0").create("PATCH-DOC", events, use_buffers=binary)
    doc._held_events = [e for e in doc._held_events if e not in events]
    return msg

def serialize_json(obj, _):
    return json.dumps(obj, cls=BokehJSONEncoder, allow_nan=False,
                      indent=None, separators=(',', ':'), sort_keys=True)

class BokehWidget(DOMWidget):
    """
    The BokehWidget wraps a bokeh model and syncs the model state
    bi-directionally.
    """
    _model_name = Unicode('BokehModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('BokehView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    render_bundle = Dict().tag(sync=True, to_json=serialize_json)

    def __init__(self, model=None, document=None, **kwargs):
        if isinstance(model, LayoutDOM):
            self.update_from_model(model, document)
        super(BokehWidget, self).__init__(**kwargs)
        self.on_msg(self._sync_model)

    @classmethod
    def _model_to_traits(cls, model, document=None):
        if document is None:
            document = Document()
            document.add_root(model)
        kwargs = {}
        (docs_json, [render_item]) = standalone_docs_json_and_render_items([model], True)
        kwargs['doc_json'] = docs_json
        kwargs['render_items'] = [render_item.to_json()]
        kwargs['div'] = div_for_render_item(render_item)
        return kwargs, document

    def update_from_model(self, model, document=None):
        self._model = model
        self.render_bundle, self._document = self._model_to_traits(model, document)
        self._document.hold()

    def _sync_model(self, _, content, buffers):
        if content.get('event', '') != 'jsevent':
            return
        new, old, attr = content['new'], content['old'], content['attr']
        submodel = self._model.select_one({'id': content['id']})
        try:
            setattr(submodel, attr, new)
        except:
            return
        for cb in submodel._callbacks.get(attr, []):
            cb(attr, old, new)

    def push(self, binary=True):
        msg = diff(self._document, binary=binary)
        if msg is None:
            return
        self.send({'msg': 'patch', 'payload': msg.header_json})
        self.send({'msg': 'patch', 'payload': msg.metadata_json})
        self.send({'msg': 'patch', 'payload': msg.content_json})
        for header, buff in msg.buffers:
            self.send({'msg': 'patch', 'payload': json.dumps(header)})
            self.send({'msg': 'patch', 'payload': buff})
