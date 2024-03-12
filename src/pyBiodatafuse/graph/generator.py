# coding: utf-8

"""Python module to construct a NetworkX graph from the annotated data frame."""

import json
import pickle

import networkx as nx
import pandas as pd


def load_dataframe_from_pickle(pickle_path: str) -> pd.DataFrame:
    """Load a previously annotated dataframe from a pickle file.

    :param pickle_path: the path to a previously obtained annotation dataframe dumped as a pickle file.
    :returns: a Pandas dataframe.
    """
    with open(pickle_path, "rb") as rin:
        df = pickle.load(rin)

    return df


def add_disgenet_disease_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for dg in annot_list:
        if not pd.isna(dg["disease_name"]):
            dg_node_label = dg["disease_name"]
            dg_node_attrs = {
                "source": "DisGeNET",
                "name": dg["disease_name"],
                "id": dg["diseaseid"],
                "labels": "Disease",
                "disease_id": dg["diseaseid"],
                "disease_class": dg["disease_class"],
                "disease_class_name": dg["disease_class_name"],
                "disease_type": dg["disease_type"],
                "disease_semantic_type": dg["disease_semantic_type"],
            }

            g.add_node(dg_node_label, attr_dict=dg_node_attrs)

            edge_attrs = {
                "source": "DisGeNET",
                "label": "associated_with",
                "score": dg["score"],
                "year_initial": dg["year_initial"] if not pd.isna(dg["year_initial"]) else "",
                "year_final": dg["year_final"] if not pd.isna(dg["year_final"]) else "",
                "ei": dg["ei"] if not pd.isna(dg["ei"]) else "",
                "el": dg["el"] if not pd.isna(dg["el"]) else "",
            }

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, dg_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, dg_node_label,  label="associated_with", attr_dict=edge_attrs)

    return g


def add_opentargets_location_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for loc in annot_list:
        if not pd.isna(loc["location"]) and not pd.isna(loc["subcellular_loc"]):
            loc_node_label = loc["location"]
            loc_node_attrs = {
                "source": "OpenTargets",
                "name": loc["location"],
                "id": loc["loc_identifier"],
                "labels": "Location",
                "subcellular_loc": loc["subcellular_loc"],
            }

            g.add_node(loc_node_label, attr_dict=loc_node_attrs)

            edge_attrs = {"source": "OpenTargets", "label": "localized_in"}

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, loc_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, loc_node_label,label="localized_in", attr_dict=edge_attrs)

    return g


def add_opentargets_go_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for go in annot_list:
        go_node_label = go["go_name"]
        go_node_attrs = {
            "source": "OpenTargets",
            "name": go["go_name"],
            "id": go["go_id"],
            "labels": "GO",
        }

        g.add_node(go_node_label, attr_dict=go_node_attrs)

        edge_attrs = {"source": "OpenTargets", "label": "part_of_go"}

        edge_hash = hash(frozenset(edge_attrs.items()))
        edge_attrs["edge_hash"] = edge_hash
        edge_data = g.get_edge_data(gene_node_label, go_node_label)
        edge_data = {} if edge_data is None else edge_data
        node_exists = [x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash]

        if len(node_exists) == 0:
            g.add_edge(gene_node_label, go_node_label, label="part_of_go",attr_dict=edge_attrs)

    return g


def add_opentargets_pathway_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for pathway in annot_list:
        if not pd.isna(pathway["pathway_id"]):
            pathway_node_label = pathway["pathway_name"]
            pathway_node_attrs = {
                "source": "OpenTargets",
                "name": pathway["pathway_name"],
                "id": pathway["pathway_id"],
                "labels": "Pathway",
            }

            g.add_node(pathway_node_label, attr_dict=pathway_node_attrs)

            edge_attrs = {"source": "OpenTargets", "label": "part_of_pathway"}

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, pathway_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, pathway_node_label, label="part_of_pathway",attr_dict=edge_attrs)

    return g


def add_opentargets_drug_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for drug in annot_list:
        if not pd.isna(drug["relation"]):
            drug_node_label = drug["drug_name"]
            drug_node_attrs = {
                "source": "OpenTargets",
                "name": drug["drug_name"],
                "id": drug["chembl_id"],
                "labels": "Compound",
                "is_a_drug": "True",
            }

            g.add_node(drug_node_label, attr_dict=drug_node_attrs)

            edge_attrs = {"source": "OpenTargets", "label": drug["relation"]}

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(drug_node_label, gene_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(drug_node_label, gene_node_label, label=drug["relation"],attr_dict=edge_attrs)

    return g


def add_opentargets_disease_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for dg in annot_list:
        if not pd.isna(dg["disease_name"]):
            dg_node_label = dg["disease_name"]
            dg_node_attrs = {
                "source": "OpenTargets",
                "name": dg["disease_name"],
                "id": dg["disease_id"],
                "labels": "Disease",
                "therapeutic_areas": dg["therapeutic_areas"],
            }

            g.add_node(dg_node_label, attr_dict=dg_node_attrs)

            edge_attrs = {"source": "OpenTargets", "label": "associated_with"}

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, dg_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, dg_node_label,label="associated_with", attr_dict=edge_attrs)

    return g


