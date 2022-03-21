import os
import json

from rdflib import Namespace
from rdflib.namespace import SKOS, RDF, DCTERMS, RDFS, DCAT, PROV, OWL, SDO

GEO = Namespace("http://www.opengis.net/ont/geosparql#")

SYSTEM_URI = os.environ.get("SYSTEM_URI", "localhost")
SYSTEM_INFO = json.loads(
    os.environ.get(
        "SYSTEM_INFO",
        """{
    "Prez": {
        "title": "SURROUND Prez",
        "desc": "Prez demo instance for SURROUND Australia"
    },
    "VocPrez": {
        "title": "SURROUND Vocabs",
        "desc": "Demo vocabularies",
        "data_uri": "http://exampledata.org"
    },
    "CatPrez": {
        "title": "",
        "desc": "",
        "data_uri": ""
    },
    "TimePrez": {
        "title": "",
        "desc": "",
        "data_uri": ""
    },
    "SpacePrez": {
        "title": "SURROUND Spatial Data",
        "desc": "Floods spatial data",
        "data_uri": "http://exampledata.org"
    }
}""",
    )
)
DEBUG = os.environ.get("DEBUG", True)
DEMO = os.environ.get("DEMO", True)
ALLOW_PARTIAL_RESULTS = os.environ.get("ALLOW_PARTIAL_RESULTS", True)
SPARQL_CREDS = json.loads(
    os.environ.get(
        "SPARQL_CREDS",
        """{
    "VocPrez": {
        "SPARQL_ENDPOINT": "http://localhost:3030/surround-vocabs",
        "SPARQL_USERNAME": "",
        "SPARQL_PASSWORD": ""
    },
    "CatPrez": {
        "SPARQL_ENDPOINT": "",
        "SPARQL_USERNAME": "",
        "SPARQL_PASSWORD": ""
    },
    "TimePrez": {
        "SPARQL_ENDPOINT": "",
        "SPARQL_USERNAME": "",
        "SPARQL_PASSWORD": ""
    },
    "SpacePrez": {
        "SPARQL_ENDPOINT": "http://localhost:3030/surround-features",
        "SPARQL_USERNAME": "",
        "SPARQL_PASSWORD": ""
    }
}""",
    )
)
ENABLED_PREZS = json.loads(
    os.environ.get("ENABLED_PREZS", '["VocPrez", "SpacePrez"]')
)  # must use proper capitalisation
THEME_VOLUME = os.environ.get("THEME_VOLUME", None)
SIDENAV = os.environ.get("SIDENAV", "False") == "True"
SEARCH_ENDPOINTS = [{"name": "Self", "url": "self"}] + json.loads(
    os.environ.get(
        "SEARCH_ENDPOINTS",
        """[]""",
    )
)

NAMESPACE_PREFIXES = {
    str(SKOS): "skos",
    str(RDF): "rdf",
    str(RDFS): "rdfs",
    str(DCAT): "dcat",
    str(DCTERMS): "dcterms",
    str(PROV): "prov",
    str(OWL): "owl",
    str(SDO): "sdo",
    str(GEO): "geo",
}