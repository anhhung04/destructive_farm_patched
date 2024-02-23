import os
CONFIG = {
    # Don't forget to remove the old database (flags.sqlite) before each competition.

    # The clients will run sploits on TEAMS and
    # fetch FLAG_FORMAT from sploits' stdout.
    'TEAMS': {'Team #{}'.format(i): os.getenv("FORMAT_URL", "10.10.0.%s") % i for i in range(1, 29 + 1)},
    'FLAG_FORMAT': os.getenv("FLAG_FORMAT", "[a-zA-Z0-9]{31}="),

    # This configures how and where to submit flags.
    # The protocol must be a module in protocols/ directory.

    # 'SYSTEM_PROTOCOL': 'ructf_tcp',
    # 'SYSTEM_HOST': '127.0.0.1',
    # 'SYSTEM_PORT': 31337,

    'SYSTEM_PROTOCOL': 'ructf_http',
    'SYSTEM_URL': f'http://{os.getenv("SCOREBOARD_URL","google.com")}/flags',
    'SYSTEM_TOKEN': f'{os.getenv("SYSTEM_TOKEN","your_secret_token")}',

    # 'SYSTEM_PROTOCOL': 'volgactf',
    # 'SYSTEM_HOST': '127.0.0.1',

    # 'SYSTEM_PROTOCOL': 'forcad_tcp',
    # 'SYSTEM_HOST': '127.0.0.1',
    # 'SYSTEM_PORT': 31337,
    # 'TEAM_TOKEN': 'your_secret_token',

    # The server will submit not more than SUBMIT_FLAG_LIMIT flags
    # every SUBMIT_PERIOD seconds. Flags received more than
    # FLAG_LIFETIME seconds ago will be skipped.
    'SUBMIT_FLAG_LIMIT': int(os.getenv("SUBMIT_FLAG_LIMIT", 10)),
    'SUBMIT_PERIOD': int(os.getenv("SUBMIT_PERIOD", 10)),
    'FLAG_LIFETIME': int(os.getenv("FLAG_LIFETIME", 60)),
    'TICK_PERIOD': int(os.getenv("TICK_PERIOD", 1)),

    # Password for the web interface. You can use it with any login.
    # This value will be excluded from the config before sending it to farm clients.
    'SERVER_PASSWORD': os.getenv("SERVER_PASSWORD", "1234"),

    # Use authorization for API requests
    'ENABLE_API_AUTH': False,
    'API_TOKEN': '00000000000000000000'
}
