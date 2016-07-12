# -*- coding: utf-8 -*-

issues_data = {
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
