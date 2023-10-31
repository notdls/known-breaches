import requests
import json
import csv
from bs4 import BeautifulSoup

"""
Scrapes in the indexed/available datasets from several data aggregators/indexers. Currently supports Dehashed, Leak-Lookup, HaveIBeenPwned
"""

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    })
    return session

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
            breaches.append({"dump_name": dump_name, "record_count": record_count, "index_date": date, "source": "leaklookup"})
        return breaches
    else:
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
                breaches.append({"dump_name": dump_name, "record_count": record_count, "breach_date": breach_date, "index_date": index_date, "description": description, "info": info, "source": "hibp"})
        return breaches
    else:
        return None


def scrape_dehashed(session=generate_requests_session()):
    """
    Scrapes the Dehashed dataset index.

    """
    breaches = []
    url = "https://webcache.googleusercontent.com/search?q=cache:https://dehashed.com/data"
    response = session.get(url)
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
            breaches.append({"dump_name": dump_name, "breach_date": breach_date, "record_count": record_count, "info": info, "source": "dehashed"})
        return breaches
    else:
        return None

if __name__ == "__main__":
    # scrape datasets from dehashed
    print("Scraping Dehashed.com")
    try:
        dehashed_result = scrape_dehashed()
        if dehashed_result:
            print("Saving results to file")
            with open("datasets/dehashed.json", "w") as f:
                json.dump(dehashed_result, f)
            with open("datasets/dehashed.csv", "w") as f:
                writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","info","source"])
                writer.writeheader()
                writer.writerows(dehashed_result)
            print("Successfully scraped {} breaches from Dehashed.com".format(len(dehashed_result)))
        else:
            print("Scraping dehashed failed")
    except:
        print("Error occured while scraping dehashed")
    # scrape datasets from HaveIBeenPwned

    print("Scraping HaveIBeenPwned.com")
    try:
        hibp_result = scrape_hibp()
        if hibp_result:
            print("Saving results to file")    
            with open("datasets/hibp.json", "w") as f:
                json.dump(hibp_result, f)
            with open("datasets/hibp.csv", "w") as f:
                writer = csv.DictWriter(f, fieldnames=["dump_name","breach_date","record_count","info","index_date","description","source"])
                writer.writeheader()
                writer.writerows(hibp_result)
        else:
            print("Scraping of HIBP failed")
    except Exception as e:
        print(str(e))
        print("Error occured while scraiping hibp")
    print("Successfully scraped {} breaches from HaveIBeenPwned.com".format(len(hibp_result)))
    
    # scrape datasets from LeakLookup
    print("Scraping Leak-Lookup.com")
    try:
        ll_result = scrape_leaklookup()
        if ll_result:
            print("Saving results to file")
            with open("datasets/leaklookup.json", "w") as f:
                json.dump(ll_result, f)
            with open("datasets/leaklookup.csv", "w") as f:
                #breaches.append({"dump_name": dump_name, "record_count": record_count, "index_date": date, "source": "leaklookup"})

                writer = csv.DictWriter(f, fieldnames=["dump_name","record_count","index_date","source"])
                writer.writeheader()
                writer.writerows(ll_result)
        else:
            print("Scraping of leak-lookup failed")
    except:
        print("Error occured while scraping Leak-Lookup")
    print("Successfully scraped {} breaches from Leak-Lookup.com".format(len(ll_result)))

    
    # load vigilante-pw datasets
    vigilante_pw_dataset = json.loads(open("datasets/vigilante-pw.json").read())

    # save combined results 
    print("Saving combined results to file")
    with open("datasets/combined.json", "w") as f:
        json.dump(dehashed_result + hibp_result + ll_result + vigilante_pw_dataset, f)

    print("Done :)")
