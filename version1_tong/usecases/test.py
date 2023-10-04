import rdflib

graph = rdflib.Graph()
def load_graph():
    graph.parse('./data/14_graph.nt', format='turtle')
    print('loaded map successfully')


def sparql(message):
    query = message
    print(query)

    try: 
        print("querying graph")
        results = graph.query(query)
        print(results)
        print("...................")
        print(type(results))

        result_list = []
        for row in results:
            print(type(row))
            print("....")
            print(row)
            result_list.append(row)
        
        # # Send a message to the corresponding chat room using the post_messages method of the room object.
        print(f"Answer to your query: '{result_list[0]}' ")

    except Exception as e:
        print(e)
        print("query failed")
        print(f"Sorry, I could not understand your query: '{message}' ")

    # finally:
        # Mark the message as processed, so it will be filtered out when retrieving new messages.
            

t='''
    PREFIX ddis: <http://ddis.ch/atai/> PREFIX wd: PREFIX wdt: PREFIX schema: SELECT ?director WHERE { ?movie rdfs:label "Apocalypse Now"@en . ?movie P57 ?directorItem . ?directorItem rdfs:label ?director . } LIMIT 1
'''
load_graph()
print(sparql(t))
