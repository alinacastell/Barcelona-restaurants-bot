"""
Template file for restaurants.py module.
The main function of this module is to read the restaurants'
data of the restaurants.csv, store it in a list and look for
restaurants that fullfil certain requests.
"""
import easyinput as ei
# Library used to initialize classes
from dataclasses import dataclass
# Library used to access different data types
from typing import Optional, TextIO, List, Tuple, Dict
# Library used to read csv docs
import pandas as pd
# Library used to filter data
from fuzzywuzzy import fuzz
# Library used to avoid accent problems while function find
from unidecode import unidecode


@dataclass
class Restaurant:
    """
    Class: Contains the attirbutes of a restaurant.
    """
    name: str                # Restaurant's name
    institution_name: str    # Institution where it's located
    street_name: str         # Street name where it's located
    neighbourhood: str       # Neighborhood where it's located
    district: str            # Disctrict where it's located
    restaurant_type: str     # Service offered by the restaurant
    x_coord: float           # Restaurant's coordenate x
    y_coord: float           # Restaurant's coordenate y
    telf: str                # Restaurant's phone number
    street_num: str          # Restaurant's street number


Restaurants = List[Restaurant]


def read() -> Restaurants:
    """
    Function: Downloads and reads the restaurant file.
    Parameters: None
    Return: A list of the restaurants from the csv.
    """
    f = open('restaurants.csv', 'r')
    name: str = 'name'
    institution_name: str = 'institution_name'
    street_name: str = 'addresses_road_name'
    neighbourhood: str = 'addresses_neighborhood_name'
    district: str = 'addresses_district_name'
    restaurant_type: str = 'secondary_filters_name'
    x_coord: str = 'geo_epgs_4326_x'
    y_coord: str = 'geo_epgs_4326_y'
    telf: str = 'values_value'
    street_num: str = 'addresses_start_street_number'

    # Defines dataframe with the data of the csv
    df = pd.read_csv(f, usecols=[name, institution_name, street_name,
                     neighbourhood, district, restaurant_type, x_coord,
                     y_coord, telf, street_num])
    # Returns dataframe with duplicated rows removed, using the name
    # to find duplicates as it is unique for every restaurant
    df = df.drop_duplicates(subset=['name'])
    restaurants = []
    # Creates a restaurant with the information read in the dataframe
    # and appends it into a list of restaurants
    for row in df.itertuples():
        rest = Restaurant(row.name, row.institution_name,
                          row.addresses_road_name,
                          row.addresses_neighborhood_name,
                          row.addresses_district_name,
                          row.secondary_filters_name, row.geo_epgs_4326_x,
                          row.geo_epgs_4326_y, row.values_value,
                          row.addresses_start_street_number)
        restaurants.append(rest)
    return restaurants


##################
# DIFFUSE SEARCH #
##################


def find_rest(query: str, restaurants: Restaurants) -> Restaurants:
    """
    Function: Finds the restaurants that fullfil the request.
    Parameters: query -> requests to find a restaurant
                restaurants -> list of restaurants where the
                               query is applied
    Return: A list of the restaurants that fullfil the request.
    """
    matching_restaurants: Restaurants = []
    # list100 contains the list of restaurants that fullfil the request with
    # an accuracy of a 100%
    list100 = rest_list(matching_restaurants, restaurants, query, 100)
    # list80 contains the list of restaurants that fullfil the request
    # with an accuracy of 80%
    list80 = rest_list(list100, restaurants, query, 80)
    # If the list80 is not full (12 elements) list60 appends to list80
    # the restaurants that fullfil the request with at least an accuracy of 60%
    if len(matching_restaurants) < 12:
        list60 = rest_list(list80, restaurants, query, 60)
        return list60
    return list80


