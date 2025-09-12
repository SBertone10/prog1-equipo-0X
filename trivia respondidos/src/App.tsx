import { useState } from 'react';
import { CategorySelector } from './components/CategorySelector';
import { QuizGame } from './components/QuizGame';
import { QuizResults } from './components/QuizResults';
import { Category } from './components/QuizData';

type AppState = 'category-selection' | 'playing' | 'results';

export default function App() {
  const [appState, setAppState] = useState<AppState>('category-selection');
  const [selectedCategory, setSelectedCategory] = useState<Category>('todas');
  const [finalScore, setFinalScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);

  const handleCategorySelect = (category: Category) => {
    setSelectedCategory(category);
    setAppState('playing');
  };

  const handleQuizFinish = (score: number, total: number, category: Category) => {
    setFinalScore(score);
    setTotalQuestions(total);
    setSelectedCategory(category);
    setAppState('results');
  };

  const handlePlayAgain = () => {
    setAppState('playing');
  };

  const handleBackToCategories = () => {
    setAppState('category-selection');
  };

  if (appState === 'category-selection') {
    return <CategorySelector onSelectCategory={handleCategorySelect} />;
  }

  if (appState === 'playing') {
    return (
      <QuizGame
        category={selectedCategory}
        onBack={handleBackToCategories}
        onFinish={handleQuizFinish}
      />
    );
  }

  if (appState === 'results') {
    return (
      <QuizResults
        score={finalScore}
        total={totalQuestions}
        category={selectedCategory}
        onPlayAgain={handlePlayAgain}
        onBackToCategories={handleBackToCategories}
      />
    );
  }

  return null;
}