from django import template
register = template.Library()

@register.filter
def display_rating(instance, args):
	"""
	allows only one argument for one exact method
	"""
	raw_rating = instance.rating(args)
	# Do string conversion here
	if not raw_rating:
		str_rating = 'N/A'
	else:
		str_rating = "{0:.2f}".format(raw_rating)
	return str_rating