def add_wikipathways_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for pathway in annot_list:
        if not pd.isna(pathway["pathwayLabel"]):
            pathway_node_label = pathway["pathwayLabel"]
            pathway_node_attrs = {
                "source": "WikiPathways",
                "name": pathway["pathwayLabel"],
                "id": pathway["pathwayId"],
                "labels": "Pathway",
                "gene_count": pathway["pathwayGeneCount"],
            }

            g.add_node(pathway_node_label, attr_dict=pathway_node_attrs)

            edge_attrs = {"source": "WikiPathways", "label": "part_of_pathway"}

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, pathway_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, pathway_node_label, label="part_of_pathway",attr_dict=edge_attrs)

    return g


def add_ppi_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for ppi in annot_list:
        edge_attrs = {"source": "STRING", "label": "interacts_with", "score": ppi["score"]}

        edge_hash = hash(frozenset(edge_attrs.items()))
        edge_attrs["edge_hash"] = edge_hash
        edge_data = g.get_edge_data(gene_node_label, ppi["stringdb_link_to"])
        edge_data = {} if edge_data is None else edge_data
        node_exists = [x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash]

        if len(node_exists) == 0:
            g.add_edge(gene_node_label, ppi["stringdb_link_to"],label= "interacts_with",attr_dict=edge_attrs)

    return g


def add_molmedb_gene_inhibitor(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for inhibitor in annot_list:
        if not pd.isna(inhibitor["InChIKey"]):
            inhibitor_node_label = inhibitor["label"]
            inhibitor_node_attrs = {
                "source": "MolMeDB",
                "id": inhibitor["molmedb_id"],
                "name": inhibitor["label"],
                "InChIKey": inhibitor["InChIKey"],
                "MolMeDB_id": inhibitor["molmedb_id"],
                "labels": "Compound",
            }

            if not pd.isna(inhibitor["SMILES"]):
                inhibitor_node_attrs["SMILES"] = inhibitor["SMILES"]
            if not pd.isna(inhibitor["pubchem_compound_id"]):
                inhibitor_node_attrs["PubChem_compound_id"] = inhibitor["pubchem_compound_id"]
            if not pd.isna(inhibitor["chebi_id"]):
                inhibitor_node_attrs["ChEBI_id"] = inhibitor["chebi_id"]
            if not pd.isna(inhibitor["drugbank_id"]):
                inhibitor_node_attrs["DrugBank_id"] = inhibitor["drugbank_id"]

            g.add_node(inhibitor_node_label, attr_dict=inhibitor_node_attrs)

            edge_attrs = {
                "source": "MolMeDB",
                "label": "inhibits",
            }

            if not pd.isna(inhibitor["source_doi"]):
                inhibitor_node_attrs["reference_doi"] = inhibitor["source_doi"]
            if not pd.isna(inhibitor["source_pmid"]):
                inhibitor_node_attrs["reference_pmid"] = inhibitor["source_pmid"]

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, inhibitor_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, inhibitor_node_label, label="inhibits",attr_dict=edge_attrs)

    return g


def add_bgee_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for annot in annot_list:
        if not pd.isna(annot["anatomical_entity_name"]):
            annot_node_label = annot["anatomical_entity_name"]
            annot_node_attrs = {
                "source": "Bgee",
                "name": annot["anatomical_entity_name"],
                "id": annot["anatomical_entity_id"],
                "labels": "Anatomical Entity",
                "anatomical_entity_id": annot["anatomical_entity_id"],
                "anatomical_entity_name": annot["anatomical_entity_name"],
            }

            if not pd.isna(annot["developmental_stage_id"]):
                annot_node_attrs["developmental_stage_id"] = annot["developmental_stage_id"]
            if not pd.isna(annot["developmental_stage_name"]):
                annot_node_attrs["developmental_stage_name"] = annot["developmental_stage_name"]
            if not pd.isna(annot["expression_level"]):
                annot_node_attrs["expression_level"] = annot["expression_level"]
            if not pd.isna(annot["confidence_level"]):
                annot_node_attrs["confidence_level"] = annot["drugbank_id"]

            g.add_node(annot_node_label, attr_dict=annot_node_attrs)

            edge_attrs = {
                "source": "Bgee",
                "label": "expressed_in",
            }

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, annot_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, annot_node_label,label="expressed_in" ,attr_dict=edge_attrs)

    return g

