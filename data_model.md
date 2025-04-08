# Neo4j Movie Graph Data Model

## Node Labels
1. **Movie** - Represents a film
   - Properties: id, title, release_date, budget, revenue, popularity, vote_average, vote_count, overview
   
2. **Person** - Represents people involved in movies
   - Properties: id, name, gender, profile_path, popularity
   
3. **Genre** - Represents movie categories
   - Properties: id, name
   
4. **Keyword** - Represents movie keywords/tags
   - Properties: id, name
   
5. **Company** - Represents production companies
   - Properties: id, name, origin_country

## Relationships
1. **ACTED_IN** - Person to Movie
   - Properties: character, order
   
2. **DIRECTED** - Person to Movie
   - Properties: job, department
   
3. **PRODUCED** - Company to Movie
   - No properties
   
4. **CATEGORIZED_AS** - Movie to Genre
   - No properties
   
5. **TAGGED_WITH** - Movie to Keyword
   - No properties
   
6. **SIMILAR_TO** - Movie to Movie
   - Properties: similarity_score
   
7. **WORKED_WITH** - Person to Person
   - Properties: movie_count

## Example Cypher Queries

### Creating Nodes
```cypher
// Create Movie nodes
CREATE (m:Movie {id: 550, title: 'Fight Club', release_date: '1999-10-15', budget: 63000000, revenue: 100853753, popularity: 0.5, vote_average: 8.3, vote_count: 3439})

// Create Person nodes
CREATE (p:Person {id: 819, name: 'Edward Norton', gender: 1})

// Create Genre nodes
CREATE (g:Genre {id: 18, name: 'Drama'})
```

### Creating Relationships
```cypher
// Actor relationship
MATCH (p:Person {id: 819}), (m:Movie {id: 550})
CREATE (p)-[:ACTED_IN {character: 'The Narrator', order: 0}]->(m)

// Director relationship
MATCH (p:Person {id: 7467}), (m:Movie {id: 550})
CREATE (p)-[:DIRECTED {job: 'Director', department: 'Directing'}]->(m)

// Genre relationship
MATCH (m:Movie {id: 550}), (g:Genre {id: 18})
CREATE (m)-[:CATEGORIZED_AS]->(g)
```

### Sample Queries for Analysis
```cypher
// Find all movies a person acted in
MATCH (p:Person {name: 'Edward Norton'})-[r:ACTED_IN]->(m:Movie)
RETURN p.name, m.title, r.character

// Find who directed movies in a specific genre
MATCH (p:Person)-[:DIRECTED]->(m:Movie)-[:CATEGORIZED_AS]->(g:Genre {name: 'Drama'})
RETURN p.name, count(m) AS movie_count
ORDER BY movie_count DESC
LIMIT 10

// Find similar movies based on shared actors
MATCH (m1:Movie {title: 'Fight Club'})<-[:ACTED_IN]-(p:Person)-[:ACTED_IN]->(m2:Movie)
WHERE m1 <> m2
RETURN m2.title, count(p) AS shared_actors
ORDER BY shared_actors DESC
LIMIT 10

// Movie recommendation based on genre and ratings
MATCH (m1:Movie {title: 'Fight Club'})-[:CATEGORIZED_AS]->(g:Genre)<-[:CATEGORIZED_AS]-(m2:Movie)
WHERE m1 <> m2 AND m2.vote_average > 7.5
RETURN m2.title, m2.vote_average, collect(g.name) AS shared_genres
ORDER BY m2.vote_average DESC
LIMIT 10
``` 