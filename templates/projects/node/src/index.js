const http = require("http");

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
    res.setHeader("Content-Type", "application/json");

    if (req.url === "/health") {
        res.writeHead(200);
        res.end(JSON.stringify({ status: "healthy" }));
        return;
    }

    res.writeHead(200);
    res.end(JSON.stringify({
        message: "Node.js application is running"
    }));
});

server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});