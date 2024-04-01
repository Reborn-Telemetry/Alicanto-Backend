from django import template

register = template.Library()

@register.filter
def number_to_words(number):
    units = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    tens = ['', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    teens = ['eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
    
    if number < 10:
        return units[number]
    elif number < 20:
        return teens[number - 11]
    else:
        digit = number % 10
        tens_digit = number // 10
        return f'{tens[tens_digit]} {units[digit]}'

