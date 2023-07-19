"""
Template file for city.py module.

This module creates and consultes the city graph, an unidrected graph formed
by the fusion of two other graphs: the graph of the streets of Barcelona
(provided by the osmnx module) and the metro graph (provided by the metro
module).
This graph will contain all the necessary information to know the fastest path
to get from one point of the city of Barcelona to another on foot or by metro.
"""

# Library used to initialize classes
from dataclasses import dataclass
# Library used to access different data types
from typing import Optional, Union, TextIO, List, Tuple, Dict
# Library used to generate undirected graphs of networkx
from typing_extensions import TypeAlias
# Library used to manipulate graphs
import networkx as nx
# Library used to get the graph of the streets of Barcelona
import osmnx as ox
# Library used to get the metro graph
from metro import *
# Library used to read csv docs
import pandas as pd
# Library used to draw a graph interactively
import matplotlib.pyplot as plt
# Library used to draw a graph on a picture
from staticmap import StaticMap, Line, CircleMarker
# Library used to draw a graph interactively
import matplotlib.pyplot as plt
# Library used to pickle and unpickle graphs in order to save them
import pickle
# Library used to access, read or write files
import os.path
# Library used to calculate distances between two points
import haversine as hs

CityGraph: TypeAlias = nx.Graph  # Undirected graph from networkx

OsmnxGraph: TypeAlias = nx.MultiDiGraph  # Directed graph with parallel edges

Coord: TypeAlias = Tuple[float, float]  # Tuple of a coord

NodeID: TypeAlias = Union[int, str]  # COMENTAR

Path: TypeAlias = List[NodeID]


@dataclass
class Edge:
    """
    Class: Contains the attributes of an edge.
    """
    type: str  # Railway, link, street
    colour: str
    distance: str


def get_speed(type: str) -> float:
    """
    Function: Assigns a speed for every type of edge.
    Parameters: type -> type of edge
    Return: The average speed in (m/s).
    """
    if type == "Railway":
        return 7.2
    if type == "Link":
        return 0.8
    return 1.4


def get_osmnx_graph() -> OsmnxGraph:
    """
    Function: Gets a graph with all Barcelona's streets, provided by the osmnx
              module.
    Parameters: None
    Return: Barcelona's streets graph with all its information.
    """
    g = ox.graph_from_place('Barcelona, Spain', network_type='walk',
                            simplify=True)
    # Calls function defined below
    save_osmnx_graph(g, 'graf.dat')
    return g


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    """
    Function: Saves the street graph into a given file.
    Parameters: g -> Barcelona's streets graph
                filename -> file containing the final graph
    Return: None.
    """
    # Goes through all OsmnxGraph edges
    for u, v, key, geom in g.edges(data="geometry", keys=True):
        if geom is not None:
            del(g[u][v][key]["geometry"])
    # Writes a pickle representation of the graph g in pickle_file
    pickle_file = open(filename, 'wb')
    pickle.dump(g, pickle_file)
    pickle_file.close()


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    """
    Function: Downloads the street graph from a given file.
    Parameters: g -> Barcelona's streets graph
                filename -> file containing the final graph
    Returns: The downloaded OsmnxGraph.
    """
    if os.path.exists(filename):
        # Reads an unpickled graph stored in pickle_file
        pickle_file = open(filename, 'rb')
        result = pickle.load(pickle_file)
        pickle_file.close()
        return result
    # Calls function previously defined
    return get_osmnx_graph()


def get_accesses(metro: MetroGraph) -> List:
    """
    Function: Given a metro graph, stores all its accesses nodes.
    Parameters: metro -> Metro graph
    Return: List with all the nodes of access type.
    """
    accesses: List = []
    for node in metro.nodes:
        if metro.nodes[node]["type"] == "access":
            accesses.append(node)
    return accesses


def get_coords(x: List, y: List, accesses: List, metro: MetroGraph) -> None:
    """
    Function: Stores the longitude and latitude of each access of the metro
              graph into 2 diferent lists.
    Parameters: x -> List of longitudes of all accesses
                y -> List of latitudes of all accesses
                accesses -> List with all access nodes of the metro graph
                metro -> Metro graph
    Return: None.
    """
    for access in accesses:
        x.append(metro.nodes[access]["location"][0])
        y.append(metro.nodes[access]["location"][1])


