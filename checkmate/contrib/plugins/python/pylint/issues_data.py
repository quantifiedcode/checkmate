# -*- coding: utf-8 -*-
from __future__ import unicode_literals

issues_data = {
    "C0202" : {
        "title" : "class method should have 'cls' as first argument",
        "description" :"%(issue.data.description)s",
        "categories" : ["maintainability","readability"],
        "severity" : 3
    },
    "C0203" : {
        "title" : "metaclass method should have 'mcs' as first argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["maintainability","readability"],
        "severity" : 3
    },
    "C0321" : {
        "title" : "more than one statement per line",
        "description" : "%(issue.data.description)",
        "categories" : ["maintainability","readability"],
        "severity" : 3
    },
    "R0201" : {
        "title" : "method could be a function",
        "description" : "%(issue.data.description)",
        "categories" : ["maintainability"],
        "severity" : 4
    },
    "E0100" : {
        "title" : "__init__ is a generator",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0101" : {
        "title" : "explicit return in __init__",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "E0104" : {
        "title" : "return outside of function",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0105" : {
        "title" : "yield outside of function",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0106" : {
        "title" : "return with argument inside generator",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0107" : {
        "title" : "use of non-existent operator",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0109" : {
        "title" : "duplicate argument name",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0202" : {
        "title" : "hidden attribute",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0203" : {
        "title" : "access before definition",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0211" : {
        "title" : "method without argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0213" : {
        "title" : "method should have 'self' as first argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0235" : {
        "title" : "__exit__ must accept 3 arguments",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0702" : {
        "title" : "illegal value raised",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0711" : {
        "title" : "NotImplemented raised",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1004" : {
        "title" : "missing arguments to 'super'",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1111" : {
        "title" : "assigning to function call that doesn't return",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1121" : {
        "title" : "too many arguments",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1123" : {
        "title" : "unexpected keyword argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1124" : {
        "title" : "parameter passed as position and keyword argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1200" : {
        "title" : "unsupported logging format character",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1201" : {
        "title" : "invalid logging format string",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1205" : {
        "title" : "too many arguments for logging format string",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1206" : {
        "title" : "not enough arguments for logging format string",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1303" : {
        "title" : "expected mapping for format string",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1305" : {
        "title" : "too many arguments for format string",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1306" : {
        "title" : "not enough arguments for format string",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "W0101" : {
        "title" : "unreachable code",
        "description" : "",
        "categories" : ["maintainability","correctness"],
        "severity" : 2
    },
    "W0102" : {
        "title" : "dangerous default value as argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["maintainability","correctness"],
        "severity" : 2
    },
    "W0104" : {
        "title" : "statement seems to have no effect",
        "description" : "",
        "categories" : ["maintainability","correctness"],
        "severity" : 2
    },
    "W0106" : {
        "title" : "expression without assignment",
        "description" : "%(issue.data.description)s",
        "categories" : ["maintainability","correctness"],
        "severity" : 2
    },
    "W0107" : {
        "title" : "unnecessary pass statement",
        "description" : "",
        "categories" : ["maintainability","correctness"],
        "severity" : 3
    },
    "W0108" : {
        "title" : "lambda might not be necessary",
        "description" : "",
        "categories" : ["readability"],
        "severity" : 3
    },
    "W0109" : {
        "title" : "duplicate key in dictionary",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0110" : {
        "title" : "map/filter could be replaced by list comprehension",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 3
    },
    "W0122" : {
        "title" : "use of exec",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness","security"],
        "severity" : 2
    },
    "W0150" : {
        "title" : "'finally' may swallow exception",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0211" : {
        "title" : "static method with self/cls as first argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0231" : {
        "title" : "init method from base class not called",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0234" : {
        "title" : "iter returns non-iterator",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0410" : {
        "title" : "__future__ not first in module",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "W0603" : {
        "title" : "use of 'global'",
        "description" : "%(issue.data.description)s",
        "categories" : ["maintainability"],
        "severity" : 3
    },
    "W0604" : {
        "title" : "use of 'global' at module level",
        "description" : "%(issue.data.description)s",
        "categories" : ["maintainability"],
        "severity" : 3
    },
    "W0613" : {
        "title" : "unused argument",
        "description" : "%(issue.data.description)s",
        "categories" : ["readability","maintainability"],
        "severity" : 3
    },
    "W0622" : {
        "title" : "redefining builtin",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0633" : {
        "title" : "attempting to unpack non-sequence",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0701" : {
        "title" : "raising a string exception",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0702" : {
        "title" : "unqualified 'except'",
        "description" : "",
        "categories" : ["maintainability"],
        "severity" : 2
    },
    "W0704" : {
        "title" : "except without action",
        "description" : "",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W1111" : {
        "title" : "assigning to function call that only returns None",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W1301" : {
        "title" : "unused key in format string dictionary",
        "description" : "%(issue.data.description)s",
        "categories" : ["readability"],
        "severity" : 3
    },
    "W1501" : {
        "title" : "not a valid mode for open",
        "description" : "%(issue.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    }
}
