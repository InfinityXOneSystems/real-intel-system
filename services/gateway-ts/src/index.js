import http from 'http';

const port = process.env.PORT || 8080;

http.createServer((_, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ service: 'gateway', status: 'alive' }));
}).listen(port);

console.log('Gateway running on port', port);
