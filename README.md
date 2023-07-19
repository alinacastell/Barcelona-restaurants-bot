# Barcelona-restaurants-bot

*Choose a restaurant and go there by metro!* 🍕 🚇

## Introducció

This README deals with the specifications of the **MetroNyam** project.

**MetroNyam** calculates and displays the fastest route from any point in Barcelona to any restaurant. The restaurant is chosen from a list of restaurants based on the preferences specified. The journey is made both by metro and on foot. The communication is done through a Telegram chat.

The *README* is organised according to the modules needed to implement the code. We specify the main functions of each one and the aspects that have been taken into account when implementing certain functions.

### Requirements

The necessary requirements for the execution of the code are a list of libraries, which we mention in the corresponding module, the use we make of them is explained in the code. In the following file we attach the commands used for their installation:

- [Requirements](https://github.com/alinacastell/Projecte2-AP2/blob/main/requirements.txt) - File with installations list

For example:
```
Bot:
pip3 install telegram
pip3 install python-telegram-bot 
pip3 install re
```

The code style is based on `pycodestyle`

## `restaurants` module

The main function of this module is to read the data of the restaurants in Barcelona (obtained from a csv file), save them in a list and make a list of the restaurants that meet certain requirements.

In this module a class is defined that contains the attributes of each restaurant. The defined attributes have been chosen for their usefulness in functions and also for their informative interest shown in the bot module.


The search of the restaurants filtered by a certain request is done in the following way:

We have a variable with the number of matches from 0 to 100. Then we prioritise the matches equal to 100, these will be the first to appear in the list of the restaurants provided. As we have implemented the search by multiple words, sometimes we it is not enough with the words with a match of 100 when we join the two matches. That is why we have separated the case of filling the list up to a match equal to 80, which will come after the match equals to 100. We have made a condition that if neither a match equal to 100 nor a match equal to 80 contains a minimum of 12 restaurants in the list, we make a last match with a match equal to 60.

In all of the above cases, the restaurants have been added to the list taking into account the elements that were already added, so as not to duplicate restaurants. Apart from these matching priorities, the restaurants are provided in the order the csv is read. Furthermore, a `drop_duplicates` has been applied to the read function in order to avoid having duplicate restaurants provided in the csv.


In our case, the three proposed optional implementations of more powerful searches have been done. Next, we will explain how to use them correctly:

- *Diffuse Search*: In this case, the search is implemented to detect similar words in order to avoid possible typing errors in the search. The way to use it is as follows: `/find <query>`, example of query: `pzza`, `piza`, `puzza`... instead of `pizza` and the result should be the same.

- *Multiple-word query*: In this case, the search is implemented to make a sarch with several queries. The final result should be a search of the intersections of the queries. The way to use it is the following: `/find <query>`, query examples: `pizza gracia`, `sushi sants`, `pizza hamburger`.... The diffuse search is also included in this one, therefore, the query can contain typing errors.

- *Logical search*: In this case, the search implements the logical operators `and`, `or` and `not`. The entries in this case would be: `and(expr,expr)`, `or(expr,expr)` and `not(expr)` or a combination of these, for example: `and(or(expr,expr),and(expr,expr))`. Therefore, the way to use it should be: `/find <query>`, with the query being the expressions mentioned above. The diffuse searcg is also included in this one, therefore, the query can contain typing errors.

## `metro` module

The main function of this module is to create a graph of the Barcelona MetroGraph metro network including stations and accesses. This graph contains information about the metro stations, their track sections, accesses and transfers. The nodes of this graph are of type station and access and the arrows are of type access, transfer and road; all have their own attributes.

The attributes defined for the two types of node have been chosen for their usefulness in various functions. For stations they are the station identifier number; the name of the station; which metro line it runs on; the exact location in latitude and longitude; the station code, which is a unique number; in relation to its line, what stop number it is; and the colour of its line. For accesses they are the identifying number; the name of the access; the exact location in latitude and longitude; the access code; and accessibility].

This module defines the classes that contain the attributes of the nodes and arrays of the metro graph. The corresponding csv files are read. A metro graph is created using own functions implemented in the same module and calling functions from external libraries.

In addition, we comment that in this module it is also possible to show the resulting graph of the Barcelona metro network, however, for the rest of the project it is not necessary and that is why when this module is executed it is not shown every time.

## `city` module

