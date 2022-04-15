import requests
import textwrap
import shutil
import math
import argparse
import os
import sys
from time import sleep
from xml.etree import ElementTree
import logging
from urllib.parse import urlencode, quote
from datetime import datetime
import contextlib

starttime = datetime.now()
######### Begin Classes #########

class config:
    def __init__(self, args):
        self.LOGLEVEL                = os.environ.get('LOGLEVEL', 'INFO').upper()
        self.bgg                     = 'https://boardgamegeek.com/xmlapi2'
        self.successful_responses    = 0
        self.dict_player_count       = {}
        self.dict_category           = {}

        self.user_name               = args.username
        self.card_mode               = args.cardmode or False
        self.index                   = args.index    or False
        self.only_own                = args.own      or False

        self.template                = "./template.html"
        self.card_template           = "./template_card.html"

        self.output                  = args.output if len(args.output) > 0 else"./output.html"
        self.collection_xml          = args.collection_xml if len(args.collection_xml) > 0 else"./collection.xml"
        self.images_path             = args.images_path if len(args.images_path) > 0 else"./Images"
        self.xml_path                = args.xml_path if len(args.xml_path) > 0 else"./game_xml"

        self.sleep_time              = int(args.minsleep) if len(args.minsleep) > 0 else 10
        self.sleep_time_max          = int(args.maxsleep) if len(args.maxsleep) > 0 else 120

class collection_information:
    def __init__(self, item, config):
        self.obj_id     = item.attrib['objectid']
        self.game_name  = item.find('name').text
        self.game_xml   = os.path.join(config.xml_path, self.obj_id + '.xml')
        self.own        = item.find('status').attrib['own'] == "1"
        self.my_rating  = item.find('stats').find('rating').attrib['value']
        self.avg_rating = item.find('stats').find('rating').find('average').attrib['value']

class game_information:
    def __init__(self, items, config, collection_info):
        self.image                  = get_prop_text(items, 'image')
        self.name                   = get_prop_value(items, 'name')
        self.obj_id                 = collection_info.obj_id
        self.my_rating              = collection_info.my_rating
        self.avg_rating             = collection_info.avg_rating
        self.minplayers             = str(get_prop_value(items, 'minplayers') or '')
        self.maxplayers             = str(get_prop_value(items, 'maxplayers') or '')
        self.published              = get_prop_value(items, 'yearpublished')
        self.publisher              = get_value_in_list(get_links(items, 'boardgamepublisher'), 0)
        self.designer               = get_value_in_list(get_links(items, 'boardgamedesigner'), 0)
        self.artist1                = get_value_in_list(get_links(items, 'boardgameartist'), 0)
        self.artist2                = get_value_in_list(get_links(items, 'boardgameartist'), 1)
        self.category1              = get_value_in_list(get_links(items, 'boardgamecategory'), 0)
        self.category2              = get_value_in_list(get_links(items, 'boardgamecategory'), 1)
        self.mechanic1              = get_value_in_list(get_links(items, 'boardgamemechanic'), 0)
        self.mechanic2              = get_value_in_list(get_links(items, 'boardgamemechanic'), 1)
        self.mechanic3              = get_value_in_list(get_links(items, 'boardgamemechanic'), 2)
        self.mechanic4              = get_value_in_list(get_links(items, 'boardgamemechanic'), 3)
        self.mintime                = str(get_prop_value(items, 'minplaytime') or '')
        self.maxtime                = str(get_prop_value(items, 'maxplaytime') or '')
        self.avg_weight             = items.find('statistics').find('ratings').find('averageweight').attrib['value']
        self.three_mechanics_length = len((self.mechanic1 or "") + (self.mechanic2 or "") + (self.mechanic3 or ""))
        self.four_mechanics_length  = len((self.mechanic1 or "") + (self.mechanic2 or "") + (self.mechanic3 or "") + (self.mechanic4 or ""))
        self.description            = textwrap.shorten(get_prop_text(items, 'description') or "", width=get_description_length(config), placeholder='...')

######### End Classes #########

######### Begin Functions #########

#command is an api command from BGG (user, collection, etc)
#params is a dictionary with parameter/value pairs for the command
def bgg_getter (command, params, config):
    sleep(.3)
    status = 0
    a = ''
    while not status == 200:
        url = '{}/{}?{}'.format(config.bgg,
                                quote(command),
                                urlencode(params),
                                )
        logging.debug(url)
        a = requests.get(url)
        status = a.status_code
        if(status != 200):
            error = ElementTree.fromstring(a.content)
            print(error);
            logging.info("Sleeping " + str(config.sleep_time) + " Seconds: " + (error.find('message').text if error != None else str(status)))
            sleep(config.sleep_time)
            config.sleep_time *= 2
            config.sleep_time = min(config.sleep_time_max,config.sleep_time)
            config.successful_responses = 0
        else:
            config.successful_responses += 1
            if(config.successful_responses % 15 == 0):
                config.sleep_time /= 2
                config.sleep_time = max(10,config.sleep_time)
    return a

