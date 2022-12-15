#!/usr/bin/env python 
from bs4 import BeautifulSoup
import csv
import requests
import sys
import re
from urllib.parse import urlparse

REGEX_FONT_DOMAINS = "(fonts.(google|gstatic))|fast.fonts"

def find_links_in_css(css_url):
    try:
        r = requests.get(css_url, allow_redirects=True)
        if (r.status_code == 200):
            try:
                findings = []

                matches = re.findall(re.compile(r"(src: url\((https:|http:|)\/\/(" + REGEX_FONT_DOMAINS + ")[^\)]*\))"), str(r.content))
                for m in matches:
                    findings.append(m[0])

                return findings
            except Exception as e:
                print (e)
    except Exception as e:
        print (e)


def scan_website(domain):
    try: 
                #check http because follow we can follow the redirect if https
                r = requests.get('http://' + domain, allow_redirects=True)
                if (r.status_code == 200):
                    try:
                        parsed_uri = urlparse(r.url)
                        mydomain_with_scheme = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
                        soup = BeautifulSoup(r.content, "html.parser")

                        findings = []
                        links = soup.findAll('link',{'href': re.compile(REGEX_FONT_DOMAINS)})
                        for x in links:
                            findings.append(str(x))

                        csslinks = soup.findAll('link', {'type': 'text/css'})
                        for x in csslinks:
                            csslink = x['href']

                            # get the full url
                            if csslink.startswith('//'):
                                csslink = 'https:' + csslink
                            elif csslink.startswith('/'):
                                csslink = mydomain_with_scheme + csslink

                            # complain about any links to external css
                            if not csslink.startswith(mydomain_with_scheme + '/'):
                                findings.append(str(x))
                            else:
                                # check local css files for links to external fonts
                                findings.extend(find_links_in_css(csslink))

                        if (len(findings) > 0):
                            result = {
                                'url' : domain,
                                'links' :  "|".join(findings)
                            }
                            return result
                    except Exception as e:
                        print (e)
    except Exception as e:
                print (e)




if __name__ == "__main__":
    if len(sys.argv) > 2:
        csv_file = sys.argv[1]
        with open(csv_file, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter=',', quotechar='|')
            results = []
            for row in reader:
                
                result = scan_website(row[0])
                if result:
                    results.append(result)

        csv_output_file = sys.argv[2]   
        with open(csv_output_file, 'w') as csvfile:
                fieldnames = ['url', 'links']
                writer = csv.DictWriter(csvfile, fieldnames)
                for data in results:
                    writer.writerow(data)

