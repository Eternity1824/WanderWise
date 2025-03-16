import sys

sys.path.append('.')  # 确保可以找到app模块

import glob
from app.ai.clustering.post_feature_calculator import PostFeatureCalculator
from app.ai.vector_database import VectorDatabase
import time

import json

posts = json.loads(open("/mnt/c/Users/qc_de/Downloads/merged_posts.json", "r").read())

image_base_dir = "/mnt/c/Users/qc_de/Downloads/images"

for post in posts:
    note_id = post['note_id']
    post['image_list'] = ','.join(list(glob.glob(image_base_dir + "/" + note_id + "/*.jpg")))

print("start inferencing")
timestamp = time.time()
content_features = PostFeatureCalculator.get_post_content_embedding(posts)
print("content embedding: ", time.time() - timestamp)
# timestamp = time.time()
# image_features = PostFeatureCalculator.get_post_image_embedding(posts)
# print("image embedding: ", time.time() - timestamp)

post_ids = [post['note_id'] for post in posts]
contentDB = VectorDatabase(content_features.shape[1], "content.db")
contentDB.add(post_ids, content_features)
contentDB.save()
# imageDB = VectorDatabase(image_features.shape[1], "image.db")
# imageDB.add(post_ids, image_features)
# imageDB.save()

# search_idx = 20
# print(posts[20]['desc'])

# print(contentDB.search(content_features[search_idx:search_idx+1]))
# print(imageDB.search(image_features[search_idx:search_idx+1]))

# test loading

# contentDB = VectorDatabase(database_path="content.db")
# imageDB = VectorDatabase(database_path="image.db")


# from app.models.clip_image_encoder import CLIPImageEncoder

# from app.ai.clustering.utils import load_image_from_file

# image_file_path = "../../../images/images/669213cb0000000025002493/0.jpg"

# clip_encoder = CLIPImageEncoder()
# a = clip_encoder.inference([load_image_from_file(image_file_path)])

# import numpy as np

# np.save('array.npy', a)
