#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/25 10:30:44.634680
Revised: 2026/03/25 12:30:30.205019
"""

import enum


class SexEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class WeightUnitEnum(str, enum.Enum):
    kg = "kg"
    lb = "lb"


class DistanceUnitEnum(str, enum.Enum):
    km = "km"
    mi = "mi"


class HeightUnitEnum(str, enum.Enum):
    cm = "cm"
    inch = "in"


class RPEEnum(str, enum.Enum):
    no_reps_left = "no_reps_left"
    could_do_1 = "could_do_1"
    could_do_2 = "could_do_2"
    could_do_3 = "could_do_3"
    could_do_4_5 = "could_do_4_5"
    very_light = "very_light"


class EventTypeEnum(str, enum.Enum):
    login = "login"
    logout = "logout"
    register = "register"


class LanguageEnum(str, enum.Enum):
    en = "en"
    gl = "gl"
