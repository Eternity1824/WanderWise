import re
from typing import List
from app.models.text_2_vec import Text2Vec
from app.models.clip_image_encoder import CLIPImageEncoder
import numpy as np
from app.ai.clustering.utils import load_image_from_file, load_image_from_url

def batch_load_images(image_list: List[str]):
    # TODO: load with file path or url
    # TODO: multiprocessing
    images = []
    for image_path in image_list:
        images.append(load_image_from_file(image_path))
    return images

def remove_emojis(text):
    # Emoji pattern covering most Unicode emoji ranges
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F680-\U0001F6FF"  # Transport & Map
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols, etc.
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed Characters
        "]+", flags=re.UNICODE)

    return emoji_pattern.sub('', text)

def remove_newline(text):
    return text.replace("\n", "").replace("\t", "")

def remove_post_tags(text):
    # This regex matches anything between two hashtags, including the hashtags themselves
    cleaned_text = re.sub(r'#.*?#', '', text)
    return cleaned_text.strip()  # Optional: remove leading/trailing whitespace


class PostFeatureCalculator:
    @staticmethod
    def get_post_content_embedding(posts):
        # 1. prepare data
        # TODO: clean data, remove location and emojis
        contents = list(map(lambda x:remove_post_tags(remove_newline(remove_emojis((x['desc'])))), posts))

        # 2. batch inference
        text_2_vec = Text2Vec()
        content_embeddings = text_2_vec.inference(contents)
        content_embeddings = content_embeddings / np.linalg.norm(content_embeddings, axis=1, keepdims=True)
 
        # 3. return result
        return content_embeddings

    @staticmethod
    def get_post_image_embedding(posts: List[dict]):
        # 1. prepare data
        all_image_paths = []
        post_image_indices = []  # To keep track of which image belongs to which post
        # Collect all image paths and map them to their posts
        for idx, post in enumerate(posts):
            if not post['image_list']:
                continue
            image_paths = post['image_list'].split(',')
            all_image_paths.extend(image_paths)
            post_image_indices.extend([idx] * len(image_paths))
        images = batch_load_images(all_image_paths)

        # 2. batch inference
        # TODO: batchify
        # def batchify(iterable, batch_size):
        #     for i in range(0, len(iterable), batch_size):
        #         yield iterable[i:i + batch_size]
        clip_image_encoder = CLIPImageEncoder()
        image_embeddings = []
        for image in images:
            image_embeddings.append(clip_image_encoder.inference(image))

        image_embeddings = np.array(image_embeddings)  # Shape: (num_images, feature_dim)
        post_image_indices = np.array(post_image_indices)  # Convert to NumPy array

        # 3. max pooling over all images from the same post
        post_image_features = []
        for i in range(len(posts)):
            # Get features of all images belonging to post i
            post_i_features = image_embeddings[post_image_indices == i]
            if len(post_i_features) == 0:
                post_image_features.append(np.zeros(image_embeddings.shape[1]))
            else:
                # Max pooling across images (dim=0)
                post_i_max_pooled = np.max(post_i_features, axis=0)
                post_image_features.append(post_i_max_pooled)

        # 3. return result
        return np.array(post_image_features)

    @staticmethod
    def get_post_tag_embedding(posts: List[dict]):
        # 1. prepare data

        # 2. batch inference

        # 3. return result

        # 4. return None

        raise NotImplemented("this method is not implemented")

