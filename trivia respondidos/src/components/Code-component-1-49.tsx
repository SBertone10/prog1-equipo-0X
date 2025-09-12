import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Trophy, RotateCcw, Home, Star } from 'lucide-react';
import { Category, categories } from './QuizData';

interface QuizResultsProps {
  score: number;
  total: number;
  category: Category;
  onPlayAgain: () => void;
  onBackToCategories: () => void;
}

export function QuizResults({ score, total, category, onPlayAgain, onBackToCategories }: QuizResultsProps) {
  const percentage = Math.round((score / total) * 100);
  const categoryInfo = categories[category];

  const getScoreMessage = () => {
    if (percentage >= 90) return {
      emoji: "🏆",
      title: "¡MAESTRO SUPREMO!",
      message: "Eres un verdadero experto en esta materia",
      color: "from-yellow-400 to-orange-500"
    };
    if (percentage >= 80) return {
      emoji: "🌟",
      title: "¡EXCELENTE!",
      message: "Tienes conocimientos muy sólidos",
      color: "from-green-400 to-blue-500"
    };
    if (percentage >= 70) return {
      emoji: "👏",
      title: "¡MUY BIEN!",
      message: "Un resultado bastante bueno",
      color: "from-blue-400 to-purple-500"
    };
    if (percentage >= 60) return {
      emoji: "👍",
      title: "¡BIEN!",
      message: "Conoces el tema, pero puedes mejorar",
      color: "from-purple-400 to-pink-500"
    };
    if (percentage >= 50) return {
      emoji: "😊",
      title: "APROBADO",
      message: "Un comienzo decente, sigue practicando",
      color: "from-pink-400 to-red-500"
    };
    return {
      emoji: "💪",
      title: "¡SIGUE INTENTANDO!",
      message: "La práctica hace al maestro",
      color: "from-gray-400 to-gray-600"
    };
  };

  const scoreInfo = getScoreMessage();

  const getStars = () => {
    if (percentage >= 90) return 5;
    if (percentage >= 80) return 4;
    if (percentage >= 70) return 3;
    if (percentage >= 60) return 2;
    if (percentage >= 50) return 1;
    return 0;
  };

  const stars = getStars();

  return (
    <div className={`min-h-screen bg-gradient-to-br ${categoryInfo.color} bg-opacity-30 p-4 flex items-center justify-center`}>
      <div className="max-w-2xl w-full">
        {/* Tarjeta principal de resultados */}
        <Card className="shadow-2xl border-4 border-white/20 backdrop-blur-sm bg-white/90">
          <CardHeader className={`bg-gradient-to-r ${scoreInfo.color} text-white text-center py-8`}>
            <div className="text-8xl mb-4">{scoreInfo.emoji}</div>
            <CardTitle className="text-4xl mb-2">{scoreInfo.title}</CardTitle>
            <p className="text-xl opacity-90">{scoreInfo.message}</p>
          </CardHeader>
          
          <CardContent className="p-8 text-center space-y-6">
            {/* Puntuación principal */}
            <div className="space-y-4">
              <div className="text-7xl text-gray-800">
                {score}/{total}
              </div>
              <div className="text-2xl text-gray-600">
                {percentage}% de aciertos
              </div>
              
              {/* Estrellas */}
              <div className="flex justify-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-8 h-8 ${
                      i < stars 
                        ? 'text-yellow-400 fill-current' 
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              
              {/* Categoría */}
              <div className="flex items-center justify-center gap-3 mt-6">
                <span className="text-3xl">{categoryInfo.icon}</span>
                <div>
                  <Badge 
                    variant="outline" 
                    className="text-lg px-4 py-2"
                  >
                    {categoryInfo.name}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Estadísticas detalladas */}
            <div className="grid grid-cols-3 gap-4 py-6 border-t border-gray-200">
              <div className="text-center">
                <div className="text-3xl text-green-500 mb-1">✅</div>
                <div className="text-2xl">{score}</div>
                <div className="text-sm text-gray-600">Correctas</div>
              </div>
              <div className="text-center">
                <div className="text-3xl text-red-500 mb-1">❌</div>
                <div className="text-2xl">{total - score}</div>
                <div className="text-sm text-gray-600">Incorrectas</div>
              </div>
              <div className="text-center">
                <div className="text-3xl text-blue-500 mb-1">📊</div>
                <div className="text-2xl">{percentage}%</div>
                <div className="text-sm text-gray-600">Precisión</div>
              </div>
            </div>

            {/* Botones de acción */}
            <div className="space-y-3 pt-4">
              <Button 
                onClick={onPlayAgain}
                size="lg"
                className={`w-full bg-gradient-to-r ${categoryInfo.color} text-white text-xl py-6 hover:opacity-90 transition-all duration-200 hover:scale-105`}
              >
                <RotateCcw className="w-5 h-5 mr-2" />
                Jugar de Nuevo
              </Button>
              
              <div className="grid grid-cols-2 gap-3">
                <Button 
                  onClick={onBackToCategories}
                  variant="outline"
                  size="lg"
                  className="text-lg py-4"
                >
                  <Home className="w-5 h-5 mr-2" />
                  Inicio
                </Button>
                
                <Button 
                  onClick={onBackToCategories}
                  variant="outline"
                  size="lg"
                  className="text-lg py-4"
                >
                  <Trophy className="w-5 h-5 mr-2" />
                  Otras Categorías
                </Button>
              </div>
            </div>

            {/* Mensaje motivacional */}
            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-gray-600 italic">
                {percentage >= 80 
                  ? "¡Sigue así! Tu conocimiento es impresionante." 
                  : percentage >= 60
                  ? "¡Buen trabajo! Con un poco más de práctica serás imparable."
                  : "¡No te rindas! Cada intento te acerca más al dominio total."
                }
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Estadística adicional */}
        <div className="mt-6 text-center">
          <p className="text-white/80 text-sm">
            ¿Sabías que el promedio en esta categoría es del 65%? 
            {percentage >= 65 ? " ¡Estás por encima!" : " ¡Puedes superarlo!"}
          </p>
        </div>
      </div>
    </div>
  );
}