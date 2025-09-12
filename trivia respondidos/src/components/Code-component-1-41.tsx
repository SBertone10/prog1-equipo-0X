import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Category, categories } from './QuizData';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface CategorySelectorProps {
  onSelectCategory: (category: Category) => void;
}

export function CategorySelector({ onSelectCategory }: CategorySelectorProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-100 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-5xl mb-4 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            🎯 Quiz Master
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Pon a prueba tus conocimientos en cultura general
          </p>
          <Badge variant="secondary" className="text-sm">
            300+ preguntas • 6 categorías • Diversión garantizada
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {Object.entries(categories).slice(0, -1).map(([key, category]) => (
            <Card
              key={key}
              className="group cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl border-2 hover:border-purple-300"
              onClick={() => onSelectCategory(key as Category)}
            >
              <div className="relative overflow-hidden">
                <ImageWithFallback
                  src={category.image}
                  alt={category.name}
                  className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300"
                />
                <div className={`absolute inset-0 bg-gradient-to-t ${category.color} opacity-75`}></div>
                <div className="absolute top-4 right-4">
                  <Badge className="bg-white/90 text-black text-lg px-3 py-1">
                    {category.icon}
                  </Badge>
                </div>
              </div>
              <CardContent className="p-6">
                <h3 className="text-2xl mb-2 text-center">
                  {category.name}
                </h3>
                <p className="text-gray-600 text-center mb-4">
                  50 preguntas únicas
                </p>
                <Button 
                  className={`w-full bg-gradient-to-r ${category.color} text-white border-0 hover:opacity-90`}
                >
                  Jugar {category.icon}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Opción "Todas las categorías" destacada */}
        <Card 
          className="group cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-2xl border-4 border-gradient-to-r from-pink-500 to-purple-500 max-w-2xl mx-auto"
          onClick={() => onSelectCategory('todas')}
        >
          <div className="relative overflow-hidden">
            <ImageWithFallback
              src={categories.todas.image}
              alt={categories.todas.name}
              className="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-300"
            />
            <div className={`absolute inset-0 bg-gradient-to-t ${categories.todas.color} opacity-80`}></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <div className="text-6xl mb-4">{categories.todas.icon}</div>
                <h3 className="text-4xl mb-2">
                  {categories.todas.name}
                </h3>
                <p className="text-xl mb-4">
                  Mezcla todas las categorías para el desafío definitivo
                </p>
                <Badge className="bg-white/90 text-purple-600 text-lg px-4 py-2">
                  300 preguntas • Máxima dificultad
                </Badge>
              </div>
            </div>
          </div>
          <CardContent className="p-8 text-center">
            <Button 
              size="lg"
              className={`text-xl px-8 py-3 bg-gradient-to-r ${categories.todas.color} text-white border-0 hover:opacity-90`}
            >
              ¡Acepto el Desafío! 🚀
            </Button>
          </CardContent>
        </Card>

        <div className="text-center mt-8">
          <p className="text-gray-500 text-sm">
            Cada partida incluye 10 preguntas aleatorias de la categoría seleccionada
          </p>
        </div>
      </div>
    </div>
  );
}