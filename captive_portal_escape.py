#!/usr/bin/env python3
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
##optional
import textwrap
from datetime import datetime

"""captive_portal_escape.py: Schedulable automatic-ish escape from a wi-fi "captive portal". 
Useful for situations such as allowing a voice-controlled assistant to remain connected.
Distributed under the MIT License.
"""
__author__      = "Justin Warwick <justin.warwick@gmail.com>"
__copyright__   = "Copyright 2022, U.S.A."
__license__     = "MIT License (https://opensource.org/licenses/MIT)"

#TODO: suggested crontab line, include alternating log/rolling
#TODO: optional parameterization for base_URL, just assume google for default case

# go to google or whatever, to elicit a captive portal page. do we want a fallback URL as well?
# then discover where it was going to go next (often the form "action")
# then "go" there.

#TODO: .netrc or some kind of graceful/best-effort .captive_portal_credentials.json read-in if found.
payload = {
    'username': 'JDoe',
    'password': 'please'
}
#base_URL = "http://katana.int.bry.com/demo/abutton.html"
#base_URL = "http://katana.int.bry.com/demo/bbutton.html"
base_URL = "https://www.google.com/"
login_URL= ""
captivity = True  # ASSUMPTION to start
verbose = False

print(datetime.now() ) 
with requests.Session() as ht_session:
    ht_probe = ht_session.get(base_URL)
    #DEBUG#this is the whole document source# print(ht_probe.text)
    doc = BeautifulSoup(ht_probe.text, 'html.parser')
    
    # First, do some kind of basic check to see if we actually /did/ make it to our litmus uri i
    # (i.e., actually not captive currently)
    for elem in doc.find_all():
        if verbose:
            print(elem.name) 
            for interesting_attribute in "name","description","alt","title","description","role":
                if elem.get(interesting_attribute): 
                    print("\t  "+elem.get(interesting_attribute), end="")
        # And here is the "litmus" (if we stuck with google as our testing base_URL) 
        # for detecting whether we indeed punched through and actually got the true content of base_URL.
        if elem.get('name') == "q" and "Search" in elem.get('title'):
            captivity = False
    if verbose:
        print("\n")

    if not captivity:
        title_detail = doc.find_all('title')[0]
        if title_detail:
            title_detail = " (" + title_detail.text + ")"
        print("Concluding that we are NOT currently captive because: found litmus element in retrieved html document. " + title_detail)
    else:
        #TODO: try to detect things like checkboxes that must be checked and submitted in the response, induce a "checked" value.
        #   /maybe/ analyse the text a little. What if it's reversed? what if its something else like "go ahead and send me spam!"
        # https://requests.readthedocs.io/en/latest/user/quickstart/#more-complicated-post-requests
        # This is real rough and NOT working right now...
        formdata=""
        '''
        checkboxen = doc.find_all('input',type="checkbox")
        if checkboxen:
            checkboxname =checkboxen[0].get('name') 
            print("got us a checkbox right here!! " + checkboxname)
            formdata = {checkboxname: "on" }
            '''
        #TODO: try to detect a text name box or email box and fill it out with (preferably mailinator class) identity info
        #TODO: perhaps also scan for crazy javascript that might be an obstacle.
        for button in doc.find_all('button'):
            if re.search(button.text,"accept|agree|confirm|submit|continue", flags=re.IGNORECASE):
                print("\tCandidate button FOUND:  " + button.text)
                print( button.parent.name )
                # walk back up until you find the ancestor form.
                ancestor_element = button.parent
                while ancestor_element.name != "form" and ancestor_element.name != "body":
                    if verbose:
                        print("\t\ttag: " + ancestor_element.name)
                    ancestor_element = ancestor_element.parent
    
                if ancestor_element.name == "form":
                    print("Based on ancestor form tag, action specified:"+ ancestor_element.get('action'))
                    login_URL = ancestor_element.get('action')
                    #TODO: should validate this string for uri-ishness. if its a javascript link, might need to get clever here.
                    #TODO: discover, record, and honor http method of the form.
                    http_method = ancestor_element.get('method')
                    if http_method:
                        print("HTTP Method specified:"+http_method)
                else:
                    print("No element found that seems like an accept/submit! Maybe portal page has weird html structure?")

        if not login_URL:
            #TODO:  also try the search again with "<input type='submit'/> :
            for button in doc.find_all('input',type="submit"):
                if button.get("type") == "submit":
                    print("\tCandidate old-style input-submit FOUND, 'value':  " + button.get('value'))
                    print("\thowever, doing something about that is #TODO :(")
        
        if login_URL.startswith("http"):
            print("Extracted URI appears to be an absolute URI, just roll with it...")
        else:
            login_URL = urljoin(base_URL, login_URL)
            print("Ok, revised login URI (because it was relative) : " + login_URL)
        #TODO: seek out <base> tag and allow that to override implicit base, if found.
        if login_URL == base_URL:
            print("Actually, probably this is not going to work. The base URL and login URL being the same is usually a sign of soft failure.")
    
        print("\nHere goes: attempting to induce acceptance/confirmation/whatever and escape captivity...\n")
        ht_action = ht_session.get(login_URL, data=formdata)
        if verbose:
            print("  ----\n" + textwrap.indent(ht_action.text,"  |  ") + "  ----\n")
        else:
            print(re.findall('success|thank you|enjoy|search', ht_action.text, flags=re.IGNORECASE))
    
        #p = ht_session.post(login_URL, data=payload)
        #print(p.text)