def parse_arguments():
    parser = argparse.ArgumentParser(description='Create an html/pdf output of board game collection based on UserName from boardgamegeek.com.')
    parser.add_argument('-u','--username', dest='username', action='store', default='', help='User to pull BGG collection data from. (Required)')
    parser.add_argument('-c','--cardmode', dest='cardmode', action='store_true', help='Create cards instead of a catalog. (default=Off)')
    parser.add_argument('-i','--index', dest='index', action='store_true', help='Enables creating an index. (default=Off)')
    parser.add_argument('--clean_images', dest='clean_images', action='store_true', help='Clear out local images cache. (default=Off)')
    parser.add_argument('--clean_xml', dest='clean_xml', action='store_true', help='Clear out local xml cache. (default=Off)')
    parser.add_argument('--clean_all', dest='clean_all', action='store_true', help='Clear out Images, XML, and all other generated files (default=Off)')
    parser.add_argument('-o','--own',dest='own', action='store_true', help='Enables pulling only games set to own on BGG. (default=Off)')
    parser.add_argument('--minsleep', dest='minsleep', action='store', default='', help='Minimum sleep duration on XML error. (Default=10)')
    parser.add_argument('--maxsleep', dest='maxsleep', action='store', default='', help='Maximum sleep duration on XML error. (Default=120)')
    parser.add_argument('--output', dest='output', action='store', default='', help='Output html file. (Default="./output.html")')
    parser.add_argument('--images_path', dest='images_path', action='store', default='', help='Images path. (Default="./Images")')
    parser.add_argument('--xml_path', dest='xml_path', action='store', default='', help='Game XML Path. (Default="./game_xml")')
    parser.add_argument('--collection_xml', dest='collection_xml', action='store', default='', help='Output collection XML file.(Default="./collection.xml")')
    return parser.parse_args()

def get_value(item):
    return item.attrib['value']

def get_value_in_list(item, i):
    if(len(item) <= i):
        return None
    else:
        return item[i].attrib['value']

def get_prop_text(elem, name):
    elem = elem.find(name)
    if elem is not None:
        return elem.text

def get_prop_value(elem, name):
    elem = elem.find(name)
    if elem is not None:
        return get_value(elem)

def get_links(elem, name):
    values = []
    elem = elem.findall('link')
    for item in elem:
        if (item.attrib['type'] == name):
            if item is not None:
                values.append(item)
    return values

def open_template(config):
    if(config.card_mode):
        with open(config.card_template, 'r') as file:
            return file.read()
    else:
        with open(config.template, 'r') as file:
            return file.read()

def get_mechanics_list_max_length(config):
    if(config.card_mode):
        return 65
    else:
        return 75

def get_description_length(config):
    if(config.card_mode):
        return 450
    else:
        return 1000

def template_to_output_entry(config, game_info):
    mechanics_list_max_length = get_mechanics_list_max_length(config)

    #Read the template.
    template = open_template(config)

    #Replace values in the template.
    template = template.replace('{{image}}'         , os.path.join(config.images_path, game_info.obj_id + ".jpg") or "")
    template = template.replace('{{GameName}}'      , game_info.name                            or "N/A")
    template = template.replace('{{Description}}'   , game_info.description                     or "N/A")
    template = template.replace('{{Published}}'     , game_info.published                       or "N/A")
    template = template.replace('{{Publisher}}'     , game_info.publisher                       or "N/A")
    template = template.replace('{{Designer}}'      , game_info.designer                        or "N/A")
    template = template.replace('{{Artist}}'        , game_info.artist1                         or "N/A")
    template = template.replace('{{Category}}'      , (game_info.category1                      or "") + "<br/>" + (game_info.category2 or ""))
    template = template.replace('{{Cat0}}'          ,         (game_info.mechanic1              or ""))
    template = template.replace('{{Cat1}}'          , " , " + (game_info.mechanic2              or ""))
    template = template.replace('{{Cat2}}'          , " , " + (game_info.mechanic3              or "") if (mechanics_list_max_length >= game_info.three_mechanics_length) else "")
    template = template.replace('{{Cat3}}'          , " , " + (game_info.mechanic4              or "") if (mechanics_list_max_length >= game_info.four_mechanics_length) else "")
    template = template.replace('{{p}}'             , game_info.minplayers + " - " + game_info.maxplayers)
    template = template.replace('{{d}}', str(game_info.mintime) + " - " + str(game_info.maxtime) if (int(game_info.mintime) < int(game_info.maxtime)) else str(game_info.mintime))
    template = template.replace('{{Weight}}'        , str(round(float(game_info.avg_weight) * 2, 1) )) #Weight is doubled to be on the same scale with rating.
    template = template.replace('{{Rating}}', str(round(float(game_info.avg_rating), 1)) if ("N/A" in game_info.my_rating) else str(round((float(game_info.avg_rating) + float(game_info.my_rating)) / 2, 1)))

    #Write to output.html
    with open('output.html', 'a', encoding="utf-8") as file:
        file.write(template)