def link(city: CityGraph, street: OsmnxGraph, metro: MetroGraph) -> None:
    """
    Function: Connects the street and metro graph into the city graph.
    Parameters: city -> City graph (merge of street and metro graphs)
                street -> Barcelona's streets graph
                metro ->  Metro graph
    Return: None.
    """
    x_coords: List = []
    y_coords: List = []

    # Calls function previously defined
    llista_accessos: List = get_accesses(metro)
    get_coords(x_coords, y_coords, llista_accessos, metro)

    # For each acces node, saves its nearest node and their distance into
    # two different lists
    nearest_nodes, dist = ox.distance.nearest_nodes(street, x_coords, y_coords,
                                                    return_dist=True)

    for i in range(0, len(llista_accessos)):
        info = Edge("Street", "#F3A83B", dist[i])
        # Calls networkx function
        city.add_edge(llista_accessos[i], nearest_nodes[i], attributes=info,
                      time=dist[i]/get_speed("Street"))


def build_bcn_graph(gb: OsmnxGraph, gc: CityGraph) -> None:
    """
    Function: Duplicates the Barcelona's OsmnxGraph into the CityGraph.
    Parameters: gb -> Barcelona's streets graph
                gc -> City graph (merge of street and metro graphs)
    Return: None.
    """
    # PREGUNTAR MARC
    # Goes through ...
    for u, nbrsdict in gb.adjacency():
        x_coord1: float = gb.nodes[u]["x"]
        y_coord1: float = gb.nodes[u]["y"]
        gc.add_node(u, type="Street", location=[x_coord1, y_coord1])
        # Goes through ...
        for v, edgesdict in nbrsdict.items():
            x_coord2: float = gb.nodes[v]["x"]
            y_coord2: float = gb.nodes[v]["y"]
            gc.add_node(v, type="Street", location=[x_coord2, y_coord2])
            dist = edgesdict[0]["length"]
            info = Edge("Street", "#FAF660", dist)
            gc.add_edge(u, v, attributes=info, time=dist/get_speed("Street"))


def build_metro_graph(gm: MetroGraph, gc: CityGraph) -> None:
    """
    Function: Duplicates the MetroGraph into the CityGraph.
    Parameters: gm -> Metro graph
                gc -> City graph (merge of street and metro graphs)
    Return: None.
    """
    for node in gm.nodes:
        gc.add_node(node, type=gm.nodes[node]["type"],
                    location=gm.nodes[node]["location"])
    for edge in gm.edges:
        # Calculates distance (meters) using haversine function
        dist = hs.haversine(gm.nodes[edge[0]]["location"],
                            gm.nodes[edge[1]]["location"], unit="m")
        info = Edge(gm.edges[edge[0], edge[1]]["type"], gm.edges[edge[0],
                    edge[1]]["colour"], dist)
        gc.add_edge(edge[0], edge[1], attributes=info,
                    time=dist/get_speed(gm.edges[edge[0], edge[1]]["type"]))


def build_city_graph(g1: OsmnxGraph, g2: MetroGraph) -> CityGraph:
    """
    Function: Creates the city graph by connecting OsmnxGraph and MetroGraph.
              Connects each access node of MetroGraph with each nearest node of
              OsmnxGraph.
    Parameters: g1 -> Barcelona's streets graph
                g2 -> Metro graph
    Return: City graph (merge of g1 and g2)
    """
    g = nx.Graph()
    # Calls function previously defined
    build_bcn_graph(g1, g)
    build_metro_graph(g2, g)
    # Removes possible loops between edges and nodes using networkx function
    g.remove_edges_from(nx.selfloop_edges(g))
    link(g, g1, g2)
    return g


def show_graph(g: CityGraph) -> None:
    """
    Function: Shows a fully interactive graph of the CityGraph in another
              window.
    Parameters: g -> City graph (merge of street and metro graphs)
    Return: None.
    """
    coords = nx.get_node_attributes(g, 'location')
    nx.draw(g, coords, node_size=10)
    plt.show()


def plot_graph(g: CityGraph, filename: str) -> StaticMap:
    """
    Function: Plots the city graph over an image of Barcelona's map.
    Parameters: g -> City graph (merge of street and metro graphs)
                filename -> file containing the final image
    Return: An image file of a graphic representation of a graph in a map.
    """
    # Gets StaticMap image
    m = StaticMap(2500, 3000, 80)
    # Calls functions defined below
    m = print_lines_graph(m, g)
    m = print_circles_graph(m, g)
    image = m.render()
    image.save(filename)


