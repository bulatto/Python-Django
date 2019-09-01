from django import template

register = template.Library()


def get(h, key):
    return h[key]


register.filter('get', get)
