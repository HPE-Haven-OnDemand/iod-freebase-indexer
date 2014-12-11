import json
import click
from iodpython.iodindex import IODClient
import shelve
from utils import FreebaseUtil

service_url = 'https://www.googleapis.com/freebase/v1/mqlread'


def deleteIndex(index):
    click.echo('deleted index %s' % index)
    client.deleteIndex(index)

@click.command()
@click.option('--config', default="config.json", prompt="Config file", type=click.File('rb'))
@click.option('--input', default="test.json", prompt="Freebase MQL json file", type=click.File('rb'))
@click.option('--delete', is_flag=True)
@click.option('--resume', is_flag=True)
def main(input,delete,resume,config):

    config=json.loads(config.read())
    config.update(json.loads(input.read()))
    client = IODClient("http://api.idolondemand.com/",
                        config["iodkey"])
    if delete:
      deleteIndex(config["iodindex"])

    category=False
    description=False
    flavor="standard"
    if config["type"]=="categories":
        category=True
        flavor="categorization"

    if config.get("description",False):
      description=True

    try:
      index=client.createIndex(config["iodindex"],flavor="categorization",index_fields=config.get("indexfields",[]), parametric_fields=config.get("parametricfields",[]))
    except:
      index=client.getIndex(config["iodindex"])

    cursor=""
    if resume:
      cursor= open('cursor','rb').read()

    query= config["freebasequery"]
    freebaseUtil = FreebaseUtil(config["freebasekey"])
    freebaseUtil.aliases=config["aliasfields"]
    freebaseUtil.runQuery(index,query,category=category,description=description,cursor=cursor)

if __name__ == '__main__':
    main()
