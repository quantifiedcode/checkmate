# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from base import BaseCommand

from collections import defaultdict

import sys
import os
import random
import os.path
import copy
import json
import time
import pprint
import hashlib
import logging

logger = logging.getLogger(__name__)

from checkmate.lib.code import CodeEnvironment
from .analze import Command as AnalyzeCommand

class Command(AnalyzeCommand):

    """
    Continuously watches a project for changes and analyzes modified file revisions
    """
