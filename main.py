from pprint import pprint

import requests
from connegp import LinkHeaderParser


class ConnegpTestClient:
    def __init__(self, host):
        self.host = host
        self.endpoints = self._get_endpoints()

    def _get_endpoints(self):
        endpoints = []
        response = requests.get(f"{self.host}/openapi.json")
        if response.status_code == 200:
            js = response.json()
            endpoints = [path for path in js["paths"]]
        return endpoints

    def _get_pmts_for_endpoint(self, endpoint):
        pmts = []
        response = requests.get(
            url=self.host + endpoint,
            params={"per_page": 1},
            headers={"Accept": "text/anot+turtle"},
        )
        if response.status_code == 200:
            try:
                lnk = response.headers["link"]
            except KeyError:
                return pmts
            lhp = LinkHeaderParser(lnk)
            profiles = lhp.profiles
            if len(profiles) > 0:
                pmts = [
                    {"profile": profiles[f"<{lh['profile']}>"], "mediatype": lh["type"]}
                    for lh in lhp.link_headers
                    if "profile" in lh
                ]
        return pmts

    def _test_pmt_for_endpoint(self, endpoint, pmt):
        r = requests.get(
            url=self.host + endpoint,
            params={
                "_profile": pmt["profile"],
                "_mediatype": pmt["mediatype"],
            },
        )
        return r.status_code

    def run_tests(self):
        results = {}
        # TODO: expand to test all endpoints
        endpoints = [ep for ep in self.endpoints if "{" not in ep]
        for endpoint in endpoints:
            results[endpoint] = []
            pmts = self._get_pmts_for_endpoint(endpoint)
            if len(pmts) < 1:
                results[endpoint].append("no pmts returned")
            else:
                for pmt in pmts:
                    pmt['status'] = self._test_pmt_for_endpoint(endpoint, pmt)
                    results[endpoint].append(pmt)
        return results


if __name__ == "__main__":
    connegp_test_client = ConnegpTestClient(host="http://localhost:8000")
    result = connegp_test_client.run_tests()
    pprint(result)
