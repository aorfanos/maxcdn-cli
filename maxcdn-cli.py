#!/usr/bin/python

from prettytable import PrettyTable
from maxcdn import MaxCDN #https://github.com/maxcdn/python-maxcdn
import fire
import os
import click

# MaxCDN("alias", "consumer_key", "consumer_secret")
api = MaxCDN("","","")

class Zone(object):
    #create zone
    def add(self,zoneName,originURL,enableFlex=False,customDomain="",zoneType="pull"):
        print("Creating pull zone "+zoneName+" with origin:"+originURL)
        request = api.post("/zones/pull.json", {'name': zoneName, 'url': originURL, 'compress': '1'})
        print("Created new pull zone with ID: "+str(request['data']['pullzone']['id']))

        if zoneType != "pull" and customDomain != "":
            print("Cannot create customDomain for "+zoneType+" type. Aborting")
            exit(1)

        #@TODO: implement Push and VOD zone api calls
        #if zoneType == "push"
        
        if customDomain != "":
            Domain().add(str(request['data']['pullzone']['id']),customDomain)

        if enableFlex != False:
            api.post('/zones/pull/'+str(request['data']['pullzone']['id'])+'/flex.json')
            print("Enabled flex mode")

    def delete(self, zoneId, force=0):
        zoneURL = str(Zone().info(zoneId, 0, "cdn_url"))
        table = PrettyTable(['Operation', 'Zone ID', 'Origin URL', 'State'])
        print("Deleting zone with ID "+str(zoneId)+" and Zone URL: "+zoneURL)

        if force == 0:
            #https://click.palletsprojects.com/en/7.x/api/#click.confirm
            if click.confirm('Are you sure you wish to proceed?', default=False):
                api.delete("/zones/pull.json/"+str(zoneId))
                table.add_row(['Delete Zone', str(zoneId) ,zoneURL, 'Deleted'])
            else:
                print("Delete operation aborted")
        else:
            api.delete("/zones/pull.json/"+str(zoneId))
            table.add_row(['Delete Zone', str(zoneId), zoneURL, 'Deleted'])
            print("Deleted zone "+str(zoneId)+" with URL "+zoneURL)


        print(table)

    class flex(object):

        def enable(self, zoneId):
            api.post('/zones/pull/'+str(zoneId)+'/flex.json')
            print("Enabled flex mode on zone with URL: "+Zone().info(str(zoneId), 0, outputField="url"))
        def disable(self, zoneId):
            api.delete('/zones/pull/'+str(zoneId)+'/flex.json')
            print("Disabled flex mode on zone with URL: "+Zone().info(str(zoneId), 0, outputField="url"))

    def update(self,zoneId, key, value):
        params = dict()
        params[key] = value
        
        #@TODO: implement solution for custom_domain update -- need to register domainID
        if key == 'custom_domain':
            try:
                api.put("/zones/pull.json/"+str(zoneId)+'/customdomains.json/', {"custom_domain":value})
            except Exception as e:
                print('(Probably custom domain creation needed- attempting to handle this internally)\nError message:'+str(e))
                Domain().add(str(zoneId),value)
                print('Done')
        else: 
            response = api.put("/zones/pull.json/"+str(zoneId), params=params)

        print("Updated zone "+str(zoneId)+" with key:value "+str(key)+":"+str(value))

    def info(self,zoneID, prettyPrint=True, outputField="", fullReport=False):
        response = api.get("/zones/pull.json/"+str(zoneID))
        cdnURL = response['data']['pullzone']['cdn_url']
        originURL = response['data']['pullzone']['url']
        prettyTable = PrettyTable(['Zone ID', 'CDN URL', 'Origin URL'])
        fullTable = PrettyTable(['Key','Value'])

        if fullReport == True:
            for field in response['data']['pullzone']:
                fullTable.add_row([field, response['data']['pullzone'][field]])
            print(fullTable)
        elif prettyPrint == True:
            prettyTable.add_row([zoneID, cdnURL, originURL])
            print(prettyTable)
        elif outputField != "":
            return(response['data']['pullzone'][outputField])
        else:
            #@TODO: properly print and handle errors
            print("Either pretty print or define desirable field to extract.")

    # get zone info
    # ARGS: zoneID (int), prettyPrint (bool)
    # prettyPrint is True by default for terminal printing use
    # and outputField (optional) values can be found at https://docs.maxcdn.com/
    def list(self):
        response = api.get('/zones/pull.json')
        table = PrettyTable(['Zone ID', 'CDN URL', 'Origin URL'])

        for count in range(0,len(response['data']['pullzones'])):
            id = response['data']['pullzones'][count]['id']
            cdn_url = response['data']['pullzones'][count]['cdn_url']
            origin_url = response['data']['pullzones'][count]['url']

            table.add_row([id, cdn_url, origin_url])

        print(table)

class Domain(object):
    
    def add(self,zoneId,domainName):
        table = PrettyTable(['Operation','Zone ID','Origin URL','Domain ID','State'])
        response = api.post('/zones/pull/'+str(zoneId)+'/customdomains.json', {"custom_domain":domainName})
        table.add_row(['Domain Add',str(zoneId),domainName,response['data']['customdomain']['id'],'Success'])
        return table

    def delete(self,zoneId,domainId):
        table = PrettyTable(['Operation','Zone ID','Zone Name','Domain ID','State'])
        api.delete('/zones/pull/'+str(zoneId)+'/customdomains.json/'+str(domainId))
        table.add_row(['Domain Delete',str(zoneId),str(Zone().info(zoneId,0,'name')),str(domainId),'Success'])
        return table
    

class Account(object):
    # get account info
    def info(self):
        response = api.get("/account.json")
        table = PrettyTable(['Key','Value'])

        for field in response['data']['account']:
            table.add_row([ field, response['data']['account'][field]])
            
        print(table)

class Cache(object):

    def purge(self,zoneId, prettyPrint=False, silent=False):
        api.purge(zoneId)
        table = PrettyTable(['Operation', 'Origin URL', 'State'])
        url = Zone().info(str(zoneId),0,outputField="url")
        table.add_row(['Purge CDN Cache',url,"Success"])
        
        if prettyPrint == True:
            return(table)
        elif silent == True:
            prettyPrint = False
            exit(0)
        else:
            prettyPrint = True
            return(table)

class SSL(object):

    def list(self):
        response = api.get('/ssl.json')
        table = PrettyTable(['Domain','Expiration Date', 'isWildcard'])

        for count in range(0,len(response['data']['certificates'])):
            table.add_row([response['data']['certificates'][count]['domain'], response['data']['certificates'][count]['date_expiration'], response['data']['certificates'][count]['wildcard']])
        print(table)

    def add(self, ssl_crt_path, ssl_key_path, ssl_cabundle_path=""):
        crt = open(ssl_crt_path,"r")
        key = open(ssl_key_path,"r")

        params = {"ssl_crt":str(crt),"ssl_key":str(key)}

        if ssl_cabundle_path != "" and os.path.exists(ssl_cabundle_path):
            cabundle = open(ssl_cabundle_path,"r")
            params = {"ssl_crt":str(crt),"ssl_key":str(key),"ssl_cabundle":str(cabundle)}

        api.post('/ssl.json',data=params)

class Pipeline(object):

    def __init__(self):
        self.zone = Zone()
        self.account = Account()
        self.cache = Cache()
        self.domain = Domain()
        self.ssl = SSL()

if __name__ == "__main__":
    fire.Fire(Pipeline)
