"""
Template file for metro.py module.
The main function of this module is to create a graph of Barcelona's metro with
its stations and accesses.
It has information about its stations, its train track section, its accesses
and train changes.
Every type of node (station and access) and edge (access, link, railway) has
its own attributes.
"""

# Library used to initialize classes
from dataclasses import dataclass
# Library used to access different data types
from typing import Optional, TextIO, List, Tuple, Dict
# Library used to generate undirected graphs of networkx
from typing_extensions import TypeAlias
# Library used to read csv docs
import pandas as pd
# Library used to manipulate graphs
import networkx as nx
# Library used to draw a graph interactively
import matplotlib.pyplot as plt
# Library used to draw a graph on a picture
from staticmap import StaticMap, Line, CircleMarker

Point: TypeAlias = Tuple[float, float]  # Tuple of a point (coord_x, coord_y)

MetroGraph: TypeAlias = nx.Graph        # Undirected graph from networkx


@dataclass
class Station:
    """
    Class: Contains the attributes of a station.
    """
    type: str               # Station's type
    id: str                 # Station's identifying number
    name: str               # Station's name
    line: str               # Station's line
    loc: Point              # Station's location
    code: str               # Station's code
    station_order: str      # Position of the station in the line
    colour: str             # Station's line colour


@dataclass
class Access:
    """
    Class: Contains the attributes of an access to a station.
    """
    type: str               # Access type
    id: str                 # Access identifying number
    name: str               # Access name
    loc: Point              # Access location
    code: str               # Station's code where it gives acces
    accessibility: str      # Access accessibility  ?


Stations = List[Station]
Accesses = List[Access]


def read_stations() -> Stations:
    """
    Function: Downloads and reads the station file.
    Parameters: None
    Return: A list of the stations in the csv.
    """
    f = open('estacions.csv', 'r')
    stations = []
    id: str = 'CODI_ESTACIO_LINIA'
    name: str = 'NOM_ESTACIO'
    line: str = 'NOM_LINIA'
    loc: str = 'GEOMETRY'
    code: str = 'CODI_ESTACIO'
    station_order: str = 'ORDRE_ESTACIO'
    colour: str = 'COLOR_LINIA'

    # Defines dataframe with the data of the csv
    df = pd.read_csv(f, usecols=[id, name, line, loc, code, station_order,
                                 colour])
    # Creates a station with the information read in the dataframe and
    # appends it into a list of stations
    for row in df.itertuples():
        point = get_location(row.GEOMETRY)
        st = Station('station', row.CODI_ESTACIO_LINIA, row.NOM_ESTACIO,
                     row.NOM_LINIA, point, row.CODI_ESTACIO, row.ORDRE_ESTACIO,
                     "#"+row.COLOR_LINIA)
        stations.append(st)
    return stations


def read_accesses() -> Accesses:
    """
    Function: Downloads and reads the accesses file.
    Parameters: None
    Return: A list of the accesses in the csv.
    """
    f = open('accessos.csv', 'r')
    accesses = []
    id:   str = 'CODI_ACCES'
    name: str = 'NOM_ACCES'
    loc:  str = 'GEOMETRY'
    code: str = 'ID_ESTACIO'
    accessibility: str = 'NOM_TIPUS_ACCESSIBILITAT'

    # Defines dataframe with the data of the csv
    df = pd.read_csv(f, usecols=[id, name, loc, code, accessibility])
    # Creates an access with the information read in the dataframe and
    # appends it into a list of accesses
    for row in df.itertuples():
        point = get_location(row.GEOMETRY)
        ac = Access('access', row.CODI_ACCES, row.NOM_ACCES, point,
                    row.ID_ESTACIO, row.NOM_TIPUS_ACCESSIBILITAT)
        accesses.append(ac)
    return accesses


def get_location(loc: str) -> Point:
    """
    Function: Splits a Point into two parts that form a tuple.
    Parameters: string -> as a Point (x_coord y_coord)
    Return: A Point tuple with format [x_coord, y_coord].
    """
    coords = loc[7:-1].split()
    return (float(coords[0]), float(coords[1]))


