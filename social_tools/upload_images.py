import os
from github import Github

g = Github('TOKEN')
repo = g.get_repo('username/project')
for img in os.listdir('imgs'):
    repo.create_file(f'images/{img}', f'Add {img}', open(f'imgs/{img}', 'rb').read())
