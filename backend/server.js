// backend/server.js
import { Pinecone } from '@pinecone-database/pinecone';  // Utilisation de Pinecone pour la version la plus récente
import { OpenAI } from 'openai';  // Importation de OpenAI
import express from 'express';
import dotenv from 'dotenv';
import PDFDocument from 'pdfkit';
import fs from 'fs';
import cors from 'cors';
import path from 'path';


// Charger les variables d'environnement depuis .env
dotenv.config();
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const PINECONE_API_KEY = process.env.PINECONE_API_KEY;
const PINECONE_ENVIRONMENT = process.env.PINECONE_ENVIRONMENT;

// Initialiser OpenAI API
const openai = new OpenAI({
  apiKey: OPENAI_API_KEY,
  model: "gpt-4-0125-preview", 
});

// Initialiser Pinecone
const pinecone = new Pinecone ({
  apiKey: PINECONE_API_KEY,
  //environment: PINECONE_ENVIRONMENT,
})


// Créer l'application Express et configurer les middlewares 
const app = express();
app.use(express.json());

// Configuration CORS
const corsOptions = {
  origin: 'http://localhost:5179',  // Remplace par l'URL de ton frontend
  methods: 'GET,POST',
};
app.use(cors(corsOptions));


// Fonction pour récupérer les embeddings depuis OpenAI
async function getEmbeddings(text) {
  try {
    const response = await openai.embeddings.create({
      model: 'text-embedding-ada-002', // Modèle d'OpenAI pour les embeddings
      input: text,
    });
    return response.data.data[0].embedding; // Récupère l'embedding du texte
  } catch (error) {
    console.error("Erreur lors de la récupération des embeddings:", error);
    throw error;
  }
}

// Fonction pour récupérer les données pertinentes de Pinecone
async function getPineconeContext(question) {
  try {
    // Utiliser l'index Pinecone 
    const index = pinecone.Index('maxdataset');
    const query = {
      vector: await getEmbeddings(question), // Récupère l'embedding de la question
      top_k: 3, // Nombre de résultats à retourner
      include_values: true,
      include_metadata: true,
    };

    const response = await index.query(query);

    // Vérification si des correspondances ont été trouvées
    if (response.matches.length === 0) {
      console.log("Aucune correspondance trouvée dans Pinecone.");
      return "Désolé, nous n'avons pas pu trouver d'informations pertinentes. Veuillez reformuler votre question.";
    }

    const context = response.matches.map(match => match.metadata.text).join('\n');
    return context;
  } catch (error) {
    console.error('Erreur Pinecone:', error);
    return 'Désolé, il y a eu une erreur lors de la recherche d\'informations.';
  }
}

// Fonction pour générer un PDF à partir du JSON de ChatGPT
function generatePDF(jsonData, res) {
  const doc = new PDFDocument();
  const pdfPath = './generated_fiche.pdf'; // Chemin temporaire pour le PDF
  doc.pipe(fs.createWriteStream(pdfPath));

  // Générer le contenu du PDF
  // Ajout du titre
  doc.fontSize(18).text('Fiche de Révision', { align: 'center' });
  doc.moveDown();

  // Ajout du contenu du cours
  doc.fontSize(12).text(`Titre du cours: ${jsonData.cours["Titre du cours"]}`);
  doc.text(`Description: ${jsonData.cours["Description du cours"]}`);
  doc.text(`Concepts clés: ${jsonData.cours["Concepts clés"].join(', ')}`);
  doc.text(`Définition et formules: ${jsonData.cours["Définitions et formules"].join(', ')}`);
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
    doc.text(`Explication: ${question.explanation}`);
    doc.moveDown();
  });

  // Finalisation du PDF
  doc.end();
}


//Endpoint pour générer le PDF
app.post('/generate-pdf', async (req, res) => {
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
    `;

    // 3. Envoyer le prompt à ChatGPT pour obtenir le JSON
    const response = await openai.chat.completions.create({
      model: 'gpt-4-0125-preview',
      messages: [{ role: 'system', content: prompt }],
    });
    
    //convertir la réponse en JSON
    const jsonData = JSON.parse(responseAI.choices[0].message.content);
    
    //générer le PDF
    generatePDF(jsonData, res);

    //envoi du pdf en telechargement
    res.download('generated_fiche.pdf', 'fiche_cours.pdf', (err) => {
      if (err) {
        console.error('Erreur lors de l\'envoi du PDF:', err);
        res.status(500).send('Erreur lors de l\'envoi du PDF');
      }
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
