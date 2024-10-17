# Dockerfile
FROM grafana/grafana:latest

# Set Grafana options
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_SECURITY_ADMIN_USER=admin
ENV GF_PATHS_PROVISIONING=/etc/grafana/provisioning

# Create directories for provisioning
RUN mkdir -p /etc/grafana/provisioning/datasources \
    && mkdir -p /etc/grafana/provisioning/dashboards

# Copy provisioning files if you have any
COPY datasources.yaml /etc/grafana/provisioning/datasources/
COPY dashboards.yaml /etc/grafana/provisioning/dashboards/

# Expose the Grafana port
EXPOSE 3000