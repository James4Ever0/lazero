from txtai.embeddings import Embeddings

embeddings = Embeddings(
    {  # this path is for alpharetta. need to change this on macos
        "path": "/root/.cache/huggingface/hub/models--sentence-transformers--distiluse-base-multilingual-cased-v1/snapshots/756c7aa7d57c27bd1c71a483367c53966465f450"
        # mac path:
        # "/Users/jamesbrown/.cache/huggingface/hub/models--sentence-transformers--distiluse-base-multilingual-cased-v1/snapshots/756c7aa7d57c27bd1c71a483367c53966465f450"
    }
)