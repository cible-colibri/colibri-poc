# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import json

# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class NonCyclycEncoder(json.JSONEncoder):

    def __init__(self, *args, **argv):
        super().__init__(*args, **argv)
        self.proc_objs = []

    def default(self, obj):
        if obj in self.proc_objs:
            # short circle the object dumping
            return obj.name
        self.proc_objs.append(obj)
        attr = obj.__dict__
        cls = type(obj).__name__
        # try:
        #     cls = obj.__class__
        # except:
        #     pass
        attr.update({'class': cls})
        return attr

# ========================================
# Functions
# ========================================
