#!/usr/bin/env node
/**
 * Embedding server using node-llama-cpp (ESM)
 * Provides /embedding endpoint on port 8080
 */
import http from 'node:http';
import {getLlama} from 'node-llama-cpp';

const MODEL_PATH = '/root/.node-llama-cpp/models/hf_ggml-org_embeddinggemma-300m-qat-Q8_0.gguf';
const PORT = 8080;

console.log('Loading model from', MODEL_PATH);
const llama = await getLlama();
const model = await llama.loadModel({modelPath: MODEL_PATH});
const context = await model.createEmbeddingContext();
console.log('Model loaded. Starting server on :' + PORT);

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === 'GET' && (req.url === '/health' || req.url === '/')) {
    res.writeHead(200);
    res.end(JSON.stringify({status: 'ok', model: 'gemma-embedding-300m'}));
    return;
  }

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
