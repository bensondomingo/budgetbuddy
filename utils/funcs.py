
def filter_dict(_dict, keys):
    '''
    Filters a dictionary based on a given keys
    _dict:  dictionary to filter
    keys:   keys of values to return
    return: filterd dictionary
    '''
    return dict(zip(keys, [_dict[k] for k in keys]))


def filter_list_of_dict(list_of_dict, keys):
    '''
    Extends filter_dict functionality to support list of dictionaries.
    returns a filtered list_of_dict
    '''
    for d in [_dict for _dict in list_of_dict]:
        yield filter_dict(d, keys)
