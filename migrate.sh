#!/bin/bash

# Run django migrations
python manage.py migrate

# Start FastAPI app
python manage.py runserver