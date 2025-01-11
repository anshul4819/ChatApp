# RUN using 
# docker build -t messenger .
# docker run -p 3000:3000 messenger

FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install gunicorn and eventlet
RUN pip3 install gunicorn eventlet

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Since you are using Flask-SocketIO, you might need to use gunicorn with eventlet
# or gevent for the web server to handle websocket properly.
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:3000", "entrypoint:app"]