# scrape-the-vote
Scraper for international election results

Architecture.

Key idea -- seperate the site-specific scraping code completely from storage

## Setup

Clone this repo & install requirements (make sure pip is installed):
```
git clone https://github.com/datamade/scrape-the-vote.git
cd scrape-the-vote
pip install -r requirements.txt
```

Create a config file from the config example:
```
cp stv/config.example.py stv/config.py
```

Open ```config.py``` and edit the values of ```DC_USER``` and ```DC_PW``` with your documentcloud credentials.

Then, run:
```
python setup.py develop
```

## Scrapers
Each election will be it's own module. The scraper will be placed in the `__init__.py` of the module.

Scrapers are subclasses of scraperlib.Scraper, and most contain

- `election_id` attribute
- `scrape` method. The scrape method should be a generator that yields a tuple like `('url_to_image', None)` if we can GET the image or or `(base_url, data)` if we have to make a POST request to get the image, where `data` is the post request.


## Scraper Runners
`stv` will be responsible for doing a few things

- creating a DocumentCloud collection based on the election_id of a scraper
- dispatching the scraper
- downloading the images/docs from the urls coming from the scraper
- comparing these images to previously seen images
- renaming images if appropriate, i.e. this image seems to be newer version of existing image 
- uploading images, when appropriate, to the appropriate DocumentCloud bucket

If using the ```stv``` command line tool for the first time, run
```
stv init
```

To run a scraper, use the `stv scrape` command. For example, to run a scraper called ```honduras_election```, use
```
stv scrape honduras_election
```

# Build order
- Write a scraper for an electoin
- Have `stv` dispatch that scraper from the command line
- Have `stv` download the first five image from that scraper
- Have `stv` uplaod the first five images. The downloading and uploading of images should be asynchrounous.




