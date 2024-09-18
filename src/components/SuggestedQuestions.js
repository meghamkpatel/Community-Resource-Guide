import React from "react";

function SuggestedQuestions({ suggestedQuestions, onQuestionSelect }) {
  return (
    <div className="suggested-questions-container">
      {suggestedQuestions.map((question, index) => (
        <div
          key={index}
          className="suggested-question"
          onClick={() => onQuestionSelect(question)}
        >
          {question}
        </div>
      ))}
    </div>
  );
}

export default SuggestedQuestions;

