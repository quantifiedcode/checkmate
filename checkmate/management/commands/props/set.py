# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from checkmate.management.commands.base import BaseCommand
from checkmate.management.helpers import save_project_config

import sys
import os
import os.path
import json
import time
import uuid

class Command(BaseCommand):

    description = "Sets a project variable"

    def run(self):
        if len(self.raw_args) < 2:
            sys.stderr.write("Usage: props set [name] [value]\n")
            return -1
        propname = self.raw_args[0]
        propvalue = self.raw_args[1]
        if not hasattr(self.project,'props'):
            self.project.props = {}
        self.project.props[propname] = propvalue
        self.backend.save(self.project)
        self.backend.commit()
        return 0
