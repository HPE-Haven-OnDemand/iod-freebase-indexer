iod-freebase-indexer
====================

Indexes text datasets or custom entity extraction datasets from freebase to IDOL OnDemand

For more information and for a list of all IDOL OnDemand APIs create an account on [idolondemand.com](http://idolondemand.com).

IDOL OnDemand offers many functionalities including text indexing and analytics capabilities which are the focus of this script.

###Context

This tool helps with the creation of Custom Entity Datasets from freebase as discussed in the following [blog post](https://community.idolondemand.com/t5/Blog/Custom-Entity-Extraction-with-IDOL-OnDemand-Categories/ba-p/1285).

It can also create custom search datasets with wikipedia descriptions, which can be very useful to say: quickly recommend TV shows similar based on description.

###Prerequisites

You'll need an IDOL OnDemand APIkey that you can get on [idolondemand.com](http://idolondemand.com)

You'll also need a Freebase API Key which you can get through a google developer account, [here](https://code.google.com/apis/console)

###Install


Just run a pip install to install the dependecies ( currently only one )

```bash
pip install -r requirements.txt
```

###Configuration

You'll need a ```config.json``` ( or any other name) file that will hold your keys.

```json
{
  "iodkey":"myapikey",
  "freebasekey":"yourfreebasekey"
}
```

###Usage

```
python commandline.py --help
```

The configs directory in the repo contains some input configurations to get you started. For example ```animalsindex.json``` will index animals data + their wikipedia descriptions

```
python commandline.py --config configs/config.json --input configs/animalsindex.json
```



###Input Formats

```json
{
  "iodindex":"animals",
  "freebasequery":[{
    "name": null,
    "mid":null,
    "/common/topic/alias": [],
    "type": "/biology/animal",
    "key": {
      "namespace": "/wikipedia/en_id",
      "value": null
    },
    "/biology/organism_classification/scientific_name": []
  }],
  "aliasfields":["alias","scientific_name"],
  "parametricfields":[],
  "type":"categories"
}
```

* **iodindex**: The IDOL OnDemand index that you want to index into
* **freebasequery**: A freebase MQL query. Create and test your own on [http://www.freebase.com/query](http://www.freebase.com/query)
* **type**: **categories** or **index** , categories will create a "categorization" flavor index and create boolean rules for matchin each element from freebase. index will create a "standard" flavor index for search.
* **description**: false by default. set to true and each document will be indexed along with its wikipedia description. IMPORTANT with type set to index.
* **aliasfields**: when doing a categories type custom entity extraction, aliasfields is a list of extra fields it will use to match against. Remember those fields should be part of the freebasequery!.
* **parametricfields**: these fields will be indexed as parametric type fields meaning that the idol field_text query operator can be used to filter against those values.


**Note**: 
   ``` "mid":null,``` is required in all freebasequeries currently as the mid is used for the unique id.
   


###Example inputs

Categories/Entity Extraction datasets
* animals.json : extract animal names based on their common aliases or scientific names
* cars.json : extract car models, filter by brands etc.
* legalcases.json : extract legal cases 
* drugs.json : extract drugs based on various denominations
* celestialobjects.json : planets, asteroids, stars can be extracted

Many of these have a bunch of fields being indexed as well allowing for even more refined extraction as well as the return of useful information on match.

Search Datasets
* animalstext.json : index the descriptions for every animal on freebase for search and analytics


###Freebase field conversion

Full path fields will only keep the final name:    
```"/biology/organism_classification/scientific_name": []``` in the freebasequery will result in a field called "scientific_name" to be stored in each idolondemand document.

```quickname:field``` will store its value as "quickname" only 

```
    "defendant:parties": [{
      "optional": true,
      "role": "Defendant",
      "parties": []
    }],
    "plaintiff:parties": [{
      "optional": true,
      "role": "Plaintiff",
      "parties": []
    }],
```

The above will store the parties field for each role as 
defendant_parties and plaintiff_parties


###Other Functionalities

####Resuming

Some freebase queries may have a lot of files. If the script can't run to completion, the ```--resume``` flag will resume the last run script to its last indexing point ( assuming --config and --input are set to be the same )

#### Ensuring index freshness

The ```--delete``` flag will DELETE the target index and create a new one before data is indexed into it.

