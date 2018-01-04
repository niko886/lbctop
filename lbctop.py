#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import unittest
import logging
import pprint
import conf
import time
import random
        
from lbcapi import api

if os.path.exists('lbctest.log'):
    os.remove('lbctest.log')

logging.basicConfig(format='%(levelname)s\t%(funcName)s\t%(lineno)d\t%(message)s', level=logging.DEBUG, filename='lbctest.log')
log = logging.getLogger("lbctest")

console = logging.StreamHandler()
console.setLevel(logging.INFO)

log.addHandler(console) 


class localBTC:

    def getMyAdInfo(self):
        
        j = self._conn.call('GET', '/api/ad-get/%s/' % self._ad_id).json()
        
        d0 = j['data']['ad_list'][0]['data']
        
        self.username = d0['profile']['username']
        
        self._ad0 =  d0
        
        return 

    def __init__(self, key, secret, id):
        
        self._conn = api.hmac(key, secret)
        
        log.debug("[*] get initial info...")
        
        self._ad_id = id
        
        self.getMyAdInfo()
                
        log.debug(pprint.pformat(self._ad0))
        
    def getMinValue(self):
         
        log.info('requesting current sell offers...')
        j = self._conn.call('GET', '/sell-bitcoins-online/UAH/.json').json()
        log.debug(pprint.pformat(j)) 
         
        adlist = j['data']['ad_list']   
         
        log.debug(pprint.pformat(adlist[0]['data']))
         
        f = float(adlist[0]['data']['temp_price'])
         
        self._minBuyValue = f + 500
         
        log.info("min sell set: %f", self._minBuyValue)
         
        return f
        
    def simpleSet(self, price):
        
        ad = self._ad0
        
        pe = ad['price_equation']
        
        log.debug("current pe = %s", pe)
        
        req = {'price_equation':  price,
               'bank_name': ad['bank_name'],
               'countrycode': ad['countrycode'],
               'currency': ad['currency'],
               'min_amount': ad['min_amount'],
               'max_amount': ad['max_amount'],
               'lat': ad['lat'],
               'lon': ad['lon'],
               'city': ad['city'],
               'account_info': ad['account_info'],
               'msg': ad['msg'],
               'visible': ad['visible'],
               'location_string': ad['location_string'],
               'sms_verification_required': ad['sms_verification_required'],
               'require_identification': ad['require_identification'],
               'track_max_amount': ad['track_max_amount'],
               'require_trusted_by_advertiser': ad['require_trusted_by_advertiser'],

            }
                 
        log.info("updating price: %s", price)
        j = self._conn.call('POST', '/api/ad/%s/' % self._ad_id, params=req ).json()    
        log.info(pprint.pformat(j))
        
    def doMagic(self):
        
        
        # get my info
        
        # ... already done in __init__
        
        # get min value
        
        self.getMinValue()
        
        # calculate lowest bid within limit

        log.info('requesting current buy offers...')
        
        j = self._conn.call('GET', '/buy-bitcoins-online/UAH/.json').json()
        
        log.debug("*** current offers ***")
        log.debug(pprint.pformat(j))
        
        adlist = j['data']['ad_list'] 
        
        
        # just dump info
        
        for a in adlist[:10]:
            log.info(" %30s   %s / $%s   (%s-%s)", 
                     a['data']['profile']['name'],
                     a['data']['temp_price'],
                     a['data']['temp_price_usd'],
                     a['data']['min_amount'],
                     a['data']['max_amount'],
                     )
        
        idx = -1
        
        for a in adlist[:10]:
            
            idx += 1
            
            
            if idx == 9:  # skip last one
                break
            
            currentMin = float(a['data']['min_amount'])
            
            currentName = a['data']['profile']['name'].split(' ')[0] # nik819 (100+; 99%) -> nik819


            if self.username == currentName:
                
                continue
                
            
            if currentMin > float(self._ad0['max_amount']):
                
                log.info("[!] skipping %s, because %s > %s",
                         a['data']['profile']['name'],
                         a['data']['min_amount'],
                         self._ad0['max_amount'])
                
                continue 
            
            
            # set us top
            
            # ... but check min value first
            
            price = float(a['data']['temp_price']) - random.randint(5, 99) - random.randint(1, 9) * 0.1
                         
            if price < self._minBuyValue + 5000:
                log.error("[!] minimum limit reached, can't set value below %f + 5000" % self._minBuyValue)
                break
        
            if float(self._ad0['temp_price']) + 100 > float(a['data']['temp_price']) and \
               float(self._ad0['temp_price']) < float(a['data']['temp_price']):
                
                log.info("all fine, skipping...")
                
            else:

                self.simpleSet(price)
                
                
            break

        
    

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDoMagic(self):


        while True:
            
            lbtc = localBTC(conf.HMAK_KEY, conf.HMAK_SECRET, conf.AD_ID)
            
            lbtc.doMagic()

            time.sleep(60)
        
if __name__ == "__main__":

    unittest.main()
    
    
    
    
