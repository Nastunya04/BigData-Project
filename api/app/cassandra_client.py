from cassandra.cluster import Cluster
from cassandra.query import dict_factory

def get_session():
    cluster = Cluster(["cassandra"])
    session = cluster.connect("wiki")
    session.row_factory = dict_factory
    return session