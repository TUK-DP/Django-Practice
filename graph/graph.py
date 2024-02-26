import pickle

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

NEO4J_PASSWORD = os.environ.get('NEO4j_PASSWORD')


class GraphVocab:
    def __init__(self, words_graph=None, words_dict=None, weights_dict=None):
        self.graph = words_graph
        self.words_dict = words_dict
        self.weights_dict = weights_dict


class GraphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def search_all(self):
        with self._driver.session() as session:
            return session.execute_write(self._search_all)

    def close(self):
        self._driver.close()

    def insert_node(self, user_id, diary_id, graph, word_dict, weights_dict):
        """
        Insert a node into the graph database.
        :param user_id: The user's ID.
        :param diary_id: The diary's ID.
        :param graph: The graph database. A Numpy array. row and column is the word.
        :param word_dict: The dictionary of words. {word_order: word_text}
        :param weights_dict: The weights of the words. {index: weight}
        """
        with self._driver.session() as session:
            session.execute_write(self._create_and_link_nodes, user_id, diary_id, graph, word_dict, weights_dict)

    @staticmethod
    def _search_all(tx):
        result = tx.run("MATCH (n) RETURN n")
        # for record in result:
        #     print(record)
        nodes = []
        for record in result:
            d = dict(record)

            n_ = d[list(d.keys())[0]]
            print(n_)
            print(dict(n_))
            # print(dict(n_))
            # print(d.keys())
            # d['n'] = d['n'].values()
            nodes.append(d)

        return nodes

    @staticmethod
    def _create_and_link_nodes(tx, user_id, diary_id, graph, word_dict, weights):
        # Create User node
        user_node = tx.run("MERGE (u:User {user_id: $user_id}) "
                           "RETURN u", user_id=user_id).single()[0]

        # Create Diary node
        diary_node = tx.run("MERGE (d:Diary {diary_id: $diary_id, date: date()}) "
                            "RETURN d", diary_id=diary_id).single()[0]

        # Create relationship between User and Diary
        tx.run("MATCH (u:User {user_id: $user_id}), (d:Diary {diary_id: $diary_id}) "
               "MERGE (u)-[:WROTE]->(d)", user_id=user_id, diary_id=diary_id)

        # graph[i][j] = weight of word i => word i
        # Create Keyword nodes and their relationships
        for i, row in enumerate(graph):
            # row[j] = weight of word i => word j
            for j, weight in enumerate(row):
                if i == j:
                    continue
                if weight == 0:
                    continue

                # Create Keyword node

                # Create i node
                i_node = tx.run("MERGE (k:Keyword {text: $text, weight: $weight}) "
                                "RETURN k", text=word_dict[i], weight=weights[i]).single()[0]

                # Create j node
                j_node = tx.run("MERGE (k:Keyword {text: $text, weight: $weight}) "
                                "RETURN k", text=word_dict[j], weight=weights[j]).single()[0]

                # Create relationship between Keyword and Diary
                tx.run("MATCH (k:Keyword {text: $text}), (d:Diary {diary_id: $diary_id}) "
                       "MERGE (k)-[:WROTE]->(d)", text=word_dict[i], diary_id=diary_id)

                # Create relationship between Keyword and Keyword
                tx.run(
                    "MATCH (k1:Keyword {text: $text1}), (k2:Keyword {text: $text2}) "
                    "MERGE (k1)-[:CONNECTED {tfidf: $tfidf}]->(k2)",
                    text1=word_dict[i],
                    text2=word_dict[j],
                    tfidf=graph[i][j]
                )


if __name__ == '__main__':
    db = GraphDB("bolt://neo4j:7687", "neo4j", NEO4J_PASSWORD)

     # db.insert_node(1, 1,
    #                graph=graph_vocab.graph,
    #                word_dict=graph_vocab.words_dict,
    #                weights_dict=graph_vocab.weights_dict
    #                )
