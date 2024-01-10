# completed 10 number points for the projects. 
# pip install rdflib requests
import rdflib
from rdflib.namespace import RDF, Namespace
import requests

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid integer.")

# Collect user preferences
username = input("May I have your username, please? (Example: Tareq) ")
name = input("Could you please enter your name? (Example: Tareq CHY) ")

# Changing the question format for the day
print("What's your preferred day for ordering? (Example: Monday, Tuesday, etc.)")
user_day_of_week = input().capitalize()  # This will ensure the first letter is capitalized

time = input("When would you like to make your order (hh:mm)? (Example: 11:45) ")
print("What is your Location? ")
latitude = get_float_input("latitude? (Example: 47.30) ")
longitude = get_float_input("longitude? (Example: 2.34) ")
radius = get_int_input("What's the furthest distance you'd consider for delivery in meters? (Example: 10) ")
max_price = get_int_input("What is the maximum amount you'd prefer to spend on this in EUR? (Example: 18) ")

# Create RDF graph
schema = Namespace("http://schema.org/")
g = rdflib.Graph()

# Explicitly bind the 'schema' prefix to the namespace
g.bind("schema", schema)

person_uri = rdflib.URIRef(f"#customer{username}")

# Add triples
g.add((person_uri, RDF.type, schema.Person))
g.add((person_uri, schema.name, rdflib.Literal(name)))
seeks_node = rdflib.BNode()
g.add((person_uri, schema.seeks, seeks_node))

# Add seeks details
g.add((seeks_node, schema.availabilityStarts, rdflib.Literal(time, datatype=schema.DateTime)))
g.add((seeks_node, schema.dayOfWeek, rdflib.Literal(user_day_of_week)))
geo_circle_node = rdflib.BNode()
g.add((seeks_node, schema.availableAtOrFrom, geo_circle_node))
g.add((geo_circle_node, RDF.type, schema.GeoCircle))
geo_midpoint_node = rdflib.BNode()
g.add((geo_circle_node, schema.geoMidpoint, geo_midpoint_node))

# Format latitude and longitude as strings to avoid scientific notation
g.add((geo_midpoint_node, schema.latitude, rdflib.Literal(f"{latitude:.1f}")))  # Use format to limit decimal places
g.add((geo_midpoint_node, schema.longitude, rdflib.Literal(f"{longitude:.1f}")))

g.add((geo_circle_node, schema.geoRadius, rdflib.Literal(radius)))
price_spec_node = rdflib.BNode()
g.add((seeks_node, schema.priceSpecification, price_spec_node))
g.add((price_spec_node, RDF.type, schema.PriceSpecification))
g.add((price_spec_node, schema.maxPrice, rdflib.Literal(max_price)))
g.add((price_spec_node, schema.priceCurrency, rdflib.Literal("EUR")))

# Serialize graph to Turtle format
ttl_data = g.serialize(format="turtle")

# Save to a file in text mode
file_name = "user_preferences.ttl"
with open(file_name, "w") as file:
    file.write(ttl_data)

# Post the file to Linked Data Platform
url = "http://193.49.165.77:3000/semweb/chy-workspace/"
headers = {"Content-Type": "text/turtle", "Slug": f"{username}.ttl"}
with open(file_name, "rb") as file:
    r = requests.post(url, headers=headers, data=file)

# Check response
if r.ok:
    print("Successfully published preferences on the Linked Data Platform.")
else:
    print("Error publishing preferences on the Linked Data Platform.")
