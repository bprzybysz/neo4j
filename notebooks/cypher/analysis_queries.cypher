// Neo4j Movie Graph Analysis Queries

// 1. Basic movie information retrieval
// Get details of a specific movie
MATCH (m:Movie {title: 'The Dark Knight'})
RETURN m;

// 2. Connected entity retrieval
// Find all actors who appeared in a specific movie
MATCH (p:Person)-[r:ACTED_IN]->(m:Movie {title: 'The Dark Knight'})
RETURN p.name, r.character
ORDER BY r.order;

// Find directors of a movie
MATCH (p:Person)-[:DIRECTED]->(m:Movie {title: 'The Dark Knight'})
RETURN p.name;

// Find all genres of a movie
MATCH (m:Movie {title: 'The Dark Knight'})-[:CATEGORIZED_AS]->(g:Genre)
RETURN g.name;

// 3. Entity relationship insights
// Movies with the most actors
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
WITH m, count(p) AS actor_count
RETURN m.title, actor_count
ORDER BY actor_count DESC
LIMIT 10;

// Actors who worked in the most movies
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
WITH p, count(m) AS movie_count
RETURN p.name, movie_count
ORDER BY movie_count DESC
LIMIT 10;

// Most common genres
MATCH (m:Movie)-[:CATEGORIZED_AS]->(g:Genre)
WITH g, count(m) AS movie_count
RETURN g.name, movie_count
ORDER BY movie_count DESC;

// 4. Path traversal and connections
// Find how actors are connected through movies (3 levels deep)
MATCH path = (p1:Person {name: 'Tom Hanks'})-[:ACTED_IN]->(:Movie)<-[:ACTED_IN]-(:Person)-[:ACTED_IN]->(:Movie)<-[:ACTED_IN]-(p2:Person)
WHERE p1 <> p2
RETURN p2.name, length(path)
ORDER BY length(path)
LIMIT 10;

// 5. Recommendations
// Movie recommendations based on genre similarity
MATCH (m:Movie {title: 'The Dark Knight'})-[:CATEGORIZED_AS]->(g:Genre)<-[:CATEGORIZED_AS]-(rec:Movie)
WHERE m <> rec
WITH rec, collect(g.name) AS genres, count(g) AS genre_overlap
WHERE genre_overlap > 2
RETURN rec.title, rec.vote_average, genres, genre_overlap
ORDER BY genre_overlap DESC, rec.vote_average DESC
LIMIT 10;

// Movie recommendations based on cast overlap
MATCH (m:Movie {title: 'The Dark Knight'})<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(rec:Movie)
WHERE m <> rec
WITH rec, collect(a.name) AS shared_actors, count(a) AS actor_count
WHERE actor_count > 1
RETURN rec.title, rec.vote_average, shared_actors, actor_count
ORDER BY actor_count DESC, rec.vote_average DESC
LIMIT 10;

// 6. Advanced pattern matching
// Find movies with the same director and lead actor
MATCH (d:Person)-[:DIRECTED]->(m:Movie)<-[:ACTED_IN]-(a:Person)
MATCH (d)-[:DIRECTED]->(m2:Movie)<-[:ACTED_IN]-(a)
WHERE m <> m2 AND a.name <> d.name
RETURN d.name AS director, a.name AS actor, m.title AS movie1, m2.title AS movie2;

// 7. Aggregations and analysis
// Average rating by genre
MATCH (m:Movie)-[:CATEGORIZED_AS]->(g:Genre)
WITH g, avg(m.vote_average) AS avg_rating, count(m) AS movie_count
WHERE movie_count > 5
RETURN g.name, avg_rating, movie_count
ORDER BY avg_rating DESC;

// Production companies by movie count
MATCH (c:Company)-[:PRODUCED]->(m:Movie)
WITH c, count(m) AS movie_count
RETURN c.name, movie_count
ORDER BY movie_count DESC
LIMIT 20;

// 8. Temporal analysis
// Movie count by year
MATCH (m:Movie)
WHERE m.release_date IS NOT NULL
WITH m.release_date.year AS year, count(m) AS movie_count
RETURN year, movie_count
ORDER BY year;

// 9. Cast and crew analysis
// Directors who worked with the same actor multiple times
MATCH (d:Person)-[:DIRECTED]->(m:Movie)<-[:ACTED_IN]-(a:Person)
WITH d, a, count(m) AS collaboration_count
WHERE collaboration_count > 1
RETURN d.name AS director, a.name AS actor, collaboration_count
ORDER BY collaboration_count DESC
LIMIT 20;

// 10. Advanced recommendations with similarity metrics
// Find similar movies using multiple criteria with weighted scoring
MATCH (m:Movie {title: 'Inception'})
MATCH (other:Movie) WHERE m <> other

// Genre similarity
OPTIONAL MATCH (m)-[:CATEGORIZED_AS]->(g:Genre)<-[:CATEGORIZED_AS]-(other)
WITH m, other, count(g) AS genre_overlap

// Director similarity
OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m), (d)-[:DIRECTED]->(other)
WITH m, other, genre_overlap, count(d) AS same_director

// Cast similarity  
OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m), (a)-[:ACTED_IN]->(other)
WITH m, other, genre_overlap, same_director, count(a) AS cast_overlap

// Calculate similarity score with weights
WITH other, 
     (genre_overlap * 3) + 
     (same_director * 5) + 
     (cast_overlap * 2) AS similarity_score
WHERE similarity_score > 0

RETURN other.title, similarity_score
ORDER BY similarity_score DESC
LIMIT 15; 