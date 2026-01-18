const functions = require("firebase-functions");
exports.health = functions.https.onRequest((req, res) => res.json({ ok: true }));
