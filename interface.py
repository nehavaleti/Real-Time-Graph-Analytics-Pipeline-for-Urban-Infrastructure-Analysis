from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, target_nodes):
        with self._driver.session() as session:
            # Convert single target node to list if needed
            if not isinstance(target_nodes, list):
                target_nodes = [target_nodes]
            
            # First find path using Cypher (simpler than GDS for this case)
            query = """
                MATCH path = shortestPath((start:Location {name: $start_node})-[*..10]-(end:Location))
                WHERE end.name IN $target_nodes
                RETURN [node in nodes(path) | {name: node.name}] AS path
                LIMIT 1
            """
            result = session.run(query, start_node=start_node, target_nodes=target_nodes)
            
            record = result.single()
            if record:
                return [{"path": record["path"]}]
            return []

    def pagerank(self, max_iterations, weight_property):
        with self._driver.session() as session:
            # Create graph projection
            session.run("""
                CALL gds.graph.project(
                    'pagerank_graph',
                    'Location',
                    {
                        TRIP: {
                            type: 'TRIP',
                            orientation: 'NATURAL',
                            properties: $weight_property
                        }
                    }
                )
            """, weight_property=weight_property)
            
            # Run PageRank algorithm
            result = session.run("""
                CALL gds.pageRank.stream(
                    'pagerank_graph',
                    {
                        maxIterations: $max_iterations,
                        dampingFactor: 0.85,
                        relationshipWeightProperty: $weight_property
                    }
                )
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC
            """, max_iterations=max_iterations, weight_property=weight_property)
            
            nodes = [dict(record) for record in result]
            
            # Clean up graph projection
            session.run("CALL gds.graph.drop('pagerank_graph')")
            
            if not nodes:
                return None, None
            
            return (nodes[0], nodes[-1])