from neo4j import GraphDatabase
from neo4j_conn import get_neo4j_session

def setup_schema():
    cypher_commands = [
        "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;",
        "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;",
        "CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE;"
    ]
    with get_neo4j_session() as session:
        for cmd in cypher_commands:
            session.run(cmd)

if __name__ == "__main__":
    setup_schema() 