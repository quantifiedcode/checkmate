# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import sys
import traceback
import os
import importlib
import yaml

from . import defaults

logger = logging.getLogger(__name__)
project_path = os.path.dirname(os.path.dirname(__file__))

from collections import defaultdict

class Settings(object):

    """
    Contains all relevant global settings:

    * Commands
    * Analyzers
    * Aggregators
    * Plugins
    * Language patterns
    * Models

    The global settings should not be confused with the project-specific
    settings, which contain e.g. specific configuration options for the
    individual analyzers.
    """

    def __init__(self,
                 commands=None,
                 analyzers=None,
                 aggregators=None,
                 plugins=None,
                 models=None,
                 hooks=None,
                 language_patterns=None):
        self.commands = commands if commands is not None else defaults.commands.copy()
        self.analyzers = analyzers if analyzers is not None else defaults.analyzers.copy()
        self.aggregators = aggregators if aggregators is not None else defaults.aggregators.copy()
        self.models = models if models is not None else defaults.models.copy()
        self.plugins = plugins if plugins is not None else defaults.plugins.copy()
        self.language_patterns = language_patterns if language_patterns is not None else defaults.language_patterns.copy()
        self.hooks = hooks if hooks is not None else defaults.hooks.copy()


    def update(self, settings):
        if settings is None:
            return
        for key in ('plugins','analyzers','aggregators','language_patterns','commands','models'):
            if key in settings:
                getattr(self,key).update(settings[key])

    def call_hooks(self,name,*args,**kwargs):
        if name in self.hooks:
            for hook in self.hooks[name]:
                hook(self,*args,**kwargs)

    def load(self, project_path=None):
        home = os.path.expanduser('~')
        possible_config_paths = [os.path.join(home),os.path.join(os.getcwd())]
        if project_path is not None:
            possible_config_paths.insert(0, project_path)
        for possible_config_path in possible_config_paths:
            possible_config_filename = os.path.join(possible_config_path,'.checkmate.yml')
            if os.path.exists(possible_config_filename) and os.path.isfile(possible_config_filename):
                with open(possible_config_filename,'r') as config_file:
                    return yaml.load(config_file.read())
        return None

    def load_plugin(self, module,name = None):
        logger.debug("Loading plugin: %s" % name)
        if hasattr(module,'analyzers'):
            self.analyzers.update(module.analyzers)
        if hasattr(module,'commands'):
            if name is None:
                raise AttributeError("You must specify a name for your plugin if you defined new commands!")
            self.commands.update({name : module.commands})
        if hasattr(module,'hooks'):
            for key,value in module.hooks.items():
                self.hooks[key].append(value)
        if hasattr(module,'models'):
            self.models.update(module.models)
        if hasattr(module,'top_level_commands'):
            self.commands.update(module.top_level_commands)

    def load_plugins(self, abort_on_error = False,verbose = False):
        for name,module_name in self.plugins.items():
            try:
                module = importlib.import_module(module_name+'.setup')
                self.load_plugin(module,name)
            except BaseException as e:
                logger.error("Cannot import plugin %s (module %s)" % (name,module_name))
                if verbose:
                    logger.error(traceback.format_exc())
                if abort_on_error:
                    raise