def print_lines_graph(m: StaticMap, g: CityGraph) -> StaticMap:
    """
    Function: Prints all the edges of g over m
    Parameters: m -> image graph to be modified
                g -> City graph (fusion of street and metro graphs)
    Return: An image file of a graphic representation of a graph in a map.
    """
    for edge in g.edges:
        # Given an edge, line get's the location of their 2 nodes, the colour
        # of that edge, i el gruix amb el qual imprimirem l'aresta.
        line = Line([g.nodes[edge[0]]["location"],
                    g.nodes[edge[1]]["location"]], g.edges[edge[0],
                    edge[1]]["attributes"].colour, 5)
        m.add_line(line)
    return m


def print_circles_graph(m: StaticMap, g: CityGraph) -> StaticMap:
    """
    Function: Prints all the nodes of g over m
    Parameters: m -> image graph to be modified
                g -> City graph (fusion of street and metro graphs)
    Return: An image file of a graphic representation of a graph in a map.
    """
    for node in g.nodes:
        tipus = g.nodes[node]["type"]
        if tipus == "access":
            colour = "#000000"
        elif tipus == "Street":
            colour = "#367C22"
        else:
            colour = "#E93224"

        # Given a node, circle gets it's location, it's colour and el gruix amb
        # el qual imprimirem el node.
        circle = CircleMarker(g.nodes[node]["location"], colour, 7)
        m.add_marker(circle)
    return m


def find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> Path:
    """
    Function: Finds the shortest path from source to destiny.
    Parameters: ox_g -> Barcelona's streets graph
                g -> City graph (merge of street and metro graphs)
                src -> Coordinate of the starting point
                dst -> Coordinate of the final point
    Return: Returns a Path.
    """
    # For source and destiny nodes, saves their nearest node and their distance
    # into two different lists
    nearest_nodes, dist = ox.distance.nearest_nodes(ox_g, [src[0], dst[0]],
                                                    [src[1], dst[1]],
                                                    return_dist=True)
    # Connects the source and destiny nodes to the CityGraph
    g.add_node('src', location=src)
    edge1 = Edge("Street", "#000000", dist[0])
    g.add_edge('src', nearest_nodes[0], attributes=edge1,
               time=dist[0]/get_speed("Street"))
    g.add_node('dst', location=dst)
    edge2 = Edge("Street", "#000000", dist[1])
    g.add_edge('dst', nearest_nodes[1], attributes=edge2,
               time=dist[0]/get_speed("Street"))
    # Looks for the shortest path using networkx function
    return nx.shortest_path(g, source="src", target="dst", weight="time")


def delete_additional_nodes(g: CityGraph) -> None:
    """
    Function: Deletes the source and destiny nodes added to the CityGraph in
              the function find_path(...) previously definded.
    Parameters: g -> City graph (merge of street and metro graphs)
    Return: None.
    """
    g.remove_node('src')
    g.remove_node('dst')


def plot_path(path: Path, city: CityGraph, filename: str) -> None:
    """
    Function: Plots the Path over an image of Barcelona's map.
    Parameters: path: COMENTAR
                city -> City graph (merge of street and metro graphs)
                filename -> file containing the final image
    Return: None.
    """
    m = StaticMap(2500, 3000, 80)
    path_lines(m, path, city)
    path_nodes(m, path, city)
    image = m.render()
    image.save(filename)


def path_nodes(m: StaticMap, path: Path, city: CityGraph) -> None:
    """
    Function: Prints all the nodes of the Path over the StaticMap.
    Parameters: m -> image graph to be modified
                path -> List of node's id COMENTAR
                city -> City graph (fusion of street and metro graphs)
    Return: None.
    """
    for element in path:
        circle = CircleMarker(city.nodes[element]["location"], "#000000", 7)
        m.add_marker(circle)


def path_lines(m: StaticMap, path: Path, city: CityGraph) -> None:
    """
    Function: Prints all the edges of CityGraph over the StaticMap.
    Parametres: m -> image graph to be modified
                path -> COMENTAR
                city -> City graph (fusion of street and metro graphs)
    Return: None.
    """
    for i in range(1, len(path)):
        edge_type = city.edges[path[i-1], path[i]]["attributes"].type
        if edge_type != "Street":
            colour = city.edges[path[i-1], path[i]]["attributes"].colour
        else:
            colour = "#000000"
        line = Line([city.nodes[path[i-1]]["location"],
                     city.nodes[path[i]]["location"]], colour, 10)
        m.add_line(line)


def time(g: CityGraph, path: Path) -> float:
    """
    Function: Calculates the average travel time.
    Parameters: g -> City graph (fusion of street and metro graphs)
                path -> COMENTAR
    Return: Float containing the average time.
    """
    time = 0
    for i in range(1, len(path)):
        time += g.edges[path[i-1], path[i]]["time"]
    return time
