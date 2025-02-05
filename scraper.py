import requests
import json
import csv
import os
from bs4 import BeautifulSoup
import traceback
import logging


"""
Scrapes in the indexed/available datasets from several data aggregators/indexers. Currently supports Dehashed, Leak-Lookup, HaveIBeenPwned
"""

def add_source(breaches, source):
    """
    Adds a source field to a list of breaches.
    """
    for breach in breaches:
        breach["source"] = source
    return breaches

def clean_json(breaches):
    """
    Cleans an array of json objects by stripping any key/value pairs where the key is not in the whitelist.
    """
    whitelist = ["dump_name","breach_date","record_count","info","index_date","description","source"]
    clean_breaches = []
    for breach in breaches:
        clean_breach = {}
        for key in breach.keys():
            if key in whitelist:
                clean_breach[key] = breach[key]
        clean_breaches.append(clean_breach)
    return clean_breaches

def remove_non_digits(string):
    """
    Removes non-digits from a string.
    """
    return ''.join(filter(lambda x: x.isdigit(), string))

def generate_requests_session():
    """
    Generates a requests session.
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    })
    return session

def get_via_flaresolverr(url, cookies_only=False):
    # This function uses a specified FlareSolverr instance to get around Cloudflare captchas/bot detection
    flaresolverr_url = os.getenv('FLARESOLVERR_URL')
    resp = requests.post(flaresolverr_url, json={
        'cmd': 'request.get',
        'url': url,
        'maxTimeout': 60000, # 60s
        'returnOnlyCookies': cookies_only
    })
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'status' in resp_json:
            if resp_json['status'] == 'ok' and 'solution' in resp_json:
                if cookies_only:
                    return resp_json['solution']['cookies'], resp_json['solution']['userAgent']
                return resp_json['solution']['response']
    return None

def scrape_leaklookup(session=generate_requests_session()):
    """
    Scrapes the Leak-Lookup dataset.
    """
    breaches = []
    url = "https://leak-lookup.com/breaches"
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_table = soup.find('table', {'id': 'datatables-indexed-breaches'})
        for entry in data_table.find('tbody').find_all('tr'):
            """
            Example <tr>
            <tr>
                <td>astropid.com</td>
                <td class="d-xl-table-cell">5,789</td>
                <td class="d-xl-table-cell">2017-02-20</td>
                <td class="table-action text-center">
                    <div class="dropdown position-relative">
                        <a href="#" data-bs-toggle="dropdown" data-bs-display="static">
                            <i class="align-middle" data-feather="more-horizontal"></i>
                        </a>

                        <div class="dropdown-menu dropdown-menu-end">
                            <a id="astropid-com" class="dropdown-item" data-bs-toggle="modal" data-id="1" data-bs-target="#breachModal">Information</a>
                        </div>
                    </div>
                </td>
            </tr>
            """
            tds = entry.find_all('td')
            dump_name = tds[0].text.strip()
            record_count = remove_non_digits(tds[1].text.replace(",","").strip())
            # YYYY-MM-DD
            date = tds[2].text.strip()
            breaches.append({"dump_name": dump_name, "record_count": record_count, "index_date": date, "source": "Leak-Lookup"})
        return breaches
    else:
        return None

def scrape_breachdirectory(session=generate_requests_session()):
    """
    Scrapes the BreachDirectory dataset index.
    """
    breaches = []
    url = "https://breachdirectory.org/tables"
    response = get_via_flaresolverr(url)
    if response:
        soup = BeautifulSoup(response, 'html.parser')
        data_table = soup.find('table', {'class': 'chakra-table'})
        for entry in data_table.find('tbody').find_all('tr'):
            """
            <tr class="css-1whkjwr">
                <td class="css-osmp5g">collection-1</td>
                <td class="css-osmp5g">2,147,483,647</td>
                <td class="css-osmp5g">2019-01-24</td>
            </tr>
            """
            tds = entry.find_all('td')
            dump_name = tds[0].text.strip()
            breach_date = tds[2].text.strip()
            record_count = remove_non_digits(tds[1].text.strip())
            breaches.append({"dump_name": dump_name, "breach_date": breach_date, "record_count": record_count, "source": "BreachDirectory"})
        return breaches
    else:
        print(f"Received non-200 status code: {response.status_code}")
        return None

def scrape_leakcheck(session=generate_requests_session()):
    """
    Scrapes the LeakCheck dataset index.
    """
    breaches = []
    url = "https://leakcheck.io/databases-list"
    response = get_via_flaresolverr(url)
    if response:
        # load as json
        soup = BeautifulSoup(response, 'html.parser')
        json_data = soup.find('pre').text.strip()
        data = json.loads(json_data)
        for entry in data['data']:
            """
            {"id":1,"name":"MyHeritage.com","count":89769623,"breach_date":"2017-10","unverified":0,"passwordless":0,"compilation":0}
            """
            dump_name = entry['name']
            breach_date = entry['breach_date']
            record_count = entry['count']
            breaches.append({"dump_name": dump_name, "breach_date": breach_date, "record_count": record_count, "source": "LeakCheck.io"})
        return breaches
    else:
        print(f"Received non-200 status code: {response.status_code}")
        return None

def scrape_scatteredsecrets(session=generate_requests_session()):
    """
    Scrapes the ScatteredSecrets dataset.
    """
    breaches = []
    url = "https://scatteredsecrets.com/"
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_table = soup.find('table', {'id': 'dumps_table'})
        for entry in data_table.find('tbody').find_all('tr'):
            try:
                """
                <tr class="odd">
                    <td class="sorting_1">0-o.ca</td>
                </tr>
                """
                    # valid entry
                dump_name = entry.find('td').text.strip()
                breaches.append({"dump_name": dump_name, "source": "ScatteredSecrets"})
            except Exception as e:
                print(f"Error grabbing dump name: {entry}")
        return breaches
    else:
        return None
    
def scrape_hashmob_official(session=generate_requests_session()):
    # Scrapes the "official" hashlists from the hashmob.net website.
    api_key = os.getenv('HASHMOB_API_KEY')
    url = "https://hashmob.net/api/v2/hashlist/official"
    response = session.get(url, headers={'api-key':api_key})
    breaches = []
    if response.status_code == 200:
        for entry in response.json():
            breaches.append({'dump_name':entry['name'], 'info': entry['algorithm'], 'record_count': entry['total_hashes'], 'source':'Hashmob'})
        return breaches
    return None

def scrape_hibp(session=generate_requests_session()):
    """
    Scrapes the HaveIBeenPwned dataset.
    """
    breaches = []
    url = "https://haveibeenpwned.com/PwnedWebsites"
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_table = soup.find_all('div', {'class': 'row'})
        for entry in data_table:
            """
            Example entry
            <div class="container">
            <hr /><a id="000webhost"></a>
            <div class="row">
            <div class="col-sm-2">
            <img class="pwnLogo large" src="/Content/Images/PwnedLogos/000webhost.png" alt="000webhost logo" />
            </div>
            <div class="col-sm-10">
            <h3>
            000webhost
            </h3>
            <p>In approximately March 2015, the free web hosting provider <a href="https://www.troyhunt.com/2015/10/breaches-traders-plain-text-passwords.html" target="_blank" rel="noopener">000webhost suffered a major data breach</a> that exposed almost 15 million customer records. The data was sold and traded before 000webhost was alerted in October. The breach included names, email addresses and plain text passwords.</p>
            <p>
            <strong>Breach date:</strong> 1 March 2015<br />
            <strong>Date added to HIBP:</strong> 26 October 2015<br />
            <strong>Compromised accounts:</strong> 14,936,670<br />
            <strong>Compromised data:</strong> Email addresses, IP addresses, Names, Passwords<br />
            <a href="#000webhost">Permalink</a>
            </p>
            </div>
            </div>
            """
            if "Breach date:" in entry.text:
                # valid entry
                dump_name = entry.find('h3').text.strip()
                breach_date = entry.find_all('p')[1].text.splitlines()[1].split(":")[1].strip()
                index_date = entry.find_all('p')[1].text.splitlines()[2].split(":")[1].strip()
                record_count = remove_non_digits(entry.find_all('p')[1].text.splitlines()[3].split(":")[1].strip())
                description = entry.find_all('p')[0].text.strip()
                info = entry.find_all('p')[1].text.splitlines()[4].split(":")[1].strip()
                breaches.append({"dump_name": dump_name, "record_count": record_count, "breach_date": breach_date, "index_date": index_date, "description": description, "info": info, "source": "HaveIBeenPwned"})
        return breaches
    else:
        return None


def scrape_dehashed(session=generate_requests_session()):
    """
    Scrapes the Dehashed dataset index.
    """
    breaches = []
    url = "https://dehashed.com/data"
    # get cf_clearance
    cookies, userAgent = get_via_flaresolverr(url, cookies_only=True)
    # update cookies
    req_cookies = {}
    for cookie in cookies:
        req_cookies[cookie['name']] = cookie['value']
    # Update user-agent to match FlareSolverr's
    session.headers.update({"User-Agent":userAgent})
    # send request with new cookies
    response = session.get(url, cookies=req_cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_table = soup.find('table', {'class': 'table table-hover'})
        for entry in data_table.find('tbody').find_all('tr'):
            """
            Example <tr>
            <tr>
            <td class="align-middle">2paclegacyboard.net</td>
            <td class="align-middle">
            <abbr class="bs-tooltip" data-placement="top" title='-'>Hover Here</abbr>
            <p></p>
            </td>
            <td class="align-middle"><span class="text-nowrap">N/A</span></td>
            <td class="align-middle"><span class="text-nowrap">1061</span></td>
            <td class="align-middle"><abbr class="bs-tooltip" data-placement="top" title='N/A'>Hover Here</abbr></td>
            </tr>
            """
            tds = entry.find_all('td')
            dump_name = tds[0].text.strip()
            breach_date = tds[2].find('span').text.strip()
            record_count = remove_non_digits(tds[3].find('span').text.replace(",","").strip())
            info = tds[4].find('abbr')['title'].strip()
            breaches.append({"dump_name": dump_name, "breach_date": breach_date, "record_count": record_count, "info": info, "source": "Dehashed"})
        return breaches
    else:
        print(f"Received non-200 status code: {response.status_code}")
        return None
    

def scrape_leaked_domains(session=generate_requests_session()):
    breaches = []
    url = "https://leaked.domains/Info/"
    # get cf_clearance
    cookies, userAgent = get_via_flaresolverr(url, cookies_only=True)
    # update cookies
    req_cookies = {}
    for cookie in cookies:
        req_cookies[cookie['name']] = cookie['value']
    # Update user-agent to match FlareSolverr's
    session.headers.update({"User-Agent":userAgent})
    # send request with new cookies
    response = session.get(url, cookies=req_cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_table = soup.find('table', {'id': 'leak_summery'})
        for entry in data_table.find('tbody').find_all('tr'):
            #print(entry)
            tds = entry.find_all('td')
            entry_type = tds[1].text.strip()
            if entry_type == "Leakdb":
                dump_name = tds[0].text.strip()
                breach_date = tds[5].text.strip()
                record_count = remove_non_digits(tds[6].text.replace(",","").strip())
                info = tds[4].text.strip()
                breaches.append({"dump_name": dump_name, "breach_date": breach_date, "record_count": record_count, "info": info, "source": "Leaked.Domains"})
        return breaches
    else:
        print(f"Received non-200 status code: {response.status_code}")
        return None

if __name__ == "__main__":
    # initialize logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # init breaches
    breaches = []
    if "FLARESOLVERR_URL" in os.environ:
        # scrape datasets from dehashed
        logging.info("Scraping Dehashed.com")
        try:
            dehashed_result = scrape_dehashed()
            if dehashed_result:
                breaches += dehashed_result
                logging.info("Saving results to file")
                with open("datasets/Dehashed.json", "w") as f:
                    json.dump(dehashed_result, f)
                with open("datasets/Dehashed.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","info","source"])
                    writer.writeheader()
                    writer.writerows(dehashed_result)
                logging.info("Successfully scraped %d breaches from Dehashed.com", len(dehashed_result))
            else:
                logging.error("Scraping dehashed failed")
        except Exception as e:
            logging.error("Error occurred while scraping dehashed: %s", str(e))

        # scrape datasets from BreachDirectory
        logging.info("Scraping BreachDirectory.org")
        try:
            bd_result = scrape_breachdirectory()
            if bd_result:
                breaches += bd_result
                logging.info("Saving results to file")
                with open("datasets/BreachDirectory.json", "w") as f:
                    json.dump(bd_result, f)
                with open("datasets/BreachDirectory.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","source"])
                    writer.writeheader()
                    writer.writerows(bd_result)
                logging.info("Successfully scraped %d breaches from BreachDirectory.org", len(bd_result))
            else:
                logging.error("Scraping BreachDirectory failed")
        except Exception as e:
            logging.error('Error occurred while scraping BreachDirectory: %s', str(e))
            logging.error('Traceback: %s', traceback.format_exc())

        # scrape datasets from Leakcheck
        logging.info("Scraping LeakCheck.io")
        try:
            lc_result = scrape_leakcheck()
            if lc_result:
                breaches += lc_result
                logging.info("Saving results to file")
                with open("datasets/LeakCheck.io.json", "w") as f:
                    json.dump(lc_result, f)
                with open("datasets/LeakCheck.io.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","source"])
                    writer.writeheader()
                    writer.writerows(lc_result)
                logging.info("Successfully scraped %d breaches from LeakCheck.io", len(lc_result))
            else:
                logging.error("Scraping Leakcheck failed")
        except Exception as e:
            logging.error('Error occurred while scraping LeakCheck: %s', str(e))
            logging.error('Traceback: %s', traceback.format_exc())

        # scrape datasets from Leaked.Domains
        logging.info("Scraping Leaked.Domains")
        try:
            ld_result = scrape_leaked_domains()
            if ld_result:
                breaches += ld_result
                logging.info("Saving results to file")
                with open("datasets/Leaked.Domains.json", "w") as f:
                    json.dump(ld_result, f)
                with open("datasets/Leaked.Domains.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","info","source"])
                    writer.writeheader()
                    writer.writerows(ld_result)
                logging.info("Successfully scraped %d breaches from Leaked.Domains", len(ld_result))
            else:
                logging.error("Scraping Leaked.Domains failed")
        except Exception as e:
            logging.error("Error occurred while scraping Leaked.Domains: %s", str(e))

    # scrape datasets from ScatteredSecrets
    logging.info("Scraping ScatteredSecrets.com")
    try:
        ss_result = scrape_scatteredsecrets()
        if ss_result:
            breaches += ss_result
            logging.info("Saving results to file")
            with open("datasets/ScatteredSecrets.json", "w") as f:
                json.dump(ss_result, f)
            with open("datasets/ScatteredSecrets.csv", "w") as f:
                writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","source"])
                writer.writeheader()
                writer.writerows(ss_result)
            logging.info("Successfully scraped %d breaches from ScatteredSecrets", len(ss_result))
        else:
            logging.error("Scraping ScatteredSecrets failed")
    except Exception as e:
        logging.error('Error occurred while scraping ScatteredSecrets: %s', str(e))
        logging.error('Traceback: %s', traceback.format_exc())

    # scrape datasets from Hashmob
    if "HASHMOB_API_KEY" in os.environ:
        logging.info("Scraping Hashmob.net")
        try:
            hm_result = scrape_hashmob_official()
            if hm_result:
                breaches += hm_result
                logging.info("Saving results to file")
                with open("datasets/Hashmob.json", "w") as f:
                    json.dump(hm_result, f)
                with open("datasets/Hashmob.csv", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","source","info"])
                    writer.writeheader()
                    writer.writerows(hm_result)
                logging.info("Successfully scraped %d breaches from Hashmob", len(hm_result))
            else:
                logging.error("Scraping Hashmob failed")
        except Exception as e:
            logging.error('Error occurred while scraping Hashmob: %s', str(e))
            logging.error('Traceback: %s', traceback.format_exc())

    # scrape datasets from HaveIBeenPwned
    logging.info("Scraping HaveIBeenPwned.com")
    try:
        hibp_result = scrape_hibp()
        if hibp_result:
            breaches += hibp_result
            logging.info("Saving results to file")    
            with open("datasets/HaveIBeenPwned.json", "w") as f:
                json.dump(hibp_result, f)
            with open("datasets/HaveIBeenPwned.csv", "w") as f:
                writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","info","index_date","description","source"])
                writer.writeheader()
                writer.writerows(hibp_result)
            logging.info("Successfully scraped %d breaches from HaveIBeenPwned.com", len(hibp_result))
        else:
            logging.error("Scraping of HaveIBeenPwned failed")
    except Exception as e:
        logging.error('Error occurred while scraping HaveIBeenPwned: %s', str(e))
        logging.error('Traceback: %s', traceback.format_exc())
    
    # scrape datasets from LeakLookup
    logging.info("Scraping Leak-Lookup.com")
    try:
        ll_result = scrape_leaklookup()
        breaches += ll_result
        if ll_result:
            logging.info("Saving results to file")
            with open("datasets/Leak-Lookup.json", "w") as f:
                json.dump(ll_result, f)
            with open("datasets/Leak-Lookup.csv", "w") as f:
                writer = csv.DictWriter(f, fieldnames=["dump_name","record_count","index_date","source"])
                writer.writeheader()
                writer.writerows(ll_result)
            logging.info("Successfully scraped %d breaches from Leak-Lookup.com", len(ll_result))
        else:
            logging.error("Scraping of leak-lookup failed")
    except Exception as e:
        logging.error('Error occurred while scraping Leak-Lookup: %s', str(e))
        logging.error('Traceback: %s', traceback.format_exc())

    # load static datasets
    # loop through each JSON file in the datasets/ directory
    ignore_files = ["combined.json","HaveIBeenPwned.json","Dehashed.json","Leak-Lookup.json","BreachDirectory.json","Hashmob.json","LeakCheck.io.json","ScatteredSecrets.json"]
    for file in os.listdir("datasets/"):
        if file.endswith(".json") and file not in ignore_files:
            logging.info("Loading %s", file)
            try:
                with open("datasets/{}".format(file), "r") as f:
                    json_data = json.loads(f.read())
                    for entry in json_data:
                        entry["source"] = file.replace(".json","")
                    breaches += json_data
                    logging.info("Extracted %d breaches from %s", len(json_data), file)
            except Exception as e:
                logging.error('Error occurred while loading %s: %s', file, str(e))
                logging.error('Traceback: %s', traceback.format_exc())

    # save combined results 
    breaches = clean_json(breaches)

    logging.info("Saving combined results to file")
    with open("datasets/combined.json", "w") as f:
        f.write(json.dumps(breaches, separators=(',', ':')))

    logging.info("Done :)")