def download_image(config, game_info):
    #If we have a local cache of the image, then don't try to redownload it, use the local copy.
    if(os.path.exists(os.path.join(config.images_path, game_info.obj_id + ".jpg")) == False):
        #Download the image to the local cache.
        res = requests.get(game_info.image, stream = True)
        if res.status_code == 200:
            logging.info("Writing: " + collection_info.game_name + " boxart to " + os.path.join(config.images_path, game_info.obj_id + ".jpg"))
            with open(os.path.join(config.images_path, game_info.obj_id + ".jpg"), 'wb') as f:
                shutil.copyfileobj(res.raw, f)

def break_if_required(file, line_text, do_break):
    if(do_break):
        file.write("</ul>\n")
        file.write('<p style="page-break-after: always;"></p>\n')
        file.write("<ul>\n")
        if(len(line_text) > 0):
            file.write("<br><li><b>" + line_text + "</b></li>\n")

def validate_username(user_name):
    validUserName   = False
    while not validUserName:
        thisdata = bgg_getter('user', {'name': user_name}, config)
        root = ElementTree.fromstring(thisdata.content)
        if root.attrib['id']:
            validUserName = True
            logging.info(f'UserName: {user_name} is valid')
        else:
            logging.warning(f'UserName: {user_name} was not valid')
            user_name = input("Enter your BGG UserName: ")
    return user_name

def clean_up(config):
    if args.clean_images or args.clean_xml or args.clean_all:
        logging.info('Cleaning...')
        if args.clean_images or args.clean_all:
            for f in os.listdir(config.images_path):
                if(os.path.exists(os.path.join(config.images_path, f))):
                    if(f == 'icon_players.png' or f == 'icon_duration.png'):
                        continue
                    os.remove(os.path.join(config.images_path, f))
        if args.clean_xml or args.clean_all:
            if(os.path.exists(config.collection_xml)):
                os.remove(config.collection_xml)
            for f in os.listdir(config.xml_path):
                if(os.path.join(config.xml_path, f)):
                    os.remove(os.path.join(config.xml_path, f))
        if args.clean_all:
            with contextlib.suppress(FileNotFoundError):
                os.remove(config.output)
                os.remove(config.collection_xml)
        sys.exit()

def write_output_header(config):
    with open(config.output, 'w') as file:
        if(config.card_mode):
            file.write('<html><head><link href="style_card.css" rel="stylesheet" type="text/css"></head><body>')
        else:
            file.write('<html><head><link href="style.css" rel="stylesheet" type="text/css"></head><body>')

def read_collection(config):
    #Check if collection.xml exists. If it does, read it.
    if(os.path.exists(config.collection_xml)):
        logging.warning('Reading ' + config.collection_xml)
        with open(config.collection_xml, 'r', encoding="utf-8") as file:
            return ElementTree.fromstring(file.read())

    #Otherwise we request the XML from BGG
    else:
        logging.warning('Reading collection from bgg')

        status = 0
        params = {'username': config.user_name, 'stats': 1}

        if config.only_own:
            params['own'] = 1

        collection_response = bgg_getter('collection',params, config)
        with open(config.collection_xml, 'w', encoding="utf-8") as file:
            file.write(collection_response.text)
            return ElementTree.fromstring(collection_response.content)

def download_and_split_collection_object_info(config, newids):
    newgamexmls = bgg_getter('thing', {'id': ','.join(newids), 'stats': 1}, config)
    for item in ElementTree.fromstring(newgamexmls.content):
        game_xml_path = os.path.join(config.xml_path, item.attrib['id'] + '.xml')
        with open(game_xml_path, 'w', encoding='utf-8') as file:
            logging.info(f'Writing to {game_xml_path}')
            file.write(ElementTree.tostring(item, encoding='unicode'))

