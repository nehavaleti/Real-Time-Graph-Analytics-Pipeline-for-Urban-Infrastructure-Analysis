import pyarrow.parquet as pq
import pandas as pd
from neo4j import GraphDatabase
import time

class DataLoader:
    def __init__(self, uri, user, password):
        """
        Connect to the Neo4j database and other init steps
        
        Args:
            uri (str): URI of the Neo4j database
            user (str): Username of the Neo4j database
            password (str): Password of the Neo4j database
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.driver.verify_connectivity()

    def close(self):
        """
        Close the connection to the Neo4j database
        """
        self.driver.close()

    def load_transform_file(self, file_path):
        """
        Load the parquet file and create nodes/relationships in Neo4j
        
        Args:
            file_path (str): Path to the parquet file to be loaded
        """
        # Read the parquet file
        trips = pq.read_table(file_path)
        trips = trips.to_pandas()

        # Some data cleaning and filtering
        trips = trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'trip_distance', 'fare_amount']]
        
        # Filter out trips that are not in bronx
        bronx = [3, 18, 20, 31, 32, 46, 47, 51, 58, 59, 60, 69, 78, 81, 94, 119, 126, 136, 147, 159, 167, 168, 169, 174, 182, 183, 184, 185, 199, 200, 208, 212, 213, 220, 235, 240, 241, 242, 247, 248, 250, 254, 259]
        trips = trips[trips['PULocationID'].isin(bronx) & trips['DOLocationID'].isin(bronx)]
        trips = trips[trips['trip_distance'] > 0.1]
        trips = trips[trips['fare_amount'] > 2.5]

        # Convert date-time columns to supported format
        trips['tpep_pickup_datetime'] = pd.to_datetime(trips['tpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
        trips['tpep_dropoff_datetime'] = pd.to_datetime(trips['tpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')

        # Create nodes and relationships in Neo4j
        with self.driver.session() as session:
            # Create Location nodes (unique)
            session.run("""
                UNWIND $locations AS loc
                MERGE (l:Location {name: loc})
            """, {"locations": list(set(trips['PULocationID'].unique().tolist() + trips['DOLocationID'].unique().tolist()))})

            # Create TRIP relationships in batches
            batch_size = 1000
            for i in range(0, len(trips), batch_size):
                batch = trips.iloc[i:i+batch_size]
                session.run("""
                    UNWIND $trips AS trip
                    MATCH (pu:Location {name: trip.PULocationID})
                    MATCH (do:Location {name: trip.DOLocationID})
                    MERGE (pu)-[r:TRIP {
                        distance: trip.trip_distance,
                        fare: trip.fare_amount,
                        pickup_dt: datetime(trip.tpep_pickup_datetime),
                        dropoff_dt: datetime(trip.tpep_dropoff_datetime)
                    }]->(do)
                """, {"trips": batch.to_dict('records')})

def main():
    total_attempts = 10
    attempt = 0

    # The database takes some time to startup!
    # Try to connect to the database 10 times
    while attempt < total_attempts:
        try:
            data_loader = DataLoader("neo4j://localhost:7687", "neo4j", "project1phase1")
            data_loader.load_transform_file("/var/lib/neo4j/import/yellow_tripdata_2022-03.parquet")
            data_loader.close()
            attempt = total_attempts
        except Exception as e:
            print(f"(Attempt {attempt+1}/{total_attempts}) Error: ", e)
            attempt += 1
            time.sleep(10)

if __name__ == "__main__":
    main()
