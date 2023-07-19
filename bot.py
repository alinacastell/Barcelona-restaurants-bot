# Accesses functionalities dependent on the Operating System
import os
# Library used to import Telegram's API
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Library used to access different data types
from typing import Optional, Union, TextIO, List, Tuple, Dict
# Imports the city functions
import city
# Imports the metro functions
import metro
# Imports the restaurants functions
import restaurants
# Library used for the split in the find function
import re


# Done once when starting the program:
# Downloads bcn graph
bcn_graph = city.load_osmnx_graph('graf.dat')
# Downloads metro graph
metro_graph = metro.get_metro_graph()
# Creates a graph with bcn graph and metro graph.
GRAPH = city.build_city_graph(bcn_graph, metro_graph)
# Downloads the restaurant's list
restaurant_list = restaurants.read()


##################
# MAIN FUNCTIONS #
##################


def start(update, context):
    """
    Function: Greets and starts the conversation. It will run when
              the bot receives the /start message.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message greeting the user.
            A message on the terminal indicating who have started using
            MetroNyam.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name + " is using MetroNyam🚇🍕.")

    context.user_data['received_loc'] = False
    context.user_data['done_find'] = False

    # Sends a message greeting the user
    message = "Hi, " + update.effective_chat.first_name
    message += " 👋🏻! I am MetroNyam🚇🍕.\nWrite /help and I will let you "
    message += "know which are my main functions.\nPlease, send your current "
    message += "location 📍 in order to guide you to your destination 👣. \n"
    message += "Remember you need to be in Barcelona for using MetroNyam🚇🍕"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def help(update, context):
    """
    Function: Offers help on available orders. It will run when the
              bot receives the /help message.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message with the possible commands and their definitions.
            A message on the terminal indicating that help have been
            requested.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name + " is asking for help.")

    # Sends a message with all the commands and their functionality
    message = "This are my functions: \n\n•/start: starts the "
    message += "conversation. \n•/help: offers help on available orders."
    message += "\n•/author: shows the name of the project's authors."
    message += "\n•/find <query>: looks for the restaurants that satisfy "
    message += "your search (12 restaurants list at most). \nExample of "
    message += "usage: /find pizza. \n•/info <number>: shows the information "
    message += "of your chosen restaurant. \nExample of usage: /info 3. \n•"
    message += "/guide <number>: shows a map of the shortest path from your "
    message += "current location to the chosen restaurant. \nExample of usage:"
    message += " /guide 3. \n•/time <number>: returns the average time to get"
    message += "to the chosen restaurant. \nExample of usage: /time 3."
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def author(update, context):
    """
    Function: Shows the name of the project's authors. It will run when
              the bot receives the /author message.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message with the name of the authors.
            A message on the terminal indicating authors have been asked.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name + " is asking for the authors.")

    # Sends a message with the authors
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="My authors are Alina Castell, Laura Ramon and Marina Grifell.🖋️"
        )


def location(update, context):
    """
    Function: When a user sends a location it takes the position and
              saves it.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message thanking for the location and indicating what
            commands can be executed next.
            A message on the terminal indicating a location has been sent.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name + " is sending a location.")
    # Takes the location coordinates
    get_loc = update.message.location
    lat, lon = get_loc.latitude, get_loc.longitude
    context.user_data['location'] = [lon, lat]
    context.user_data['received_loc'] = True

    # Sends a message with the possible steps to follow after sending the
    # location
    message = "Thank you for sending your location, "
    message += "now we know where to start the route from.\n"
    message += "If you have already made your chose try "
    message += "/guide to get the path 👣 or /time to know how far you are"
    message += " from the restaurant of your chose ⌚️."
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def find(update, context):
    """
    Function: Looks for the restaurants that satisfy the request.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message with the list of the selected restaurants,
            12 at most.
            Returns error message if there is no query entered or if
            there are no restaurants that fullfil the request.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name +
          " is trying to find a restaurant.")
    # Sends an error message if a query is not entered
    if len(context.args) == 0:
        error_message1 = "💣 Please execute the /find function with "
        error_message1 += "any chosen request."
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message1
        )
    else:
        query: str = context.args
        # Treats each different search as a particular case
        # Case1: multiple word search
        if len(query) != 1:
            sel_list = restaurants.create_multiple(query)
        else:
            # Splits the string by every non-word character found
            pattern = r'\W+'
            splited = re.split(pattern, query[0])
            word1 = splited[0]

            # Case2: logic search
            if word1 == 'and' or word1 == 'or' or word1 == 'not':
                sel_list = restaurants.logic_search(splited, word1)

            # Case3: diffuse search
            else:
                sel_list = restaurants.find_rest(query[0],
                                                 restaurant_list)

    # Gets the twelve firsts restaurants from the resultant list
    sel_list = sel_list[:12]
    length = len(sel_list)
    context.user_data['done_find'] = True
    context.user_data['selection_list'] = sel_list

    # Sends an error message if no restaurants that fullfil the request are
    # found
    if length == 0:
        message = "💣 There are no restaurants that fullfil your request. "
        message += "Please execute the function /find again with another "
        message += "requirement.\n"
    # Prints a list of the restaurants resultant from the search
    else:
        message = "This are the restaurants that fulfil your request: \n \n"
        for i in range(1, length+1):
            message += str(i) + ". " + str(sel_list[i-1].name) + "\n"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def info(update, context):
    """
    Function: Shows the information of the chosen restaurant.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message with the information of the restaurant:
            name, address, neighborhood, district and phone number.
            An error message if there if no information entered, if
            the function is executed before /find, if the
            restaurant's number does not belong to the list provided
            or if the information entered is not a number.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name + " is asking for info.")
    # Detects the possible errors that can occur and sends an error
    # message
    error = errors(update, context, 'info')
    # If there are no errors, sends a message with the restaurants'
    # information
    if not error:
        number: int = context.args[0]
        sel_list = context.user_data['selection_list']
        message = "Restaurant's information:\n\nName: "
        message += str(sel_list[int(number)-1].name)
        message += "\nAdress: " + str(sel_list[int(number)-1].street_name)
        message += ", num "
        message += str(int(float(sel_list[int(number)-1].street_num)))
        message += "\nNeighbourhood: "
        message += str(sel_list[int(number)-1].neighbourhood)
        message += "\nDistrict: " + str(sel_list[int(number)-1].district)
        # Detects if the restaurant has no phone number
        if sel_list[int(number)-1].telf == 'nan':
            message += "\nTel. number: does not have a number"
        elif sel_list[int(number)-1].telf == '-':
            message += "\nTel. number: does not have a number"
        else:
            message += "\nTel. number: "
            message += str(sel_list[int(number)-1].telf)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
            )


