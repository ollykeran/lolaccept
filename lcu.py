from random import randint

from lcu_driver import Connector

connector = Connector()


# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')

    # check if the user is already logged into his account
    config = await connection.request('get','/lol-platform-config/v1/initial-configuration-complete')
    print(config.json)
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    print(summoner)
    game_state = await connection.request('get', '/lol-champ-select/v1/session/my-selection')
    print(game_state)
    response = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
    print(response.json)

# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    print('The client have been closed!')

# starts the connector
connector.start()