def rest_list(list_rest: list, restaurants: Restaurants, query: str,
              x: int) -> Restaurants:
    """
    Function: Finds the restaurants that fullfil the request.
    Parameters: list_rest -> list of restaurants where the restaurants that
                fullfil the request with an accuracy of at least x are going to
                be appended
                restaurants -> list of restaurants where to apply the query
                query -> requests to find a restaurant
                x -> value of accuracy needed
    Return: A list of the restaurants that fullfil the request.
    """
    for restaurant in restaurants:
        # Treats rest as a list in order to get each of the attributes easier
        rest = [str(restaurant.name), str(restaurant.institution_name),
                str(restaurant.street_name), str(restaurant.neighbourhood),
                str(restaurant.district), str(restaurant.restaurant_type),
                str(restaurant.x_coord), str(restaurant.y_coord),
                str(restaurant.telf), str(restaurant.street_num)]
        for i in range(len(rest)):
            # Filters the accents in the query and attribute
            quer = unidecode(query.lower())
            attr = unidecode(rest[i].lower())
            # Returns the value of accuracy of the query and the attribute
            value = fuzz.partial_ratio(quer, attr)
            # Reconverts rest into a Restaurant in order to return a list of
            # Restaurants
            r = Restaurant(rest[0], rest[1], rest[2], rest[3], rest[4],
                           rest[5], float(rest[6]), float(rest[7]), rest[8],
                           rest[9])
            # Treats two different cases: value of accuracy needed = 100 or
            # lower
            if x != 100:
                # If it is not equal to 100, only appends the restaurants that
                # exceeded the value needed but not the ones with accuracy =
                # 100 because they are already in the list, and they would be
                # repeated if added. Treats both 60% and 80% cases, that is why
                # x+20 is a condition.
                if value >= x and value < x+20:
                    list_rest.append(r)
                    break
            else:
                # If it is equal to 100, only appends the restaurants that have
                # an accuracy of a 100
                if value >= x:
                    list_rest.append(r)
                    break
    return list_rest


# Used in most of the functions below
restaurant_list = read()


########################
# MULTIPLE WORD SEARCH #
########################


def create_multiple(query: list) -> Restaurants:
    """
    Function: Implements the logic operand 'and' to all the lists resultant
              the search of each query.
    Parameters: query -> requests to find a restaurant
    Return: A list of the intersected restaurants.
    """
    list1 = find_rest(query[0], restaurant_list)
    for i in range(1, len(query)):
        list2: List = []
        sel_list = find_rest(query[i], restaurant_list)
        for rest1 in list1:
            for rest2 in sel_list:
                # Compares the restaurants' names from both lists
                if rest1.name == rest2.name:
                    list2.append(rest1)
        # Saves the resultat list to list1 in order to work with the
        # intersected restaurants for every iteration of the loop
        list1 = drop_dupplicates(list2)
    return list1


################
# LOGIC SEARCH #
################


def logic_search(query: list, word1: str) -> Restaurants:
    """
    Function: Given a logic set of querys, applies the logic_search and
              looks for restaurants that fullfil the requests.
    Parameters: query -> list of querys
                word1 -> first request of the list
    Return: A list of the selected restaurants.
    """
    sel_list: Restaurants = []
    result: List = [sel_list]
    query = query[1:-1]

    # Treats all the possible cases that still have opperations to do
    while len(query) > 0 or len(result) == 2:
        word2 = query[0]
        length = len(query)
        list1: Restaurants = []
        list2: Restaurants = []
        # Every time an opperation is done, it is erased from the query
        if word2 == 'and':
            sel_list = create_and(query[1:3], list1, list2)
            result.append(sel_list)
            query = query[3:length]
        elif word2 == 'or':
            sel_list = create_or(query[1:3], list1, list2)
            result.append(sel_list)
            query = query[3:length]
        elif word2 == 'not':
            sel_list = create_not(query[1:2], list1)
            result.append(sel_list)
            query = query[2:length]
        # Two posisble cases: opperation with only two querys (one in case
        # of not) or tow lists (one in case of not)
        else:
            # Case of opperation with two lists, otherwise, list1 and list2
            # are empty
            if len(result[0]) != 0:
                list1 = result[0]
                if word1 != 'not':
                    list2 = result[1]
            if word1 == 'and':
                sel_list = create_and(query[0:2], list1, list2)
            elif word1 == 'or':
                sel_list = create_or(query[0:2], list1, list2)
            else:
                sel_list = create_not(query[0:2], list1)
            # Once all the opperations are done, empties the lists in order
            # to end the loop
            query = []
            result = [[]]
    return sel_list


