# gunicorn_config.py

# The IP address to bind
bind = '0.0.0.0:5000'

# The number of worker processes for handling requests
workers = 4

# The number of threads for handling requests
threads = 2

# The timeout for workers
timeout = 120

