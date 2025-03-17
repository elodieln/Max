// backend/server.js
import { Pinecone } from '@pinecone-database/pinecone';  // Utilisation de Pinecone pour la version la plus récente
import { AzureOpenAI } from 'openai/index.mjs';
import { OpenAI} from 'openai';
import express from 'express';
import dotenv from 'dotenv';
import puppeteer from 'puppeteer';
import fs from 'fs';
import Handlebars from 'handlebars'; // Pour le templating
import { PassThrough } from 'stream';
import cors from 'cors';
import path from 'path';
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

async function generatePDF(jsonData) {
  // Transformer les noms de propriétés pour Handlebars
  const transformedData = {
    cours: {
      Titre_du_cours: jsonData.cours["Titre du cours"],
      Description_du_cours: jsonData.cours["Description du cours"],
      Concepts_cles: jsonData.cours["Concepts clés"],
      Definitions_et_Formules: jsonData.cours["Définitions et Formules"] || jsonData.cours["Définition et formules"],
      Exemple_concret: jsonData.cours["Exemple concret"],
      Points_cles: jsonData.cours["Bullet points avec les concepts clés"] || jsonData.cours["Les concepts clés"]
    },
    qcm: jsonData.qcm,
    dateGeneration: new Date().toLocaleDateString('fr-FR')
  };
  
  // Lire le template HTML
  const templateSource = fs.readFileSync('./templates/fiche-template.html', 'utf8');
  
  // Compiler le template avec Handlebars
  const template = Handlebars.compile(templateSource);
  
  // Ajouter un helper pour comparer des valeurs (pour les réponses QCM)
  Handlebars.registerHelper('eq', function (a, b) {
    return parseInt(a) + 1 === parseInt(b);
  });
  
  // Générer le HTML avec les données transformées
  const html = template(transformedData);
  
  // Lancer Puppeteer
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  // Définir le contenu HTML
  await page.setContent(html, { waitUntil: 'networkidle0' });
  
  // Injecter un script pour gérer la pagination
  await page.evaluate(() => {
    // Obtenir toutes les pages
    const contentPages = document.querySelectorAll('.content-page, .qcm-page');
    
    // Mettre à jour les numéros de page
    contentPages.forEach((contentPage, index) => {
      const footer = contentPage.querySelector('.footer') || document.createElement('div');
      footer.textContent = `Page ${index + 1} sur ${contentPages.length}`;
    });
  });
  
  // Générer le PDF
  const pdfBuffer = await page.pdf({
    format: 'A4',
    printBackground: true,
    margin: {
      top: '20mm',
      right: '20mm',
      bottom: '20mm',
      left: '20mm'
    }
  });
  
  // Fermer le navigateur
  await browser.close();
  
  // Créer un stream
  const stream = new PassThrough();
  stream.end(pdfBuffer);
  
  return stream;
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

    const jsonData = JSON.parse(completionText);
    
    //générer le PDF
    const pdfStream = await generatePDF(jsonData);

    //configurer l'en tete pour forcer le telechargement
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="Fiche_cours.pdf"`);
    
    //envoyer le pdf en streaming
    pdfStream.pipe(res);

  } catch (error) {
    console.error('Erreur lors de la génération du PDF:', error);
    res.status(500).send('Erreur lors de la génération du PDF.');
  }
});

// Ajouter cet endpoint à server.js
app.post('/generate-card-data', async (req, res) => {
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
    
    // Supprimer les occurrences de ``` et ```json
    completionText = completionText.replace(/```(\w+)?/g, '').replace(/```/g, '');
    console.log(completionText);

    const jsonData = JSON.parse(completionText);
    
    // Renvoyer les données JSON
    res.status(200).json({ 
      success: true, 
      data: jsonData 
    });

  } catch (error) {
    console.error('Erreur lors de la génération des données:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Erreur lors de la génération des données.', 
      error: error.message 
    });
  }
});


// Lancer le serveur
app.listen(5001, () => {
  console.log('Serveur démarré sur http://localhost:5001');
  });
