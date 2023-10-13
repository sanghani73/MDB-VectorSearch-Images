# This script should be used to load the files from the ./static/images directory.
# It is written to be multi-threaded so depending on the spec of machine you are running this on, 
# increase the thread count (NUM_OF_WORKERS) accordingly
# 
from sentence_transformers import SentenceTransformer, util
from PIL import Image
import pymongo, os
import concurrent.futures
import random
import settings

# number of worker threads to initialize that each thread encodes images in the folder concurrently
NUM_OF_WORKERS=8

mongo_uri = settings.MONGODB_URI
db_name = settings.DB
collection_name = settings.COLLECTION
imageDirectory = './static/images'

files = [] 
for filename in os.listdir(imageDirectory):
    f = os.path.join(imageDirectory, filename)
    files.append(f)


connection = pymongo.MongoClient(mongo_uri)
product_collection = connection[db_name][collection_name]
product_collection.delete_many({})

preTrainedModelName = "clip-ViT-L-14"
model = SentenceTransformer(preTrainedModelName)

def vectorize(imageFiles,threadNo):
    number_of_files_processed = 0
    for f in imageFiles:
        if os.path.isfile(f):
            encoded = model.encode(Image.open(f)).tolist()
            image = {
                "imageFile": f,
                "imageVector": encoded,
                "price": round(random.uniform(5.0, 100.0),2),
                "discountPercentage" : random.randint(5,25),
                "averageRating": round(random.uniform(3.0, 5.0),2),
            }
            product_collection.insert_one(image)
            number_of_files_processed = number_of_files_processed + 1
            remaining_number_of_files = len(imageFiles) - number_of_files_processed
            print(f"[Thread no: {threadNo}][{remaining_number_of_files} files left] Image has been embedded as a vector in the document:{f}")
        
    return f"Thread number {threadNo} completed, {len(imageFiles)} files have been loaded"

# enable multi-threading for encoding thousands of image files
with concurrent.futures.ThreadPoolExecutor(max_workers = NUM_OF_WORKERS) as executor:

    images_length = len(files)
    number_of_images_per_thread = round(images_length/NUM_OF_WORKERS)
    print(f"Number of images per thread: {number_of_images_per_thread}")
    futures = [] 

    for i in range(1,NUM_OF_WORKERS+1):
        start_index_included= (i-1)*number_of_images_per_thread
        if i < NUM_OF_WORKERS:
            end_index_excluded = i*number_of_images_per_thread
            imageFiles = files[start_index_included:end_index_excluded]
        elif i == NUM_OF_WORKERS:
            imageFiles = files[start_index_included:]
        print(f"Thread number {i} is going to be submitted with the Start Index: {start_index_included}, Length: {len(imageFiles)}")
        future = executor.submit(vectorize,imageFiles,i)
        futures.append(future)
    
    for completed_future in concurrent.futures.as_completed(futures):
        result = completed_future.result()
        print(f"Result: {result}")

   