def add_minerva_subgraph(g, gene_node_label, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for pathway in annot_list:
        if not pd.isna(pathway["pathwayLabel"]):
            pathway_node_label = pathway["pathwayLabel"]
            pathway_node_attrs = {
                "source": "MINERVA",
                "name": pathway["pathwayLabel"],
                "id": pathway["pathwayId"],
                "labels": "pathway",
                "gene_count": pathway["pathwayGeneCount"],
            }

            g.add_node(pathway_node_label, attr_dict=pathway_node_attrs)

            edge_attrs = {"source": "MINERVA", "type": "part_of_pathway"}

            edge_hash = hash(frozenset(edge_attrs.items()))
            edge_attrs["edge_hash"] = edge_hash
            edge_data = g.get_edge_data(gene_node_label, pathway_node_label)
            edge_data = {} if edge_data is None else edge_data
            node_exists = [
                x for x, y in edge_data.items() if y["attr_dict"]["edge_hash"] == edge_hash
            ]

            if len(node_exists) == 0:
                g.add_edge(gene_node_label, pathway_node_label, label="part_of_pathway",attr_dict=edge_attrs)

    return g

def add_drug_disease_subgraph(g, gene_node_label_2, annot_list):
    """Construct part of the graph by linking the gene to a list of annotation entities (disease, drug ..etc).

    :param g: the input graph to extend with new nodes and edges.
    :param gene_node_label: the gene node to be linked to annotation entities.
    :param annot_list: list of annotations from a specific source (e.g. DisGeNET, WikiPathways ..etc).
    :returns: a NetworkX MultiDiGraph
    """
    for ddi in annot_list:
        edge_attrs = {"source": "OpenTargets", "type": "treated_with"}

        edge_hash = hash(frozenset(edge_attrs.items()))
        edge_attrs["edge_hash"] = edge_hash
        
        new_edge = (ddi["umls"],gene_node_label_2)

        # Check if the edge already exists
        if not g.has_edge(*new_edge):
            # Add the edge to the graph
            g.add_edge(ddi["umls"],gene_node_label_2 ,label='treated_with', attr_dict=edge_attrs)
       

    return g

def generate_networkx_graph(fuse_df: pd.DataFrame,drug_disease=None):
    """Construct a NetWorkX graph from a Pandas DataFrame of genes and their multi-source annotations.

    :param fuse_df: the input dataframe to be converted into a graph.
    :param drug_disease: the input dataframe containing drug_disease relationships
    :returns: a NetworkX MultiDiGraph
    """
    g = nx.MultiDiGraph()

    dea_columns = [c for c in fuse_df.columns if c.endswith("_dea")]

    func_dict = {
        "DisGeNET": add_disgenet_disease_subgraph,
        "OpenTargets_Location": add_opentargets_location_subgraph,
        "GO_Process": add_opentargets_go_subgraph,
        "Reactome_Pathways": add_opentargets_pathway_subgraph,
        "ChEMBL_Drugs": add_opentargets_drug_subgraph,
        "OpenTargets_Diseases": add_opentargets_disease_subgraph,
        "WikiPathways": add_wikipathways_subgraph,
        "MINERVA":add_minerva_subgraph,
        "transporter_inhibitor": add_molmedb_gene_inhibitor,
        "Bgee": add_bgee_subgraph,
    }

    for _i, row in fuse_df.iterrows():
        gene_node_label = row["identifier"]
        gene_node_attrs = {
            "source": "BridgeDB",
            "labels": row["identifier"],
            "id": row["target"],
            "node_type": "Gene",
            row["target.source"]: row["target"],
        }

        for c in dea_columns:
            gene_node_attrs[c[:-4]] = row[c]

        g.add_node(gene_node_label, attr_dict=gene_node_attrs)

        for annot_key in func_dict:
            if annot_key in row:
                annot_list = json.loads(json.dumps(row[annot_key]))

                if not isinstance(annot_list, list):
                    annot_list = []

                func_dict[annot_key](g, gene_node_label, annot_list)

    if "stringdb" in row:
        for _i, row in fuse_df.iterrows():
            ppi_list = json.loads(json.dumps(row["stringdb"]))

            if ppi_list is None:
                ppi_list = []

            add_ppi_subgraph(g, gene_node_label, ppi_list)
            
    if drug_disease is not None:
        fuse_df= pd.concat([fuse_df, drug_disease[['identifier','drug_diseases']]], ignore_index=True)
        if "drug_diseases" in row:
            for _i, row in fuse_df.iterrows():
                gene_node_label_2= row['identifier']
                ddi_list = json.loads(json.dumps(row["drug_diseases"]))

                if type(ddi_list) == float :
                    ddi_list = []

                add_drug_disease_subgraph(g, gene_node_label_2, ddi_list)
        
    for node in g.nodes():
        for k, v in g.nodes[node]["attr_dict"].items():
            if v is not None:
                g.nodes[node][k] = v

        del g.nodes[node]["attr_dict"]

    for u, v, k in g.edges(keys=True):
        if "attr_dict" in g[u][v][k]:
            for x, y in g[u][v][k]["attr_dict"].items():
                if y is not None and x != "edge_hash":
                    g[u][v][k][x] = y

            del g[u][v][k]["attr_dict"]

    return g
