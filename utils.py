import json
import urllib
import requests
import itertools
import time


class FreebaseUtil(object):

    freebase_topic_url="https://www.googleapis.com/freebase/v1/topic{}?filter=/common/topic/description&key={}"

    service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
    aliases=[]
    def __init__(self,freebase_key):
        self.freebase_key=freebase_key


    def runQuery(self,index,query,cursor="",category=False,description=False,):
        count=100
        if not cursor:
          cursor = self.do_query(index,query,cursor=cursor,category=category,description=description)
        while(cursor):
            print cursor
            count+=100
            print count
            open('cursor','wb').write(cursor)
            cursor = self.do_query(index,query,cursor=cursor,category=category,description=description)


    def do_query(self,index,query,cursor="",category=False,description=False):
        params = {
                'query': json.dumps(query),
                'key': self.freebase_key
        }
        params['cursor']=cursor

        url = self.service_url + '?' + urllib.urlencode(params)
        response = requests.get(url).json()#json.loads(urllib2.urlopen(url).read())
        for result in response['result']:
            #print result['mid']
            #print result
            if description:
                try:
                    freebase_url=self.freebase_topic_url.format(result["mid"],self.freebase_key)
                    content = requests.get(freebase_url).json()
                    content=content["property"]["/common/topic/description"]["values"][0]["value"]
                    result["content"]=content
                except:
                    pass
                    #print result
                    #print content, freebase_topic_url.format(result["mid"],api_key)
            else:
                result["content"]=""

            result["reference"] = result.pop("mid")
            result["title"] = result.pop("name")
            #characters= result["issues"];
            #if characters:
            #    characters=map(lambda x: x.get('characters_on_cover',[]) ,characters )
            #    characters=reduce(lambda x, y: x+y, characters)
            #result["featured_characters"]+=characters
            #result.pop('issues')
            result= self.flatten(result)

            result= self.flattenlists(result)
            if category:
              result= self.standardize(result)
              result=self.prepareCategory(result)
              if result==0:
                continue
            #print result
            if "authorname" in result:
                result["category"]=result["authorname"]
            index.pushDoc(result)
            #print json.dumps(flatten(result),indent=4)
            #print result["continues"]
        try:
            print "trying to index"
            print index.commit(async=True).jobID

        except:
            print "indexing failed"

#        try:
#            print "trying to index"
#        except:
#            print "indexing failed"

        return response.get("cursor")

    def do_query_category(self,index,cursor=""):

        self.params['cursor']=cursor

        url = self.service_url + '?' + urllib.urlencode(self.params)
        response = requests.get(url).json()#json.loads(urllib2.urlopen(url).read())
        try:
          a=response['result']
        except:
          print response
        for result in response['result']:



            #print result['mid']
            #print result
            if self.description:
                try:
                    freebase_url=self.freebase_topic_url.format(result["mid"],self.params["key"])
                    content = requests.get(freebase_url).json()
                    content=content["property"]["/common/topic/description"]["values"][0]["value"]
                    result["content"]=content
                except:
                    pass
                    #print result
                    #print content, freebase_topic_url.format(result["mid"],api_key)
            else:
                result["content"]=""

            result["reference"] = result.pop("mid")
            result["title"] = result.pop("name")
            #characters= result["issues"];
            #if characters:
            #    characters=map(lambda x: x.get('characters_on_cover',[]) ,characters )
            #    characters=reduce(lambda x, y: x+y, characters)
            #result["featured_characters"]+=characters
            #result.pop('issues')

            result= self.flatten(result)
            result= self.flattenlists(result)
            result= self.standardize(result)
            result=self.prepareCategory(result)

            index.pushDoc(result)
            #print json.dumps(flatten(result),indent=4)
            #print result["continues"]
        #print index.name
        try:
            print "trying to index"
            print index.commit(async=True).jobID

        except:
            print "indexing failed"

        return response.get("cursor")

    def standardize(self,result):
        #print result,"hello"
        for k,v in result.iteritems():
          splits = k.split("/")
          #print len(splits)
          if len(splits)>1:
            result[splits[len(splits)-1]]=v
            result.pop(k)

        if 'key_namespace' in result:
          result.pop('key_namespace')
          result['wikipedia_url']="http://en.wikipedia.org/wiki/index.html?curid=%s" % result.pop("key_value")
        return result


    def prepareCategory(self,result):

        phrase = result["title"]
        if not phrase:
          return 0
        rest='("'+phrase+'") '
        content=phrase+" "
        #print result
        for aliaskey in self.aliases:
          for alias in result[aliaskey]:
            content+=alias+" "
            rest+=" OR (\"%s\") " % alias



        if "," in phrase:
          phrase =phrase.split(',')[0]
          rest+="OR (\"%s\") " % phrase

        if "Street" in phrase:
          rest+=" OR (\"%s\") " % phrase.replace("Street","")

        result['booleanrestriction']=rest
        result['content']=content
        return result

    def flatten(self,obj, key=""):
        key=key.split(":")[0]

        if type(obj) is dict:
            orig=dict(obj)
            for k,v in obj.iteritems():
                #print k,v
                #key=key.split(":")[0]
                #splits = key.split("/")
                #print len(splits)
                #key=splits[len(splits)-1]

                newkey=""
                if key:
                    newkey=key+"_"
                newkey+=k
                if type(v) is dict:
                    orig.update(self.flatten(v,newkey))
                    orig.pop(k)
                elif type(v) is list:
                        flatlist=self.flatten(v,newkey);

                        if flatlist:
                            orig.update(flatlist)
                            orig.pop(k)
                        #print flatten(val,newkey)
                        #orig.update(flatten(v,newkey))
                else:
                    if key:
                        orig[newkey]=v
                        orig.pop(k)
            return orig
        if type(obj) is list:

            new={}
            for a in obj:

                if type(a) is dict:
                    #key=key.split(":")[0]

                    for k,v in self.flatten(a,key).iteritems():
                        #print new.get(k,[]).append(v)
                        #print k,v
                        if type(v) is list:
                          k=key+"_"+k
                        new[k]=new.get(k,[])
                        new[k].append(v)


            if not new:
                return False
            return new
        return obj


    def flattenlists(self,obj):
        for k,v in obj.iteritems():
            if type(v) is list and len(v)>0 and not isinstance(v[0], basestring):
                obj[k]=list(itertools.chain(*v))

        return obj
