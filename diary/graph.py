import json
import os
from datetime import datetime

import numpy as np
from dotenv import load_dotenv
from neo4j import GraphDatabase

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

    def find_all_by_user_diary(self, user_id: int = 1, diary_id: int = 1):
        with self._driver.session() as session:
            return session.execute_write(self._find_all_by_user_diary, user_id, diary_id)

    def close(self):
        self._driver.close()

    def insert_node(self, user_id: int, diary_id: int, graph: np.ndarray, word_dict: dict, weights_dict: dict):
        """
        Insert a node into the graph database.
        :param user_id: The user's ID.
        :param diary_id: The diary's ID.
        :param graph: The graph database. A Numpy array. row and column is the word. == TextRank.words_graph
        :param word_dict: The dictionary of words. {word_order: word_text} == TextRank.words_dict
        :param weights_dict: The weights of the words. {index: weight} == Rank.get_ranks(graph)
        """
        with self._driver.session() as session:
            session.execute_write(self._create_and_link_nodes, user_id, diary_id, graph, word_dict, weights_dict)

    @staticmethod
    def _find_all_by_user_diary(tx, user_id=1, diary_id=1):
        """
        {
            User : user_id,
            Diary : {
                diary_id,
                date,
            }
            CONNECTED : [
                {
                    tfidf : tfidf,
                    start : {
                        text,
                        weight
                    },
                    end : {
                        text,
                        weight
                    }
                },
                ...
            ],
        }
        """

        # Find User and Diary nodes
        user_diary_result = tx.run("MATCH (u:User {user_id: $user_id}) "
                                   "MATCH (d:Diary {diary_id: $diary_id}) "
                                   "RETURN u, d", user_id=user_id, diary_id=diary_id)

        dic = {}

        for record in user_diary_result:
            dic['User'] = record['u']['user_id']
            _date = record['d']['date']
            dic['Diary'] = {
                'diary_id': record['d']['diary_id'],
                'date': datetime(_date.year, _date.month, _date.day).isoformat()
            }

        # Find connected Keywords and include in Diary

        connected_result = tx.run(
            f"MATCH (:Diary {{diary_id : {diary_id}}})-[:INCLUDE]-(k:Keyword)-[c:CONNECTED]->(other:Keyword) "
            f"RETURN k, other, c"
        )

        connected = []

        for record in connected_result:
            connected.append({
                'tfidf': record['c']['tfidf'],
                'start': {
                    'text': record['k']['text'],
                    'weight': record['k']['weight']
                },
                'end': {
                    'text': record['other']['text'],
                    'weight': record['other']['weight']
                }
            })

        dic['CONNECTED'] = connected

        return dic

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
                       "MERGE (k)-[:INCLUDE]->(d)", text=word_dict[i], diary_id=diary_id)

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

    dic = db.find_all_by_user_diary()

    # Korean
    print(json.dumps(dic, indent=2, ensure_ascii=False))

    # rank = TextRank("\n".join(""""이 새벽을 비추는 초생달
    # 오감보다 생생한 육감의 세계로
    # 보내주는 푸르고 투명한 파랑새
    # 술 취한 몸이 잠든 이 거릴
    # 휘젓고 다니다 만나는 마지막 신호등이
    # 뿜는 붉은 신호를 따라 회색 거리를 걸어서
    # 가다 보니 좀 낯설어
    # 보이는 그녀가 보인적 없던 눈물로 나를 반겨
    # 태양보다 뜨거워진 나
    # 그녀의 가슴에 안겨 (안겨)
    # 창가로 비친 초승달
    # 침대가로 날아온 파랑새가 전해준
    # 그녀의 머리핀을 보고 눈물이 핑돌아
    # 순간 픽하고 나가버린 시야는
    # 오감의 정전을 의미 이미 희미해진 내 혼은
    # 보랏빛 눈을 가진 아름다운 그녀를 만나러
    # 사랑하는""".rsplit("\n")))
    # weights_dict = Rank.get_ranks(rank.words_graph)
    # graph_vocab = GraphVocab(rank.words_graph, rank.words_dict, weights_dict=weights_dict)
    #
    # db.insert_node(
    #     1,
    #     1,
    #     graph=graph_vocab.graph,
    #     word_dict=graph_vocab.words_dict,
    #     weights_dict=graph_vocab.weights_dict
    # )
