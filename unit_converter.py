TIP = """\nAfter pressing RUN, enter any of the following format:-
---------------------------------------
4, km
4, kilometer
4, kilometer, mile
help
help mass
help pressure

--------------| Features |-------------

1. Supports almost all day to day units,
   Enter 'help' to know more.
2. Supports full forms as well as abbreviations
3. Spelling correction & suggestions
4. Pretty output
5. Also shows formula

---------------------------------------
Author: Or-i0n © 2019-20 All Rights Reserved
Version: 2.0.2-20190718

Upvote my code if you like 😊👍
"""

FORMAT = """

-----------| Input Format |-----------

Number, ConvertFrom, *ConvertTo
      ^            ^
            or
            
help *Category

* ConvertTo & Category are optional
"""

import json
from urllib import request
from urllib import error
import socket
import sys


sys.stdout.reconfigure(encoding="utf-16")

LINE = "-" * 40
TRIANGLE = "\u25B6"
CIRCLE = "\u25CF"


url = ("https://raw.githubusercontent.com/Or-i0n/unit_converter/master/"
       "dataset4.json")

# Loading dataset
try:
    full_data = json.load(request.urlopen(url))
    data = full_data["unit types"]
    abbreviations = full_data["abbreviations"]
except (socket.gaierror, error.URLError):
    print("Dataset Error: Failed to load online dataset!\n\nContact author OR!ON at https://www.sololearn.com/Profile/5351922/?ref=app")
    exit()


class Converter:
    def formula(self, convert_from, convert_to, category):
        """Fetches the formula for conversion of units"""

        subtypes = data[category]
        positions = list(subtypes.keys())
        unit1_position = positions.index(convert_from)
        unit2_position = positions.index(convert_to)

        if unit1_position < unit2_position:
            formula_is = subtypes[convert_from][unit2_position - 1]
        else:
            formula_is = subtypes[convert_from][unit2_position]
        return formula_is

    def convert(self, n, convert_from, convert_to, category):
        """Converts number to another unit type by evaluating the formula
        fetched"""

        # n is number that user wants to convert
        # note: do not change variable name 'n' to anything else because
        # this variable is used inside formula which is then evaluated by
        # eval() function
        try:
            result = eval(self.formula(convert_from, convert_to, category))

            if result > 1_000_000 or result < 0.00001:
                return f"{result: .2e}"
            rightpart = str(result).split(".")[1]
            if all(digit == "0" for digit in rightpart):
                return f" {int(result)}"
            return f"{result: .5f}"
        except TypeError:  # formula not available
            return "N/A"


class Suggest:
    def levenshtein_distance(self, string1, string2):
        """This function returns Levenshtein distance (LD) which is a measure
        of the similarity between two strings. The distance is the number of
        deletions, insertions, or substitutions required to transform string1
        into string2."""

        # lowercasing the string to equalize both strings
        string1, string2 = string1.lower(), string2.lower()

        # creating an matrix to compare two strings
        matrix = []

        # first row of the matrix
        matrix.append([index for index in range(len(string1) + 1)])

        # filling first row and column with string index and rest with zeros
        for row in range(len(string2)):
            matrix.append([row + 1])
            for col in range(len(string1)):
                matrix[row + 1].append(0)

        # calculating edit distance
        for index2 in range(len(string2)):
            for index1 in range(len(string1)):
                # calculating distance cost when both the character are similar
                if string2[index2] == string1[index1]:
                    matrix[index2 + 1][index1 + 1] = matrix[index2][index1]
                # calculating distance cost when both the characters are
                # different
                else:
                    top = matrix[index2][index1]
                    left = matrix[index2][index1 + 1]
                    bottom = matrix[index2 + 1][index1]

                    min_of_three = min([top, left, bottom])

                    matrix[index2 + 1][index1 + 1] = min_of_three + 1

        # return the distance calculated after all the process
        return matrix[-1][-1]

    def suggestions(self, database, user_input):
        """This function handles suggestion process and returns spelling
        corrections.
        Note: Suggestion process is case-insensitive."""

        direct_suggestions = []
        hit_dict = {}

        # comparing user input with words in database
        for word in database:
            # if there is a direct match for that string in any of the
            # database's word then adding that to a list
            if user_input in word.lower():
                direct_suggestions.append(word)
            # calculating and storing edit distance of user input with each word
            # in database
            hit_dict[word] = self.levenshtein_distance(user_input, word)

        # if there are any direct suggestions return them
        if direct_suggestions:
            return direct_suggestions

        # else search for best match according to edit distance and add that to
        # the list
        best_match = []
        for word in hit_dict:
            if hit_dict[word] == min(hit_dict.values()):
                best_match.append(word)

        # print(hit_dict)
        return best_match


