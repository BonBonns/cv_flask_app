# Set environment variables


# Set environment variables


# Set the working directory in the container
FROM python:3.8-slim

# Set the PATH variable to include additional directories
ENV PATH="/usr/local/bin:${PATH}"

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python3", "./app.py"]



