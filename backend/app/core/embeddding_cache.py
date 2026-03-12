"""

Embedding Cache
===============
Pre computes and persists two embeddings per camera image
    - full-embedding: 2048 dim fused embedding -> used for image - to - image search.
    - sem-emb : 512 dim semantic (clip) -> Used for text to image search


"""

import logging
