# New pipeline
import re
import math

kw_duration = {
    'hour'  : ['hour', 'hours', 'hr', 'hrs', 'h'],
    'day'   : ['day', 'days', 'd'],
    'week'  : ['week', 'weeks', 'wks', 'w'],
    'month' : ['mont', 'month', 'months', 'montths', 'monnths', 'm', 'mo', 'mths'],
    'year'  : ['year', 'years', 'yr', 'y', 'yrs']
}

def text_to_int(textnum, numwords={}):
    """Convert numbers as text to numbers as integers

    Args:
        textnum (str): string to be converted to numbers
        numwords (dict, optional): [description]. Defaults to {}.

    Raises:
        Exception: word is not a number or unit

    Returns:
        float: converted numbers
    """
    try: # if numbers as int
        return float(textnum)
    except:
        if not numwords:
            units = {
                "zero": 0,
                "a half": 0.5,
                "half": 0.5,
                "one": 1,
                "a": 1,
                "two": 2,
                "three": 3, 
                "four": 4, 
                "five": 5, 
                "six": 6, 
                "seven": 7, 
                "eight": 8,
                "nine": 9, 
                "ten": 10, 
                "eleven": 11, 
                "twelve": 12, 
                "thirteen": 13, 
                "fourteen": 14, 
                "fifteen": 15,
                "sixteen": 16, 
                "seventeen": 17, 
                "eighteen": 18, 
                "nineteen": 19
            }
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

            scales = ["hundred", "thousand", "million", "billion", "trillion"]

            numwords["and"] = (1, 0)
            for key, value in units.items():      numwords[key] = (1, value)
            for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
            for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

        current = result = 0
        for word in textnum.split():
            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0

        return result + current

def check_units_present(values_dict, searchFor): # search if dictionary value contains certain string --> return key, else return string
    """Search if unit is contained in unit dictionary i.e. search if dictionary value contains certain string. 

    Args:
        values_dict (dict): duration keyword dictionary to search for values
        searchFor (str): string to search for

    Returns:
        tuple: (int,str,str) returns 1 if keyword is in dictionary, else 0. Returns key if keyword is in dictionary, else original word.
    """
    for k in values_dict:
        for v in values_dict[k]:
            if str(searchFor) == v:
                return 1, k, ''
    return 0, searchFor, searchFor

def convert_to_day(number, unit): 
    """Standardise input unit to day

    Args:
        number (str|int|float): input number of units is converted to N number of days
        unit (str): any of the dictionary keys i.e. 'hour', 'day', 'week', 'month', or 'year'

    Returns:
        float: converted N number of days
    """
    number = float(number)
    unit_conversion = {
        'hour': number / 24,
        'day': number,
        'week': number * 7,
        'month': number * 30,
        'year': number * 365
    }
    return unit_conversion[unit]

def convert_half(n_string):
    """Convert '1 / 2' to '.5'

    Args:
        n_string (str): string of numbers e.g. '1 1 / 2'

    Returns:
        str: replaced string '1.5'
    """
    return n_string.replace('1 / 2','.5').replace(' ','')

def split_to_double(string):
    """Split string into a list of double words

    Args:
        string (str): a string of words e.g. '1 month 2 day'

    Returns:
        list: list of double words e.g. ['1 month', '2 day']
    """
    words = string.split()
    grouped_words = [' '.join(words[i: i + 2]) for i in range(0, len(words), 2)]
    return grouped_words

def check_two_units(string):
    """Check if string is of the form `N unit N unit`

    Args:
        string (str): any string e.g. '1 month 2 day'

    Returns:
        bool: True or False depending on whether the pattern is matched e.g. True
    """
    regex = r'^([0-9]+)\s+((\byear\b)|(\bmonth\b)|(\bweek\b)|(\bday\b)|(\bhour\b))\s+([0-9]+)\s+((\byear\b)|(\bmonth\b)|(\bweek\b)|(\bday\b)|(\bhour\b))$'
    return bool(re.match(regex,string))

def remove_false_hypen(string):
    """Remove hypen in between N and word (does not signify `to`)

    Args:
        string (str): string to remove false hypen

    Returns:
        str: string with removed hypen. If no hypen, return original string.
    """
    regex = '([0-9]+)-([a-zA-z])'
    if bool(re.match(regex,string)):
        return string.replace('-',' ')
    return string

