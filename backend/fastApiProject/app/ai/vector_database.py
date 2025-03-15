import faiss
import numpy as np
import os
import json

"""
An implementation of vector database using FAISS

"""
class VectorDatabase:
    def __init__(self, dim=None, database_path="faiss.db"):
        """
        Initialize the FAISS Vector Database.
        
        Args:
            dim (int): Dimension of the embedding vectors. writing mode should be set. reading mode is not necessary.
            database_path (str): Path to save/load the index file.
        """
        self.database_path = database_path
        self.index_path = database_path + ".index"
        self.meta_path = database_path + ".meta"
        if os.path.exists(self.meta_path):
            self.meta = json.loads(open(self.meta_path, "r").read())
        else:
            self.meta = {"ids": [], "id2index": {}}
        if dim is None:
            # load from index
            self.index = faiss.read_index(self.index_path)
            self.dim = self.index.d
        else:
            self.dim = dim
            self.index = faiss.IndexFlatIP(self.dim)  # cosine similarity
    
    def add(self, ids, vectors):
        """
        Add vectors to the index.
        
        Args:
            vectors (np.ndarray): Array of shape (n_samples, dim).
        """
        assert vectors.shape[1] == self.dim, "Vector dimension mismatch."
        start_index = self.index.ntotal
        self.index.add(vectors.astype(np.float32))
        end_index = self.index.ntotal
        print(end_index, start_index, len(ids))
        assert len(ids) == end_index - start_index
        # TODO: if same id, keep the latest added vector
        self.meta["ids"].extend(ids)
        for i in range(start_index, end_index):
            self.meta["id2index"][ids[i - start_index]] = start_index

    
    def search(self, query_vector, k=5):
        """
        Search for top k nearest vectors.
        
        Args:
            query_vector (np.ndarray): Array of shape (1, dim).
            k (int): Number of nearest neighbors to return.
        
        Returns:
            distances, indices: The distances and indices of the top k vectors.
        """
        assert query_vector.shape[1] == self.dim, "Query vector dimension mismatch."
        distances, indices = self.index.search(query_vector.astype(np.float32), k)
        import pdb
        pdb.set_trace()
        return distances, [[self.meta["ids"][idx] for idx in index] for index in indices]
    
    def save(self):
        """
        Save the index to disk.
        """
        faiss.write_index(self.index, self.index_path)
        open(self.meta_path, "w").write(json.dumps(self.meta, indent=2))
        print(f"Index saved to {self.database_path}")
    