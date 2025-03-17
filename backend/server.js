// backend/server.js
import { Pinecone } from '@pinecone-database/pinecone';  // Utilisation de Pinecone pour la version la plus récente
import { AzureOpenAI } from 'openai/index.mjs';
import { OpenAI} from 'openai';
import express from 'express';
import dotenv from 'dotenv';
import PDFDocument from 'pdfkit';
import fs from 'fs';
import cors from 'cors';
import path from 'path';
import { PassThrough } from 'stream';
import { json } from 'stream/consumers';

// Charger les variables d'environnement depuis .env
dotenv.config();
const AZURE_API_KEY = process.env.AZURE_API_KEY;
const PINECONE_API_KEY = process.env.PINECONE_API_KEY;
const PINECONE_ENVIRONMENT = process.env.PINECONE_ENVIRONMENT;
const AZURE_ENDPOINTS = process.env.AZURE_ENDPOINTS;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

console.log(OPENAI_API_KEY);



// Inititaliser Azure OpenAI
const client = new AzureOpenAI ({
  endpoint: AZURE_ENDPOINTS,
  apiKey: AZURE_API_KEY,
  apiVersion: "2023-09-01-preview",
})

//Initialiser OpenRouter
const openai = new OpenAI ({
  apiKey: OPENAI_API_KEY,
  baseURL: "https://openrouter.ai/api/v1",
})

// Initialiser Pinecone
const pinecone = new Pinecone ({
  apiKey: PINECONE_API_KEY,
  //environment: PINECONE_ENVIRONMENT,
});

// Créer l'application Express et configurer les middlewares 
const app = express();
app.use(express.json());

// Configuration CORS
const corsOptions = {
  origin: 'http://localhost:5173',  // Remplace par l'URL de ton frontend
  methods: ['GET,POST'],
};
app.use(cors(corsOptions));

// Fonction pour récupérer les données pertinentes de Pinecone
async function getPineconeContext(question) {
  try {
    // Utiliser l'index Pinecone 
    const index = pinecone.Index('maxdataset');
    
    //Récupérer les embeddings depuis Azure Openai
    const embeddingResponse = await client.embeddings.create({
      input: question,
      model: "text-embedding-ada-002",
    });
    console.log("Full embeddings response :", embeddingResponse);
    
    //Extraire le tableau d'embedding
    const embedding = embeddingResponse.data[0].embedding;
    console.log('Embedding array', embedding);
    
    const query = {
      topK: 5,
      vector: embedding, // Récupère l'embedding de la question
      includeMetadata : true,
    };

    const response = await index.query(query);

    // Vérification si des correspondances ont été trouvées
    if (response.matches.length === 0) {
      console.log("Aucune correspondance trouvée dans Pinecone.");
      return "Désolé, nous n'avons pas pu trouver d'informations pertinentes. Veuillez reformuler votre question.";
    }

    const context = response.matches.map(match => match.metadata.text).join('\n');
    console.log('Le contexte : ',context);
    return context;
  } catch (error) {
    console.error('Erreur Pinecone:', error);
    return 'Désolé, il y a eu une erreur lors de la recherche d\'informations.';
  }
}

// Fonction utilitaire pour écrire un titre souligné
function writeUnderlinedTitle(doc, title, options = {}) {
  doc.font('Helvetica-Bold').fontSize(16).text(title, options);
  // Dessiner une ligne sous le titre
  const textWidth = doc.widthOfString(title);
  const x = doc.x;
  const y = doc.y;
  doc.moveTo(x, y).lineTo(x + textWidth, y).strokeColor('#000').lineWidth(1).stroke();
  doc.moveDown(0.5);
}

