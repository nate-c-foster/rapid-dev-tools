import functools
import time
import math




def timeIt(func):
	
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
	
		start = time.time()
		val = func(*args, **kwargs)
		end = time.time()
		
		print "------- Time taken by function '" + func.__name__ + "': " + str(end - start) + " seconds"
		
		return val
		
	return wrapper
	
	
	

def debug(func):

	@functools.wraps(func)
	def wrapper(*args, **kwargs):
	
		argsList = [repr(a) for a in args]
		kwargsList = ["{" + k + ":" + v + "}" for k,v in kwargs.items()]
		argumentsString = ", ".join(argsList + kwargsList)
		print "------- Calling function '" + func.__name__ + "' with arguments: " + argumentsString

		val = func(*args, **kwargs)

		print "------- Returned by function '" + func.__name__ + "': " + str(val)

		return val
		
	return wrapper
	
	

def exception(logger):

	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwarg):
		
			try:
				return func(*args, **kwargs)
				
			except:
				message = "************ Exception in function '" + func.__name__ + "' ************"
				logger.exception(message)
			
			raise
			
		return wrapper
	return decorator