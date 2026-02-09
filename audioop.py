# Dummy audioop module for Python 3.13 compatibility
# This module was removed in Python 3.13 but discord.py still tries to import it
# We create a dummy module so the import doesn't fail

# Discord.py only needs these if using voice features, which we're not using

class error(Exception):
    pass

def ratecv(*args, **kwargs):
    raise NotImplementedError("Voice features not available")

def lin2lin(*args, **kwargs):
    raise NotImplementedError("Voice features not available")

def tomono(*args, **kwargs):
    raise NotImplementedError("Voice features not available")

def tostereo(*args, **kwargs):
    raise NotImplementedError("Voice features not available")
