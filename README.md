# bgg_collection2pdf 

Create a pdf file of your game lists on Board Game Geek

## Description

This is a python script that will generate a HTML  (PDF as an extra step) catalog for your board game collection. Currently the output can be in the form of pages or card images of the games in your collection.

## Getting Started

### Dependencies

* bgg account
* python3 and requests library
** use pip install requests


### Installing

*  git clone this directory :-)

### Executing program

* How to run the program
```
generate_pdf.py
Enter your BGG UserName: migio
Card Mode? : (y/N)y
```
Wait for the script to run. It will take a bit to download all of the information needed from BGG.

Open the output.html page that was generated in Firefox. Other browsers may not format the page correctly. Your mileage may vary.

Print with no margins on US Letter paper. Make sure you enable "Print Backgrounds." You may need to adjust the scale when printing card mode output.

## Help

Any advise for common problems or issues.
```
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        User to pull BGG collection data from. (Required)
  -c, --cardmode        Create cards instead of a catalog. (default=Off)
  -i, --index           Enables creating an index. (default=Off)
  --clean_images        Clear out local images cache. (default=Off)
  --clean_xml           Clear out local xml cache. (default=Off)
```

## Authors

Contributors names and contact info

* Daniel Shourd
** [on BGG](https://boardgamegeek.com/user/RKDN)
** [her on github](https://github.com/RKDN)

## Version History

* 0.2
    * Various bug fixes and optimizations
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
*  README.md https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc#file-readme-template-md
*  README Tester https://github.com/joeyespo/grip
*  BGG forum link https://boardgamegeek.com/thread/2846310/bgg-pdf-python-script/page/1

