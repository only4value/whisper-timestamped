# Use the official Python image as the base image
FROM python:3.8

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -c "import whisper; whisper.load_model('base', device='cpu')"

# Copy the current directory contents into the container at /app
COPY . /app/

# # Make port 3000 available to the world outside this container
# EXPOSE 3000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
