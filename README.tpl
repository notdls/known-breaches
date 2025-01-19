# Known Breaches
A compliation of breach information gathered from data aggregators, breach lookup and similar services. This also ships with a basic HTML/JS client-side search (now using [sql.js](https://sql.js.org/#/)) for the datasets, this can be hosted on any webserver or ran locally, alternatively you can search the data online [here](https://breaches.dls.sh/).

## Indexed Services
README_TABLE

You can find the datasets in `datasets/`, each file here contains data obtained from the individual providers with the exception of `combined.json` which is a compilation of all data.

As vigilante.pw is currently down and has been for a while, the data set from the following github repository was used [https://github.com/wedataintelligence/Vigilante.pw](https://github.com/wedataintelligence/Vigilante.pw).

If you have any suggestions feel free to create an issue or submit a PR :)

## Usage
### Updating the datasets
If you would like to run this yourself, the scraper now requires two things to run successfully:
 - A FlareServerr Host (`FLARESERVERR_URL`) - This is used to get around Cloudflare bot checks
 - A Hashmob API Key (`HASHMOB_API_KEY`) - This is used to interact with the Hashmob API to retrieve a list of official breaches.

These values are expected to be passed as environment variables (`FLARESERVERR_URL` and `HASHMOB_API_KEY`).

It is possible to run the script without them, but the generated datasets will be missing several live sources.

To run the script, you simply need to run the following command. This will reach out to all of the live providers, and update their datasets as well as regenerate the combined dataset.

```
$ FLARESOLVERR_URL=REPLACEME HASHMOB_API_KEY=REPLACEME python3 scraper.py
```

### Viewing the datasets
A very simple static site is provided within this repository, you can simply drag and drop, clone or copy this repository to a webserver and it should work fine, alternatively, you can also run a simple python webserver by running `python3 -m http.server` and viewing the site on `http://localhost:8000`, or view the public instance [here](https://breaches.dls.sh/).

## TODO
 - Normalize breach dates