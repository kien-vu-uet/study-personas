# Build the Docker image for the MCP Brainstorm with LLMs service
docker build -t mcp/brainstorm_with_llms:latest .

# Run the container with the necessary environment variables
docker run -d \
  --name mcp_brainstorm_with_llms \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  mcp/brainstorm_with_llms:latest fastmcp run main.py --transport=stdio --log-level=DEBUG