def transform_duration(txt):
    # 1. Remove false hypen 
    # Add space between numeric and alphabet
    # Remove `.` and `,` at the start and end of string
    txt = remove_false_hypen(txt)
    txt = re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1 ", txt).lower().strip().rstrip('.|,').lstrip('.|,')

    # 2. Detect the number of units
    word_list = txt.split()
    # word_list = re.findall(r"[\w']+|[.,!?;]",txt)
    # print('word_list: ',word_list)
    word_list = [check_units_present(kw_duration, w) for w in word_list]
    n_units = sum([x[0] for x in word_list if x[0]==1])
    unit_string = ' '.join([x[1] for x in word_list if x[0]==1])
    left_string = ' '.join([x[2] for x in word_list if x[0]==0])
    clean_string = ' '.join([x[1] for x in word_list])
    # print('\nword_list: ', word_list)
    # print('n_units: ', n_units)
    # print('unit_string: ', unit_string)
    # print('left_string: ', left_string)
    # print('clean_string: ', clean_string)
    # print('...')
    
    # 2a. No units --> unidentified
    if n_units == 0:
        # '128' --> (0, 'unidentified')
        return 0.0, 'unidentified' 
    
    # 2b. 1 unit --> check if remaining string is float
    elif n_units == 1: 
        try: # if successful, return N and unit
            # '6 months' --> (6.0, 'month')
            return float(left_string), unit_string 
        
        except: # if not successful, split the string based on `-` or `to `
            chunk_list = re.split('-|to |or |,', left_string)
            try: # try float on each chunk. if successful, take average
                # convert number as words to number int
                # '1/2 months' --> (0.5, 'month')
                # 'A day or two' --> (1.5, 'day')
                return sum([text_to_int(convert_half(x.strip()).replace('a half', 'half')) for x in chunk_list]) / len(chunk_list), unit_string
            
            except: # if not successful, split the string based on `and ` and sum up
                # '1 and 1/2 months' --> (1.5, 'month')
                try: # convert number text to integer
                    return sum([text_to_int(x.replace('a half', 'half')) for x in chunk_list]), unit_string
                except:
                    try: # split on `and ` and get sum of both number int
                        chunk_list = re.split('and ',''.join(chunk_list))
                        return sum([float(convert_half(x.strip())) for x in chunk_list]), unit_string
                    except: # contains other words
                        return 0.0, 'unidentified'
    
    # 2c. >1 unit
    else:
        # split based on `-`, `to `, or `or `
        # extract the unit within each chunk
        chunk_list = re.split('-|to |or ', txt)
        chunk_list = [[check_units_present(kw_duration, w) for w in re.split(' |,', chunk)] for chunk in chunk_list]
        n_units = [sum([x[0] for x in word_list if x[0]==1]) for word_list in chunk_list]
        unit_string = [' '.join([x[1] for x in word_list if x[0]==1]) for word_list in chunk_list]
        left_string = [' '.join([x[2] for x in word_list if x[0]==0]) for word_list in chunk_list]
        clean_string = [' '.join([x[1] for x in word_list]) for word_list in chunk_list][0] # returns a string

        if sum(n_units) / len(n_units) != 1: # >1 unit per chunk
            if check_two_units(clean_string): # check if clean_string has regex pattern 'N unit N unit'
                # standardise both units to day and sum
                grouped_words = split_to_double(clean_string)
                return sum([convert_to_day(x.split()[0],x.split()[1]) for x in grouped_words]), 'day'
            else: # clean_string contains other words
                return 0.0, 'unidentified'
        else: # 1 unit per chunk
            try: # standardise unit to day
                return sum([convert_to_day(x[0], x[1]) for x in zip(left_string, unit_string)]) / len(left_string), 'day'
            except: # txt contains other words
                return 0.0, 'unidentified'

print(transform_duration('6-months'))
# print(transform_duration('one and a half thousand days'))

# # Cases

# # No units
# print('\n(1) Cases with no unit\n=======')
# for x in ['NaN', '128']:
#     print(f'{x:20s}', transform_duration(x))

# # 1 unit
# print('\n(2) Cases with a unit\n=======')
# for x in ['2 days', '2 to 4 days', '11/2 day', '3 1/2 - 4 months', 
#           ', 4 days', '2 or 3 weeks', 'A day or two', 'a day.',
#           '1 and 1/2 day', 'one and a half day', 'one and a half thousand days', 
#             '1 and a half day', # cannot take into account string with numbers as mixture of int and words
#            '6-months', 'a day an half'
#          ]:
#     print(f'{x:20s}', transform_duration(x))

# # 2 units
# print('\n(3) Cases with more than one unit\n=======')
# for x in ['1 day to 2 weeks', '1 year 6 months', '5 months,3week']:
#     print(f'{x:20s}', transform_duration(x))

# # Not considered
# print('\n(4) Cases not accounted for\n=======')
# for x in ['a few weeks', 'last 12 hours', '1weekend']:
#     print(f'{x:20s}', transform_duration(x))
