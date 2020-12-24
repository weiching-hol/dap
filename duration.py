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

def text2int(textnum, numwords={}):
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

def search(values, searchFor): # search if dictionary value contains certain string --> return key, else return string
    for k in values:
        for v in values[k]:
            if str(searchFor) == v:
                return 1, k, ''
    return 0, searchFor, searchFor

def convert_to_day(number, unit): 
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
    return n_string.replace('1 / 2','.5').replace(' ','')


def transform_duration(txt):
    # 1. Add space between numeric and alphabet
    # Remove `.` and `,` at the start and end of string
    txt = re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1 ", txt).lower().strip().rstrip('.|,').lstrip('.|,')
    
    # 2. Detect the number of units
    word_list = txt.split()
    word_list = [search(kw_duration, w) for w in word_list]
    n_units = sum([x[0] for x in word_list if x[0]==1])
    unit_string = ' '.join([x[1] for x in word_list if x[0]==1])
    left_string = ' '.join([x[2] for x in word_list if x[0]==0])
    clean_string = ' '.join([x[1] for x in word_list])
    # print('word_list: ', word_list)
    # print('n_units: ', n_units)
    # print('unit_string: ', unit_string)
    # print('left_string: ', left_string)
    # print('clean_string: ', clean_string)
    # print('...')
    
    # 2a. No units --> unidentified
    if n_units == 0:
#         print('0 unit')
        # '128' --> (0, 'unidentified')
        return 0.0, 'unidentified' 
    
    # 2b. 1 unit --> check if remaining string is float
    elif n_units == 1: 
#         print('1 unit')
        try: # if successful, return N and unit
            # '6 months' --> (6.0, 'month')
            return float(left_string), unit_string 
        
        except: # if not successful, split the string based on `-` or `to `
            chunk_list = re.split('-|to |or ', left_string)
            # print(chunk_list)
            # print('...',[text2int(convert_half(x.strip()).replace('a half', 'half')) for x in chunk_list])
            try: # try float on each chunk. if successful, take average
                # convert number as words to number int
                # '1/2 months' --> (0.5, 'month')
                # 'A day or two' --> (1.5, 'day')
                return sum([text2int(convert_half(x.strip()).replace('a half', 'half')) for x in chunk_list]) / len(chunk_list), unit_string
            
            except: # if not successful, split the string based on `and ` and sum up
                # '1 and 1/2 months' --> (1.5, 'month')
                chunk_list = re.split('and |,',''.join(chunk_list))
                # print(chunk_list)
                try:
                    return sum([float(convert_half(x.strip())) for x in chunk_list]), unit_string
                except: 
                    try: # convert number as words to number int
                        return sum([sum([text2int(x.strip()) for x in phrase.replace('a half', 'half').split()]) for phrase in chunk_list]), unit_string 
                        
                    except: # txt contains other words
                        return 0.0, 'unidentified'
    
    # 2c. >1 unit
    else:
#         print('>1 unit')
        

        chunk_list = re.split('-|to |or ', txt)
        chunk_list = [[search(kw_duration, w) for w in chunk.split()] for chunk in chunk_list]
        n_units = [sum([x[0] for x in word_list if x[0]==1]) for word_list in chunk_list]
        unit_string = [' '.join([x[1] for x in word_list if x[0]==1]) for word_list in chunk_list]
        left_string = [' '.join([x[2] for x in word_list if x[0]==0]) for word_list in chunk_list]
#         print('n_units: ', n_units)
#         print('unit_string: ', unit_string)
#         print('left_string: ', left_string)
#         print('...')
        
        if sum(n_units) / len(n_units) != 1: # >1 unit per chunk
            return 0.0, 'unidentified'
        else: # 1 unit per chunk
            try: # standardise unit to day
                return sum([convert_to_day(x[0], x[1]) for x in zip(left_string, unit_string)]) / len(left_string), 'day'
            except: # txt contains other words
                return 0.0, 'unidentified'


# print(transform_duration('A day or two'))
# print(transform_duration('1 and 1/2 day'))
# print(transform_duration('one and a half thousand days'))

# Cases

# No units
print('\n(1) Cases with no unit\n=======')
for x in ['NaN', '128']:
    print(f'{x:20s}', transform_duration(x))

# 1 unit
print('\n(2) Cases with a unit\n=======')
for x in ['2 days', '2 to 4 days', '11/2 day', '3 1/2 - 4 months', 
          '1 and 1/2 day', 'one and a half day', '1 and a half day', 
          ', 4 days', '2 or 3 weeks', 'A day or two', 'a day.',
          '2 or 3 days', 'one and a half thousand days', 'a day an half'
         ]:
    print(f'{x:20s}', transform_duration(x))

# 2 units
print('\n(3) Cases with more than one unit\n=======')
for x in ['1 day to 2 weeks', '1 year 6 months', '5 months,3week']:
    print(f'{x:20s}', transform_duration(x))

# Not considered
print('\n(4) Cases not accounted for\n=======')
for x in ['6-months', 'a few weeks', 'last 12 hours', '1weekend']:
    print(f'{x:20s}', transform_duration(x))