def add_acces_node(G: MetroGraph, stations: List, accesses: List) -> None:
    """
    Function: Adds access nodes to the graph and accces edges from an access
              point to a station.
    Parameters: graph -> MetroGraph with stations as nodes
                stations -> a list of stations
                accesses -> a list of accesses that lead to stations
    Return: None.
    """
    for access in accesses:
        # Creates new node for an access point (ignores this action if this
        # node already exists)
        G.add_node(access.id, type=access.type, location=access.loc)
        found = False
        i = 0
        while i < len(stations) and not found:
            station = stations[i]
            # If it is an access to that station, add access edge
            if access.code == station.code:
                G.add_edge(station.id, access.id, type='Access',
                           colour='#000000')
                found = True
            i += 1


def add_edges(G: MetroGraph, stations: List) -> None:
    """
    Function: Adds link edges and railway edges between stations.
    Parameters: graph -> MetroGraph with stations as nodes
                stations -> a list of stations
    Return: None.
    """
    for station1 in stations:
        for station2 in stations:
            if station1.name == station2.name:
                if station1.line != station2.line:
                    G.add_edge(station1.id, station2.id, type='Link',
                               colour='#000000')
            # If stations with same line are consecutives, add railway edge
            if int(station1.station_order) + 1 == int(station2.station_order):
                if station1.line == station2.line:
                    G.add_edge(station1.id, station2.id, type='Railway',
                               colour=station1.colour)


def get_metro_graph() -> MetroGraph:
    """
    Function: Creates a MetroGraph by adding nodes (station and access) and
              edges (link and railway) with all their information.
    Parameters: None
    Return: A complete graph that represents Barcelona's metro network.
    """
    stations = read_stations()
    accesses = read_accesses()
    G = nx.Graph()
    for station in stations:
        # Call networkx function
        G.add_node(station.id, type=station.type, line=station.line,
                   location=station.loc, name=station.name)
    # Calls functions previously defined
    add_acces_node(G, stations, accesses)
    add_edges(G, stations)
    return G


def show(G: MetroGraph) -> None:
    """
    Function: Displays an interactive graph of the metro in another window.
    Parameters: graph -> MetroGraph that will be displayed
    Return: A graphic representation of the metro graph.
    """
    # Calls networkx and matplotlib.pyplot functions
    coords = nx.get_node_attributes(G, 'location')
    nx.draw(G, coords, node_size=10)
    plt.show()


def plot(G: MetroGraph, filename: str) -> StaticMap:
    """
    Function: Gets image of a map of Barcelona city, prints the graph over it
              and saves it in a file.
    Parameters: graph -> MetroGraph to be printed over the image
                filename -> file containing the final image
    Return: An image file of a graphic representation of a graph in a map.
    """
    # Gets StaticMap image
    map = StaticMap(2500, 3000, 80)
    # Calls functions defined below
    map = print_lines(map, G)
    map = print_circles(map, G)
    image = map.render()
    image.save('bcn.png')


def print_lines(map: StaticMap, G: MetroGraph) -> StaticMap:
    """
    Function: Creates different lines for every type of edge of the graph.
    Parameters: map -> image map to be modified
                graph -> MetroGraph with the edges to be printed as lines
    Return: A map with the graph's edges as lines.
    """
    for edge in G.edges:
        # Tuples = (Points, colour, width)
        if G.edges[edge[0], edge[1]]["type"] == "Access":
            line = Line([G.nodes[edge[0]]["location"],
                        G.nodes[edge[1]]["location"]], "#000000", 15)
        elif G.edges[edge[0], edge[1]]["type"] == "Link":
            line = Line([G.nodes[edge[0]]["location"],
                        G.nodes[edge[1]]["location"]], "#000000", 5)
        else:
            line = Line([G.nodes[edge[0]]["location"],
                        G.nodes[edge[1]]["location"]],
                        G.edges[edge[0], edge[1]]["colour"], 5)
        map.add_line(line)
    return map


def print_circles(map: StaticMap, G: MetroGraph) -> StaticMap:
    """
    Function: Creates circles for every node of the graph by calling the
              CircleMarker function.
    Parameters: map -> image map to be modified
                graph -> MetroGraph with the nodes to be printed as circles
    Return: A map with the graph's nodes as circles.
    """
    for node in G.nodes:
        # Tuples = (Points, colour, width)
        circle = CircleMarker(G.nodes[node]["location"], "#FB0006", 7)
        map.add_marker(circle)
    return map
