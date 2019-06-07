// Copyright (c) Philipp Rudiger
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

import {Document} from "@bokehjs/document"
import {values} from "@bokehjs/core/util/object"
import {Receiver} from "@bokehjs/protocol/receiver"
import {_resolve_element, _resolve_root_elements} from "@bokehjs/embed/dom"
import {add_document_standalone} from "@bokehjs/embed/standalone"
import {Div, Slider, RadioButtonGroup, TextInput, Select} from "@bokehjs/models/widgets"
import {overrides} from "@bokehjs/base"

overrides["Div"] = Div as any
overrides["Slider"] = Slider as any
overrides["RadioButtonGroup"] = RadioButtonGroup as any
overrides["TextInput"] = TextInput as any
overrides["Select"] = Select as any

export
class BokehModel extends DOMWidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_name: BokehModel.model_name,
      _model_module: BokehModel.model_module,
      _model_module_version: BokehModel.model_module_version,
      _view_name: BokehModel.view_name,
      _view_module: BokehModel.view_module,
      _view_module_version: BokehModel.view_module_version,
      render_bundle: {}
    };
  }

  static serializers: ISerializers = {
      ...DOMWidgetModel.serializers,
      // Add any extra serializers here
    }

  static model_name = 'BokehModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'BokehView';   // Set to null if no view
  static view_module = MODULE_NAME;   // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export
class BokehView extends DOMWidgetView {
  private _document: Document | null
  private _receiver: Receiver
  private _blocked: boolean

  constructor(options?: any) {
    super(options);
    this._document = null;
    this._blocked = false;
    this._receiver = new Receiver();
    this.model.on('change:render_bundle', this.rerender, this);
    this.listenTo(this.model, 'msg:custom', (msg: any) => this._consume_patch(msg));
  }

  render() {
    this.rerender();
  }

  rerender() {
    const bundle = JSON.parse(this.model.get('render_bundle'));
    const {doc_json, render_items, div} = bundle
    this.el.innerHTML = div;
    const element = this.el.children[0];
    const json: any = values(doc_json)[0];
    this._document = Document.from_json(json)
    for (const item of render_items) {
      const roots: {[key: string]: HTMLElement} = {}
      for (const root_id in item.roots)
        roots[root_id] = element;
      add_document_standalone(this._document, element, roots)
    }
    this._document.on_change((event) => this._change_event(event))
  }

  _change_event(event: any) {
    if (!this._blocked)
      this.send({'event': 'jsevent', id: event.model.id, new: event.new_, attr: event.attr, old: event.old})
  }

  _consume_patch(content: any) {
    if (this._document === null)
      return
    if (content.msg == 'patch') {
      this._receiver.consume(content.payload)
      const comm_msg = this._receiver.message;
      if ((comm_msg != null) && (Object.keys(comm_msg.content).length > 0)) {
        this._blocked = true;
        this._document.apply_json_patch(comm_msg.content, comm_msg.buffers)
        this._blocked = false;
      }
    }
  }
}
