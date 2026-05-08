#!/usr/bin/env node
/**
 * Embedded embedding service using node-llama-cpp.
 * Drop-in replacement for llama-server :8080/embedding
 */
const http = require('http');
const {getLlama, LlamaEmbedding} = require('node-llama-cpp');

const MODEL_PATH = '/root/.node-llama-cpp/models/hf_ggml-org_embeddinggemma-300m-qat-Q8_0.gguf';
const PORT = 8080;

async function main() {
  console.log('Loading model...');
  const llama = await getLlama();
  const model = await llama.loadModel({modelPath: MODEL_PATH});
  const context = await model.createEmbeddingContext();
  console.log('Model loaded. Starting server on :' + PORT);

  const server = http.createServer(async (req, res) => {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Content-Type', 'application/json');

    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    // Health check
    if (req.method === 'GET' && (req.url === '/health' || req.url === '/')) {
      res.writeHead(200);
      res.end(JSON.stringify({status: 'ok', model: 'gemma-embedding-300m'}));
      return;
    }

    // Embedding endpoint
    if (req.method === 'POST' && (req.url === '/embedding' || req.url === '/v1/embeddings')) {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', async () => {
        try {
          const input = JSON.parse(body);
          const text = input.content || input.input || '';
          if (!text) {
            res.writeHead(400);
            res.end(JSON.stringify({error: 'Missing content'}));
            return;
          }

          const embedding = await context.getEmbeddingFor(text);
          const vector = Array.from(embedding.vector);

          // Support both /embedding and /v1/embeddings formats
          const isV1 = req.url === '/v1/embeddings';
          if (isV1) {
            res.writeHead(200);
            res.end(JSON.stringify({
              object: 'list',
              data: [{object: 'embedding', index: 0, embedding: vector}],
              model: 'gemma-embedding-300m',
            }));
          } else {
            res.writeHead(200);
            res.end(JSON.stringify({embedding: vector}));
          }
        } catch (err) {
          res.writeHead(500);
          res.end(JSON.stringify({error: err.message}));
        }
      });
      return;
    }

    res.writeHead(404);
    res.end(JSON.stringify({error: 'Not found'}));
  });

  server.listen(PORT, '0.0.0.0');
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
