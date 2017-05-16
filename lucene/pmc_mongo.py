from pymongo import MongoClient

client = MongoClient('localhost')
db = client.pmc


def fetch_text(pmid, id_):
    return db.text.find_one({"pmid": pmid, "id": int(id_)})
