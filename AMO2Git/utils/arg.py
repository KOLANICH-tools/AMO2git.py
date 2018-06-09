import functools


def arg(func):
	"""Transforms min, max and similar functions into the ones returning args"""

	@functools.wraps(func)
	def argfunc(it, **kwargs):
		keyModifier = lambda p: p[1]
		modifiedKey = keyModifier
		if "key" in kwargs:
			if key is not None:
				modifiedKey = lambda p: key(keyModifier(p))
		return func(enumerate(it), key=modifiedKey)[0]

	argfunc.__name__ = "arg" + argfunc.__name__
	return argfunc


argmax = arg(max)
argmin = arg(min)
