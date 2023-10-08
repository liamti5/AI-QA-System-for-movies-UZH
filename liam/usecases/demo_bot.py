from speakeasypy import Speakeasy, Chatroom
from typing import List
import time
from kg_hanldler import create_graph, create_namespaces

DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2


class Agent:
    def __init__(self, username, password):
        self.username = username
        # Initialize the Speakeasy Python framework and login.
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL, username=username, password=password)
        self.speakeasy.login()  # This framework will help you log out automatically when the program terminates.

    def listen(self):
        while True:
            # only check active chatrooms (i.e., remaining_time > 0) if active=True.
            rooms: List[Chatroom] = self.speakeasy.get_rooms(active=True)
            for room in rooms:
                if not room.initiated:
                    # send a welcome message if room is not initiated
                    room.post_messages(f'Hello! This is a welcome message from {room.my_alias}.')
                    room.initiated = True
                # Retrieve messages from this chat room.
                # If only_partner=True, it filters out messages sent by the current bot.
                # If only_new=True, it filters out messages that have already been marked as processed.
                for message in room.get_messages(only_partner=True, only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new message #{message.ordinal}: '{message.message}' "
                        f"- {self.get_time()}")

                    room.post_messages(f"Received your message: '{message.message}' ")

                    # # Implement your agent here #
                    # Define a SPARQL query from user input
                    print(message.message)
                    
                    query = message.message.replace('"', '')
                    print(query)

                    try: 
                        print("querying graph")
                        results = g.query(query)
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
                        room.post_messages(f"Answer to your query: '{result_list[0]}' ")

                    except Exception as e:
                        print(e)
                        print("query failed")
                        room.post_messages(f"Sorry, I could not understand your query: '{message.message}' ")
                        continue

                    finally:
                        # Mark the message as processed, so it will be filtered out when retrieving new messages.
                        room.mark_as_processed(message)                    

                # Retrieve reactions from this chat room.
                # If only_new=True, it filters out reactions that have already been marked as processed.
                for reaction in room.get_reactions(only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new reaction #{reaction.message_ordinal}: '{reaction.type}' "
                        f"- {self.get_time()}")

                    # Implement your agent here #

                    room.post_messages(f"Received your reaction: '{reaction.type}' ")
                    room.mark_as_processed(reaction)

            time.sleep(listen_freq)

    @staticmethod
    def get_time():
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())


if __name__ == '__main__':
    ns1, ns2, ns3 = create_namespaces()
    print("creating graph ...")
    g = create_graph('./data/14_graph.nt', 'turtle')
    print("graph created!")
    demo_bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    demo_bot.listen()