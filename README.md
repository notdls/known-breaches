# Known Breaches
A compliation of breach information gathered from data aggregators, breach lookup and similar services. This also ships with a basic HTML/JS client-side search (now using [sql.js](https://sql.js.org/#/)) for the datasets, this can be hosted on any webserver or ran locally, alternatively you can search the data online [here](https://breaches.dls.sh/).

## Indexed Services
| Service Name | Breach Count | Total Records | Automatic Updates |
| ------------ | ------------ | ------------- |        :--:       |
| BreachDirectory | 4,437 | 27,978,047,211 | ✅ |
| Dehashed | 1,071 | 16,133,955,377 | ✅ |
| Hashmob | 2,715 | 5,155,117,301 | ✅ |
| HaveIBeenPwned | 883 | 14,952,812,162 | ✅ |
| Leak-Lookup | 4,439 | 28,015,244,367 | ✅ |
| LeakCheck.io | 1,304 | 6,482,029,102 | ✅ |
| Leaked.Domains | 307 | 10,390,618,831 | ✅ |
| ScatteredSecrets | 4,736 | Unavailable | ✅ |
| BreachAware | 3,685 | 6,117,426,271 | ❌ |
| BreachForums_Official_Index | 1,006 | 16,041,441,468 | ❌ |
| BreachForums_Unofficial_Index | 184 | 1,335,823,055 | ❌ |
| BreachNet.pw | 662 | 3,220,636,003 | ❌ |
| Cit0day | 23,562 | 1,215,545 | ❌ |
| Citadel.pw | 475 | Unavailable | ❌ |
| databases.today | 1,256 | Unavailable | ❌ |
| DataViper.io | 8,225 | 14,699,175,144 | ❌ |
| DeepSearch | 111 | 2,292,279,815 | ❌ |
| Hacked-Emails | 16,497 | 10,767,621,128 | ❌ |
| HackNotice.com | 50,967 | 11,194,593,862 | ❌ |
| Hashes.org | 2,508 | 3,259,811,660 | ❌ |
| Keeper | 2,939 | Unavailable | ❌ |
| LeakBase.pw | 655 | 4,335,625,510 | ❌ |
| LeakCheck.net | 780 | Unavailable | ❌ |
| leakfind | 660 | Unavailable | ❌ |
| RaidForums | 505 | 10,586,929,316 | ❌ |
| Siphon | 765 | Unavailable | ❌ |
| Snusbase | 673 | Unavailable | ❌ |
| vigilante-pw | 6,413 | 6,263,886,497 | ❌ |
| WeLeakInfo_1 | 10,369 | Unavailable | ❌ |
| WeLeakInfo_2 | 945 | Unavailable | ❌ |
| xam | 308 | 5,789,597 | ❌ |


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