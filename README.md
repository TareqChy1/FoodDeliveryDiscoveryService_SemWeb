# Semantic Web Project: Food Delivery Discovery Service

This Semantic Web project is a comprehensive and practical exercise in developing a food delivery discovery service that adheres to the principles of the Semantic Web, particularly focusing on Linked Data. Here's a breakdown of the key components and steps need to follow:

## Main Objectives
The primary goal of the Semantic Web project is to create a dynamic food delivery discovery service using Semantic Web technologies. This service will use standardized data representations to recommend food ordering options based on user preferences like location, time, and price range. The project involves integrating various data sources, developing a command-line application, and employing technologies like RDF, SPARQL, and SHACL.

The technical requirements for the project include setting up a triplestore(Apache Jena Fuseki) for data storage, developing programs to collect and query data from CoopCycle, utilizing SPARQL for data querying, implementing SHACL for data validation, and creating a command-line interface for user interactions. The application must also dynamically incorporate new businesses and user preferences.

## Required Tools 

- **Apache Jena Fuseki**: RDF data storage and SPARQL querying.
- **RDF Libraries**: Handling RDF data serialization/deserialization.
- **SHACL Processor**: RDF data validation.
- **HTML and JSON-LD Processors**: Extracting data from web pages and handling JSON-LD.
- **Linked Data Platform Server**: 
  - *Community Solid Server*: Managing user preferences.
    - Access it at: [Community Solid Server Workspace](http://193.49.165.77:3000/semweb/chy-workspace/)
- **Programming Environment**: Python.
- **Development Tools**: VSCode IDE.


## Development Steps

1. **Setup Triplestore**
   - **Tool**: Apache Jena Fuseki
   - **Dataset Name**: `dataset_det`

2. **Data Collection Program: `collect.py`**
   - Collects information about local businesses from CoopCycle.
   - Prevents data duplication in the triplestore.

3. **Basic Query Program: `query1.py`**
   - Finds restaurants open at specific dates/times using SPARQL.
   - Command-line interface only.

4. **Location-Based Query: `query2.py`**
   - Adds location-based search functionality to `query1.py`.

5. **Price-Based Query: `query3.py`**
   - Adds price-based search into `query2.py`.

6. **Ranking Feature: `query4.py`**
   - Enables ranking of restaurants by distance or price into `query3.py`.

7. **User Preference Query: `query5.py`**
   - Modified `query4.py` to Fetche and Integrate user preferences from RDF URIs.
   - Supports partial match queries.

8. **Diverse Preferences Query: `query6.py`**
   - Modified `query5.py` to Test with different sets of user preferences from the **Linked Data Platform Server** [Community Solid Server Workspace](http://193.49.165.77:3000/semweb/chy-workspace/pref-chy.ttl)

9. **Enhanced Data Collection: `collectShapeValidation.py`**
   - Modified `collect.py` to validate RDF data using SHACL `shape.ttl` before storage and to collect data from any CoopCycle member.

10. **Preference Setting Program: `describe.py`**
    - Assists users in setting preferences via Q&A.
    - Publishes preferences as RDF on the Linked Data Platform.

### *Note: **`main.py`** acts as a central command center, allows to run any of the listed scripts with ease. User can simply choose the desired script number from the menu.*


## Running the Project

To execute the python scripts in this project, follow these steps:

1. **Start the Central Command Script**:
   - Run `main.py` by executing below command in command line

        ```
            python main.py
        ```
   - This script serves as a central hub to run all other scripts.

2. **Select the Desired Operation**:
   - Upon running `main.py`, a menu will be displayed.
   - Choose the script you want to run by entering its corresponding number.

### List of Scripts:
- `1`: Collect information from CoopCycle (`collect.py`)
- `2`: Query restaurants open at a specific date and time (`query1.py`)
- `3`: Query restaurants by location and opening times (`query2.py`)
- `4`: Query restaurants by delivery price (`query3.py`)
- `5`: Rank restaurants by distance or price (`query4.py`)
- `6`: Query restaurants with preferences from RDF URI (`query5.py`)
- `7`: Query with different sets of preferences on LDP (`query6.py`)
- `8`: Collect data with SHACL shape validation (`collectShapeValidation.py`)
- `9`: Set user preferences and publish on LDP (`describe.py`)

3. **Follow Script-Specific Prompts**:
   - Each script may have its own set of instructions or prompts.
   - Follow these as they appear in command line.

4. **Repeat or Exit**:
   - After a script completes, choose to run another script or exit the program.