The city module is responsible for creating and consulting the city map that will represent all the information needed to get from one crossroad in the city of Barcelona to another as quickly as possible on foot or by metro. The city map will be an undirected graph resulting from the merge of two other graphs: the Barcelona streets graph (which will be provided by the `osmnx` module) and the metro graph (which will be provided by the `metro` module). The city graph will be of the following type: `CityGraph : TypeAlias = networkx.Graph. Each edge will have an attribute `info` of type `Edge`, which includes three fields:
- `type`: Indicates whether it is a `railway`, `link` or `street` type edge.
- `colour`: Represents the colour with which we have to paint each of the edges of the graph.
- `distance`: Counts the distance between two nodes joined by a given line. These three fields have been chosen according to the needs that will appear throughout the module.

First of all, we create the `CityGraph`. To do this, we create an empty graph of this type and copy each of the nodes and edges of the graph of the streets of Barcelona. Then, we repeat this procedure with the metro graph. So, the city's graph already contains the graph of the streets and the metro, now we have to join them so that they are connected. Therefore, for each `access` type node, we look for the nearest `OsmnxGraph` node and we join them by means of a new `street` node. This tab, as each one of the `CityGraph`'s arrays, will contain the two nodes that it links, the previously defined as `info` type attribute and the distance that is traced to traverse the edge. We obtain the time it takes to go from one node to another by dividing the distance of the nodes by the speed. This speed will depend on the type of line on which we travel. We have approximated the metro time (`railway` type node) and the walking time (`street` type node) to the maximum according to the times provided by Google Maps. The metro time has been slightly decreased, as it moves at approximately 7.2m/s, but this speed does not take into account the stops. On the other hand, we have also decreased the speed of the `link` type nodes, because walking along the transfers is slower than walking along the road. Moreover, this also helps us to avoid unnecessary line changes and to get as close as possible to the Google Maps result.

Secondly, once we have the `CityGraph`, we deal with the second objective of this module: to find the shortest distance to go from one part of the city to another. To do this, we add to our `CityGraph` a node to the user's starting point and a node to the destination he/she wishes to reach. These are connected to the graph using the shortest_path function of networkx. Once the action is finished, we delete these two additional nodes from the graph to avoid errors during execution.

Finally, once we have the desired path, we paint it on the map of Barcelona so that the user knows where to go. To make the map more interpretative, we have decided to paint the sections that the user has to walk on foot in black. On the other hand, the sections that are by metro appear in the colour corresponding to the metro line. Finally, we have created a function that returns the time taken to travel a certain route.

## `bot` module

The `bot` module is responsible for the connection of the rest of the modules and their presentation via **Telegram**. It is the module that allows interacting with the programme and obtaining the results. Attached is an example video of how does the bot work, also as a way of presenting the final result.

[Video](https://youtube.com/shorts/4conTO2cq1c)

In our case, an extra command has been added to the bot:
- `/time <number>`: returns the approximate travel time from the user's location to the chosen restaurant. In this way, it can serve as an extra piece of information when choosing a restaurant. This function can be requested after making a `/find`. It is also returned automatically whenever a `/guide` is made.

We thought it was useful to define this extra function because the code had to be implemented anyway in the `/guide`. We think that the possibility of calling the function also as a command is a way to give more use to the code and we also think that it can be useful for the user. The approximate walking time can be a decisive factor when choosing a restaurant.

### Errors

In our case, the following error detection messages have been added. These should be taken into account when using the relevant commands in the bot:

- There is a particular case of an error that has been dealt with in a general way. This is the case of an error message if anything other than a command is sent to the bot.

- If you try to send any of the commands `/find`, `/info`, `/guide` or `/time` without passing the necessary input information, query or number, an error message is sent.

- A message is also sent warning that there are no search results if the `/find` is not able to form a list of restaurants.

- If you try to use the `/guide` or `/time` function without having previously sent a location, an error message is also displayed on the screen.

The rest of the error messages are included in the three functions `/info`, `/guide` and `/time`:

- Error message if any of these functions is executed before doing a `/find` because we need a `<number>` from the list to be able to call them.

- An error message also appears on the screen if the information entered together with the function name is not a `<number>`.

- If the `<number>` provided does not belong to the list provided by find, an error message will also be displayed on the screen.

Finally, a whole series of auxiliary functions have been created to facilitate the reading and understanding of the program, which are attached after all the functions related to the commands. The particular auxiliary functions of the `/find` just above have been added to make them easier to read, as we believe that it is easier to have them at hand when reading the relevant code.


## Authors

Laura Ramon, Marina Grifell i Alina Castell.

Data Science and Engineering, 
Universitat Politècnica de Catalunya, 2022
