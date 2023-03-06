FROM ubuntu:20.04

# Install necessary packages
RUN apt-get update && \
    apt-get install -y tpm2-tools python3-flask

# Copy the Flask app to the container
COPY app.py /

# Expose port 5000 for Flask app
EXPOSE 5000

# Run the Flask app
CMD ["python3", "/app.py"]
