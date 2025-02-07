


def create_dependecty(obj: object, _type: object):
    if obj is None:
        return obj
    else:
        if type(obj) != _type:
            raise TypeError(
                f"Invalid parameter: The '{obj}' argument "
                f"must be of type '{type(obj)}'."
                f""
            )
        return obj