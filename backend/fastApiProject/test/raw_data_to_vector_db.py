import sys

sys.path.append('.')  # 确保可以找到app模块

from app.ai.vector_database import VectorDatabase

import json
import numpy as np



post_image_indices = np.load("/mnt/c/Users/qc_de/Documents/post_image_indices.npy")
image_embeddings = np.load("/mnt/c/Users/qc_de/Documents/post_raw_image_embeddings.npy")
image_embeddings = np.squeeze(image_embeddings)
post_ids = json.loads(open("/mnt/c/Users/qc_de/Documents/post_note_ids.json").read())

post_image_features = []
for i in range(len(post_ids)):
    # Get features of all images belonging to post i
    post_i_features = image_embeddings[post_image_indices == i]
    if len(post_i_features) == 0:
        post_image_features.append(np.zeros(image_embeddings.shape[1]))
    else:
        # Max pooling across images (dim=0)
        post_i_max_pooled = np.max(post_i_features, axis=0)
        post_image_features.append(post_i_max_pooled)

post_image_features = np.array(post_image_features)

print(post_image_features.shape)

imageDB = VectorDatabase(post_image_features.shape[1], "/home/gophers/WanderWise/backend/fastApiProject/post_image.db")
imageDB.add(post_ids, post_image_features)
imageDB.save()
