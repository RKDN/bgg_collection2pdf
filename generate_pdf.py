import requests
import textwrap
import shutil
import math
from time import sleep
from os.path import exists
from xml.etree import ElementTree

UserName             = input("Enter your BGG UserName: ")
sleep_time           = 10
successful_responses = 0

def remove_non_english_chars(input):
    encoded_string = input.encode("ascii", "ignore")
    return encoded_string.decode()

def get_value(item):
    return item.attrib['value']

def get_value_in_list(item, i):
    if(len(item) <= i):
        return "";
    else:
        return item[i].attrib['value']

def get_text(item):
    return item.text

def get_prop_text(elem, name):
    elem = elem.find(name)
    if elem is not None:
        return get_text(elem)

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

with open('output.html', 'w') as file:
        file.write('<html><head><link href="style.css" rel="stylesheet" type="text/css"></head><body>')

if(exists('collection.xml')):
    with open('collection.xml', 'r') as file:
        ur = file.read()
        items = ElementTree.fromstring(ur)
else:
    ur = requests.get("https://boardgamegeek.com/xmlapi2/collection?username=" + UserName + "&stats=1")
    with open('collection.xml', 'w') as file:
        file.write(ur.text)
        items = ElementTree.fromstring(ur.content)

#Reading user collection XML
for item in items:
    obj_id     = item.attrib['objectid']
    name       = item.find('name').text
    game_xml   = './game_xml/' + obj_id + '.xml'
    own        = item.find('status').attrib['own'] == "1"
    my_rating  = item.find('stats').find('rating').attrib['value']
    avg_rating = item.find('stats').find('rating').find('average').attrib['value']

    if(own):
        if(exists(game_xml)):
            with open(game_xml, 'r') as file:
                gr = file.read()
                items = ElementTree.fromstring(gr)
        else:
            return_text = "<error>"
            while("<error>" in return_text):
                sleep(.5)
                gr = requests.get("https://boardgamegeek.com/xmlapi2/thing?id=" + obj_id + "&stats=1")
                return_text = gr.text

                if("<error>" in return_text):
                    error = ElementTree.fromstring(return_text)
                    print("Sleeping " + str(sleep_time) + " Seconds: " + error.find('message').text)
                    sleep(sleep_time)
                    sleep_time *= 2
                    successful_responses = 0
                else:
                    successful_responses += 1
                    if(successful_responses > 15):
                        sleep_time /= 2
                        sleep_time = max(10,sleep_time)


            with open(game_xml, 'w') as file:
                print("Writing: " + name + " to " + game_xml)
                file.write(gr.text)
                items = ElementTree.fromstring(gr.content)

        if(items[0].attrib['type'] == "boardgame"):
            #Reading the Game XML
            image       = get_prop_text(items[0], 'image')
            name        = get_prop_value(items[0], 'name')
            description = textwrap.shorten(get_prop_text(items[0], 'description') or "", width=1100, placeholder='...')
            minplayers  = str(get_prop_value(items[0], 'minplayers') or '')
            maxplayers  = str(get_prop_value(items[0], 'maxplayers') or '')
            published   = get_prop_value(items[0], 'yearpublished')
            publisher   = get_value_in_list(get_links(items[0], 'boardgamepublisher'), 0)
            designer    = get_value_in_list(get_links(items[0], 'boardgamedesigner'), 0)

            artist1    = get_value_in_list(get_links(items[0], 'boardgameartist'), 0)
            artist2    = get_value_in_list(get_links(items[0], 'boardgameartist'), 1)

            category1    = get_value_in_list(get_links(items[0], 'boardgamecategory'), 0)
            category2    = get_value_in_list(get_links(items[0], 'boardgamecategory'), 1)

            mechanic1    = get_value_in_list(get_links(items[0], 'boardgamemechanic'), 0)
            mechanic2    = get_value_in_list(get_links(items[0], 'boardgamemechanic'), 1)
            mechanic3    = get_value_in_list(get_links(items[0], 'boardgamemechanic'), 2)
            mechanic4    = get_value_in_list(get_links(items[0], 'boardgamemechanic'), 3)

            mintime  = str(get_prop_value(items[0], 'minplaytime') or '')
            maxtime  = str(get_prop_value(items[0], 'maxplaytime') or '')

            avg_weight = items[0].find('statistics').find('ratings').find('averageweight').attrib['value']


            if(exists('./Images/' + obj_id + ".jpg") == False):
                #Download the image to the local cache.
                res = requests.get(image, stream = True)
                if res.status_code == 200:
                    with open('./Images/' + obj_id + ".jpg", 'wb') as f:
                        shutil.copyfileobj(res.raw, f)

            with open('template.html', 'r') as file:
                template = file.read()

            template = template.replace('{{image}}', "./Images/" + obj_id + ".jpg" or "")
            template = template.replace('{{GameName}}', name or "")
            template = template.replace('{{Description}}', description or "")
            template = template.replace('{{Published}}', published or "")
            template = template.replace('{{Publisher}}', publisher or "")
            template = template.replace('{{Designer}}', designer or "")
            template = template.replace('{{Artist}}', artist1 or "")
            template = template.replace('{{Category}}', category1 + "<br/>" + category2)

            max_length = 75
            three_mechanics_length= len(mechanic1 + mechanic2 + mechanic3)
            four_mechanics_length = len(mechanic1 + mechanic2 + mechanic3 + mechanic4)
            if(len(mechanic1) > 0):
                template = template.replace('{{Cat0}}', mechanic1)
            else:
                template = template.replace('{{Cat0}}', "")
            if(len(mechanic2) > 0):
                template = template.replace('{{Cat1}}', " , " + mechanic2)
            else:
                template = template.replace('{{Cat1}}', "")
            if(len(mechanic3) > 0 and max_length >= three_mechanics_length):
                template = template.replace('{{Cat2}}', " , " + mechanic3)
            else:
                template = template.replace('{{Cat2}}', "")
            if(len(mechanic4) > 0 and max_length >= four_mechanics_length):
                template = template.replace('{{Cat3}}', " , " + mechanic4)
            else:
                template = template.replace('{{Cat3}}', "")
            
            template = template.replace('{{p}}', minplayers + " - " + maxplayers)         
            
            #If there is a range
            if(int(mintime) < int(maxtime)):
                template = template.replace('{{d}}', str(mintime) + " - " + str(maxtime))
            #Single game length
            else:
                template = template.replace('{{d}}', str(mintime))

            template = template.replace('{{Weight}}', str(round(float(avg_weight) * 2, 1) ))

            if("N/A" in my_rating):
                template = template.replace('{{Rating}}', str(round(float(avg_rating), 1)))
            else:
                template = template.replace('{{Rating}}', str(round((float(avg_rating) + float(my_rating)) / 2, 1)))

            with open('output.html', 'a') as file:
                file.write(template)

with open('output.html', 'a') as file:
        file.write("</body></html>")















