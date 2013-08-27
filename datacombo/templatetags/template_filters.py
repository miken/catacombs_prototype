from django import template
register = template.Library()

@register.filter
def calculate_average(instance, args):
	"""
	allows only one argument for one exact method
	"""
	return instance.rating(args)