import re


def prepare_pedigree_number_number(number):
    parsed_number = u''
    if number:
        parsed_number = re.sub(r'[^\w]', u'.', number.lower().strip().replace(u'_', '.'), flags=re.UNICODE)
    return parsed_number