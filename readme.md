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
Configure a MongoDB Atlas cluster following the instructions from [here](https://www.mongodb.com/docs/atlas/getting-started/).
If you create a dedicated cluster, ensure that your chose the latest version (it should running version 7.0.2 or greater) and update the connection details in [settings.py](settings.py).
Note 
```
MONGODB_URI = "<enter your Atlas connection string here>"
```
### Python Installation
Install Python and the dependencies captured in the [requirements.txt](requirements.txt) file (only dependencies are `flask`, `pymongo` & `sentence transformers`)

```bash 
pip install -r requirements.txt
```
### Load the Image Data
Download the image files from Kaggle and them to the directory from which the app can display them as part of the results. To do this, download the dataset from [here](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small/download?datasetVersionNumber=1) and unzip its contents so that all the image files are in a directory called "_images_" in the [static](static) directory. 

Once this is done, you have two ways in which you can get the image data loaded into your MongoDB Atlas cluster:

+ You can execute the encoder_and_loader.py script to generate the vector embeddings and load the data into your MongoDB Atlas cluster from your client. This will take a fair bit of time as we're processing 44,000 images and because its running on the client side, increasing the cluster resources won't really help. The script is written to be multi-threaded so feel free to increase the number of threads based on your environment. On my M1 Macbook this took around 3 hrs to load.
```
python3 encoder_and_loader.py
```
+ Alternatively (__and this will be much quicker__) use the mongodump file to load this data directly into your cluster using the `mongorestore` command line tool. If you do chose to use this approach make sure you clone this repo  have the command line tools installed on your laptop. See [here](https://www.mongodb.com/docs/database-tools/installation/installation/) for more details. Then restore the collection using the `mongorestore` command as per the following example (run this from the MongoDBExportZip directory of the repo), for example:
```sh
cd MDBExportZip
mongorestore --uri mongodb+srv://<username>:<password>@anandorgdev.zbcqwov.mongodb.net --gzip
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
__Important__: If you do chose to use this method then please be aware that the mongodump file containing the data is stored using [Git lfs](https://git-lfs.com/) as it's around 200MB. So you will need to ensure that you have installed this on your machine and that you clone this repo using git lfs (e.g. `git lfs clone git@github.com:sanghani73/MDB-VectorSearch-Images.git`).

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
To start the demo application, run [app.py](app.py) if you are running this on an Atlas cluster that is running 7.0.2 or greater.
```python
python3 app.py
```
If however you created this on a sandbox (or other shared cluster) and the version is less that 7.0.2 then run [app-MDBv6.py](app-MDBv6.py) as this will use the [knnBeta](https://www.mongodb.com/docs/atlas/atlas-search/knn-beta/) search operator (which has been deprecated so will stop working at some point in time).

```python
python3 app-MDBv6.py
```
This will launch the app in a local `flask` server on the default port [http://127.0.0.1:5000](http://127.0.0.1:5000)

