import torch
from transformers import BertForSequenceClassification, BertTokenizer
from models.singleton_meta import SingletonMeta

"""
Direct Pytorch inference
token size < 512
TODO: bad performance, compile with ai hub
"""
class Text2Vec(metaclass=SingletonMeta):
    def __init__(self):
        self.text_tokenizer = BertTokenizer.from_pretrained("IDEA-CCNL/Taiyi-CLIP-Roberta-large-326M-Chinese")
        self.text_encoder = BertForSequenceClassification.from_pretrained("IDEA-CCNL/Taiyi-CLIP-Roberta-large-326M-Chinese").eval()

    def inference(self, input_data):
        text = self.text_tokenizer(input_data, return_tensors='pt', padding=True, truncation=True, max_length=512)['input_ids']
        with torch.no_grad():
            query_embedding = self.text_encoder(text).logits
            query_embedding = query_embedding / query_embedding.norm(p=2, dim=-1, keepdim=True)  # Normalize

        return query_embedding.cpu().numpy()
