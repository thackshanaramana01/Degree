import csv
import sys
from collections import deque
from util import Node, StackFrontier, QueueFrontier  # Ensure these utilities are available

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person_id = row["id"]
            name = row["name"]
            birth = row["birth"]
            people[person_id] = {
                "name": name,
                "birth": birth,
                "movies": set()
            }
            name_lower = name.lower()
            if name_lower not in names:
                names[name_lower] = {person_id}
            else:
                names[name_lower].add(person_id)

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = row["id"]
            title = row["title"]
            year = row["year"]
            movies[movie_id] = {
                "title": title,
                "year": year,
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person_id = row["person_id"]
            movie_id = row["movie_id"]
            if person_id in people and movie_id in movies:
                people[person_id]["movies"].add(movie_id)
                movies[movie_id]["stars"].add(person_id)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            print(f"ID: {person_id}, Name: {person['name']}, Birth: {person['birth']}")
        person_id = input("Intended Person ID: ")
        if person_id in person_ids:
            return person_id
        return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for neighbor_id in movies[movie_id]["stars"]:
            if neighbor_id != person_id:
                neighbors.add((movie_id, neighbor_id))
    return neighbors

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Initialize the frontier with the starting node
    frontier = QueueFrontier()
    frontier.add((None, source))
    
    # Keep track of explored nodes to avoid revisiting
    explored = set()
    explored.add(source)
    
    # Keep track of paths to reconstruct the solution later
    came_from = {}
    
    while not frontier.empty():
        # Get the current node from the frontier
        movie_id, person_id = frontier.remove()
        
        # Check if we've reached the target
        if person_id == target:
            # Reconstruct the path
            path = []
            while (movie_id, person_id) in came_from:
                path.append((movie_id, person_id))
                movie_id, person_id = came_from[(movie_id, person_id)]
            path.reverse()
            return path
        
        # Get neighbors (movie_id, person_id) pairs for the current person
        neighbors = neighbors_for_person(person_id)
        
        for movie_id, neighbor_id in neighbors:
            if neighbor_id not in explored:
                # Add this node to the frontier
                frontier.add((movie_id, neighbor_id))
                # Mark this node as explored
                explored.add(neighbor_id)
                # Track the path taken to reach this node
                came_from[(movie_id, neighbor_id)] = (movie_id, person_id)
    
    # If we exhaust the frontier without finding the target, return None
    return None

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source_name = input("Name: ")
    target_name = input("Name: ")
    source = person_id_for_name(source_name)
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(target_name)
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

if __name__ == "__main__":
    main()
