import os
import yaml
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
import webbrowser
import threading
import time
import logging
from flask.cli import show_server_banner

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "interface", "static"),
    template_folder=os.path.join(os.path.dirname(__file__), "interface", "templates"),
)

# Путь к файлу конфигурации
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


def load_config():
    """Загрузка конфигурации из YAML файла"""
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)


def save_config(config):
    """Сохранение конфигурации в YAML файл"""
    with open(CONFIG_PATH, "w") as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)


@app.route("/")
def index():
    """Главная страница с интерфейсом конфигурации"""
    return render_template("config.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    """API для получения текущей конфигурации"""
    config = load_config()
    return jsonify(config)


@app.route("/api/config", methods=["POST"])
def update_config():
    """API для обновления конфигурации"""
    try:
        new_config = request.json
        save_config(new_config)
        return jsonify(
            {"status": "success", "message": "Configuration saved successfully"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def open_browser():
    """Открывает браузер после запуска сервера"""
    time.sleep(2)  # Даем серверу время на запуск
    webbrowser.open(f"http://127.0.0.1:5000")


def create_required_directories():
    """Создает необходимые директории для шаблонов и статических файлов"""
    # Изменяем пути для сохранения файлов
    base_dir = os.path.join(os.path.dirname(__file__), "config_interface")
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    css_dir = os.path.join(static_dir, "css")
    js_dir = os.path.join(static_dir, "js")

    # Создаем все необходимые директории
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)

    # Создаем HTML шаблон
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StarLabs Configuration</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="background-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
        <div class="shape shape-6"></div>
    </div>
    
    <div class="app-container">
        <header>
            <div class="logo">
                <i class="fas fa-star"></i>
                <h1>StarLabs Configuration</h1>
            </div>
            <div class="header-controls">
                <button id="saveButton" class="btn save-btn"><i class="fas fa-save"></i> Save Configuration</button>
            </div>
        </header>
        
        <main>
            <div class="sidebar">
                <div class="sidebar-menu">
                    <div class="sidebar-item active" data-section="settings">
                        <i class="fas fa-cog"></i>
                        <span>Settings</span>
                    </div>
                    <div class="sidebar-item" data-section="flow">
                        <i class="fas fa-exchange-alt"></i>
                        <span>Flow</span>
                    </div>
                    <div class="sidebar-item" data-section="swaps">
                        <i class="fas fa-sync"></i>
                        <span>Hub 0G Swaps</span>
                    </div>
                    <div class="sidebar-item" data-section="captcha">
                        <i class="fas fa-robot"></i>
                        <span>Captcha</span>
                    </div>
                    <div class="sidebar-item" data-section="rpcs">
                        <i class="fas fa-network-wired"></i>
                        <span>RPCs</span>
                    </div>
                    <div class="sidebar-item" data-section="others">
                        <i class="fas fa-ellipsis-h"></i>
                        <span>Others</span>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <div id="configContainer">
                    <!-- Здесь будут динамически созданные элементы конфигурации -->
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Loading configuration...</p>
                    </div>
                </div>
            </div>
        </main>
        
        <footer>
            <div class="system-status">
                <span class="status-indicator online"></span>
                System ready
            </div>
            <div class="version">v1.0.0</div>
        </footer>
    </div>
    
    <!-- Модальное окно для уведомлений -->
    <div id="notification" class="notification">
        <div class="notification-content">
            <i class="fas fa-check-circle notification-icon success"></i>
            <i class="fas fa-exclamation-circle notification-icon error"></i>
            <p id="notification-message"></p>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/config.js') }}"></script>
</body>
</html>
"""

    # Создаем CSS файл с улучшенным дизайном
    css_content = """:root {
    /* Основные цвета */
    --primary-blue: #3A86FF;      /* Основной синий */
    --secondary-blue: #4361EE;    /* Вторичный синий */
    --dark-blue: #2B4EFF;         /* Темно-синий */
    --light-blue: #60A5FA;        /* Светло-синий */
    
    /* Неоновые акценты (приглушенные) */
    --neon-blue: #4895EF;         /* Неоновый синий */
    --neon-purple: #8B5CF6;       /* Неоновый фиолетовый */
    --neon-pink: #EC4899;         /* Неоновый розовый (приглушенный) */
    --neon-cyan: #22D3EE;         /* Неоновый голубой */
    
    /* Статусы */
    --success: #10B981;           /* Зеленый */
    --error: #EF4444;             /* Красный */
    --warning: #F59E0B;           /* Оранжевый */
    --info: #3B82F6;              /* Синий */
    
    /* Фоны */
    --bg-dark: #1A1A2E;           /* Темно-синий фон */
    --bg-card: rgba(26, 26, 46, 0.6); /* Полупрозрачный фон карточек */
    --bg-card-hover: rgba(26, 26, 46, 0.8); /* Фон карточек при наведении */
    
    /* Текст */
    --text-primary: #F8FAFC;      /* Основной текст */
    --text-secondary: #94A3B8;    /* Вторичный текст */
    
    /* Тени */
    --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.15);
    --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.2);
    
    /* Градиенты */
    --gradient-blue: linear-gradient(135deg, var(--primary-blue), var(--dark-blue));
    --gradient-purple-blue: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
    --gradient-blue-cyan: linear-gradient(135deg, var(--neon-blue), var(--neon-cyan));
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Poppins', sans-serif;
    background: var(--bg-dark);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    position: relative;
    overflow-x: hidden;
    background: linear-gradient(135deg, #6A11CB, #FC2D7F, #FF9800);
}

/* Фоновые формы */
.background-shapes {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
}

.shape {
    position: absolute;
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0.4;
}

.shape-1 {
    top: 10%;
    left: 10%;
    width: 300px;
    height: 300px;
    background: var(--neon-purple);
    animation: float 15s infinite alternate;
}

.shape-2 {
    top: 60%;
    left: 20%;
    width: 200px;
    height: 200px;
    background: var(--neon-blue);
    animation: float 12s infinite alternate-reverse;
}

.shape-3 {
    top: 20%;
    right: 15%;
    width: 250px;
    height: 250px;
    background: var(--neon-pink);
    animation: float 18s infinite alternate;
}

.shape-4 {
    bottom: 15%;
    right: 10%;
    width: 180px;
    height: 180px;
    background: var(--neon-cyan);
    animation: float 10s infinite alternate-reverse;
}

.shape-5 {
    top: 40%;
    left: 50%;
    width: 150px;
    height: 150px;
    background: var(--primary-blue);
    animation: float 14s infinite alternate;
}

.shape-6 {
    bottom: 30%;
    left: 30%;
    width: 120px;
    height: 120px;
    background: var(--secondary-blue);
    animation: float 16s infinite alternate-reverse;
}

@keyframes float {
    0% {
        transform: translate(0, 0) scale(1);
    }
    100% {
        transform: translate(30px, 30px) scale(1.1);
    }
}

.app-container {
    width: 90%;
    max-width: 1400px;
    background: rgba(26, 26, 46, 0.7);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 1;
    height: 90vh;
}

/* Заголовок */
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 30px;
    background: rgba(26, 26, 46, 0.8);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
}

header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent, 
        var(--neon-blue), 
        var(--primary-blue), 
        var(--neon-blue), 
        transparent
    );
    opacity: 0.6;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo i {
    font-size: 28px;
    color: var(--neon-blue);
    text-shadow: 0 0 10px rgba(72, 149, 239, 0.5);
}

.logo h1 {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
    position: relative;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 15px;
}

.btn {
    padding: 10px 20px;
    border-radius: 12px;
    border: none;
    background: rgba(58, 134, 255, 0.15);
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
}

.btn:hover {
    background: rgba(58, 134, 255, 0.25);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.save-btn {
    background: var(--gradient-blue);
    padding: 12px 30px;
    font-size: 18px;
    font-weight: 600;
    min-width: 220px;
}

.save-btn:hover {
    box-shadow: 0 5px 15px rgba(58, 134, 255, 0.3);
}

/* Основной контент */
main {
    flex: 1;
    display: flex;
    overflow: hidden;
}

/* Боковое меню */
.sidebar {
    width: 250px;
    background: rgba(26, 26, 46, 0.8);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px 0;
    overflow-y: auto;
}

.sidebar-menu {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.sidebar-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 8px;
    margin: 0 10px;
}

.sidebar-item:hover {
    background: rgba(58, 134, 255, 0.1);
}

.sidebar-item.active {
    background: rgba(58, 134, 255, 0.2);
    color: var(--neon-blue);
}

.sidebar-item i {
    font-size: 20px;
    width: 24px;
    text-align: center;
}

.sidebar-item span {
    font-size: 16px;
    font-weight: 500;
}

/* Основной контент */
.content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
}

/* Секции конфигурации */
.config-section {
    display: none;
    animation: fadeIn 0.3s ease;
}

.config-section.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.section-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--neon-blue);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Карточки настроек */
.config-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.config-card {
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}

.config-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
    background: var(--bg-card-hover);
}

.card-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.card-title i {
    color: var(--neon-blue);
    font-size: 20px;
}

/* Поля ввода */
.config-field {
    margin-bottom: 20px;
}

.field-label {
    font-size: 16px;
    color: var(--text-primary);
    margin-bottom: 10px;
    display: block;
    font-weight: 500;
}

.field-input {
    background: rgba(26, 26, 46, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 12px 15px;
    color: var(--text-primary);
    font-size: 16px;
    width: 100%;
    transition: all 0.3s ease;
    font-weight: 500;
}

.field-input:focus {
    outline: none;
    border-color: var(--neon-blue);
    box-shadow: 0 0 0 2px rgba(72, 149, 239, 0.2);
}

.range-input {
    display: flex;
    gap: 10px;
    align-items: center;
}

.range-input input {
    flex: 1;
    text-align: center;
    font-weight: 600;
}

.range-separator {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 18px;
}

/* Чекбоксы */
.checkbox-field {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    cursor: pointer;
}

.checkbox-input {
    appearance: none;
    width: 24px;
    height: 24px;
    background: rgba(26, 26, 46, 0.5);
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    position: relative;
    cursor: pointer;
    transition: all 0.3s ease;
}

.checkbox-input:checked {
    background: var(--neon-blue);
    border-color: var(--neon-blue);
}

.checkbox-input:checked::after {
    content: '✓';
    position: absolute;
    color: white;
    font-size: 16px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.checkbox-label {
    font-size: 16px;
    color: var(--text-primary);
    cursor: pointer;
    font-weight: 500;
}

/* Списки */
.list-field {
    position: relative;
}

.list-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.list-item {
    background: rgba(58, 134, 255, 0.2);
    border-radius: 8px;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.list-item span {
    font-size: 14px;
    color: var(--text-primary);
}

.list-item button {
    background: none;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    font-size: 14px;
    opacity: 0.7;
    transition: opacity 0.3s;
}

.list-item button:hover {
    opacity: 1;
}

.add-list-item {
    display: flex;
    align-items: center;
    margin-top: 10px;
}

.add-list-item input {
    flex: 1;
    background: rgba(26, 26, 46, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px 0 0 12px;
    padding: 10px 15px;
    color: var(--text-primary);
    font-size: 14px;
}

.add-list-item button {
    background: var(--neon-blue);
    border: none;
    border-radius: 0 12px 12px 0;
    padding: 10px 15px;
    color: white;
    cursor: pointer;
    transition: background 0.3s;
}

.add-list-item button:hover {
    background: var(--dark-blue);
}

/* Футер */
footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background: rgba(26, 26, 46, 0.8);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 14px;
    color: var(--text-secondary);
    position: relative;
}

footer::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent, 
        var(--neon-blue), 
        var(--primary-blue), 
        var(--neon-blue), 
        transparent
    );
    opacity: 0.6;
}

.system-status {
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.status-indicator.online {
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
    animation: pulse 2s infinite;
    opacity: 0.9;
}

@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 0.9; }
    100% { opacity: 0.6; }
}

.version {
    font-size: 14px;
}

/* Загрузка */
.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 20px;
}

.spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(72, 149, 239, 0.2);
    border-radius: 50%;
    border-top-color: var(--neon-blue);
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Уведомления */
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(26, 26, 46, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 15px 20px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    transform: translateX(150%);
    transition: transform 0.3s ease;
    z-index: 1000;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.notification.show {
    transform: translateX(0);
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 15px;
}

.notification-icon {
    font-size: 28px;
    display: none;
}

.notification-icon.success {
    color: var(--success);
}

.notification-icon.error {
    color: var(--error);
}

.notification.success .notification-icon.success {
    display: block;
}

.notification.error .notification-icon.error {
    display: block;
}

#notification-message {
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 500;
}

/* Адаптивность */
@media (max-width: 1024px) {
    .config-cards {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .app-container {
        width: 100%;
        height: 100vh;
        border-radius: 0;
    }
    
    header, footer {
        padding: 15px;
    }
    
    main {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px 0;
    }
    
    .sidebar-menu {
        flex-direction: row;
        overflow-x: auto;
        padding: 0 10px;
    }
    
    .sidebar-item {
        padding: 10px 15px;
        white-space: nowrap;
    }
    
    .content {
        padding: 15px;
    }
}

/* Скроллбар */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(26, 26, 46, 0.3);
}

::-webkit-scrollbar-thumb {
    background: rgba(72, 149, 239, 0.5);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(72, 149, 239, 0.7);
}

/* Стилизация для маленьких числовых полей */
.small-input {
    max-width: 100px;
    text-align: center;
}

/* Стилизация для средних полей */
.medium-input {
    max-width: 200px;
}

/* Подсказки */
.tooltip {
    position: relative;
    display: inline-block;
    margin-left: 5px;
    color: var(--neon-blue);
    cursor: pointer;
}

.tooltip .tooltip-text {
    visibility: hidden;
    width: 200px;
    background: rgba(26, 26, 46, 0.95);
    color: var(--text-primary);
    text-align: center;
    border-radius: 8px;
    padding: 10px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 14px;
    font-weight: normal;
    box-shadow: var(--shadow-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

/* Стили для списков с тегами */
.tags-input {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px;
    background: rgba(26, 26, 46, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    min-height: 50px;
}

.tag {
    display: flex;
    align-items: center;
    background: rgba(58, 134, 255, 0.2);
    padding: 5px 10px;
    border-radius: 6px;
    gap: 8px;
}

.tag-text {
    font-size: 14px;
    color: var(--text-primary);
}

.tag-remove {
    background: none;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    font-size: 14px;
    opacity: 0.7;
    transition: opacity 0.3s;
}

.tag-remove:hover {
    opacity: 1;
}

.tags-input input {
    flex: 1;
    min-width: 60px;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-primary);
    font-size: 14px;
    padding: 5px;
}

.tags-input input::placeholder {
    color: var(--text-secondary);
    opacity: 0.7;
}
"""

    # Создаем JavaScript файл с улучшенной логикой
    js_content = """document.addEventListener('DOMContentLoaded', function() {
    // Загружаем конфигурацию при загрузке страницы
    fetchConfig();
    
    // Обработчик для кнопки сохранения
    document.getElementById('saveButton').addEventListener('click', saveConfig);
    
    // Обработчики для пунктов меню
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.addEventListener('click', function() {
            // Убираем активный класс у всех пунктов
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            // Добавляем активный класс текущему пункту
            this.classList.add('active');
            
            // Показываем соответствующую секцию
            const section = this.dataset.section;
            document.querySelectorAll('.config-section').forEach(s => s.classList.remove('active'));
            document.getElementById(`${section}-section`).classList.add('active');
        });
    });
});

// Функция для форматирования названий полей
function formatFieldName(name) {
    // Заменяем подчеркивания на пробелы
    let formatted = name.replace(/_/g, ' ');
    
    // Делаем первую букву заглавной, остальные строчными
    return formatted.charAt(0).toUpperCase() + formatted.slice(1).toLowerCase();
}

// Функция для загрузки конфигурации с сервера
async function fetchConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        renderConfig(config);
    } catch (error) {
        showNotification('Failed to load configuration: ' + error.message, 'error');
    }
}

// Функция для сохранения конфигурации
async function saveConfig() {
    try {
        const config = collectFormData();
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification('Configuration saved successfully!', 'success');
        } else {
            showNotification('Error: ' + result.message, 'error');
        }
    } catch (error) {
        showNotification('Failed to save configuration: ' + error.message, 'error');
    }
}

// Функция для сбора данных формы
function collectFormData() {
    const config = {};
    
    // Собираем данные из всех полей ввода
    document.querySelectorAll('[data-config-path]').forEach(element => {
        const path = element.dataset.configPath.split('.');
        let current = config;
        
        // Создаем вложенные объекты по пути
        for (let i = 0; i < path.length - 1; i++) {
            if (!current[path[i]]) {
                current[path[i]] = {};
            }
            current = current[path[i]];
        }
        
        // Устанавливаем значение
        const lastKey = path[path.length - 1];
        
        if (element.type === 'checkbox') {
            current[lastKey] = element.checked;
        } else if (element.classList.contains('range-min')) {
            // Для диапазонов (min-max)
            const rangeKey = lastKey.replace('_MIN', '');
            if (!current[rangeKey]) {
                current[rangeKey] = [0, 0];
            }
            current[rangeKey][0] = parseInt(element.value);
        } else if (element.classList.contains('range-max')) {
            const rangeKey = lastKey.replace('_MAX', '');
            if (!current[rangeKey]) {
                current[rangeKey] = [0, 0];
            }
            current[rangeKey][1] = parseInt(element.value);
        } else if (element.classList.contains('list-input')) {
            // Для списков (разделенных запятыми)
            current[lastKey] = element.value.split(',')
                .map(item => item.trim())
                .filter(item => item !== '');
                
            // Преобразуем в числа, если это числовой список
            if (element.dataset.type === 'number-list') {
                current[lastKey] = current[lastKey].map(item => parseInt(item));
            }
        } else {
            // Для обычных полей
            if (element.dataset.type === 'number') {
                current[lastKey] = parseInt(element.value);
            } else {
                current[lastKey] = element.value;
            }
        }
    });
    
    return config;
}

// Функция для отображения конфигурации
function renderConfig(config) {
    const container = document.getElementById('configContainer');
    container.innerHTML = ''; // Очищаем контейнер
    
    // Создаем секции для каждой категории
    const sections = {
        'settings': { key: 'SETTINGS', title: 'Settings', icon: 'cog' },
        'flow': { key: 'FLOW', title: 'Flow', icon: 'exchange-alt' },
        'swaps': { key: 'HUB_0G_SWAPS', title: 'Hub 0G Swaps', icon: 'sync' },
        'captcha': { key: 'CAPTCHA', title: 'Captcha', icon: 'robot' },
        'rpcs': { key: 'RPCS', title: 'RPCs', icon: 'network-wired' },
        'others': { key: 'OTHERS', title: 'Others', icon: 'ellipsis-h' }
    };
    
    // Создаем все секции
    Object.entries(sections).forEach(([sectionId, { key, title, icon }], index) => {
        const section = document.createElement('div');
        section.id = `${sectionId}-section`;
        section.className = `config-section ${index === 0 ? 'active' : ''}`;
        
        const sectionTitle = document.createElement('h2');
        sectionTitle.className = 'section-title';
        sectionTitle.innerHTML = `<i class="fas fa-${icon}"></i> ${title}`;
        section.appendChild(sectionTitle);
        
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'config-cards';
        section.appendChild(cardsContainer);
        
        // Заполняем секцию данными
        if (config[key]) {
            if (key === 'SETTINGS') {
                // Карточка для основных настроек
                createCard(cardsContainer, 'Basic Settings', 'sliders-h', [
                    { key: 'THREADS', value: config[key]['THREADS'] },
                    { key: 'ATTEMPTS', value: config[key]['ATTEMPTS'] },
                    { key: 'SHUFFLE_WALLETS', value: config[key]['SHUFFLE_WALLETS'] }
                ], key);
                
                // Карточка для диапазонов аккаунтов
                createCard(cardsContainer, 'Account Settings', 'users', [
                    { key: 'ACCOUNTS_RANGE', value: config[key]['ACCOUNTS_RANGE'] },
                    { key: 'EXACT_ACCOUNTS_TO_USE', value: config[key]['EXACT_ACCOUNTS_TO_USE'], isSpaceList: true }
                ], key);
                
                // Карточка для пауз
                createCard(cardsContainer, 'Timing Settings', 'clock', [
                    { key: 'PAUSE_BETWEEN_ATTEMPTS', value: config[key]['PAUSE_BETWEEN_ATTEMPTS'] },
                    { key: 'PAUSE_BETWEEN_SWAPS', value: config[key]['PAUSE_BETWEEN_SWAPS'] },
                    { key: 'RANDOM_PAUSE_BETWEEN_ACCOUNTS', value: config[key]['RANDOM_PAUSE_BETWEEN_ACCOUNTS'] },
                    { key: 'RANDOM_PAUSE_BETWEEN_ACTIONS', value: config[key]['RANDOM_PAUSE_BETWEEN_ACTIONS'] },
                    { key: 'RANDOM_INITIALIZATION_PAUSE', value: config[key]['RANDOM_INITIALIZATION_PAUSE'] }
                ], key);
                
                // Карточка для Telegram
                createCard(cardsContainer, 'Telegram Settings', 'paper-plane', [
                    { key: 'SEND_TELEGRAM_LOGS', value: config[key]['SEND_TELEGRAM_LOGS'] },
                    { key: 'TELEGRAM_BOT_TOKEN', value: config[key]['TELEGRAM_BOT_TOKEN'] },
                    { key: 'TELEGRAM_USERS_IDS', value: config[key]['TELEGRAM_USERS_IDS'], isSpaceList: true }
                ], key);
            } else if (key === 'RPCS') {
                // Создаем карточку для RPCs с поддержкой списков
                createCard(cardsContainer, 'RPC Settings', 'network-wired', 
                    Object.entries(config[key]).map(([k, v]) => ({ 
                        key: k, 
                        value: v, 
                        isList: true 
                    })), 
                    key
                );
            } else {
                // Остальные категории
                createCard(cardsContainer, `${title} Settings`, icon, 
                    Object.entries(config[key]).map(([k, v]) => ({ key: k, value: v })), 
                    key
                );
            }
        }
        
        container.appendChild(section);
    });
}

// Функция для создания карточки
function createCard(container, title, iconClass, fields, category) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'config-card';
    
    const titleDiv = document.createElement('div');
    titleDiv.className = 'card-title';
    
    const icon = document.createElement('i');
    icon.className = `fas fa-${iconClass}`;
    titleDiv.appendChild(icon);
    
    const titleText = document.createElement('span');
    titleText.textContent = title;
    titleDiv.appendChild(titleText);
    
    cardDiv.appendChild(titleDiv);
    
    fields.forEach(({ key, value, isList, isSpaceList }) => {
        if (typeof value === 'boolean') {
            createCheckboxField(cardDiv, key, value, `${category}.${key}`);
        } else if (Array.isArray(value) && value.length === 2 && typeof value[0] === 'number' && typeof value[1] === 'number') {
            createRangeField(cardDiv, key, value, `${category}.${key}`);
        } else if (Array.isArray(value) && isList) {
            createTagsField(cardDiv, key, value, `${category}.${key}`, false);
        } else if (Array.isArray(value) && isSpaceList) {
            createTagsField(cardDiv, key, value, `${category}.${key}`, true);
        } else if (Array.isArray(value)) {
            createListField(cardDiv, key, value, `${category}.${key}`);
        } else {
            createTextField(cardDiv, key, value, `${category}.${key}`);
        }
    });
    
    container.appendChild(cardDiv);
}

// Создание текстового поля
function createTextField(container, key, value, path) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'config-field';
    
    const label = document.createElement('label');
    label.className = 'field-label';
    label.textContent = formatFieldName(key);
    fieldDiv.appendChild(label);
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'field-input';
    input.value = value;
    input.dataset.configPath = path;
    
    if (typeof value === 'number') {
        input.dataset.type = 'number';
        input.type = 'number';
        input.className += ' small-input';
    }
    
    fieldDiv.appendChild(input);
    container.appendChild(fieldDiv);
}

// Создание поля диапазона
function createRangeField(container, key, value, path) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'config-field';
    
    const label = document.createElement('label');
    label.className = 'field-label';
    label.textContent = formatFieldName(key);
    fieldDiv.appendChild(label);
    
    const rangeDiv = document.createElement('div');
    rangeDiv.className = 'range-input';
    
    const minInput = document.createElement('input');
    minInput.type = 'number';
    minInput.className = 'field-input range-min small-input';
    minInput.value = value[0];
    minInput.dataset.configPath = `${path}_MIN`;
    minInput.dataset.type = 'number';
    
    const separator = document.createElement('span');
    separator.className = 'range-separator';
    separator.textContent = '-';
    
    const maxInput = document.createElement('input');
    maxInput.type = 'number';
    maxInput.className = 'field-input range-max small-input';
    maxInput.value = value[1];
    maxInput.dataset.configPath = `${path}_MAX`;
    maxInput.dataset.type = 'number';
    
    rangeDiv.appendChild(minInput);
    rangeDiv.appendChild(separator);
    rangeDiv.appendChild(maxInput);
    
    fieldDiv.appendChild(rangeDiv);
    container.appendChild(fieldDiv);
}

// Создание чекбокса
function createCheckboxField(container, key, value, path) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'checkbox-field';
    
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.className = 'checkbox-input';
    input.checked = value;
    input.dataset.configPath = path;
    input.id = `checkbox-${path.replace(/\\./g, '-')}`;
    
    const label = document.createElement('label');
    label.className = 'checkbox-label';
    label.textContent = formatFieldName(key);
    label.htmlFor = input.id;
    
    fieldDiv.appendChild(input);
    fieldDiv.appendChild(label);
    container.appendChild(fieldDiv);
}

// Создание списка
function createListField(container, key, value, path) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'config-field';
    
    const label = document.createElement('label');
    label.className = 'field-label';
    label.textContent = formatFieldName(key);
    fieldDiv.appendChild(label);
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'field-input list-input';
    input.value = value.join(', ');
    input.dataset.configPath = path;
    
    // Определяем, является ли это списком чисел
    if (value.length > 0 && typeof value[0] === 'number') {
        input.dataset.type = 'number-list';
    }
    
    fieldDiv.appendChild(input);
    container.appendChild(fieldDiv);
}

// Создание поля с тегами (для списков)
function createTagsField(container, key, value, path, useSpaces) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'config-field';
    
    const label = document.createElement('label');
    label.className = 'field-label';
    label.textContent = formatFieldName(key);
    fieldDiv.appendChild(label);
    
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'tags-input';
    tagsContainer.dataset.configPath = path;
    tagsContainer.dataset.useSpaces = useSpaces ? 'true' : 'false';
    
    // Добавляем существующие теги
    value.forEach(item => {
        const tag = createTag(item);
        tagsContainer.appendChild(tag);
    });
    
    // Добавляем поле ввода для новых тегов
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Add item...';
    
    // Обработчик для добавления нового тега
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ' && useSpaces) {
            e.preventDefault();
            const value = this.value.trim();
            if (value) {
                const tag = createTag(value);
                tagsContainer.insertBefore(tag, this);
                this.value = '';
            }
        }
    });
    
    tagsContainer.appendChild(input);
    
    // Функция для создания тега
    function createTag(text) {
        const tag = document.createElement('div');
        tag.className = 'tag';
        
        const tagText = document.createElement('span');
        tagText.className = 'tag-text';
        tagText.textContent = text;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'tag-remove';
        removeBtn.innerHTML = '&times;';
        removeBtn.addEventListener('click', function() {
            tag.remove();
        });
        
        tag.appendChild(tagText);
        tag.appendChild(removeBtn);
        
        return tag;
    }
    
    fieldDiv.appendChild(tagsContainer);
    container.appendChild(fieldDiv);
}

// Функция для отображения уведомления
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.className = `notification ${type} show`;
    
    document.getElementById('notification-message').textContent = message;
    
    setTimeout(() => {
        notification.className = 'notification';
    }, 3000);
}
"""

    # Записываем файлы в соответствующие директории
    template_path = os.path.join(
        os.path.dirname(__file__), "config_interface", "templates", "config.html"
    )
    css_path = os.path.join(
        os.path.dirname(__file__), "config_interface", "static", "css", "style.css"
    )
    js_path = os.path.join(
        os.path.dirname(__file__), "config_interface", "static", "js", "config.js"
    )

    with open(template_path, "w", encoding="utf-8") as file:
        file.write(html_template)

    with open(css_path, "w", encoding="utf-8") as file:
        file.write(css_content)

    with open(js_path, "w", encoding="utf-8") as file:
        file.write(js_content)


def run():
    """Запускает веб-интерфейс для редактирования конфигурации"""
    import threading
    import os
    import sys

    # Создаем необходимые директории и файлы
    create_required_directories()

    # Запускаем браузер в отдельном потоке
    threading.Thread(target=open_browser).start()

    # Выводим информацию о запуске с выделением
    logger.info("Starting web configuration interface...")
    logger.info("\n" + "=" * 50)
    logger.info(
        f"🌐 Configuration interface available at: \033[1;36mhttp://127.0.0.1:5000\033[0m"
    )
    logger.info(f"⚠️  To exit and return to main menu: \033[1;33mPress CTRL+C\033[0m")
    logger.info("=" * 50 + "\n")

    try:
        # Запускаем Flask без логов
        import logging

        log = logging.getLogger("werkzeug")
        log.disabled = True
        app.logger.disabled = True

        app.run(debug=False)
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 50)
        logger.info("✅ Web configuration interface stopped")
        logger.info("=" * 50 + "\n")
