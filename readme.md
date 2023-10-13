# MongoDB Atlas Vector Search on Images

# Atlas Vector Search on Images

Ever wonder how you can search through images of products by simply describing what you're looking for? Well this little demo will help you understand how this is acheived by using a combination of the [HuggingFace Sentence Transformer framework](https://huggingface.co/sentence-transformers) and the [Vector Search](https://www.mongodb.com/products/platform/atlas-vector-search) cabapility of MongoDB Atlas.

The demo leverages the 44,000 images from the _fashion products_ dataset on [Kaggle](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small).

A [pre-trained model](https://huggingface.co/sentence-transformers/clip-ViT-L-14) from the [huggingface framework](https://huggingface.co/sentence-transformers) is applied to the images from the dataset which generates a textual descripton of the image as vector embeddings.

These are stored in a MongoDB collection (along with some generated price and rating data) where a search index is created to allow the images to be queried using semantic search. The data model looks like this:
```json
{
    "imageFile": "images/7475.jpg",
    "price": 15.66,
    "discountPercentage": 7,
    "avgRating" : 3.47
}
```

A simple UI is used to capture a search criteria and generate a vector which is then used to perform a _nearest neighbour_ search to return the most relevant products. 

The demo also shows how additional filtering can be applied in combination with the search criteria via the `"Advanced"` search screen.

## Set Up
- Configure a MongoDB Atlas cluster running version 7.0.2 or greater and update the connection details in [settings.py](settings.py)
```
MONGODB_URI = "<enter your Atlas connection string here>"
```
- Install Python and the dependencies captured in the [requirements.txt](requirements.txt) file (only dependencies are `flask`, `pymongo` & `sentence transformers`)

```bash 
pip install -r requirements.txt
```
- Execute the encoder_and_loader.py script to generate the vector embeddings and load the data into your MongoDB Atlas cluster. Note this will take some time (as we're processing 44,000 images). The script is written to be multi-threaded so feel free to increase the number of threads based on your environment.
```
python3 encoder_and_loader.py
```
- Create the search index on the database and collection specified in [settings.py](settings.py). Use the default index name (which is `default `) and the following JSON for the index configuration:

```json
{
  "mappings": {
    "fields": {
      "imageVector": [
        {
          "dimensions": 768,
          "similarity": "cosine",
          "type": "knnVector"
        }
      ],
      "price": {
        "type": "number"
      },
      "averageRating": {
         "type": "number"
      }
    }
  }
}
```


## Run
To start the demo application, run [app.py](app.py)
```python
python3 app.py
```
This will launch the app in a local `flask` server on the default port [http://127.0.0.1:5000](http://127.0.0.1:5000)

