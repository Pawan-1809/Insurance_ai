# Deployment Guide

This guide covers different deployment options for the LLM-Powered Intelligent Query-Retrieval System.

## Local Development

### Prerequisites
- Python 3.8+
- pip
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Insurance_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your OpenAI API key

# Run startup script
python start.py
```

## Docker Deployment

### Local Docker
```bash
# Build the image
docker build -t hackrx-system .

# Run the container
docker run -p 8000:8000 --env-file .env hackrx-system
```

### Docker Compose
Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_URL=${POSTGRES_URL}
      - HACKRX_TOKEN=${HACKRX_TOKEN}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment

### Railway
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `POSTGRES_URL` (Railway provides PostgreSQL)
   - `HACKRX_TOKEN`
3. Deploy automatically on push

### Render
1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENAI_API_KEY`
   - `POSTGRES_URL`
   - `HACKRX_TOKEN`

### Heroku
1. Create a new Heroku app
2. Add PostgreSQL addon
3. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set HACKRX_TOKEN=your_token
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

## Production Considerations

### Environment Variables
Ensure these are set in production:
- `OPENAI_API_KEY`: Your OpenAI API key
- `POSTGRES_URL`: Database connection string
- `HACKRX_TOKEN`: Authentication token
- `LOG_LEVEL`: Set to INFO or WARNING for production

### Database Setup
For production, use PostgreSQL:
```bash
# Example PostgreSQL URL
POSTGRES_URL=postgresql://username:password@host:port/database
```

### Security
- Use strong, unique tokens
- Enable HTTPS in production
- Set up proper firewall rules
- Monitor API usage and costs

### Monitoring
- Set up health checks: `GET /health`
- Monitor application logs
- Set up error tracking (e.g., Sentry)
- Monitor OpenAI API usage

### Scaling
- Use multiple workers with Gunicorn
- Set up load balancing
- Consider using Redis for caching
- Monitor FAISS index size

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Verify the key is correct
   - Check account has sufficient credits
   - Ensure key has proper permissions

2. **Database Connection Error**
   - Verify database URL format
   - Check network connectivity
   - Ensure database is running

3. **FAISS Index Issues**
   - Check disk space
   - Verify file permissions
   - Restart application if index is corrupted

4. **Memory Issues**
   - Monitor FAISS index size
   - Consider using smaller chunk sizes
   - Implement index cleanup

### Logs
Check application logs for detailed error information:
```bash
# Docker logs
docker logs <container_id>

# Application logs
tail -f app.log
```

## Performance Optimization

### FAISS Index
- Use appropriate index type for your use case
- Consider using GPU-accelerated FAISS for large datasets
- Implement index compression

### Document Processing
- Optimize chunk size and overlap
- Use async processing for large documents
- Implement caching for processed documents

### API Response
- Set appropriate timeouts
- Implement request rate limiting
- Use connection pooling for database

## Backup and Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump $POSTGRES_URL > backup.sql

# SQLite backup
cp hackrx.db hackrx.db.backup
```

### FAISS Index Backup
```bash
# Backup index files
cp faiss_index.index faiss_index.index.backup
cp faiss_index_metadata.pkl faiss_index_metadata.pkl.backup
```

### Recovery
1. Restore database from backup
2. Restore FAISS index files
3. Restart application

## Support

For deployment issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Test with the provided test script: `python test_system.py`
4. Check the README.md for additional information 