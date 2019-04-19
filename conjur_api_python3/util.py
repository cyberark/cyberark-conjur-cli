# -*- coding: utf-8 -*-

"""
Util module

This module contains any non-specific helpers that we may use
"""

import ast
import inspect

# Introspect the API module and figure out what methods are a pass-through
def get_api_methods(target):
    """
    This method is used to return a map of all 'client_api_method'-decorated
    methods in the target class. Currently this method is not generic but it
    probably should be in the future as it's rather useful.
    """

    api_methods = {}

    def visit_function_def(node):
        for decorator in node.decorator_list:
            name = None
            if isinstance(decorator, ast.Call):
                #pylint: disable=line-too-long
                name = decorator.func.attr if isinstance(decorator.func, ast.Attribute) else decorator.func.id
            else:
                name = decorator.attr if isinstance(decorator, ast.Attribute) else decorator.id

            if name == 'client_api_method':
                mapped_name = node.name
                if hasattr(decorator, 'args'):
                    mapped_name = decorator.args[0].s

                api_methods[mapped_name] = {'matching_method_name': node.name,
                                            'args': node.args}

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_function_def
    node_iter.visit(ast.parse(inspect.getsource(target)))
    return api_methods
