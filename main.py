from collections import defaultdict

import requests

from colorama import Fore, Style
from connegp import LinkHeaderParser

base_url = "http://localhost:8000"
endpoints = [
    "/v/collection",
    "/v/profiles",
    "/v/vocab",
    "/c/catalogs",
    "/c/profiles",
    "/s/datasets",
    "/s/profiles",
]
def parse_headers():

    for endpoint in endpoints:
        print(f"Testing endpoint {endpoint}")
        print("-"*40, end="\n\n")

        # TODO: use HEAD instead of GET (currently unsupported in prez)
        response = requests.get(
            url=base_url + endpoint,
            params={'per_page': 1},
            headers={'Accept': 'text/anot+turtle'}
        )
        if response.status_code == 200:

            lnk = response.headers['link']
            lhp = LinkHeaderParser(lnk)
            profiles = lhp.profiles
            if len(profiles) == 0:
                print("No profiles returned")
                break

            # get the profiles and media types from the link header
            pmts = [ {
                'profile': profiles[f"<{lh['profile']}>"],
                'mediatype': lh['type']
            } for lh in lhp.link_headers if 'profile' in lh]

            # make a new request for each available profile and media type
            print(f"{'profile':<25}{'mediatype':<25}status_code")
            for pmt in pmts:
                print(f"{pmt['profile']:<25}{pmt['mediatype']:<25}", end="")
                r = requests.get(
                    url=base_url + endpoint,
                    params={"_profile": pmt['profile'], "_mediatype": pmt['mediatype']}
                )
                colors = defaultdict()
                colors[200] = Fore.GREEN
                print(colors.get(r.status_code, Fore.RED) + str(r.status_code))
                print(Style.RESET_ALL, end="")
        else:
            print("Error: " + str(response.status_code))
        print("\n\n")


if __name__ == '__main__':
    parse_headers()
