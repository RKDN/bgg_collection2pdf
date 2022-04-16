# bgg_collection2pdf 

Create a pdf file of your game lists on Board Game Geek

## Description

This is a python script that will generate a HTML  (PDF as an extra step) catalog for your board game collection. Currently the output can be in the form of pages or card images of the games in your collection.

### Dependencies

* bgg account
* python3 and requests library
** use pip install requests

### Installing

*  git clone this directory :-)

### Executing program

* How to run the program
```
python generate_pdf.py --username USER
```
Wait for the script to run. It will take a bit to download all of the information needed from BGG.

Open the output.html page that was generated in Firefox. Other browsers may not format the page correctly. Your mileage may vary.

Print with no margins on US Letter paper. Make sure you enable "Print Backgrounds."

## Help

```
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        User to pull BGG collection data from. (Required)
  -c, --cardmode        Create cards instead of a catalog. (default=Off)
  -i, --index           Enables creating an index. (default=Off)
  --clean_all           Clear out Images, XML, and all other generated files. (default=Off)
  --clean_images        Clear out local images cache. (default=Off)
  --clean_xml           Clear out local xml cache. (default=Off)
  -o, --own             Enables pulling only games set to own on BGG. (default=Off)
  --minsleep MINSLEEP   Minimum sleep duration on XML error. (Default=10)
  --maxsleep MAXSLEEP   Maximum sleep duration on XML error. (Default=120)
  --no_cache            Turn off all caching (default=Off)
  --output OUTPUT       Output html file. (Default="./output.html")
  --images_path IMAGES_PATH
                        Images path. (Default="./Images")
  --xml_path XML_PATH   Game XML Path. (Default="./game_xml")
  --collection_xml COLLECTION_XML
                        Output collection XML file.(Default="./collection.xml")

```

## Authors

Contributors names and contact info

* Daniel Shourd
** [on BGG](https://boardgamegeek.com/user/RKDN)
** [here on github](https://github.com/RKDN)


## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
*  README.md https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc#file-readme-template-md
*  README Tester https://github.com/joeyespo/grip
*  BGG forum link https://boardgamegeek.com/thread/2846310/bgg-pdf-python-script/page/1

