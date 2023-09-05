def stringToBool(strBool: str, default: bool):
    if strBool.lower() == "true":
        return True
    if strBool.lower() == "false":
        return False
    return default
