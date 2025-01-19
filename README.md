# Known Breaches
A compliation of breach information gathered from data aggregators, breach lookup and similar services. This also ships with a basic HTML/JS client-side search (now using [sql.js](https://sql.js.org/#/)) for the datasets, this can be hosted on any webserver or ran locally, alternatively you can search the data online [here](https://breaches.dls.sh/).

## Indexed Services
| Service Name | Breach Count | Total Records | Automatic Updates |
| ------------ | ------------ | ------------- |        :--:       |
| HaveIBeenPwned | 851 | 14,505,253,859 | ✅ |
| Dehashed | 1,071 | 16,133,955,377 | ✅ |
| Hashmob | 2,647 | 4,649,520,532 | ✅ |
| BreachDirectory | 4,276 | 26,536,733,833 | ✅ |
| LeakCheck.io | 1,010 | 6,251,599,721 | ✅ |
| ScatteredSecrets | 4,669 | Unavailable | ✅ |
| Leak-Lookup | 4,409 | 27,850,174,836 | ✅ |
| xam | 308 | 5,789,597 | ❌ |
| LeakBase.pw | 655 | 10,640 | ❌ |
| Hacked-Emails | 16,497 | 1,620,592 | ❌ |
| RaidForums | 505 | 1,625 | ❌ |
| Keeper | 2,939 | Unavailable | ❌ |
| vigilante-pw | 6,413 | 6,263,886,497 | ❌ |
| Hashes.org | 2,508 | 3,259,811,660 | ❌ |
| DataViper.io | 8,225 | 14,699,175,144 | ❌ |
| Citadel.pw | 475 | Unavailable | ❌ |
| leakfind | 660 | Unavailable | ❌ |
| databases.today | 1,256 | Unavailable | ❌ |
| DeepSearch | 111 | 3,142 | ❌ |
| WeLeakInfo_2 | 945 | Unavailable | ❌ |
| Siphon | 765 | Unavailable | ❌ |
| LeakCheck.net | 780 | Unavailable | ❌ |
| WeLeakInfo_1 | 10,369 | Unavailable | ❌ |
| BreachNet.pw | 662 | 3,220,636,003 | ❌ |
| BreachAware | 3,685 | 6,117,426,271 | ❌ |
| Snusbase | 673 | Unavailable | ❌ |
| HackNotice.com | 50,967 | 11,194,593,862 | ❌ |
| Cit0day | 23,562 | 1,588,612 | ❌ |


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