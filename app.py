from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import uvicorn
import yaml
import os, signal
import logging
from traceback import format_exc

logging.basicConfig(level=logging.INFO, filename="report.log",filemode="a", format='%(asctime)s %(levelname)s %(message)s')

users = {}
tracks = []


def load_users_data() -> dict:
    try:
        with open('data/users.yml', 'r') as f:
            userdata = yaml.safe_load(f)
            if userdata:
                logging.info(f'User data loaded with users: {userdata.keys()}')
                return userdata
            else:
                logging.info('User data empty? Loaded')
                return {}
    except:
        logging.error(format_exc())
        return {}
        
def save_users_data(data: dict):
    with open('data/users.yml', 'w') as f:
        yaml.safe_dump(data, f)
        logging.info('Users data saved')

@asynccontextmanager
async def lifespan(app: FastAPI):
    global records
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data/tracks'):
        os.mkdir('data/tracks')

    users = load_users_data()
    save_users_data(users)

    yield


app = FastAPI(lifespan=lifespan)


@app.get('/records')
async def get_records(request: Request):
    return records

@app.post('/get_playlists')
async def get_playlists(request: Request):
    global users
    data = await request.json()
    if 'name' in data.keys() and 'pass' in data.keys():
        name = data['name']
        if name not in users.keys():
            users[name] = {
                'pass': data['pass'],
                'playlists': {
                    'Beloved': []
                }
            }
            save_users_data(users)
            return {'mes': 'OK', 'playlists': users[name]['playlists']}
        elif data['pass'] == users[name]['pass']:
            return {'mes': 'OK', 'playlists': users[name]['playlists']}
        else:
            return {'mes': 'Wrong pass'}     
    else:
        return {'mes': 'Bad request'}
    
@app.post('/add-to-playlist')
def add_to_playlist(request: Request):
    data = await request.json()
    if 'name' in data.keys() and 'pass' in data.keys():
    pass
        
@app.get('/kys')
def kill(request: Request):
    os.kill(os.getpid(), signal.SIGKILL)
    return {'mes': 'Ok, bye'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)