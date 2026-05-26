import numpy as np
import pickle
import os
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

class DinoAI:
    def __init__(self):
        # MLPClassifier - это нейронная сеть в sklearn
        # hidden_layer_sizes=(64, 32) - два скрытых слоя
        # max_iter=1000 - количество эпох обучения
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32), 
            activation='relu', 
            solver='adam', 
            max_iter=1000,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.model_path = "dino_ai_model_sklearn.pkl"
        self.fitted = False
        
        # Загрузка модели, если она существует
        if os.path.exists(self.model_path):
            self.load_model()

    def get_features(self, game_state):
        """
        Преобразует состояние игры в вектор признаков для нейросети.
        Возвращает список значений: [расстояние, тип, высота_препятствия, позиция_птицы_y]
        """
        # game_state - это словарь или объект, содержащий данные о ближайшем препятствии
        # Если препятствий нет, возвращаем "безопасные" значения
        if not game_state['obstacle']:
            return np.array([[1.0, 0.0, 0.0, 0.0]]) # 1.0 = далеко, безопасно
        
        obs = game_state['obstacle']
        
        # Нормализуем расстояние (ширина экрана 800)
        distance = obs.x / 800.0
        
        # Тип препятствия: 0 = Кактус, 1 = Птица
        obs_type = 1.0 if obs.type == "bird" else 0.0
        
        # Высота препятствия (нормализованная)
        # Высота кактуса ~30-50, Птица ~30
        height_norm = obs.height / 100.0
        
        # Y-позиция (важно для птиц: высоко или низко)
        # Земля примерно на y=300
        y_pos_norm = obs.y / 400.0
        
        return np.array([[distance, obs_type, height_norm, y_pos_norm]])

    def predict_action(self, game_state):
        """
        Предсказывает действие на основе данных сенсора.
        0 - Ничего, 1 - Прыжок (Space), 2 - Приседание (Ctrl)
        """
        features = self.get_features(game_state)
        
        if not self.fitted:
            return 0 # Если модель не обучена, ничего не делаем
            
        # Масштабируем данные так же, как при обучении
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        return int(prediction)

    def collect_data_manually(self, game_state, action):
        """
        Метод для сбора данных во время игры человеком.
        action: 0 (idle), 1 (jump), 2 (duck)
        """
        features = self.get_features(game_state).flatten()
        return features, action

    def train_with_synthetic_data(self):
        """
        Автоматическая генерация данных для обучения.
        Создает "идеальные" ситуации и правильные ответы на них.
        """
        print("Генерация синтетических данных для обучения...")
        X_train = []
        y_train = []
        
        # Генерируем 5000 случайных ситуаций
        for _ in range(5000):
            distance = np.random.uniform(0.0, 1.0)
            obs_type = np.random.choice([0, 1]) # 0 кактус, 1 птица
            height = np.random.uniform(0.2, 0.6)
            y_pos = np.random.uniform(0.3, 0.8)
            
            features = [distance, obs_type, height, y_pos]
            X_train.append(features)
            
            # Логика "правильного" действия
            action = 0 # По умолчанию ничего не делаем
            
            # Если препятствие близко
            if distance < 0.25:
                if obs_type == 0: # Кактус -> Прыжок
                    action = 1
                else: # Птица
                    # Если птица низко (y_pos большой, т.к. 0 это верх экрана в математике, но в pygame наоборот)
                    # В нашем случае: y_pos ~ 0.75 (низко, нужно прыгать)
                    # y_pos ~ 0.5 (высоко, нужно приседать)
                    # Допустим, y < 260 это низко (нужен прыжок), y >= 260 это высоко (нужен уклон)
                    # Нормализованно: 260/400 = 0.65
                    if y_pos > 0.65: 
                        action = 1 # Прыжок через низко летящую птицу
                    else:
                        action = 2 # Приседание под высоко летящую птицу
            
            y_train.append(action)
            
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Обучение модели
        print("Обучение нейронной сети...")
        self.scaler.fit(X_train)
        X_scaled = self.scaler.transform(X_train)
        
        self.model.fit(X_scaled, y_train)
        self.fitted = True
        self.save_model()
        print("Обучение завершено! Модель сохранена.")

    def save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.model, self.scaler), f)
        print(f"Модель сохранена в {self.model_path}")

    def load_model(self):
        with open(self.model_path, 'rb') as f:
            self.model, self.scaler = pickle.load(f)
        self.fitted = True
        print("Модель загружена.")