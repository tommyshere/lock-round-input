# Use the official Amazon Linux image as the base image
FROM public.ecr.aws/lambda/python:3.10

# Set environment variables to force AWS DNS resolution inside a VPC
ENV RES_OPTIONS="ndots:0"

# Install necessary system dependencies (CA certificates & curl for debugging)
RUN yum install -y ca-certificates curl && yum clean all

# Copy the rest of your application code to the container
COPY . .

# Copy and install the requirements.txt file to the container
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

RUN curl -v https://httpbin.org/get || echo "Outbound request failed"

# Set the entry point command for running your application
CMD ["handler.main"]

