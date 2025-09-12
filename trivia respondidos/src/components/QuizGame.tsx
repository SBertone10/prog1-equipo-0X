import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { ArrowLeft, Clock, Target } from 'lucide-react';
import { Question, Category, categories, getQuestionsByCategory } from './QuizData';

interface QuizGameProps {
  category: Category;
  onBack: () => void;
  onFinish: (score: number, total: number, category: Category) => void;
}

export function QuizGame({ category, onBack, onFinish }: QuizGameProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [timeLeft, setTimeLeft] = useState(30);
  const [isTimeUp, setIsTimeUp] = useState(false);

  useEffect(() => {
    const gameQuestions = getQuestionsByCategory(category, 10);
    setQuestions(gameQuestions);
  }, [category]);

  useEffect(() => {
    if (timeLeft > 0 && !showResult && !isTimeUp) {
      const timer = setTimeout(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !showResult) {
      setIsTimeUp(true);
      setShowResult(true);
    }
  }, [timeLeft, showResult, isTimeUp]);

  const handleAnswerSelect = (answerIndex: number) => {
    if (selectedAnswer !== null || isTimeUp) return;
    
    setSelectedAnswer(answerIndex);
    setShowResult(true);

    if (answerIndex === questions[currentQuestionIndex].correctAnswer) {
      setScore(score + 1);
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowResult(false);
      setTimeLeft(30);
      setIsTimeUp(false);
    } else {
      onFinish(score, questions.length, category);
    }
  };

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <h2 className="text-2xl">Preparando tu quiz...</h2>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const categoryInfo = categories[category];

  return (
    <div className={`min-h-screen bg-gradient-to-br ${categoryInfo.color.replace('from-', 'from-').replace('to-', 'to-')} bg-opacity-20 p-4`}>
      <div className="max-w-4xl mx-auto">
        {/* Header del juego */}
        <div className="flex items-center justify-between mb-6">
          <Button 
            variant="outline" 
            onClick={onBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Volver
          </Button>
          
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              {score}/{questions.length}
            </Badge>
            <Badge 
              variant={timeLeft <= 10 ? "destructive" : "secondary"}
              className="flex items-center gap-2"
            >
              <Clock className="w-4 h-4" />
              {timeLeft}s
            </Badge>
          </div>
        </div>

        {/* Progreso y categoría */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{categoryInfo.icon}</span>
              <div>
                <h2 className="text-xl">{categoryInfo.name}</h2>
                <p className="text-sm text-gray-600">
                  Pregunta {currentQuestionIndex + 1} de {questions.length}
                </p>
              </div>
            </div>
            <Badge variant="outline" className="text-sm">
              {currentQuestion.category}
            </Badge>
          </div>
          <Progress value={progress} className="h-3" />
        </div>

        {/* Tarjeta de pregunta */}
        <Card className="shadow-2xl border-2">
          <CardHeader className={`bg-gradient-to-r ${categoryInfo.color} text-white`}>
            <CardTitle className="text-2xl text-center">
              {currentQuestion.question}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="grid gap-4">
              {currentQuestion.options.map((option, index) => {
                let buttonVariant: "default" | "destructive" | "secondary" | "outline" = "outline";
                let additionalClasses = "";
                
                if (showResult) {
                  if (index === currentQuestion.correctAnswer) {
                    buttonVariant = "default";
                    additionalClasses = "bg-green-500 text-white border-green-500 hover:bg-green-600";
                  } else if (index === selectedAnswer && index !== currentQuestion.correctAnswer) {
                    buttonVariant = "destructive";
                  } else {
                    additionalClasses = "opacity-50";
                  }
                }

                return (
                  <Button
                    key={index}
                    onClick={() => handleAnswerSelect(index)}
                    variant={buttonVariant}
                    className={`w-full justify-start h-auto p-6 text-left text-lg transition-all duration-200 hover:scale-105 ${additionalClasses}`}
                    disabled={selectedAnswer !== null || isTimeUp}
                  >
                    <span className="mr-4 shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-800">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span className="flex-1">{option}</span>
                  </Button>
                );
              })}
            </div>

            {showResult && (
              <div className="mt-8 p-6 bg-gray-50 rounded-lg border-t-4 border-purple-500">
                <div className="text-center space-y-4">
                  {isTimeUp ? (
                    <div className="text-orange-600">
                      <div className="text-4xl mb-2">⏰</div>
                      <h3 className="text-xl">¡Se acabó el tiempo!</h3>
                      <p className="text-gray-600">
                        La respuesta correcta era: <strong>{currentQuestion.options[currentQuestion.correctAnswer]}</strong>
                      </p>
                    </div>
                  ) : selectedAnswer === currentQuestion.correctAnswer ? (
                    <div className="text-green-600">
                      <div className="text-4xl mb-2">🎉</div>
                      <h3 className="text-xl">¡Excelente!</h3>
                      <p className="text-gray-600">Respuesta correcta</p>
                    </div>
                  ) : (
                    <div className="text-red-600">
                      <div className="text-4xl mb-2">❌</div>
                      <h3 className="text-xl">No es correcto</h3>
                      <p className="text-gray-600">
                        La respuesta correcta era: <strong>{currentQuestion.options[currentQuestion.correctAnswer]}</strong>
                      </p>
                    </div>
                  )}
                  
                  <Button 
                    onClick={nextQuestion}
                    size="lg"
                    className={`bg-gradient-to-r ${categoryInfo.color} text-white px-8`}
                  >
                    {currentQuestionIndex < questions.length - 1 ? 'Siguiente Pregunta' : 'Ver Resultados'}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Indicador de tiempo visual */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-1000 ${
                timeLeft <= 10 ? 'bg-red-500' : timeLeft <= 20 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${(timeLeft / 30) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}