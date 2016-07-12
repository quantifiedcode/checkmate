
def update(d,ud):
    """
    Recursively merge the values of ud into d.
    """
    if ud is None:
        return
    for key,value in ud.items():
        if not key in d:
            d[key] = value
        elif isinstance(value,dict):
            update(d[key],value)
        else:
            d[key] = value