def drop_dupplicates(list1: Restaurants) -> Restaurants:
    """
    Function: Given a list, removes the dupplicate restaurants
    Parameters: list1 -> list of restaurants
    Return: A list of restaurants without dupplicates.
    """
    for i in range(len(list1)):
        for j in range(len(list1)):
            # If the length of list1 has shortened after removing an element
            # increments j until the next iteration because it has already
            # run through all the new length of the list
            if i < len(list1) and j < len(list1):
                # If two restaurants of the list have the same name but are in
                # different positions, it means that the restaurant is
                # dupplicate
                if list1[i].name == list1[j].name and i != j:
                    list1.remove(list1[i])
                    # As an element of the list has been removed, the following
                    # restaurant occupies its position in the list an has not
                    # been checked yet
                    i -= 1
                    j -= 1
                j += 1
    return list1


def create_and(query: list, l1: Restaurants, l2: Restaurants) -> Restaurants:
    """
    Function: Implements the logic operand 'and' to both lists resultant from a
              search.
    Parameters: query -> requests to find a restaurant
                list1 -> list of restaurants
                list2 -> list of restaurants
    Return: A list of the intersected restaurants.
    """
    sel_list = []
    # As this function is implemented for the case that we have to create two
    # lists from two querys using the function find, or also to intersect two
    # lists already created, this condition makes sure the lists are only
    # created in the first case
    if len(l1) == 0 and len(l2) == 0:
        l1 = find_rest(query[0], restaurant_list)
        l2 = find_rest(query[1], restaurant_list)
    for rest1 in l1:
        for rest2 in l2:
            # Compares the restaurants' names from both lists
            if rest1.name == rest2.name:
                sel_list.append(rest1)
    return drop_dupplicates(sel_list)


def create_or(query: list, l1: Restaurants, l2: Restaurants) -> Restaurants:
    """
    Function: Implements the logic operand 'or' to both lists resultant from a
              search.
    Parameters: query -> requests to find a restaurant
                list1 -> list of restaurants
                list2 -> list of restaurants
    Return: A list of the merged restaurants.
    """
    # As this function is implemented for the case that we have to create
    # two lists from two querys using the function find, or also to merge
    # two lists already created, this condition makes sure the lists are
    # only created in the first case
    if len(l1) == 0 and len(l2) == 0:
        l1 = find_rest(query[0], restaurant_list)
        l2 = find_rest(query[1], restaurant_list)
    # As two lists have been merged, removes the restaurants that have been
    # dupplicated
    for rest2 in l2:
        cont = 0
        for rest1 in l1:
            # Compares each restaurant from list2 and, if it is not in list1
            # already appends it to the list
            if rest1.name != rest2.name:
                cont += 1
        if cont == len(l1):
            l1.append(rest2)
    return l1


def create_not(query: list, l1: Restaurants) -> Restaurants:
    """
    Function: Implements the logic operand 'not' to the list resultant from a
              search.
    Parameters: query -> requests to find a restaurant
                list1 -> list of restaurants
    Return: A list without the restaurants found.
    """
    # As this function is implemented for the case that we have to create a
    # list from a query using the function find, or also to work with a list
    # already created, this condition makes sure the list is only created
    # in the first case
    if len(l1) == 0:
        l1 = find_rest(query[0], restaurant_list)
    # Creates a list of all the restaurants from the cvs
    l2 = find_rest('Barcelona', restaurant_list)
    for rest1 in l1:
        for rest2 in l2:
            # Compares the restaurants' names from both lists
            if rest1.name == rest2.name:
                l2.remove(rest1)
    return l2
