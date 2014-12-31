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

    description = "Gets a project variable"

    def run(self):
        if len(self.raw_args) < 1:
            sys.stderr.write("Usage: props get [name]\n")
            return -1
        propname = self.raw_args[0]
        if not hasattr(self.project,'props'):
            self.project.props = {}
        if propname in self.project.props:
            print self.project.props[propname]
            return 0
        else:
            sys.stderr.write("Unknown property: %s\n" % propname)
            return -1
