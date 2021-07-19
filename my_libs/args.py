def args_kwargs(*args, **kwargs):
    return args, kwargs

def str2akrgs(s):
    return eval(f'args_kwargs({s})')
