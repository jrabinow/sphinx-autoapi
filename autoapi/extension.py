# -*- coding: utf-8 -*-
"""
Sphinx Auto-API Top-level Extension.

This extension allows you to automagically generate API documentation from your project.
"""
import os
import shutil

from sphinx.util.console import darkgreen, bold
from sphinx.addnodes import toctree

from .mappers import DotNetSphinxMapper, PythonSphinxMapper, GoSphinxMapper, JavaScriptSphinxMapper

default_options = ['members', 'undoc-members', 'private-members', 'special-members']


def run_autoapi(app):
    """
    Load AutoAPI data from the filesystem.
    """

    if not app.config.autoapi_dir:
        print "You must configure an autodapi_dir setting."
        return

    app.env.autoapi_data = []

    mapping = {
        'python': PythonSphinxMapper,
        'dotnet': DotNetSphinxMapper,
        'go': GoSphinxMapper,
        'javascript': JavaScriptSphinxMapper,
    }

    domain = mapping[app.config.autoapi_type]
    domain_obj = domain(app, template_dir=app.config.autoapi_template_dir)

    app.info(bold('[AutoAPI] ') + darkgreen('Loading Data'))
    domain_obj.load(
        pattern=app.config.autoapi_file_pattern,
        dir=os.path.normpath(app.config.autoapi_dir),
        ignore=app.config.autoapi_ignore,
    )

    app.info(bold('[AutoAPI] ') + darkgreen('Mapping Data'))
    domain_obj.map(options=app.config.autoapi_options)

    app.info(bold('[AutoAPI] ') + darkgreen('Rendering Data'))
    domain_obj.output_rst(
        root=app.config.autoapi_root,
        # TODO: Better way to determine suffix?
        source_suffix=app.config.source_suffix[0],
    )


def build_finished(app, exception):
    if not app.config.autoapi_keep_files:
        if app.verbosity > 1:
            app.info(bold('[AutoAPI] ') + darkgreen('Cleaning generated .rst files'))
        shutil.rmtree(app.config.autoapi_root)


def doctree_read(app, doctree):
    all_docs = set()
    insert = True
    if app.env.docname == 'index':
        nodes = doctree.traverse(toctree)
        if not nodes:
            return
        for node in nodes:
            for entry in node['entries']:
                all_docs.add(entry[1])
        for doc in all_docs:
            if app.config.autoapi_root in doc:
                insert = False
        if insert and app.config.autoapi_add_toctree_entry:
            nodes[-1]['entries'].append(
                (None, u'%s/index' % app.config.autoapi_root)
            )
            nodes[-1]['includefiles'].append(u'%s/index' % app.config.autoapi_root)
            app.info(bold('[AutoAPI] ') + darkgreen('Adding AutoAPI TOCTree to index.rst'))


def setup(app):
    app.connect('builder-inited', run_autoapi)
    app.connect('build-finished', build_finished)
    app.connect('doctree-read', doctree_read)
    app.add_config_value('autoapi_type', 'python', 'html')
    app.add_config_value('autoapi_root', 'autoapi', 'html')
    app.add_config_value('autoapi_ignore', ['*migrations*'], 'html')
    app.add_config_value('autoapi_options', default_options, 'html')
    app.add_config_value('autoapi_file_pattern', '*', 'html')
    app.add_config_value('autoapi_dir', 'autoapi', 'html')
    app.add_config_value('autoapi_keep_files', False, 'html')
    app.add_config_value('autoapi_add_toctree_entry', True, 'html')
    app.add_config_value('autoapi_template_dir', [], 'html')
    app.add_stylesheet('autoapi.css')
