# Use the official Python image from Docker Hub
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Copy the .env file into the container
COPY .env .env

# Set environment variables from the .env file
ENV $(cat .env | xargs)

# Install required Python packages
RUN pip install -r requirements.txt

# Expose the port your Flask app will run on
EXPOSE 5000

# Command to start your application
CMD ["python", "run.py"]