def guide(update, context):
    """
    Function: Shows the user a map to get from their current
              position to destination point chosen for the
              shortest path according to the concept of speed.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message with an image of the map with the shortest
            path shown from the users location to the restaurant.
            An error message if there if no information entered, if
            the function is executed before /find, if the
            restaurant's number does not belong to the list provided,
            if the information entered is not a number or if the
            location has not been sent yet.
    """
    # Prints a message on the terminal
    print(update.effective_chat.first_name +
          " needs a path to get to the restaurant.")
    # Detects the possible errors that can occur and sends an error
    # message
    error = errors(update, context, 'guide')
    # If there are no errors, sends a message with aproximate travel
    # time and the shortest path to get to the restaurant from the
    # users location
    if not error:
        number: int = context.args[0]
        sel_list = context.user_data['selection_list']
        message1 = "Let's go!"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message1
            )
        # Gets the travel time and path and prints a time message
        time(update, context)
        message = "The fastest path to go from "
        message += "your location to "
        message += str(sel_list[int(number)-1].name) + " at "
        message += str(sel_list[int(number)-1].street_name) + ", "
        message += str(int(float(sel_list[int(number)-1].street_num))) + " is:"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
            )
        # Plots the path in the screen
        # Defines an interactive name to avoid problems when the bot is
        # executedbsimultaneously by more than one user
        name = str(update.effective_chat.first_name) + ".png"
        city.plot_path(context.user_data['path'], GRAPH,  name)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(name, 'rb')
            )
        city.delete_additional_nodes(GRAPH)
        os.remove(name)


