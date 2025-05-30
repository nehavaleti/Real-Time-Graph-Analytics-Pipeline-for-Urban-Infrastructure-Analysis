# Project 1: Data Processing at Scale with Neo4j and Docker

## Overview
This project sets up a Neo4j database in a Docker container and loads taxi trip data into it. The project includes implementing graph algorithms using the Neo4j Graph Data Science (GDS) plugin.

## Prerequisites
Before you begin, ensure you have the following installed:
- Docker
- Git
- A GitHub personal access token (PAT) for cloning private repositories
- Python 3.x
- Neo4j Browser (optional, for exploring the database)

## Repository Structure
```
.
├── Dockerfile             # Defines the container environment
├── data_loader.py         # Loads data into Neo4j
├── interface.py           # Implements graph algorithms
├── yellow_tripdata_2022-03.parquet # Sample dataset
├── tester.py              # Script to test implementation
└── README.md              # Project documentation
```

## Setting Up and Running the Project
### 1. Build the Docker Image
To build the Docker image, run the following command in the project directory:
```sh
export GIT_TOKEN=<your-github-token>
docker build --build-arg Token=$GIT_TOKEN -t neo4j_project .
```
Replace `<your-github-token>` with your actual GitHub personal access token.

### 2. Run the Docker Container
To start the Neo4j container, run:
```sh
docker run -d --name neo4j_container -p 7474:7474 -p 7687:7687 neo4j_project
```
This will:
- Start the Neo4j service
- Load the taxi trip data
- Expose ports 7474 (Neo4j browser) and 7687 (Bolt protocol)

### 3. Verify Neo4j Setup
Once the container is running, you can check the status by running:
```sh
docker logs neo4j_container
```
To access the Neo4j browser, go to:
[http://localhost:7474](http://localhost:7474) and log in using:
- Username: `neo4j`
- Password: `project1phase1`

Run the following queries to verify data is loaded:
```cypher
CALL db.schema.visualization();
MATCH (n) RETURN n LIMIT 25;
```

## Running Graph Algorithms
The `interface.py` file contains implementations for graph algorithms. To run it:
```sh
python3 interface.py
```
This script connects to the running Neo4j instance and performs:
1. **PageRank Algorithm** to evaluate node importance.
2. **Breadth-First Search (BFS)** for graph traversal.

## Running Tests
To validate your implementation, run:
```sh
python3 tester.py
```
This script checks if the data is correctly loaded and algorithms are implemented properly.

## Troubleshooting
- If Neo4j fails to start, check container logs:
  ```sh
  docker logs neo4j_container
  ```
- If data is not loaded, rerun `data_loader.py` inside the container:
  ```sh
  docker exec -it neo4j_container python3 /var/lib/neo4j/import/data_loader.py
  ```
- If connection issues arise, verify that the ports (7474, 7687) are properly mapped and accessible.

## Cleanup
To stop and remove the container, run:
```sh
docker stop neo4j_container && docker rm neo4j_container
```
To remove the built Docker image:
```sh
docker rmi neo4j_project
```

## Notes
- Allow 2-4 minutes for the Neo4j service to become available after starting the container.
- Modify `neo4j.conf` as needed to adjust database settings.

## References
- [Neo4j Docker Documentation](https://neo4j.com/developer/docker-run-neo4j/)
- [Graph Data Science Plugin](https://neo4j.com/product/graph-data-science/)
- [GitHub Personal Access Tokens](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)

---
Developed for CSE511 - Data Processing at Scale

