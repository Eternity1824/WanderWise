import sys

sys.path.append('.')  # 确保可以找到app模块

from app.ai.vector_database import VectorDatabase

import numpy as np


content_db_path = "/home/gophers/WanderWise/backend/fastApiProject/place_content.db"
image_db_path = "/home/gophers/WanderWise/backend/fastApiProject/place_image.db"


contentDB = VectorDatabase(database_path=content_db_path)
imageDB = VectorDatabase(database_path=image_db_path)

file_paths = [
    ('0001', '/mnt/c/Users/qc_de/Downloads/user0001_places.txt'),
    ('0002', '/mnt/c/Users/qc_de/Downloads/user0002_places.txt'),
    ('0003', '/mnt/c/Users/qc_de/Downloads/user0003_places.txt'),
]


def generate_user_embedding(file_path):
    user_post_ids =[x for x in open(file_path, "r").read().split("\n") if x != ""]
    content_embeddings = []
    image_embeddings = []

    for file_line in user_post_ids:
        user_post_id, frequency = file_line.split(" ")
        content_embeddings.extend([contentDB.get(user_post_id)] * int(frequency))
        image_embeddings.extend([imageDB.get(user_post_id)] * int(frequency))

    content_embeddings = np.vstack(content_embeddings)
    image_embeddings = np.vstack(image_embeddings)

    joint_feature = np.concatenate((content_embeddings, image_embeddings), axis=1)

    user_feature = np.mean(joint_feature, axis=0)

    return user_feature

user_ids = []
user_features = []
for user_id, file_path in file_paths:
    user_ids.append(user_id)
    user_features.append(generate_user_embedding(file_path))
user_features = np.array(user_features)

user_post_db = "/home/gophers/WanderWise/backend/fastApiProject/user_place.db"
db = VectorDatabase(user_features.shape[1], user_post_db)
db.add(user_ids, user_features)
db.save()


# def get_index_as_nparray(db):
#     content_index = db.index

#     total_vectors = content_index.ntotal

#     # Create an empty NumPy array to hold the retrieved vectors
#     content_vectors = np.zeros((total_vectors, db.dim), dtype='float32')

#     # Reconstruct the entire index (all vectors)
#     content_index.reconstruct_n(0, total_vectors, content_vectors)

#     return content_vectors

# content_vectors = get_index_as_nparray(contentDB)
# post_ids = contentDB.meta['ids']
# image_vectors = get_index_as_nparray(imageDB)

# post_vectors = np.concatenate((content_vectors, image_vectors), axis=1)

# postDB = VectorDatabase(post_vectors.shape[1], "post_combined.db")

# postDB.add(post_ids, post_vectors)

# print(postDB.search(np.array([user_feature])))

