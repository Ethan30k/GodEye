#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from GodEyeClient.core import main

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

if __name__ == "__main__":
    client = main.command_handler(sys.argv)
