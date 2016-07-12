# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from base import BaseCommand

import sys

import code
"""
Opens a REPL
"""

class Command(BaseCommand):

    def run(self):
        return code.interact(local = {'backend' : self.backend,
                                      'project' : self.project,
                                      })
