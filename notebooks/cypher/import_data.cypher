// Neo4j Movie Graph Import Script

// Reset database (optional - use carefully in production)
MATCH (n) DETACH DELETE n;

// Create constraints for better performance
CREATE CONSTRAINT movie_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (g:Genre) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT keyword_id IF NOT EXISTS FOR (k:Keyword) REQUIRE k.id IS UNIQUE;
CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;

// Import Movie nodes
LOAD CSV WITH HEADERS FROM 'file:///movies.csv' AS row
CREATE (m:Movie {
  id: toInteger(row.id),
  title: row.title,
  release_date: date(row.release_date),
  budget: toInteger(row.budget),
  revenue: toInteger(row.revenue),
  popularity: toFloat(row.popularity),
  vote_average: toFloat(row.vote_average),
  vote_count: toInteger(row.vote_count),
  overview: row.overview
});

// Import Person nodes
LOAD CSV WITH HEADERS FROM 'file:///persons.csv' AS row
CREATE (p:Person {
  id: toInteger(row.id),
  name: row.name,
  gender: toInteger(row.gender),
  profile_path: row.profile_path
});

// Import Genre nodes
LOAD CSV WITH HEADERS FROM 'file:///genres.csv' AS row
CREATE (g:Genre {
  id: toInteger(row.id),
  name: row.name
});

// Import Keyword nodes
LOAD CSV WITH HEADERS FROM 'file:///keywords.csv' AS row
CREATE (k:Keyword {
  id: toInteger(row.id),
  name: row.name
});

// Import Company nodes
LOAD CSV WITH HEADERS FROM 'file:///companies.csv' AS row
CREATE (c:Company {
  id: toInteger(row.id),
  name: row.name,
  origin_country: row.origin_country
});

// Import ACTED_IN relationships
LOAD CSV WITH HEADERS FROM 'file:///acted_in.csv' AS row
MATCH (p:Person {id: toInteger(row.person_id)})
MATCH (m:Movie {id: toInteger(row.movie_id)})
CREATE (p)-[:ACTED_IN {character: row.character, order: toInteger(row.order)}]->(m);

// Import DIRECTED relationships
LOAD CSV WITH HEADERS FROM 'file:///directed.csv' AS row
MATCH (p:Person {id: toInteger(row.person_id)})
MATCH (m:Movie {id: toInteger(row.movie_id)})
CREATE (p)-[:DIRECTED {job: row.job, department: row.department}]->(m);

// Import PRODUCED relationships
LOAD CSV WITH HEADERS FROM 'file:///produced.csv' AS row
MATCH (c:Company {id: toInteger(row.company_id)})
MATCH (m:Movie {id: toInteger(row.movie_id)})
CREATE (c)-[:PRODUCED]->(m);

// Import CATEGORIZED_AS relationships
LOAD CSV WITH HEADERS FROM 'file:///categorized_as.csv' AS row
MATCH (m:Movie {id: toInteger(row.movie_id)})
MATCH (g:Genre {id: toInteger(row.genre_id)})
CREATE (m)-[:CATEGORIZED_AS]->(g);

// Import TAGGED_WITH relationships
LOAD CSV WITH HEADERS FROM 'file:///tagged_with.csv' AS row
MATCH (m:Movie {id: toInteger(row.movie_id)})
MATCH (k:Keyword {id: toInteger(row.keyword_id)})
CREATE (m)-[:TAGGED_WITH]->(k);

// Create derived SIMILAR_TO relationships based on genre overlap
MATCH (m1:Movie)-[:CATEGORIZED_AS]->(g:Genre)<-[:CATEGORIZED_AS]-(m2:Movie)
WHERE m1 <> m2
WITH m1, m2, count(g) AS weight
WHERE weight > 2
MERGE (m1)-[r:SIMILAR_TO]-(m2)
ON CREATE SET r.similarity_score = weight;

// Create derived WORKED_WITH relationships between actors who appeared in the same movie
MATCH (p1:Person)-[:ACTED_IN]->(:Movie)<-[:ACTED_IN]-(p2:Person)
WHERE p1 <> p2
WITH p1, p2, count(*) AS movie_count
WHERE movie_count > 1
MERGE (p1)-[r:WORKED_WITH]-(p2)
ON CREATE SET r.movie_count = movie_count;

// Create indexes for commonly searched properties
CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title);
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX genre_name IF NOT EXISTS FOR (g:Genre) ON (g.name);
CREATE INDEX keyword_name IF NOT EXISTS FOR (k:Keyword) ON (k.name);
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name); 