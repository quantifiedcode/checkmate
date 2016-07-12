# -*- coding: utf-8 -*-

issues_data = {
    "C0202" : {
        "title" : "class method should have 'cls' as first argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["maintainability","readability"],
        "severity" : 3
    },
    "C0203" : {
        "title" : "metaclass method should have 'mcs' as first argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["maintainability","readability"],
        "severity" : 3
    },
    "C0321" : {
        "title" : "more than one statement per line",
        "description" : "",
        "categories" : ["maintainability","readability"],
        "severity" : 3
    },
    "R0201" : {
        "title" : "method could be a function",
        "description" : "",
        "categories" : ["maintainability"],
        "severity" : 4
    },
    "E0100" : {
        "title" : "__init__ is a generator",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0101" : {
        "title" : "explicit return in __init__",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "E0104" : {
        "title" : "return outside of function",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0105" : {
        "title" : "yield outside of function",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0106" : {
        "title" : "return with argument inside generator",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0107" : {
        "title" : "use of non-existent operator",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0109" : {
        "title" : "duplicate argument name",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0202" : {
        "title" : "hidden attribute",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0203" : {
        "title" : "access before definition",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0211" : {
        "title" : "method without argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0213" : {
        "title" : "method should have 'self' as first argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0235" : {
        "title" : "__exit__ must accept 3 arguments",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0702" : {
        "title" : "illegal value raised",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E0711" : {
        "title" : "NotImplemented raised",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1004" : {
        "title" : "missing arguments to 'super'",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1111" : {
        "title" : "assigning to function call that doesn't return",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1121" : {
        "title" : "too many arguments",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1123" : {
        "title" : "unexpected keyword argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1124" : {
        "title" : "parameter passed as position and keyword argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1200" : {
        "title" : "unsupported logging format character",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1201" : {
        "title" : "invalid logging format string",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1205" : {
        "title" : "too many arguments for logging format string",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1206" : {
        "title" : "not enough arguments for logging format string",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1303" : {
        "title" : "expected mapping for format string",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1305" : {
        "title" : "too many arguments for format string",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "E1306" : {
        "title" : "not enough arguments for format string",
        "description" : "%(occurence.data.description)s",
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
        "description" : "%(occurence.data.description)s",
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
        "description" : "%(occurence.data.description)s",
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
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0110" : {
        "title" : "map/filter could be replaced by list comprehension",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 3
    },
    "W0122" : {
        "title" : "use of exec",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness","security"],
        "severity" : 2
    },
    "W0150" : {
        "title" : "'finally' may swallow exception",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0211" : {
        "title" : "static method with self/cls as first argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0231" : {
        "title" : "init method from base class not called",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0234" : {
        "title" : "iter returns non-iterator",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0410" : {
        "title" : "__future__ not first in module",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 1
    },
    "W0603" : {
        "title" : "use of 'global'",
        "description" : "%(occurence.data.description)s",
        "categories" : ["maintainability"],
        "severity" : 3
    },
    "W0604" : {
        "title" : "use of 'global' at module level",
        "description" : "%(occurence.data.description)s",
        "categories" : ["maintainability"],
        "severity" : 3
    },
    "W0613" : {
        "title" : "unused argument",
        "description" : "%(occurence.data.description)s",
        "categories" : ["readability","maintainability"],
        "severity" : 3
    },
    "W0622" : {
        "title" : "redefining builtin",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0633" : {
        "title" : "attempting to unpack non-sequence",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W0701" : {
        "title" : "raising a string exception",
        "description" : "%(occurence.data.description)s",
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
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    },
    "W1301" : {
        "title" : "unused key in format string dictionary",
        "description" : "%(occurence.data.description)s",
        "categories" : ["readability"],
        "severity" : 3
    },
    "W1501" : {
        "title" : "not a valid mode for open",
        "description" : "%(occurence.data.description)s",
        "categories" : ["correctness"],
        "severity" : 2
    }
}
