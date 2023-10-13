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
### MongoDB Atlas
Configure a MongoDB Atlas cluster running version 7.0.2 or greater and update the connection details in [settings.py](settings.py)
```
MONGODB_URI = "<enter your Atlas connection string here>"
```
### Python Installation
Install Python and the dependencies captured in the [requirements.txt](requirements.txt) file (only dependencies are `flask`, `pymongo` & `sentence transformers`)

```bash 
pip install -r requirements.txt
```
### Load the Image Data
You have two options to load the image data into the MongoDB Atlas cluster:

+ You can download the image files from Kaggle, use a script to generate the vector embeddings and load them into the cluster. To do this, download the dataset from [here](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small/download?datasetVersionNumber=1) and unzip its contents so that all the image files are in a directory called "_images_" in the [static](static) directory. Then, execute the encoder_and_loader.py script to generate the vector embeddings and load the data into your MongoDB Atlas cluster. Note this will take some time (as we're processing 44,000 images). The script is written to be multi-threaded so feel free to increase the number of threads based on your environment.
```
python3 encoder_and_loader.py
```
+ Alternatively (__and this will be much quicker__) use the mongodump file to load this data directly into your cluster using the `mongorestore` command line tool. If you do chose to use this approach make sure you have the command line tools installed on your laptop. See [here]( ) for more details. Then restore the collection using the `mongorestore` command as per the following example (run this from the root directory of the repo), for example:
```sh
mongorestore --uri mongodb+srv://<username><password>@anandorgdev.zbcqwov.mongodb.net --dir=MDBExport    
```
You should see the output end with after 2-3 minutes:
```
2023-10-13T14:22:46.068+0100	[###################.....]  vector_search.products  344MB/424MB  (81.0%)
2023-10-13T14:22:49.067+0100	[###################.....]  vector_search.products  353MB/424MB  (83.3%)
2023-10-13T14:22:52.067+0100	[####################....]  vector_search.products  363MB/424MB  (85.5%)
2023-10-13T14:22:55.067+0100	[#####################...]  vector_search.products  372MB/424MB  (87.8%)
2023-10-13T14:22:58.067+0100	[######################..]  vector_search.products  391MB/424MB  (92.3%)
2023-10-13T14:23:01.067+0100	[######################..]  vector_search.products  391MB/424MB  (92.3%)
2023-10-13T14:23:04.068+0100	[######################..]  vector_search.products  401MB/424MB  (94.5%)
2023-10-13T14:23:07.066+0100	[#######################.]  vector_search.products  410MB/424MB  (96.8%)
2023-10-13T14:23:10.068+0100	[#######################.]  vector_search.products  410MB/424MB  (96.8%)
2023-10-13T14:23:13.068+0100	[#######################.]  vector_search.products  420MB/424MB  (99.0%)
2023-10-13T14:23:16.071+0100	[########################]  vector_search.products  424MB/424MB  (100.0%)
2023-10-13T14:23:16.323+0100	[########################]  vector_search.products  424MB/424MB  (100.0%)
2023-10-13T14:23:16.323+0100	finished restoring vector_search.products (44441 documents, 0 failures)
2023-10-13T14:23:16.324+0100	no indexes to restore for collection vector_search.products
2023-10-13T14:23:16.324+0100	44441 document(s) restored successfully. 0 document(s) failed to restore.
anand.sanghani@M-FRFJ6FPH37 MDB-VectorSearch-Images % 
```

### Create Index

Create the search index on the database and collection specified in [settings.py](settings.py). Use the default index name (which is `default `) and the following JSON for the index configuration:

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

