from ai.vector_database import VectorDatabase
import numpy as np

place_content_db = VectorDatabase(database_path="/home/gophers/WanderWise/backend/fastApiProject/place_content.db")
place_image_db = VectorDatabase(database_path="/home/gophers/WanderWise/backend/fastApiProject/place_image.db")
post_content_db = VectorDatabase(database_path="/home/gophers/WanderWise/backend/fastApiProject/post_content.db")
post_image_db = VectorDatabase(database_path="/home/gophers/WanderWise/backend/fastApiProject/post_content.db")
user_db = VectorDatabase(database_path="/home/gophers/WanderWise/backend/fastApiProject/user_place.db")


def create_search_db(find_ids, content_db, image_db):
    content_embeddings = []
    image_embeddings = []
    valid_ids = []
    for find_id in find_ids:
        content_feature = content_db.get(find_id)
        image_feature = image_db.get(find_id)
        if content_feature is None or image_feature is None:
            continue
        content_embeddings.append(content_feature)
        image_embeddings.append(image_feature)
        valid_ids.append(find_id)
    content_embeddings = np.vstack(content_embeddings)
    image_embeddings = np.vstack(image_embeddings)
    search_embeddings = np.concatenate((content_embeddings, image_embeddings), axis=1)
    search_db = VectorDatabase(search_embeddings.shape[1])
    search_db.add(valid_ids, search_embeddings)
    return search_db


def findKClosestPlaces(k: int, placeIds: list, userId: str) -> list:
    # closest_places = ["ChIJ-bfVTh8VkFQRDZLQnmioK9s","ChIJVTtr1kUVkFQRh-YAfijbQXs","ChIJY8p6-EYVkFQREthJEc0p6dE","ChIJUS2ELmoVkFQRjrUkJB5o9zM","ChIJkx6Hjk71mlQRRQOiffP85FA"]
    place_db = create_search_db(placeIds, place_content_db, place_image_db)
    user_feature = user_db.get(userId)
    user_feature = np.expand_dims(user_feature, axis=0)
    distances, closest_places = place_db.search(user_feature, k)
    print("search result ", distances, closest_places)
    return closest_places[0]


def findKClosestPosts(k: int, postIds: list, userId: str) -> list:
    # closest_posts = ["666677f6000000000d00ca27","674c12d30000000002029b74","6698f97500000000250045db","66f8beda000000002a031121","61e39d0d000000002103bc8a"]
    post_db = create_search_db(postIds, post_content_db, post_image_db)
    user_feature = user_db.get(userId)
    user_feature = np.expand_dims(user_feature, axis=0)
    distances, closest_posts = post_db.search(user_feature, k)
    print("search result ", distances, closest_posts)
    return closest_posts[0]