def find_and_download_new_collection_object_info(config, collection):
    newids = set()
    for item in collection:
        collection_info = collection_information(item, config)
        if not (os.path.exists(collection_info.game_xml)):
            newids.add(collection_info.obj_id)
            logging.debug(f'Adding ID: {collection_info.obj_id} for download')
        else:
            logging.debug(f'Skipping ID: {collection_info.obj_id} for download')
        if len(newids)>100:
            logging.debug(f'Collected 100 ids - passing for download')
            download_and_split_collection_object_info(config, newids)
            newids = set()
    if newids:
        logging.debug(f'Downloading remaining new ids')
        download_and_split_collection_object_info(config, newids)

def gather_index_info(config, gameinfo, item):
    for count in range(int(gameinfo.minplayers), int(gameinfo.maxplayers)):
        if(count not in config.dict_player_count):
            config.dict_player_count[count] = []
        config.dict_player_count[count].append(gameinfo)

    for x in get_links(item, 'boardgamecategory'):
        category = x.attrib['value']
        if(category not in config.dict_category):
            config.dict_category[category] = []
        config.dict_category[category].append(gameinfo)

def write_index(config):
    if(config.index):

        with open(config.output, 'a') as file:
            i = 1
            break_point = 250

            file.write('<p style="page-break-after: always;"></p>\n')
            file.write("<ul>\n")
            for count in range(1,10):
                file.write("<br><li><b>" + str(count) + " player games:" + "</b></li>\n")
                i += 1
                break_if_required(file, "",i % break_point == 0)
                for game in config.dict_player_count[count]:
                    file.write("<li>" + game.name + "</li>\n")
                    i += 1
                    break_if_required(file, str(count) + " player games:", i % break_point == 0)
            file.write("</ul>\n")

            i = 1
            break_point = 250

            file.write('<p style="page-break-after: always;"></p>\n')
            file.write('<ul>\n')
            for cat in sorted(config.dict_category):
                file.write("<br><li><b>" + str(cat) + " games:" + "</b></li>\n")
                i += 1
                break_if_required(file, "", i % break_point == 0)
                for game in config.dict_category[cat]:
                    file.write("<li>" + game.name + "</li>\n")
                    i += 1
                    break_if_required(file, str(cat) + " games:", i % break_point == 0)
            file.write("</ul>\n")

def write_output_trailer(config):
    #Write the html trailer.
    with open(config.output, 'a') as file:
            file.write("</body></html>")

######### End Functions #########

#Get arguments.
args = parse_arguments()

#Create config.
config = config(args)

#Set loging level.
logging.basicConfig(level=config.LOGLEVEL)

#Cleanup if args set.
clean_up(config)

# Create the XML path if it does not exist.
os.makedirs(config.xml_path, exist_ok=True)

#Validate the username
config.user_name = validate_username(config.user_name)

logging.info('starting')

#Write the html header and link to the approprate CSS file.
write_output_header(config)

#Read in the collection xml file.
items = read_collection(config)

find_and_download_new_collection_object_info(config, items)

#Parsing user collection XML
for item in items:
    collection_info = collection_information(item, config)

    #Grab only games we own unless own isn't set.
    if(config.only_own == False or collection_info.own):
        #Check to see if the XML already exists. If it does, don't re-request it.
        if(os.path.exists(collection_info.game_xml)):
            with open(collection_info.game_xml, 'r', encoding="utf-8") as file:
                thisgameitems = ElementTree.fromstring(file.read())
        else:
            logging.error('game not found')
            #Pull the game info XML
            game_info_response = bgg_getter('thing', {'id': collection_info.obj_id, 'stats': 1} , config)

            #Write out the game info XML.
            with open(collection_info.game_xml, 'w', encoding="utf-8") as file:
                logging.info("Writing: " + collection_info.game_name + " to " + collection_info.game_xml)
                file.write(game_info_response.text)
                thisgameitems = ElementTree.fromstring(game_info_response.content)

        #Now that we have all of the information we need, create the HTML page.
        if(thisgameitems.attrib['type'] == "boardgame"):
            game_info = game_information(thisgameitems, config, collection_info)
            download_image(config, game_info)
            template_to_output_entry(config, game_info)
            gather_index_info(config, game_info, thisgameitems)

#Write the index.
write_index(config)

#Write the trailer.
write_output_trailer(config)

endtime = datetime.now()
totaltime = endtime - starttime
logging.info(f'command: {sys.argv}')
logging.info(f'total time: {totaltime}')













