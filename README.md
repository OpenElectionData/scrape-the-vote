# scrape-the-vote
A scraper for international election results. 

Design considerations:
- the site-specific scraping (grabbing URLs of images) is completely separate from storage (keeping track of what has been downloaded, uploading images)
- each site-specific election scraper will be it's own module. each scraper will store images in its own project on DocumentCloud.
- a local sqlite3 database will keep track of what urls have been seen by the crawler, & only new urls or existing urls with updated files will be uploaded to DocumentCloud

## Setup
1. **Make sure you have [python](https://www.python.org/), [git](http://www.git-scm.com/), and [pip](https://pip.pypa.io/en/stable/) installed**
2. **Clone this repo & install requirements**
  
  ```
  git clone https://github.com/datamade/scrape-the-vote.git
  cd scrape-the-vote
  pip install -r requirements.txt
  ```
  
  *NOTE: Mac users might need [this lxml workaround](http://stackoverflow.com/questions/22313407/clang-error-unknown-argument-mno-fused-madd-python-package-installation-fa).*
  
3. **Create a config file from the config example**
  
  ```
  cp stv/config.example.py stv/config.py
  ```

  Open ```config.py``` in a text editor and edit the values of ```DC_USER``` and ```DC_PW``` with your DocumentCloud credentials.

4. **Build this package**
  ```
  python setup.py develop
  ```
  This will allow you to use the stv command line tool. You can run `stv -h` at the command line to see the available commands - `init`, `dispatch`, &`testcrawl`.
  
5. **Initialize the scraper runner**
  ```
  stv init
  ```

## Scrapers
Each election will be it's own module. The scraper will be placed in the `__init__.py` of the module.

Scrapers are subclasses of scraperlib.Scraper, and must contain

- `election_id` attribute
- `crawl` method. This method should be a generator that yields a tuple `(url, metadata, post_data)` for each image, where:
  - `url` is the url of the image
  - `metadata` is any information about the hierarchy of the pages to get to the image, represented as a string (e.g. `'/ATLANTIDA/LA CEIBA/CENTRO EVANGELICO BETHEL/1'`)
  - `post_data` is None if we can GET the image, or the post data if we have to make a POST request

The `dc_project` attribute specifies the name of the DocumentCloud project where images will be uploaded.

## Scraper Runners
The `stv` command line tool will be responsible for doing a few things

- dispatching the scraper (to crawl an election website in search of image URLs)
- creating a DocumentCloud project based on the `dc_project` attribute of a scraper
- storing the image urls & relevant metadata coming from the scraper
- downloading images from the urls coming from the scraper
- comparing downloaded images to previously seen images (via URLs & file hash)
- uploading images, when appropriate, to DocumentCloud


#### Running a scraper
To run a scraper, use the `stv dispatch` command. For example, to run a scraper called `honduras_election`, use

```
stv dispatch honduras_election
```

You can also add additional arguments to the command (to see all available arguments, run `stv dispatch -h`). For example, to run the `honduras_election` scraper with 20 requsts per minute, use

```
stv dispatch honduras_election --requests-per-minute=20
```

#### Testing a scraper
To test a scraper without storing URLs and uploading images to DocumentCloud, use the `stv testcrawl` command. For example, to run only the crawler for the ```honduras_election``` scraper, use

```
stv testcrawl honduras_election
```
