const express = require('express');
const app = express();
const path = require('path');

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Route principale
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Démarrer le serveur
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Serveur actif sur http://localhost:${PORT}`);
});
