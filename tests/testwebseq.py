import mechanize
import cookielib
import json
import urllib
import urllib2
import requests
from requests.auth import HTTPBasicAuth

import json

def seqPostPause():

    data = {'action':
            {'type':'BUTTONCLICK',
            'target_id':'PAUSERUN'}}

    url = "http://localhost/Elixys/RUN"

    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostAbort():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'ABORTRUN'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostHome():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'HOME'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostTimerOverride():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'TIMEROVERRIDE'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostTimerContinue():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'TIMERCONTINUE'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostUserInput():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'USERINPUT'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostUserInput():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'USERINPUT'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r

def seqPostContinueRun():
    data = {'action':
            {'type':'BUTTONCLICK',
             'target_id':'CONTINUERUN'}}

    url = "http://localhost/Elixys/RUN"
    r = requests.post(url,
            data=json.dumps(data),
            auth=HTTPBasicAuth('devel','devel'))
    return r


postSeqTests = [seqPostPause,
                seqPostAbort,
                seqPostHome,
                seqPostTimerOverride,
                seqPostTimerContinue,
                seqPostUserInput,
                seqPostContinueRun]

if __name__ == '__main__':


    for test in postSeqTests:
        r = test()
        print r.text

    from IPython import embed
    embed()
