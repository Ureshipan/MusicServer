from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import yaml
import os, signal
import logging
from traceback import format_exc
from mutagen.easyid3 import EasyID3

logging.basicConfig(level=logging.INFO, filename="report.log",filemode="a", format='%(asctime)s %(levelname)s %(message)s')

users = {}
tracks = {}


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

def load_tracks_metadata() -> dict:
    out_tracks = {}
    if os.path.exists('data/tracks'):
        for filename in os.listdir('data/tracks'):
            if '.mp3' in filename:
                path = 'data/tracks/' + filename
                track = EasyID3(path)
                if len(track['title']) > 0:
                    out_tracks[track['title'][0]] = path
                else:
                    out_tracks[filename] = path
    return out_tracks

def encode(input_string):
    return '-'.join(str(ord(char)) for char in input_string)


def decode(encoded_string):
    return ''.join(chr(int(code)) for code in encoded_string.split('-'))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global users, tracks
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data/tracks'):
        os.mkdir('data/tracks')

    users = load_users_data()
    save_users_data(users)
    tracks = load_tracks_metadata()

    yield


app = FastAPI(lifespan=lifespan)


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
        if data['pass'] == users[name]['pass']:
            return JSONResponse({'mes': 'OK', 'playlists': {**dict(All=list(tracks.keys())), **users[name]['playlists']}})
        else:
            return JSONResponse({'mes': 'Wrong pass'}, status_code=400)
    else:
        return JSONResponse({'mes': 'Bad request'}, status_code=400)
    
@app.post('/add-to-playlist')
async def add_to_playlist(request: Request):
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
        if data['pass'] == users[name]['pass']:
            if 'song' in data.keys():
                if 'playlist' in data.keys():
                    if data['playlist'] in users[name]['playlists']:
                        users[name]['playlists'][data['playlist']].append(data['song'])
                        save_users_data(users)
                        logging.info(f'Song "{data['song']}" added to playlist "{data['playlist']}" by user {name}')
                        return JSONResponse({'mes': 'OK'})
                    else:
                        logging.info(f'User {name} tryed to add song "{data['song']}" to non-existed playlist')
                        return JSONResponse({'mes': 'Playlist doesnt exist'}, status_code=400)
                else:
                    logging.info(f'User {name} tryed to add song "{data['song']}" without playlist')
                    return JSONResponse({'mes': 'Playlist doesnt specified in request'}, status_code=400)
            else:
                logging.info(f'User {name} tryed to add song without song name')
                return JSONResponse({'mes': 'Song doesnt specified in request'}, status_code=400)
        else:
            logging.info(f'User {name} tryed add song with wrong pass')
            return JSONResponse({'mes': 'Wrong pass'}, status_code=400)
    else:
        return JSONResponse({'mes': 'Bad request'}, status_code=400)


@app.post('/delete-from-playlist')
async def delete_from_playlist(request: Request):
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
            return JSONResponse({'mes': 'Bro you are new user'}, status_code=400)
        if data['pass'] == users[name]['pass']:
            if 'song' in data.keys():
                if 'playlist' in data.keys():
                    if data['playlist'] in users[name]['playlists']:
                        if data['song'] in users[name]['playlists'][data['playlist']]:
                            users[name]['playlists'][data['playlist']].remove(data['song'])
                            save_users_data(users)
                            logging.info(f'Song "{data['song']}" deleted from playlist "{data['playlist']}" by user {name}')
                            return JSONResponse({'mes': 'OK'})
                        else:
                            logging.info(f'User {name} tryed to delete song "{data['song']}" from playlist "{data['playlist']}" but there is no that song')
                            return JSONResponse({'mes': 'Song is not in that playlist'}, status_code=404)
                    else:
                        logging.info(f'User {name} tryed to add song "{data['song']}" to non-existed playlist')
                        return JSONResponse({'mes': 'Playlist doesnt exist'}, status_code=400)
                else:
                    logging.info(f'User {name} tryed to add song "{data['song']}" without playlist')
                    return JSONResponse({'mes': 'Playlist doesnt specified in request'}, status_code=400)
            else:
                logging.info(f'User {name} tryed to add song without song name')
                return JSONResponse({'mes': 'Song doesnt specified in request'}, status_code=400)
        else:
            logging.info(f'User {name} tryed add song with wrong pass')
            return JSONResponse({'mes': 'Wrong pass'}, status_code=400)
    else:
        return JSONResponse({'mes': 'Bad request'}, status_code=400)


@app.post('/create-playlist')
async def create_playlist(request: Request):
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
        if data['pass'] == users[name]['pass']:
            if 'playlist' in data.keys():
                if data['playlist'] not in users[name]['playlists']:
                    users[name]['playlists'][data['playlist']] = []
                    save_users_data(users)
                    return JSONResponse({'mes': 'OK'})
                else:
                    return JSONResponse({'mes': 'Playlist already exists'}, status_code=400)
            else:
                return JSONResponse({'mes': 'Playlist dont specified'}, status_code=400)
        else:
            return JSONResponse({'mes': 'Wrong pass'}, status_code=400)
    else:
        return JSONResponse({'mes': 'Bad request'}, status_code=400)


@app.post('/delete-playlist')
async def delete_playlist(request: Request):
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
        if data['pass'] == users[name]['pass']:
            if 'playlist' in data.keys():
                if data['playlist'] in users[name]['playlists']:
                    users[name]['playlists'].pop(data['playlist'])
                    save_users_data(users)
                    return JSONResponse({'mes': 'OK'})
                else:
                    return JSONResponse({'mes': 'Playlist doesnt exist'}, status_code=404)
            else:
                return JSONResponse({'mes': 'Playlist dont specified'}, status_code=400)
        else:
            return JSONResponse({'mes': 'Wrong pass'}, status_code=400)
    else:
        return JSONResponse({'mes': 'Bad request'}, status_code=400)


@app.get('/get_song/{song_id}')
async def get_song(song_id: str):
    if decode(song_id) in tracks.keys():
        return FileResponse(tracks[decode(song_id)])
    else:
        return JSONResponse({'mes': 'No such track'}, status_code=404)



@app.get('/kys')
def kill(request: Request):
    os.kill(os.getpid(), signal.SIGKILL)
    return JSONResponse({'mes': 'Ok, bye'})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)