# coding: utf-8

"""Python file for queriying the MINERVA platform (https://minerva.pages.uni.lu/doc/)."""

from typing import Tuple

import pandas as pd
import requests

from pyBiodatafuse.utils import collapse_data_sources, get_identifier_of_interest

# URL of MINERVA's API endpoint
base_url = "https://covid19map.elixir-luxembourg.org/minerva/api/"


def get_version_minerva() -> dict:
    """Get version of minerva API.

    :returns: a string containing the version information
    """
    response = requests.get(base_url + "/configuration/")
    conf_dict = response.json()

    return conf_dict["version"]


def get_minerva_components(get_elements=True, get_reactions=True) -> pd.DataFrame:
    """Get information about MINERVA componenets.

    :param get_elements: XXXX
    :param get_reactions: XXXX

    :returns: a DataFrame containing XXXX.
    """
    # Login
    # session = requests.Session()
    # INPUT YOUR CREDENTIALS TO LOGIN to PD map instance
    # login = "anonymous"
    # password = ""
    # login_request = session.post(base_url + "/doLogin", data={"login": login, "password": password})
    # print(login_request.text, "\n")
    # print(session.cookies.get_dict(), "\n")

    # Request configuration data
    response = requests.get(base_url + "/configuration/")
    conf_dict = response.json()

    # Extract project ID
    project_id = [
        option["value"]
        for option in conf_dict.get("options", [])
        if option.get("type") == "DEFAULT_MAP"
    ]
    project_txt = ", ".join(project_id)

    # Request project data using the extracted project ID
    response = requests.get(base_url + "/projects/" + project_txt + "/models/")
    models = response.json()
    map_components = {"models": models}

    if get_elements:
        # Get elements of the chosen diagram
        model_elements = {}
        for model in models:
            model = str(model["idObject"])
            url = (
                base_url
                + "/projects/"
                + project_txt
                + "/models/"
                + model
                + "/"
                + "bioEntities/elements/"
            )
            response_data = requests.get(url)
            model_elements[model] = response_data.json()
        map_components["map_elements"] = model_elements

    if get_reactions:
        # Get reactions of the chosen diagram
        model_reactions = {}
        for model in models:
            model = str(model["idObject"])
            url = (
                base_url
                + "/projects/"
                + project_txt
                + "/models/"
                + model
                + "/"
                + "bioEntities/reactions/"
            )
            response_data = requests.get(url)
            model_reactions[model] = response_data.json()
        map_components["map_reactions"] = model_reactions

    return map_components


def get_gene_minerva_pathways(
    bridgedb_df: pd.DataFrame,
    map_components: pd.DataFrame,
    input_type: str = "Protein",
) -> Tuple[pd.DataFrame, dict]:
    """Get information about MINERVA pathways associated with a gene.

    :param bridgedb_df: BridgeDb output for creating the list of gene ids to query
    :param map_components: XXXX
    :param input_type: XXXX

    :returns: a DataFrame containing XXXX.
    """
    # In the type parameter you can select which kind of informationyou want to get from:
    # {'Compartment','Complex', 'Drug', 'Gene', 'Ion','Phenotype','Protein','RNA','Simple molecule'}
    map_elements = map_components.get("map_elements", {})
    models = map_components.get("models", {})

    data_df = get_identifier_of_interest(bridgedb_df, "NCBI Gene")

    names = []
    for value in models:
        name = value["name"]
        names.append(name)

    row = 1
    combined_df = pd.DataFrame()
    for x in names:
        index_to_extract = row
        row = 1 + row

        list_at_index = list(map_elements.values())[index_to_extract - 1]
        common_keys = ["type", "references", "symbol", "name"]
        # Initialize empty lists to store values for each common key
        type = []
        refs = []
        symbol = []
        name = []

        # Iterate through the list of dicts
        for d in list_at_index:
            for key in common_keys:
                if key in d:
                    if key == "type":
                        type.append(d[key])
                    elif key == "references":
                        refs.append(d[key])
                    elif key == "symbol":
                        symbol.append(d[key])
                    elif key == "name":
                        name.append(d[key])

        data = pd.DataFrame()
        data["symbol"] = symbol
        data["pathwayLabel"] = x
        data["pathwayGeneCount"] = len(symbol) - symbol.count(None)
        data["pathwayId"] = models[index_to_extract - 1]["idObject"]
        data["refs"] = refs
        data["type"] = type

        combined_df = pd.concat([combined_df, data], ignore_index=True)
        combined_df = combined_df[combined_df["type"] == input_type]

    if "symbol" not in combined_df:
        return pd.DataFrame()
    else:
        # Add Minverva output as a new column to BridgeDb file
        combined_df.rename(columns={"symbol": "identifier"}, inplace=True)
        combined_df["identifier"] = combined_df["identifier"].values.astype(str)

        selected_columns = ["pathwayId", "pathwayLabel", "pathwayGeneCount"]

        # Merge the two DataFrames based on 'geneid', 'gene_symbol', 'identifier', and 'target'
        merged_df = collapse_data_sources(
            data_df=data_df,
            source_namespace="NCBI Gene",
            target_df=combined_df,
            common_cols=["identifier"],
            target_specific_cols=selected_columns,
            col_name="Minerva",
        )

        # Remove duplicates
        minerva_colum = dict(merged_df.Minerva)
        new_minerva_colum = []
        for key in minerva_colum:
            current_list = minerva_colum[key]

            one_gene = []
            for item in current_list:
                item = str(item)
                one_gene.append(item)
            unique_list = list(set(one_gene))
            new_minerva_colum.append(unique_list)

        merged_df["Minverva"] = new_minerva_colum
    return merged_df