// Fonction pour générer un PDF à partir du JSON de ChatGPT
function generatePDF(jsonData) {
  const doc = new PDFDocument({autoFirstPage: false, margin: 50});

  // Générer le contenu du PDF
  doc.addPage();
  // Ajout du titre
  doc.font('Helvetica-Bold').fontSize(18).text(`Fiche : ${jsonData.cours["Titre du cours"]}`, { align: 'center' });
  doc.moveDown(1);

  // Ajout du contenu du cours
  //doc.font('Helvetica').fontSize(12).text(`Titre du cours: ${jsonData.cours["Titre du cours"]}`);
  writeUnderlinedTitle(doc, 'Description');
  doc.font('Helvetica').fontSize(12).text(jsonData.cours["Description du cours"], {indent: 20 });
  doc.moveDown(1);

  writeUnderlinedTitle(doc, 'Concepts clés');
  const concepts = jsonData.cours["Concepts clés"] || [];
  concepts.forEach(item => {
    doc.font('Helvetica').fontSize(12).text(`• ${item}`, { indent: 30 });
  });
  doc.moveDown(1);
  
  writeUnderlinedTitle(doc, 'Définitions et formules');
  const defFormules = jsonData.cours["Définitions et Formules"] || jsonData.cours["Définition et formules"] || [];
  defFormules.forEach(item => {
    doc.font('Helvetica').fontSize(12).text(`• ${item}`, { indent: 30 });
  });
  doc.moveDown(1);

  writeUnderlinedTitle(doc, 'Exemple concret');
  doc.font('Helvetica').fontSize(12).text(jsonData.cours["Exemple concret"], {indent:20});
  doc.moveDown(1);

  writeUnderlinedTitle(doc, 'Points clés');
  const bulletPoints =jsonData.cours["Bullet points avec les concepts clés"] || jsonData.cours["Les concepts clés"] || [];
  bulletPoints.forEach(item => {
    doc.font('Helvetica').fontSize(12).text(`• ${item}`, { indent: 30 });
  })
  doc.moveDown(2);

  // Ajout du QCM
  doc.addPage();
  doc.font('Helvetica-Bold').fontSize(14).text('QCM');
  doc.moveDown(1);
  doc.font('Helvetica').fontSize(12);

  jsonData.qcm.questions.forEach((question, idx) => {
    doc.font('Helvetica-Bold').fontSize(12).text(`Question ${question.numero} : ${question.question}`, {indent: 10});
    doc.moveDown(0.2);

    doc.font('Helvetica').fontSize(12);
    question.choix.forEach((choix, index) => {
      doc.text(`${index + 1}. ${choix}`, {indent:20});
    });
    doc.moveDown(0.2);

    doc.text(`Bonne réponse: ${question.bonne_reponse}`, {indent:10});
    doc.moveDown(0.2);
    doc.text(`Explication: ${question.explication || question.explication || ''}`, {indent:10});
    doc.moveDown(1);

    // Séparateur entre les questions
    if (idx !== jsonData.qcm.questions.length - 1) {
      doc.moveTo(doc.page.margins.left, doc.y)
         .lineTo(doc.page.width - doc.page.margins.right, doc.y)
         .strokeColor('#cccccc')
         .lineWidth(0.5)
         .stroke();
      doc.moveDown(0.5);
    }

  });

  // Finalisation du PDF
  doc.end();
  return doc;
}


//Endpoint pour générer le PDF
app.post('/generate-pdf', async (req, res) => {
  console.log('req.body =', req.body);
  const { question } = req.body;

  try {
    // 1. Récupérer les informations depuis Pinecone
    const context = await getPineconeContext(question);

     // Si le contexte est une erreur, retourner directement cette erreur
     if (context.startsWith("Désolé") || context.startsWith("Aucune correspondance")) {
      return res.status(400).json({ success: false, message: context });
    }

    // 2. Préparer le prompt structuré
    const prompt = `
      Vous êtes un assistant expert en électronique, capable de fournir des explications détaillées et de suivre les instructions données pour formater les réponses de manière précise.

      Contexte: ${context}
      Question: ${question}

      Générer une fiche complète pour un cours d'électronique ainsi qu'un QCM en retournant un JSON structuré comme suit:
      {
        "cours": {
          "Titre du cours": "",
          "Description du cours": "",
          "Concepts clés": [],
          "Définitions et Formules": [],
          "Exemple concret": "",
          "Bullet points avec les concepts clés": []
        },
        "qcm": {
          "questions": [
            {
              "numero": 1,
              "question": "",
              "choix": [],
              "bonne_reponse": "",
              "explication": ""
            }
          ]
        }
      }

      Règles à suivre:
      - Respectez exactement les noms des champs
      - Les autres champs doivent contenir des chaînes simples
      - Formater les formules de manière simple
      - Assurez-vous que la réponse est strictement au format JSON valide
      - Ne mets pas de backticks ou de code block dans ta réponse.
      - Ta réponse doit être strictement au format JSON valide, sans texte supplémentaire.
    `;

    const response = await openai.chat.completions.create({
      model: 'google/gemini-2.0-flash-001',
      messages: [{ role: 'system', content: prompt }],
    });
    let completionText = response.choices[0].message.content;
    console.log('==== Completion TEXT ====');
    

    //supprimer les occurenres de ``` et ```json
    completionText = completionText.replace(/```(\w+)?/g, '').replace(/```/g, '');
    console.log(completionText);

    const jsonData =  JSON.parse(completionText);
    
    //générer le PDF
    const doc = generatePDF(jsonData);

    //configurer l'en tete pour forcer le telechargement
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="Fiche_cours.pdf"`);
    
    //envoyer le pdf en streaming
    doc.pipe(res);

    doc.on('error', (err) => {
      console.error('Erreur de génération PDF:', err);
      return res.status(500).send('Erreur lors de la génération du PDF.');
    });

  } catch (error) {
    console.error('Erreur lors de la génération du PDF:', error);
    res.status(500).send('Erreur lors de la génération du PDF.');
  }
});


// Lancer le serveur
app.listen(5001, () => {
  console.log('Serveur démarré sur http://localhost:5001');
  });
