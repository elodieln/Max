import React from 'react';
import { FiDownload, FiChevronsRight } from 'react-icons/fi';
import './CardViewer.css';

const CardViewer = ({ cardData, onDownload }) => {
  if (!cardData) {
    return (
      <div className="card-viewer">
        <div className="card-viewer-header">
          <h2>Prévisualisation de la fiche</h2>
        </div>
        <div className="card-viewer-body">
          <div className="card-viewer-placeholder">
            Générez une fiche pour la prévisualiser ici
          </div>
        </div>
      </div>
    );
  }

  const { cours, qcm } = cardData;

  return (
    <div className="card-viewer">
      <div className="card-viewer-header">
        <h2>{cours["Titre du cours"] || "Prévisualisation de la fiche"}</h2>
        <div className="card-viewer-header-actions">
          <button 
            className="card-viewer-header-button"
            onClick={onDownload}
            title="Télécharger la fiche"
          >
            <FiDownload size={18} />
          </button>
        </div>
      </div>
      <div className="card-viewer-body">
        {/* Description */}
        <div className="card-viewer-section">
          <h3 className="card-viewer-section-title">Description</h3>
          <p className="card-viewer-description">
            {cours["Description du cours"]}
          </p>
        </div>

        {/* Concepts clés */}
        <div className="card-viewer-section">
          <h3 className="card-viewer-section-title">Concepts clés</h3>
          <ul className="card-viewer-list">
            {(cours["Concepts clés"] || []).map((concept, index) => (
              <li key={index} className="card-viewer-list-item">
                <span className="card-viewer-list-item-bullet">•</span>
                <span>{concept}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Définitions et formules */}
        <div className="card-viewer-section">
          <h3 className="card-viewer-section-title">Définitions et formules</h3>
          <ul className="card-viewer-list">
            {(cours["Définitions et Formules"] || cours["Définition et formules"] || []).map((formule, index) => (
              <li key={index} className="card-viewer-list-item">
                <span className="card-viewer-list-item-bullet">•</span>
                <span>{formule}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Exemple concret */}
        <div className="card-viewer-section">
          <h3 className="card-viewer-section-title">Exemple concret</h3>
          <div className="card-viewer-example">
            <p>{cours["Exemple concret"]}</p>
          </div>
        </div>

        {/* Points clés */}
        <div className="card-viewer-section">
          <h3 className="card-viewer-section-title">Points clés</h3>
          <ul className="card-viewer-list">
            {(cours["Bullet points avec les concepts clés"] || cours["Les concepts clés"] || []).map((point, index) => (
              <li key={index} className="card-viewer-list-item">
                <span className="card-viewer-list-item-bullet">
                  <FiChevronsRight />
                </span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* QCM */}
        {qcm && qcm.questions && qcm.questions.length > 0 && (
          <div className="card-viewer-qcm">
            <h3 className="card-viewer-qcm-title">QCM pour tester vos connaissances</h3>
            
            {qcm.questions.map((question, index) => (
              <div key={index} className="card-viewer-question">
                <div className="card-viewer-question-title">
                  Question {question.numero}: {question.question}
                </div>
                
                <div className="card-viewer-choices">
                  {question.choix.map((choix, choixIndex) => (
                    <div key={choixIndex} className="card-viewer-choice">
                      <div className={`card-viewer-choice-bullet ${
                        choixIndex + 1 === parseInt(question.bonne_reponse) ? 'correct' : ''
                      }`}></div>
                      <div>{choix}</div>
                    </div>
                  ))}
                </div>
                
                <div className="card-viewer-explanation">
                  <div className="card-viewer-explanation-title">Explication:</div>
                  <p>{question.explication}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CardViewer;