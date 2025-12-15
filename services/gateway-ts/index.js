const express = require("express");
const app = express();
app.use(express.json());

app.get("/", (_, res) =>
  res.json({ service: "InfinityX Gateway", status: "online" })
);

app.get("/health", (_, res) => res.json({ ok: true }));

app.post("/ingest", (req, res) => {
  res.json({ ok: true });
});

app.post("/query", (req, res) => {
  if (!req.body || !req.body.intent) {
    return res.status(400).json({
      error: "missing intent",
      example: { intent: "find_distressed_properties" }
    });
  }
  res.json({ result: "stubbed-response", confidence: 0.99 });
});

app.listen(8080, "0.0.0.0", () =>
  console.log("Gateway listening on 8080")
);
