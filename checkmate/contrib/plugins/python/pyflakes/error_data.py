# -*- coding: utf-8 -*-
"""
This file is part of checkmate, a meta code checker written in Python.

Copyright (C) 2015 Andreas Dewes, QuantifiedCode UG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

error_data = {
    "UndefinedName" : {
                        "title" : "undefined variable",
                        "categories" : ["correctness"],
                        "severity" : 1,
                        "description" : "%(occurence.data.description)s"
                      },
    "ImportStarUsed" : {
                        "title"  : "wildcard (*) import used",
                        "categories" : ["readability","maintainability"],
                        "severity" : 3,
                        "description" : "%(occurence.data.description)s"
                        },
    "UnusedImport" : {
                        "title"  : "unused import",
                        "categories" : ["readability","maintainability","efficiency"],
                        "severity" : 3,
                        "description" : "%(occurence.data.description)s"
                     },
    "UnusedVariable" : {
                        "title"  : "unused variable",
                        "categories" : ["readability","maintainability","efficiency"],
                        "severity" : 3,
                        "description" : "%(occurence.data.description)s"
                        },
    "RedefinedWhileUnused" : {
                        "title" : "redefined while unused",
                        "categories" : ["readability","maintainability","correctness","efficiency"],
                        "severity" : 2,
                        "description" : "%(occurence.data.description)s"
                        },
    "RedefinedInListComp" : {
                        "title" : "redefined in list comprehension",
                        "categories" : ["correctness","readability"],
                        "severity" : 2,
                        "description" : "%(occurence.data.description)s"
                        },
    "ImportShadowedByLoopVar" : {
                        "title" : "import shadowed by loop variable",
                        "categories" : ["correctness","maintainability"],
                        "severity" : 2,
                        "description" : "%(occurence.data.description)s"
                        },
    "DoctestSyntaxError" : {
                        "title" : "syntax error in doctest",
                        "categories" : ["correctness"],
                        "severity" : 2,
                        "description" : "%(occurence.data.description)s"
                        },
    "UndefinedExport" : {
                        "title" : "undefined export",
                        "categories" : ["correctness"],
                        "severity" : 1,
                        "description" : "%(occurence.data.description)s"
                        },
    "UndefinedLocal" : {
                        "title" : "undefined local variable",
                        "categories" : ["correctness"],
                        "severity" : 1,
                        "description" : "%(occurence.data.description)s"
                        },
    "Redefined" : {
                        "title" : "redefined object",
                        "categories" : ["maintainability","correctness"],
                        "severity" : 2,
                        "description" : "%(occurence.data.description)s"
                        }
}