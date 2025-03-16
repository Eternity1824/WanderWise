import torch
from models.singleton_meta import SingletonMeta
import onnxruntime as ort
import numpy as np

MODEL_PATH = "/home/gophers/openai_clip-clipimageencoder.onnx"


def preprocess_image(img, target_size=(224, 224), normalize=True):  
    # Step 2: Resize the image to the target size (height, width)
    img = img.resize(target_size)

    img = img.convert("RGB")

    # Step 3: Convert the image to a NumPy array
    img_array = np.array(img)

    # Step 4: Normalize the image (if needed)
    if normalize:
        img_array = img_array.astype(np.float32) / 255.0  # Convert to float32 and scale to [0, 1]

    # Step 5: Change the color format if necessary (HWC -> CHW)
    img_array = np.transpose(img_array, (2, 0, 1))  # (height, width, channels) -> (channels, height, width)
    
    # Step 6: Add a batch dimension (1, channels, height, width)
    img_array = np.expand_dims(img_array, axis=0)  # Shape becomes (1, channels, height, width)
    
    return img_array


class CLIPImageEncoder(metaclass=SingletonMeta):
    def __init__(self):
        self.session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    
    def inference(self, input_data):
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        return self.session.run([output_name], {input_name: preprocess_image(input_data)})[0]

# from transformers import CLIPProcessor, CLIPModel

# """
# convert an image to vector space
# """
# class CLIPImageEncoder(metaclass=SingletonMeta):
#     def __init__(self):
#         self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
#         self.model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

#     def inference(self, input_data):
#         inputs = self.processor(images=input_data, return_tensors="pt")
#         with torch.no_grad():
#             embedding = self.model.get_image_features(**inputs)
#             embedding = embedding / embedding.norm(p=2, dim=-1, keepdim=True)  # Normalize
#         return embedding.cpu().numpy()[0]
