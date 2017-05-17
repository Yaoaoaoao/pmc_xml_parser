from pymongo import MongoClient

client = MongoClient('localhost')
db = client.pmc


def fetch_text(pmid, pmcid, id_):
    return db.text.find_one({"pmid": pmid, "pmcid": pmcid, "id": int(id_)})
