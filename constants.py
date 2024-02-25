VENV_NAME = "umuenv"

class Operators:
    EXACT = "=="
    PATCH = "~="
    GREATER_EQ = ">="
    LESS_EQ = "<="

    ALL = [EXACT, PATCH, GREATER_EQ, LESS_EQ]

from enum import Enum

class CPPVersion(str, Enum):
    CPP_98 = "cpp_93"
    CPP_03 = "cpp_03"
    CPP_11 = "cpp_11"
    CPP_14 = "cpp_14"
    CPP_17 = "cpp_17"
    CPP_20 = "cpp_20"
    CPP_23 = "cpp_23"
