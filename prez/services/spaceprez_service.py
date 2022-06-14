from typing import Optional

from async_lru import alru_cache

from functools import lru_cache

from prez.services.sparql_utils import *


async def count_datasets():
    q = f"""
        PREFIX dcat: <{DCAT}>
        SELECT (COUNT(?d) as ?count)
        WHERE {{
            ?d a dcat:Dataset .
        }}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def list_datasets(page: Optional[int] = None, per_page: Optional[int] = None):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        PREFIX xsd: <{XSD}>
        SELECT DISTINCT ?d ?id ?label
        WHERE {{
            ?d a dcat:Dataset ;
                dcterms:identifier ?id ;
                dcterms:title ?label .
            OPTIONAL {{
                ?d dcterms:description ?desc .
            }}
            FILTER((lang(?label) = "" || lang(?label) = "en" || lang(?label) = "en-AU") && DATATYPE(?id) = xsd:token)
        }}{f"LIMIT {per_page} OFFSET {(page - 1) * per_page}" if page is not None and per_page is not None else ""}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def get_dataset_construct(
    dataset_id: Optional[str] = None, dataset_uri: Optional[str] = None
):
    if dataset_id is None and dataset_uri is None:
        raise ValueError("Either an ID or a URI must be provided for a SPARQL query")

    # when querying by ID via regular URL path
    query_by_id = f"""
        ?d dcterms:identifier "{dataset_id}"^^xsd:token ;
            a dcat:Dataset .
        BIND("{dataset_id}" AS ?id)
    """
    # when querying by URI via /object?uri=...
    query_by_uri = f"""
        BIND (<{dataset_uri}> as ?d)
        ?d a dcat:Dataset .
    """

    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX rdfs: <{RDFS}>
        PREFIX xsd: <{XSD}>
        CONSTRUCT {{
            ?d ?p1 ?o1 ;
                rdfs:member ?coll .
            ?coll dcterms:identifier ?coll_id ;
                dcterms:title ?coll_title .
            {construct_all_prop_obj_info}
            {construct_all_bnode_prop_obj_info}
        }}
        WHERE {{
            {query_by_id if dataset_id is not None else query_by_uri}
            ?d ?p1 ?o1 ;
                rdfs:member ?coll .
            ?coll dcterms:identifier ?coll_id ;
                dcterms:title ?coll_title .
            {get_all_bnode_prop_obj_info}
            {get_all_prop_obj_info}
        }}
    """
    r = await sparql_construct(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def count_collections(dataset_id: Optional[str] = None):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX xsd: <{XSD}>
        SELECT (COUNT(?coll) as ?count)
        WHERE {{
            ?d dcterms:identifier ?d_id ;
                a dcat:Dataset ;
                rdfs:member ?coll .
            FILTER ({f'STR(?d_id) = "{dataset_id}" && ' if dataset_id is not None else ""}DATATYPE(?d_id) = xsd:token)
            ?coll a geo:FeatureCollection .
        }}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def list_collections(
    dataset_id: Optional[str] = None, page: Optional[int] = None, per_page: Optional[int] = None
):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        PREFIX xsd: <{XSD}>
        SELECT DISTINCT *
        WHERE {{
            ?d dcterms:identifier ?d_id ;
                a dcat:Dataset ;
                dcterms:title ?d_label ;
                rdfs:member ?coll .
            FILTER(lang(?d_label) = "" || lang(?d_label) = "en" || lang(?label) = "en-AU")
            FILTER ({f'STR(?d_id) = "{dataset_id}" && ' if dataset_id is not None else ""}DATATYPE(?d_id) = xsd:token)
            ?coll a geo:FeatureCollection ;
                dcterms:identifier ?id ;
                dcterms:title ?label .
            OPTIONAL {{
                ?coll dcterms:description ?desc .
            }}
            FILTER(lang(?label) = "" || lang(?label) = "en" || lang(?label) = "en-AU")
            FILTER(DATATYPE(?id) = xsd:token)
        }}{f"LIMIT {per_page} OFFSET {(page - 1) * per_page}" if page is not None and per_page is not None else ""}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def get_collection_construct_1(
    dataset_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    collection_uri: Optional[str] = None,
):
    if collection_id is None and collection_uri is None:
        raise ValueError("Either an ID or a URI must be provided for a SPARQL query")

    # when querying by ID via regular URL path
    query_by_id = f"""
        FILTER (STR(?d_id) = "{dataset_id}")
        ?coll a geo:FeatureCollection ;
            dcterms:identifier ?id .
        ?d a dcat:Dataset ;
            rdfs:member ?fc ;
            dcterms:identifier ?d_id .
        FILTER (STR(?id) = "{collection_id}")
    """
    # when querying by URI via /object?uri=...
    query_by_uri = f"""
        BIND (<{collection_uri}> as ?coll)
        ?coll a geo:FeatureCollection .
    """

    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        PREFIX xsd: <{XSD}>
        CONSTRUCT {{
            ?coll ?p1 ?o1 .
            
            {construct_all_prop_obj_info}
            {construct_all_bnode_prop_obj_info}

            ?d a dcat:Dataset ;
                dcterms:identifier ?d_id ;
                dcterms:title ?d_label ;
                rdfs:member ?coll .
        }}
        WHERE {{
            {query_by_id if collection_id is not None else query_by_uri}
            ?coll ?p1 ?o1 .
            
            FILTER(!STRENDS(STR(?p1), "member"))

            ?d a dcat:Dataset ;
                rdfs:member ?fc ;
                dcterms:identifier ?d_id ;
                dcterms:title ?d_label .
            FILTER(DATATYPE(?d_id) = xsd:token)
            {get_all_bnode_prop_obj_info}
            {get_all_prop_obj_info}
        }}
    """
    r = await sparql_construct(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def get_collection_construct_2(
    dataset_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    collection_uri: Optional[str] = None,
):
    if collection_id is None and collection_uri is None:
        raise ValueError("Either an ID or a URI must be provided for a SPARQL query")

    # when querying by ID via regular URL path
    query_by_id = f"""
        FILTER (STR(?d_id) = "{dataset_id}")
        ?coll a geo:FeatureCollection ;
            dcterms:identifier ?id .
        ?d a dcat:Dataset ;
            dcterms:identifier ?d_id ;
            rdfs:member ?fc .
        FILTER (STR(?id) = "{collection_id}")
    """
    # when querying by URI via /object?uri=...
    query_by_uri = f"""
        BIND (<{collection_uri}> as ?coll)
        ?coll a geo:FeatureCollection .
    """

    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        CONSTRUCT {{
            ?coll rdfs:member ?mem .
        }}
        WHERE {{
            {query_by_id if collection_id is not None else query_by_uri}
            ?coll rdfs:member ?mem .
        }} LIMIT 20
    """
    r = await sparql_construct(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


@alru_cache(maxsize=20)
async def count_features(
    dataset_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    cql_query: Optional[str] = None,
):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX xsd: <{XSD}>
        
        SELECT (COUNT(?f) as ?count) 
        WHERE {{
            ?d dcterms:identifier ?d_id ;
                a dcat:Dataset ;
                rdfs:member ?coll .
            FILTER ({f'STR(?d_id) = "{dataset_id}" && ' if dataset_id is not None else ""}DATATYPE(?d_id) = xsd:token)
            ?coll dcterms:identifier ?coll_id ;
                a geo:FeatureCollection ;
                rdfs:member ?f .
            FILTER ({f'STR(?coll_id) = "{collection_id}" && ' if collection_id is not None else ""}DATATYPE(?coll_id) = xsd:token)
            ?f a geo:Feature .
            {cql_query or ""}
        }}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


@alru_cache(maxsize=20)
async def list_features(
    dataset_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    cql_query: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        PREFIX xsd: <{XSD}>
        SELECT DISTINCT *
        WHERE {{
            ?d dcterms:identifier ?d_id ;
                a dcat:Dataset ;
                dcterms:title ?d_label ;
                rdfs:member ?coll .
            FILTER(lang(?d_label) = "" || lang(?d_label) = "en")
            FILTER ({f'STR(?d_id) = "{dataset_id}" && ' if dataset_id is not None else ""}DATATYPE(?d_id) = xsd:token)
            ?coll a geo:FeatureCollection ;
                dcterms:identifier ?coll_id ;
                dcterms:title ?coll_label ;
                rdfs:member ?f .
            FILTER(lang(?coll_label) = "" || lang(?coll_label) = "en")
            FILTER ({f'STR(?coll_id) = "{collection_id}" && ' if collection_id is not None else ""}DATATYPE(?coll_id) = xsd:token)
            ?f a geo:Feature ;
                dcterms:identifier ?id .
            FILTER(DATATYPE(?id) = xsd:token)
            OPTIONAL {{
                ?f dcterms:description ?desc .
            }}
            OPTIONAL {{
                ?f dcterms:title ?label .
                FILTER(lang(?label) = "" || lang(?label) = "en" || lang(?label) = "en-AU")
            }}
            {cql_query if cql_query is not None else ""}
        }}{f" LIMIT {per_page} OFFSET {(page - 1) * per_page}" if page is not None and per_page is not None else ""}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")

async def get_uri(item_id: str = None, klass: URIRef = None):
    if item_id:
        r = await sparql_query(
            f"""PREFIX dcterms: <{DCTERMS}>
                PREFIX rdf: <{RDF}>
                PREFIX xsd: <{XSD}>
                SELECT ?item_uri ?class {{ ?item_uri dcterms:identifier "{item_id}"^^xsd:token ;
                                    rdf:type <{str(klass)}> . }}""",
            "SpacePrez",
        )
        if r[0]:
            return r[1][0]["item_uri"]["value"]


@lru_cache(maxsize=50)
def get_object_uri_and_classes(
    feature_id: str = None,
    collection_id: str = None,
    dataset_id: str = None,
    feature_uri: str = None,
    collection_uri: str = None,
    dataset_uri: str = None,
):
    if dataset_id:
        r = sparql_query_non_async(
            f"""PREFIX dcat: <{DCAT}>
                PREFIX dcterms: <{DCTERMS}>
                PREFIX geo: <{GEO}>
                PREFIX rdfs: <{RDFS}>
                PREFIX xsd: <{XSD}>

                SELECT ?f ?fc ?d ?class {{
                        OPTIONAL {{ ?d dcterms:identifier "{dataset_id}"^^xsd:token ;
                                a dcat:Dataset . }}
                        OPTIONAL {{ ?fc dcterms:identifier "{collection_id}"^^xsd:token ;
                                a geo:FeatureCollection .
                            ?d rdfs:member ?fc . }}
                        OPTIONAL {{ ?f dcterms:identifier "{feature_id}"^^xsd:token ;
                                a geo:Feature ;
                                a ?class .
                            ?fc rdfs:member ?f . }}
                            }} """,
            "SpacePrez",
        )
        if r[0]:
            f = r[1][0].get("f")
            fc = r[1][0].get("fc")
            d = r[1][0].get("d")
            classes = []
            if f:  # find feature classes
                classes = [c["class"]["value"] for c in r[1]]
            return (
                feature_id,
                collection_id,
                dataset_id,
                f["value"] if f else None,
                fc["value"] if fc else None,
                d["value"] if d else None,
                classes,
            )
    elif feature_uri or collection_uri or dataset_uri:
        r = sparql_query_non_async(
            f"""SELECT ?f ?fc ?d ?class
                {{
                    BIND(<{feature_uri}> AS ?f)
                    BIND(<{collection_uri}> AS ?fc)
                    BIND(<{dataset_uri}> AS ?d)
                    ?f a ?class ;
                        rdfs:member^ ?fc ;
                        dcterms:identifier ?f_id^^xsd:token .
                    ?fc a geo:FeatureCollection ;
                        rdfs:member^ ?d ;
                        dcterms:identifier ?fc_id^^xsd:token .
                    ?d a dcat:Dataset ;
                        dcterms:identifier ?d_id^^xsd:token .
                }}""",
            "SpacePrez",
        )
        if r[0]:
            return (
                r[1][0]["f_id"]["value"],
                r[1][0]["fc_id"]["value"],
                r[1][0]["d_id"]["value"],
                r[1][0]["f"]["value"],
                r[1][0]["fc"]["value"],
                r[1][0]["d"]["value"],
                [c["class"]["value"] for c in r[1]],
            )

    return None, None, None, None, None  # effectively 404 - can't find this thing


@lru_cache(maxsize=20)
def get_feature_construct(feature_uri: Optional[str]):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        PREFIX xsd: <{XSD}>

        CONSTRUCT {{
            ?f ?p1 ?o1 ;
                dcterms:title ?title .

            {construct_all_prop_obj_info}
            {construct_all_bnode_prop_obj_info}

            dcterms:title rdfs:label "Title" .

            ?coll a geo:FeatureCollection ;
                dcterms:identifier ?coll_id ;
                dcterms:title ?coll_label ;
                rdfs:member ?f .

            ?d a dcat:Dataset ;
                dcterms:identifier ?d_id ;
                dcterms:title ?d_label .
        }}
        WHERE {{
            BIND (<{feature_uri}> as ?f)
            ?f a geo:Feature ;
               ?p1 ?o1 .

            ?coll
                a geo:FeatureCollection ;
                dcterms:identifier ?coll_id ;
                dcterms:title ?coll_label ;
                rdfs:member ?f .

            ?d
                a dcat:Dataset ;
                dcterms:identifier ?d_id ;
                dcterms:title ?d_label ;
                rdfs:member ?coll .

            {get_all_bnode_prop_obj_info}
            {get_all_prop_obj_info}
            OPTIONAL {{
                ?f dcterms:title ?given_title .
            }}
            OPTIONAL {{
                ?f rdfs:label ?given_label .
            }}
            BIND(COALESCE(COALESCE(?given_label, ?given_title), CONCAT("Feature ", ?id)) AS ?title)
        }}
    """
    r = sparql_construct_non_async(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def cql_search(
    params: Dict, page: int, per_page: int, collection_id: Optional[str] = None
):
    limit = params.get("limit")
    offset = params.get("offset")
    bbox = params.get("bbox")

    # TODO convert bbox into polygon
    bbox_polygon = ""

    bbox_query = (
        f'FILTER(geo:sfIntersects(?geom, "POLYGON(({bbox_polygon}))"^^geo:wktLiteral) )'
    )

    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX skos: <{SKOS}>
        PREFIX xsd: <{XSD}>
        SELECT DISTINCT *
        WHERE {{
            {bbox_query if bbox is not None else ""}
        }} LIMIT {per_page} OFFSET {(page - 1) * per_page}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")


async def get_collection_info_queryables(
    dataset_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    collection_uri: Optional[str] = None,
):
    if collection_id is None and collection_uri is None:
        raise ValueError("Either an ID or a URI must be provided for a SPARQL query")

    # when querying by ID via regular URL path
    query_by_id = f"""
        ?d a dcat:Dataset ;
            rdfs:member ?fc ;
            dcterms:identifier ?d_id .
        FILTER (STR(?d_id) = "{dataset_id}" && DATATYPE(?d_id) = xsd:token)
        ?coll a geo:FeatureCollection ;
            dcterms:identifier ?id .
        FILTER (STR(?id) = "{collection_id}" && DATATYPE(?id) = xsd:token)
    """
    # when querying by URI via /object?uri=...
    query_by_uri = f"""
        BIND (<{collection_uri}> as ?coll)
        ?coll a geo:FeatureCollection .
    """

    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX rdfs: <{RDFS}>
        PREFIX xsd: <{XSD}>
        SELECT ?title ?desc
        WHERE {{
            {query_by_id if collection_id is not None else query_by_uri}
            ?coll dcterms:title ?title .
            OPTIONAL {{
                ?coll dcterms:description ?desc .
            }}
            FILTER(lang(?title) = "" || lang(?title) = "en")
        }}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")

async def get_dataset_info_queryables(
    dataset_id: Optional[str] = None,
    dataset_uri: Optional[str] = None,
):
    if dataset_id is None and dataset_uri is None:
        raise ValueError("Either an ID or a URI must be provided for a SPARQL query")

    # when querying by ID via regular URL path
    query_by_id = f"""
        ?d a dcat:Dataset ;
            dcterms:identifier ?d_id .
        FILTER (STR(?d_id) = "{dataset_id}" && DATATYPE(?d_id) = xsd:token)
    """
    # when querying by URI via /object?uri=...
    query_by_uri = f"""
        BIND (<{dataset_uri}> as ?d)
        ?d a dcat:Dataset .
    """

    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX rdfs: <{RDFS}>
        PREFIX xsd: <{XSD}>
        SELECT ?title ?desc
        WHERE {{
            {query_by_id if dataset_id is not None else query_by_uri}
            ?d dcterms:title ?title .
            OPTIONAL {{
                ?d dcterms:description ?desc .
            }}
            FILTER(lang(?title) = "" || lang(?title) = "en")
        }}
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")

async def get_dataset_label(
    dataset_id: str
):
    q = f"""
        PREFIX dcat: <{DCAT}>
        PREFIX dcterms: <{DCTERMS}>
        PREFIX xsd: <{XSD}>
        SELECT ?title
        WHERE {{
            ?d a dcat:Dataset ;
                dcterms:title ?title ;
                dcterms:identifier ?d_id .
            FILTER (STR(?d_id) = "{dataset_id}" && DATATYPE(?d_id) = xsd:token)
            FILTER(lang(?title) = "" || lang(?title) = "en")
        }} LIMIT 1
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")

async def get_collection_label(
    collection_id: str
):
    q = f"""
        PREFIX dcterms: <{DCTERMS}>
        PREFIX geo: <{GEO}>
        PREFIX xsd: <{XSD}>
        SELECT ?title
        WHERE {{
            ?coll a geo:FeatureCollection ;
                dcterms:title ?title ;
                dcterms:identifier ?coll_id .
            FILTER (STR(?coll_id) = "{collection_id}" && DATATYPE(?coll_id) = xsd:token)
            FILTER(lang(?title) = "" || lang(?title) = "en")
        }} LIMIT 1
    """
    r = await sparql_query(q, "SpacePrez")
    if r[0]:
        return r[1]
    else:
        raise Exception(f"SPARQL query error code {r[1]['code']}: {r[1]['message']}")