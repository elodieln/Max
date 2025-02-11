// backend/server.js
const express = require('express');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 5000;

app.use(express.json());  // Middleware pour analyser le corps de la requête (JSON)

app.post('/generate-pdf', async (req, res) => {
  const { question } = req.body;  // Récupérer la question de l'utilisateur

  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([600, 800]);
  const { width, height } = page.getSize();

  // Ajouter du texte dans le PDF
  page.drawText(`Question: ${question}`, { x: 50, y: height - 100, size: 18 });

  // Sauvegarder le PDF
  const pdfBytes = await pdfDoc.save();
  const pdfPath = path.join(__dirname, 'output', 'generated.pdf');
  fs.writeFileSync(pdfPath, pdfBytes);

  res.json({ pdfPath: `/pdfs/generated.pdf` });
});

// Route pour servir les fichiers PDF générés
app.use('/pdfs', express.static(path.join(__dirname, 'output')));

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
