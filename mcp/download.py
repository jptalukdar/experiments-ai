import requests
import json

r1 = requests.get('https://api.semanticscholar.org/datasets/v1/release').json()
print(r1[-3:])
# ['2023-03-14', '2023-03-21', '2023-03-28']

r2 = requests.get('https://api.semanticscholar.org/datasets/v1/release/latest').json()
print(r2['release_id'])
# 2023-03-28

print(json.dumps(r2['datasets'][0], indent=2))
# {
#     "name": "abstracts",
#     "description": "Paper abstract text, where available. 100M records in 30 1.8GB files.",
#     "README": "Semantic Scholar Academic Graph Datasets The "abstracts" dataset provides..."
# }

r3 = requests.get('https://api.semanticscholar.org/datasets/v1/release/latest/dataset/abstracts').json()
print(json.dumps(r3, indent=2))
# {
#   "name": "abstracts",
#   "description": "Paper abstract text, where available. 100M records in 30 1.8GB files.",
#   "README": "Semantic Scholar Academic Graph Datasets The "abstracts" dataset provides...",
#   "files": [
#     "https://ai2-s2ag.s3.amazonaws.com/dev/staging/2023-03-28/abstracts/20230331_0..."
#   ]
# }