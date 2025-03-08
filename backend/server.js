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

// Charger les variables d'environnement depuis .env
dotenv.config();
const AZURE_API_KEY = process.env.AZURE_API_KEY;
const PINECONE_API_KEY = process.env.PINECONE_API_KEY;
const PINECONE_ENVIRONMENT = process.env.PINECONE_ENVIRONMENT;
const AZURE_ENDPOINTS = process.env.AZURE_ENDPOINTS;
const OPENAI_APY_KEY = process.env.OPENAI_APY_KEY;

// Inititaliser Azure OpenAI
const client = new AzureOpenAI ({
  endpoint: AZURE_ENDPOINTS,
  apiKey: AZURE_API_KEY,
  apiVersion: "2023-09-01-preview",
})

//Initialiser OpenRouter
const openai = new OpenAI ({
  apiKey: OPENAI_APY_KEY,
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

// Fonction pour générer un PDF à partir du JSON de ChatGPT
function generatePDF(jsonData) {
  const doc = new PDFDocument({autoFirstPage: false});
  ////////////////////////////////a enlever 
  //const pdfPath = './generated_fiche.pdf'; // Chemin temporaire pour le PDF
  //doc.pipe(fs.createWriteStream(pdfPath));

  // Générer le contenu du PDF
  doc.addPage();
  // Ajout du titre
  doc.fontSize(18).text('Fiche de Révision', { align: 'center' });
  doc.moveDown();

  // Ajout du contenu du cours
  doc.fontSize(12).text(`Titre du cours: ${jsonData.cours["Titre du cours"]}`);
  doc.text(`Description: ${jsonData.cours["Description du cours"]}`);
  doc.text(`Concepts clés: ${jsonData.cours["Concepts clés"].join(', ')}`);
  doc.text(`Définition et formules: ${jsonData.cours["Définitions et Formules"].join(', ')}`);
  doc.text(`Exemple concret: ${jsonData.cours["Exemple concret"]}`);
  doc.text(`Points clés: ${jsonData.cours["Bullet points avec les concepts clés"].join(', ')}`);
  doc.moveDown();

  // Ajout du QCM
  doc.fontSize(14).text('QCM:');
  jsonData.qcm.questions.forEach((question) => {
    doc.fontSize(12).text(`Question ${question.numero}: ${question.question}`);
    question.choix.forEach((choix, index) => {
      doc.text(`${index + 1}. ${choix}`);
    });
    doc.text(`Bonne réponse: ${question.bonne_reponse}`);
    doc.text(`Explication: ${question.explication}`);
    doc.moveDown();
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

    // 3. Envoyer le prompt à ChatGPT pour obtenir le JSON
    /*//////////////////////////////////////////////////////// VERSION AZURE////////////////
    const response = await client.completions.create({
      deployment:'gpt-4',
      prompt: prompt,
      
    });
    
    //convertir la réponse en JSON
    const jsonData = JSON.parse(response.choices[0].text);*/

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
    res.setHeader('Content-Disposition', 'attachment; filename="fiche_cours.pdf"');
    
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
app.listen(5000, () => {
  console.log('Serveur démarré sur http://localhost:5000');
  });