class App(Converter):
    def __init__(self):
        self.suggest = Suggest()

    def helper(self, category=None):
        """Prints units and their categories that are supported"""

        if not category:
            print(f"{'Available Categories': ^40}\n{LINE}\n")
            for cat in data:
                print(f"{TRIANGLE} {cat.capitalize()}")
            print("\nEnter 'help <category>' to see units inside a category.")
        elif category in data:
            print(f"{'Units': ^40}\n{LINE}\n")
            for cat in data:
                print(f"{TRIANGLE} {cat.capitalize()}")
                if cat == category:
                    for unit in data[category]:
                        print(f"\t\t{CIRCLE} {unit.title()}")
        else:
            suggested_categories = self.suggest.suggestions(data, category)
            if len(suggested_categories) == 1:
                print(f"Did you mean '{suggested_categories[0]}'?\n")
                self.helper(suggested_categories[0])
            else:
                print(f"Suggestions for '{category}': {suggested_categories}")

    def valid_num(self, num):
        """Checks whether a number is valid or not by trying to convert it to
        float"""

        try:
            num = float(num)
        except ValueError:  # non valid number:
            return False, num
        return True, num

    def valid_unit(self, user_unit):
        """Checks whether user entered unit is available for conversion or
        not"""

        for category in data:
            for unit in data[category]:
                if user_unit.lower() == unit.lower():
                    return True, category
        return False, None

    def valid_abbreviation(self, abbreviation):
        """Checks whether user entered abbreviation is valid or not by checking
        it in abbreviation database"""

        if abbreviation in abbreviations.keys():
            return True
        return False

    def suggest_unit(self, unit):
        """Suggests unit names like kilometer or km based on suggestion
        algorithm from class Suggest()"""

        all_units = []
        for abbreviation, fullform in abbreviations.items():
            all_units.extend([abbreviation, fullform])

        # converting all_units to set to remove duplicate entries
        all_units = set(all_units)

        return self.suggest.suggestions(all_units, unit)

    def prettify_suggestions(self, old_suggestions):
        """Adds full form with suggested words if they are
        abbreviations and remove full forms if they clash
        with our provided full forms.
        Example:
        old_suggestions = ['week', 'foot', 'ft']
        prettify_suggestions = ['week', 'foot (ft)']

        or

        old_suggestions = ['kibibit', 'Kib, 'kibibyte', 'KiB']
        prettify_suggestios = ['kibibyte (KiB)', 'kibibit (Kib)']
        """

        for word in old_suggestions[:]:
            if self.valid_abbreviation(word):
                fullform = abbreviations[word]
                old_suggestions.remove(word)
                old_suggestions.append(f"{fullform} ({word})")
                if fullform in old_suggestions:
                    old_suggestions.remove(fullform)

        return old_suggestions

    def handle_errors(self, num, unit):
        """Handle errors after all fields are filled by user"""

        num_is_digit, num = self.valid_num(num)
        unit_is_valid, category = self.valid_unit(unit)
        abbreviation_is_valid = self.valid_abbreviation(unit)

        if len(str(num)) != 0:
            if num_is_digit:
                if len(unit) != 0:
                    if unit_is_valid:
                        return num, unit, category
                    elif not unit_is_valid:
                        if abbreviation_is_valid:
                            fullform = abbreviations[unit]
                            category = self.valid_unit(fullform)[1]
                            return num, fullform, category
                        elif not abbreviation_is_valid:
                            suggested = self.suggest_unit(unit)
                            old_unit = unit
                            if len(suggested) == 1:
                                unit = suggested[0]
                                if self.valid_abbreviation(unit):
                                    fullform = abbreviations[unit]
                                    category = self.valid_unit(fullform)[1]
                                    print(f"Showing result for '{unit}' "
                                          f"instead of '{old_unit}'\n")
                                    return num, fullform, category
                                else:
                                    category = self.valid_unit(unit)[1]
                                    print(f"Showing result for '{unit}' "
                                          f"instead of '{old_unit}'\n")
                                    return num, unit, category
                            elif len(suggested) <= 8:
                                print(f"Unit Error! Unit '{unit}' not found!\n\nSuggestion for '{old_unit}':",
                                      f"{self.prettify_suggestions(suggested)}"
                                      "\n")
                            else:
                                print(f"There are '{len(suggested)}' "
                                      f"related item to your query '{unit}'. Please be more specific.\n")
                    else:
                        print(f"Unit Error! "
                              f"'{unit}' is either not available or "
                              "is invalid.")
                else:
                    print(f"Unit Error! Unit at position 2 can't be empty.{FORMAT}\n")
            else:
                print(f"Value Error! '{num}' is not a valid number.")
        else:
            print("Value Error! Value can't be empty.\nTip: Enter 1, km")
        return None, None, None

    def parse_input(self, query):
        """Parse user input and handle any errors when fields are empty"""

        if len(query) != 0:
            if "," not in query:
                print("Comma Missing! Separate value and its unit with a "
                      "comma.\nLike: 1, km")
            elif query.count(",") not in range(1, 3):
                print("Multiple Commas! Only one or max two commas "
                      "are allowed.")
            else:
                if query.count(",") == 1:
                    num, unit = [each.strip() for each in query.split(",")]
                    return self.handle_errors(num, unit)
                elif query.count(",") == 2:
                    num, unit, unit2 = [each.strip()
                                        for each in query.split(",")]

                    # float number, unit1 name, unit1 category
                    fnum, u1name, u1category = None, None, None
                    u2name, u2category = None, None

                    # if unit is not blank
                    if unit:
                        fnum, u1name, u1category = self.handle_errors(num, unit)
                        # if unit2 is not blank
                        if unit2:
                            # fix for bug 6
                            # this is to stop self.handle_errors() from running
                            # again because it was printing out value error
                            # again when running for second time with unit2
                            # (first time when running with unit) if no value
                            # is given but units are given (like: ,km,m)
                            if fnum is not None:
                                handle_u2errors = self.handle_errors(1, unit2)
                                # Note: _fnum should not be used anywhere
                                _fnum, u2name, u2category = handle_u2errors
                        else:
                            print(f"Unit Error! Unit at position 3 is empty.{FORMAT}")
                    else:
                        print(f"Unit Error! Unit at position 2 is empty.{FORMAT}")
                    return fnum, u1name, u2name, u1category, u2category
        else:
            print(f"Input Error! Input can't be empty.\n{TIP}")
        return None, None, None

    def run(self):
        user_input = input()

        ask_help = user_input.strip().split()
        if not user_input:
            print(f"Input Error! Input can't be empty.\n{TIP}")
        elif ask_help[0].lower() == "help" and len(ask_help) == 1:
            self.helper()
        elif ask_help[0].lower() == "help" and len(ask_help) == 2:
            self.helper(ask_help[1].lower())
        else:
            # when user does not specify in which unit he wants to convert to
            if user_input.count(",") == 1:
                num, convert_from, category = self.parse_input(user_input)
                if (num is not None and convert_from is not None and category is not None):
                    print(f"{category.capitalize(): ^40}\n{LINE}\n"
                          f"{num: >18}: {convert_from.title()}\n{LINE}\n")

                    for convert_to in data[category]:
                        if convert_to != convert_from.lower():
                            converted = self.convert(num, convert_from,
                                                     convert_to, category)
                            print(f"{converted: >18}: {convert_to.title()}")
                    print(LINE)
            # when user specifies in which unit he wants to convert to
            elif user_input.count(",") == 2:
                parsed = self.parse_input(user_input)
                num, convert_from, convert_to, u1category, u2category = parsed

                if (num is not None and convert_from is not None and
                        u1category is not None and u2category is not None):
                    if u1category == u2category:
                        print(f"{u1category.capitalize(): ^40}\n{LINE}\n"
                              f"{num: >18}: {convert_from.title()}")
                        print(LINE)
                        # fix for bug 7
                        # while converting to same unit like mm to mm
                        if convert_from == convert_to:
                            print(f"{num:>18}: {convert_to.title()}")
                        else:
                            converted = self.convert(num,
                                                     convert_from, convert_to,
                                                     u1category)
                            formula = self.formula(convert_from, convert_to,
                                                   u1category)
                            print(f"{converted: >18}: "
                                  f"{convert_to.title()}")
                            print(LINE)
                            print(f"{'Formula': ^40}\n{LINE}\n"
                                  f"{formula}\n"
                                  f"Where n = {num}")
                        print(LINE)

                    else:
                        print("Invalid Units! Expecting both units of same "
                              f"category, found ({u1category}, {u2category}).")
            else:
                self.parse_input(user_input)


app = App()
app.run()
