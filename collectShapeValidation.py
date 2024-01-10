# pip install pyshacl
# pip install rdflib requests beautifulsoup4 pyshacl
# completed 9 number points for the projects. 

import json
import requests
from bs4 import BeautifulSoup
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from pyshacl import validate
import sys

# Define namespaces
SCHEMA = Namespace("https://schema.org/")

def format_time(time_str):
    placeholder_date = '1970-01-01'
    return f"{placeholder_date}T{time_str}:00"

def format_float(value):
    return f"{value:.4f}"

def check_existing_data(store, uri):
    ask_query = f"ASK {{ <{uri}> ?p ?o }}"
    result = store.query(ask_query)

    # Check if the result is not None and then get the 'ASK' value
    if result is not None:
        return list(result)[0]
    else:
        # If the result is None, it means the query didn't execute correctly
        print(f"Error executing ASK query for URI: {uri}")
        return False


def validate_graph(graph, shapes_file):
    with open(shapes_file, 'r') as f:
        shapes_graph = Graph().parse(data=f.read(), format='turtle')
    conforms, results_graph, results_text = validate(graph, shacl_graph=shapes_graph)
    return conforms, results_text


# Accept URI as an input from the user
member_uri = input("Enter the CoopCycle Member URI (Example: https://beefast.coopcycle.org): ")


# Create RDF graph
g = Graph()
g.bind("schema", SCHEMA)

# Connect to the Fuseki store
fuseki_store = SPARQLUpdateStore()
fuseki_store.open(('http://localhost:3030/dataset_det/query', 'http://localhost:3030/dataset_det/update'))

# Process the provided URI
print(f"Processing URL: {member_uri}")
try:
    # Scrape the webpage
    page = requests.get(member_uri)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find restaurant items
    restaurant_items = soup.select('div.restaurant-item>a[href]')
    restaurant_urls = {member_uri + item['href'] for item in restaurant_items}

    for restaurant_url in restaurant_urls:
        restaurant_uri = URIRef(restaurant_url)

        # Check if the restaurant data already exists in the store
        if check_existing_data(fuseki_store, restaurant_uri):
            print(f"Data for {restaurant_uri} already exists in the store. Skipping...")
            continue

        restaurant_page = requests.get(restaurant_url)
        restaurant_soup = BeautifulSoup(restaurant_page.content, 'html.parser')

        # Extract JSON-LD data
        json_ld_data = restaurant_soup.find('script', {'type': 'application/ld+json'})
        if json_ld_data:
            restaurant_data = json.loads(json_ld_data.string)

            # Create resources for restaurant
            g.add((restaurant_uri, RDF.type, SCHEMA.ProfessionalService))
            g.add((restaurant_uri, SCHEMA.name, Literal(restaurant_data.get('name'))))

            # Extract and add telephone information from address
            telephone = restaurant_data.get('address', {}).get('telephone', "None")
            g.add((restaurant_uri, SCHEMA.telephone, Literal(telephone)))

            # Add location data
            location_uri = URIRef(restaurant_url + "#location")
            g.add((restaurant_uri, SCHEMA.location, location_uri))
            g.add((location_uri, RDF.type, SCHEMA.Place))

            address_uri = URIRef(restaurant_url + "#address")
            g.add((location_uri, SCHEMA.address, address_uri))
            g.add((address_uri, RDF.type, SCHEMA.PostalAddress))
            # Extract country and city from restaurant_data
            # Assuming restaurant_data contains an 'address' field with 'addressCountry' and 'addressLocality'
            country = restaurant_data.get('address', {}).get('addressCountry', 'UNKNOWN').upper()
            city = restaurant_data.get('address', {}).get('addressLocality', 'unknown')

            g.add((address_uri, SCHEMA.addressCountry, Literal(country)))
            g.add((address_uri, SCHEMA.addressLocality, Literal(city)))

            # Add geographical coordinates with formatted precision
            geo = restaurant_data.get('address', {}).get('geo', {})
            latitude = format_float(float(geo.get('latitude')))
            longitude = format_float(float(geo.get('longitude')))
            g.add((location_uri, SCHEMA.latitude, Literal(latitude, datatype=XSD.decimal)))
            g.add((location_uri, SCHEMA.longitude, Literal(longitude, datatype=XSD.decimal)))

            # Add opening hours
            opening_hours = restaurant_data.get('openingHoursSpecification', [])
            for oh in opening_hours:
                oh_uri = URIRef(restaurant_url + "#openingHoursSpecification")
                g.add((restaurant_uri, SCHEMA.openingHoursSpecification, oh_uri))
                g.add((oh_uri, RDF.type, SCHEMA.OpeningHoursSpecification))
                g.add((oh_uri, SCHEMA.dayOfWeek, Literal(str(oh.get('dayOfWeek')))))

                # Format the opening and closing times
                opens = format_time(oh.get('opens'))
                closes = format_time(oh.get('closes'))
                g.add((oh_uri, SCHEMA.opens, Literal(opens, datatype=XSD.dateTime)))
                g.add((oh_uri, SCHEMA.closes, Literal(closes, datatype=XSD.dateTime)))
                
            # Extract price specifications
            price_spec = restaurant_data.get('potentialAction', {}).get('priceSpecification', {})
            price_spec_uri = URIRef(restaurant_url + "#priceSpecification")
            g.add((restaurant_uri, SCHEMA.priceSpecification, price_spec_uri))
            g.add((price_spec_uri, RDF.type, SCHEMA.PriceSpecification))

            # Add delivery charge specification
            delivery_charge_price = format_float(float(price_spec.get('price', 0.0)))
            delivery_currency = price_spec.get('priceCurrency', 'EUR')
            g.add((price_spec_uri, SCHEMA.deliveryChargePrice, Literal(delivery_charge_price, datatype=XSD.decimal)))
            g.add((price_spec_uri, SCHEMA.priceCurrency, Literal(delivery_currency)))

            # Add eligible transaction volume specification
            eligible_volume_price = format_float(float(price_spec.get('eligibleTransactionVolume', {}).get('price', 0.0)))
            eligible_volume_currency = price_spec.get('eligibleTransactionVolume', {}).get('priceCurrency', 'EUR')
            g.add((price_spec_uri, SCHEMA.eligibleTransactionVolume, Literal(eligible_volume_price, datatype=XSD.decimal)))
            g.add((price_spec_uri, SCHEMA.priceCurrency, Literal(eligible_volume_currency)))

            print(f"Restaurant data {restaurant_uri} added to graph")

except requests.exceptions.RequestException as e:
    print(f"Error scraping {member_uri}: {e}")

# Validate the graph against SHACL shapes
shapes_file = 'C:\\Users\\nushr\\Desktop\\Semantic_Web\\Project\\shape.ttl'
conforms, validation_report = validate_graph(g, shapes_file)
if not conforms:
    print("Graph does not conform to SHACL shapes. Errors:")
    print(validation_report)
    sys.exit(1)

print("Graph conforms to SHACL shapes. SHACL validation successful.")
print("Proceeding with serialization...")

# Serialize the graph in Turtle format
output_path = 'C:\\Users\\nushr\\Desktop\\Semantic_Web\\Project\\output_new_data.ttl'
g.serialize(destination=output_path, format='turtle')
print(f"Data written to {output_path}")

# Insert each triple in the graph into the store
for triple in g:
    fuseki_store.add(triple)

# Close the store connection
fuseki_store.close()

print("Data added to Fuseki store.")
