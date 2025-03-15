import torch
from app.models.singleton_meta import SingletonMeta
# import onnxruntime as ort

# MODEL_PATH = "openai_clip-clipimageencoder.onnx"

# class CLIPImageEncoder(metaclass=SingletonMeta):
#     def __init__(self):
#         self.model = ort.InferenceSession(MODEL_PATH, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    
#     def inference(self, input_data):
#         return self.model.run([self.get_output_name], {self.get_input_name: input_data})

#     def get_input_name(self):
#         return self.model.get_inputs()[0].name
    
#     def get_output_name(self):
#         return self.model.get_outputs()[0].name


from transformers import CLIPProcessor, CLIPModel

"""
convert an image to vector space
"""
class CLIPImageEncoder(metaclass=SingletonMeta):
    def __init__(self):
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

    def inference(self, input_data):
        inputs = self.processor(images=input_data, return_tensors="pt")
        with torch.no_grad():
            embedding = self.model.get_image_features(**inputs)
            embedding = embedding / embedding.norm(p=2, dim=-1, keepdim=True)  # Normalize
        return embedding.cpu().numpy()[0]
