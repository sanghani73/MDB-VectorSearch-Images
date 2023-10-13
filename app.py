from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import settings

app = Flask(__name__, static_folder="static")


mongo_uri = settings.MONGODB_URI
db_name = settings.DB
collection_name = settings.COLLECTION

#Load CLIP model
preTrainedModelName = "clip-ViT-L-14"
model = SentenceTransformer(preTrainedModelName)

# Define the folder where image files are stored on the server
# app.config['UPLOAD_FOLDER'] = 'setup/images'  # Change 'images' to your folder name

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory("static", filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form)
        search_query = request.form['search_query']
        print('in post of /', search_query)
        return redirect(url_for('search',search_query=search_query))

    return render_template('index.html')

@app.route('/search/<search_query>', methods=['GET','POST'])
def search(search_query):
    print('search query ', search_query)
    results = run_query(search_query)
    return render_template('index.html', results=results, search_query=search_query)

def run_query(search_query):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    print('running query with', search_query)
    # regular search with no filter
    search = {
            "$vectorSearch": {
                "index": "default",
                "path": "imageVector",
                "queryVector": model.encode(search_query).tolist(),
                "numCandidates": 200,
                "limit": 20
            }
        }

    project =  {
            "$project": {
                "imageVector": {"$slice": ["$imageVector", 5]},
                "imageFile": 1,
                "price": 1,
                "discountPercentage": 1,
                "averageRating" : 1,
                "_id": 0,
                'score': {'$meta': 'vectorSearchScore'}
            }
        }

    pipeline = [search, project]    
    results = list(collection.aggregate(pipeline))
    client.close()
    
    return results

@app.route('/advanced', methods=['GET', 'POST'])
def advanced():
    if request.method == 'POST':
        print(request.form)
        search_query = request.form['search_query']
        maxPrice = request.form.get('maxPrice')
        if maxPrice == '':
            maxPrice = 100.0
        minRating = request.form.get('minRating')
        if minRating == '':
            minRating = 1
        sortBy = request.form.get('sortBy')
        print('in post', search_query, maxPrice, minRating, sortBy)
        return redirect(url_for('advancedSearch',search_query=search_query, maxPrice=maxPrice, minRating=minRating, sortBy=sortBy))

    return render_template("advanced.html")

@app.route('/advancedSearch/<search_query>/<sortBy>/<float(signed=True):maxPrice>/<int(signed=True):minRating>', methods=['GET','POST'])
def advancedSearch(search_query, maxPrice, minRating, sortBy):
    print('advanced search query ', search_query, maxPrice, minRating, sortBy)
    results = run_advanced_query(search_query, maxPrice, minRating, sortBy)
    return render_template('advanced.html', results=results, search_query=search_query, maxPrice=maxPrice, minRating=minRating, sortBy=sortBy)

def run_advanced_query(search_query, maxPrice, minRating, sortBy):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    print('running query with', search_query, maxPrice, minRating, sortBy)
    # regular search with no filter
    search = {
            "$vectorSearch": {
                "index": "default",
                "path": "imageVector",
                "queryVector": model.encode(search_query).tolist(),
                "numCandidates": 200,
                "limit": 20,
                "filter": {
                    "$and": [{"price": {"$lt": maxPrice}},
                            {"averageRating": {"$gte": minRating}}
                    ]
                }
            }
        }
    # if (maxPrice != -1) and (minRating != -1):
    #     # Both maxPrice and minRating supplied
    #     search['$vectorSearch']['filter'] = {
    #                 "$and": [{"price": {"$lt": maxPrice}},
    #                         {"averageRating": {"$gte": minRating}}
    #                 ]
    #             }
    # elif (maxPrice != -1) and (minRating == -1):
    #     # Only maxPrice supplied
    #     search['$vectorSearch']['filter'] = {
    #                 "$and": [{"price": {"$lt": maxPrice}}]
    #             }
    # elif (maxPrice == -1) and (minRating != -1):
    #     # Only minRating supplied
    #     search['$vectorSearch']['filter'] = {
    #                 "$and": [{"averageRating": {"$gte": minRating}}]
    #             }
        
    project =  {
            "$project": {
                "imageVector": {"$slice": ["$imageVector", 5]},
                "imageFile": 1,
                "price": 1,
                "discountPercentage": 1,
                "averageRating" : 1,
                "_id": 0,
                'score': {'$meta': 'vectorSearchScore'}
            }
        }

    sortField = {"score": 1}

    if (sortBy=="price"):
        sortField = {"price":1}
    elif (sortBy=="rating"):
        sortField = {"averageRating":-1}
    
    sort = {"$sort": sortField}
    print(sort)
    pipeline = [search, project, sort]    
    results = list(collection.aggregate(pipeline))
    client.close()
    
    return results

if __name__ == '__main__':
    app.run(debug=True)