def time(update, context) -> None:
    """
    Function: Shows the aproximate travel time from the users location
              to the chosen restaurant.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: A message with an image of the map with the shortest
            path shown from the users location to the restaurant.
            An error message if there if no information entered, if
            the function is executed before /find, if the
            restaurant's number does not belong to the list provided,
            if the information entered is not a number or if the
            location has not been sent yet.
    """
    # Detects the possible errors that can occur and sends an error
    # message
    error = errors(update, context, 'time')
    # If there are no errors, sends a message with aproximate travel
    # time
    if not error:
        number: int = context.args[0]
        sel_list = context.user_data['selection_list']
        loc = context.user_data['location']
        destiny = (float(sel_list[int(number)-1].y_coord),
                   float(sel_list[int(number)-1].x_coord))
        # Finds the shortest path
        context.user_data['path'] = city.find_path(bcn_graph, GRAPH,
                                                   loc, destiny)
        # Calculates the travel time of the shortests path
        time = city.time(GRAPH, context.user_data['path'])
        print_time(update, context, time)


######################
# AUXILIAR FUNCTIONS #
######################


def errors(update, context, func: str) -> bool:
    """
    Function: Detects all possible errors.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
                func -> name of the command
    Return: True if there is an error and False if there are no errors.
    """
    error = False
    # Error if there are no arguments sent
    if len(context.args) == 0:
        error_message1 = "💣 Please execute the /" + func + " function with "
        error_message1 += "the number of the restaurant you choose."
        error = True
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message1
        )
    else:
        number: int = context.args[0]
        # Error if there find function has not been executed yet
        if not context.user_data['done_find']:
            error_message1 = "💣 Please execute the /find function and "
            error_message1 += "try /" + func + " after."
            error = True
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message1
            )
        else:
            sel_list = context.user_data['selection_list']
            # Error if the information entered is not a number
            s = str(number)
            if not s.isdigit():
                error_message2 = "💣 Remember you need to enter a number for "
                error_message2 += "the /" + func + " function."
                error = True
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message2
                )
            # Error if if the number does not belong to the list provided
            elif int(number) <= 0 or int(number) > len(sel_list):
                error_message3 = "💣 Your chosen number is not in the list "
                error_message3 += "provided."
                error = True
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message3
                )
            # Error if the location has not been sent yet, only for guide and
            # time functions (not info)
            elif func == 'guide' or func == 'time':
                if not context.user_data['received_loc']:
                    error_message4 = "💣 We have not received your location yet"
                    error_message4 += ".\nPlease send your location to start "
                    error_message4 += " the route and try /" + func + " again."
                    error = True
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=error_message4
                        )
    return error


def print_time(update, context, time: float) -> None:
    """
    Function: Converts the provided time (sec) into hours, minutes
              and seconds.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
                time -> calculated travel time in seconds
    Return: A message of the aproximate travel time converted.
    """
    hours: float = 0
    min: float = 0
    sec: float = 0
    if time > 3600:
        hours = time/3600
    if time % 3600 >= 60:
        res = time % 3600
        min = res / 60
    if min % 60 != 0 or time < 60:
        sec = min/60
        # Aproximates seconds to minutes
        if sec > 30:
            min += 1

    # Sends a message with the aproximated travel time
    message = "The average travel time is "
    if hours == 0:
        if min == 0:
            message += " ... You are less than 1 minute away! 🤩🥳"
        else:
            message += str(int(float(min))) + " minute(s)."
    else:
        message += str(int(float(hours))) + " hour(s) and "
        message += str(int(float(min))) + " minute(s)."

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def warn(update, context) -> None:
    """
    Function: Detects if the input is not a defined command of the bot.
    Parameters: update and context -> objects that allow us to have
                more details of the user information and perform
                actions with the bot
    Return: An error message if input is not a defined command.
    """
    # Sends a message suggesting to execute the function help
    message = "'" + update.message.text + "'"
    message += " is not one of my commands. Please execute /help again to "
    message += "know which are the commands that you can use."
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


######################
# BOT INITIALIZATION #
######################


# Declares a constant with the access token that reads from token.txt
TOKEN = open('token.txt').read().strip()

# Creates objects to work with Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Exectutes the warning function to detect possible input errors
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), warn))
# Indicates when the bot receives a command and exectutes its function
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(CommandHandler('find', find))
dispatcher.add_handler(CommandHandler('info', info))
dispatcher.add_handler(CommandHandler('guide', guide))
dispatcher.add_handler(CommandHandler('time', time))

# Starts the bot
updater.start_polling()
updater.idle()
