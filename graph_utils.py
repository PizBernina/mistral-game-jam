import networkx as nx

class WorldGraph(nx.DiGraph):
    def __init__(self, path_to_originial_map):
        super().__init__()
        self.load_graph_from_file(path_to_originial_map)

    def load_graph_from_file(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()

                if parts[2] in ['own', 'friendliness']:
                    # Add directed edge with type and value
                    self.add_edge(parts[0], parts[1], relationship=parts[2], value=int(parts[3]))
                else:
                    # Node attributes: country, money, warming, army
                    try:
                        self.add_node(parts[0], money=int(parts[1]), warming=float(parts[2]), army=int(parts[3]), leader=parts[4])
                    except IndexError:
                        self.add_node(parts[0], money=int(parts[1]), warming=float(parts[2]), army=int(parts[3]))

    def get_countries_at_war(self):
        """
        Returns a list of tuples representing pairs of countries that are at war 
        (friendliness == -2).

        :param graph: A NetworkX DiGraph with 'relationship' and 'value' edge attributes.
        :return: List of tuples (country1, country2)
        """
        war_pairs = []

        for u, v, data in graph.edges(data=True):
            if data.get('relationship') == 'friendly' and data.get('value') == -2:
                war_pairs.append((u, v))

        return war_pairs

    def get_control_of(self, owner, owned):
        """
        Transfers ownership of `owned` country to `owner` country.

        Steps:
        1. Update relationships to reflect ownership (owner -> owned = +1, owned -> owner = -1).
        2. Remove all other relationships for the `owned` country.
        3. Transfer attributes (Money, Warming, Army) to the `owner` and set them to 0 for the `owned` country.

        :param graph: A NetworkX DiGraph
        :param owner: The country that will take ownership
        :param owned: The country being owned
        """
        # Step 1: Set ownership relationships
        self.add_edge(owner, owned, relationship='own', value=1)
        self.add_edge(owned, owner, relationship='own', value=-1)

        # Step 2: Remove all other edges related to `owned`
        for neighbor in list(self.successors(owned)) + list(self.predecessors(owned)):
            if neighbor != owner:  # Don't remove the ownership link
                self.remove_edge(owned, neighbor)
                self.remove_edge(neighbor, owned)

        # Step 3: Transfer attributes
        owner_data = self.nodes[owner]
        owned_data = self.nodes[owned]

        owner_data['Money'] += owned_data['Money']
        owner_data['Warming'] += owned_data['Warming']
        owner_data['Army'] += owned_data['Army']

        # Set owned country attributes to 0
        self.nodes[owned]['Money'] = 0
        self.nodes[owned]['Warming'] = 0.0
        self.nodes[owned]['Army'] = 0

    def save_graph_as_edgelist(self, filename):
        """
        Saves the graph to an edgelist file with relationships and node attributes.

        :param filename: The name of the file to save the edgelist.
        """
        with open(filename, 'w') as f:
            # Write edges with relationship type and value
            f.write("# Own and friendly relationships\n")
            for u, v, data in self.edges(data=True):
                relationship = data['relationship']
                value = data['value']
                f.write(f"{u} {v} {relationship} {value}\n")

            f.write("\n# Node attributes (country Money Warming Army)\n")
            for node, data in self.nodes(data=True):
                try:
                    f.write(f"{node} {data['money']} {data['warming']} {data['army']}\n")
                except KeyError:
                    f.write(f"{node} {data['money']} {data['warming']} {data['army']} {data['leader']}\n")


""" Object manipulation
>>> graph['China']['Taiwan'] 
{'relationship': 'own', 'value': 1}

>>> graph['China']['Russia'] 
{'relationship': 'friendliness', 'value': 1}

>>> graph.nodes['France']
{'money': 70, 'warming': 0.7, 'army': 50, 'leader': 'Macron'}

"""

if __name__ == '__main__':
    G = WorldGraph('original_setup/contexts/world_map.edgelist')
    G.save_graph_as_edgelist('test.edgelist')