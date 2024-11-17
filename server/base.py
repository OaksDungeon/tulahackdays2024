from fastapi import FastAPI, HTTPException, File, UploadFile, Form
import cv2
import os
import random
import sqlite3
from datetime import datetime
from ultralytics import YOLO
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import imghdr
from fastapi.responses import StreamingResponse
import base64
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Система обнаружения мусора",
    description="Данное API осуществляет возможность автоматического обнаружения мусора на контейнерных площадках с помощью обработки фотографий (или кадров видеотрансляции) нейронной сетью Yolo8. \nВ системе так же предусмотрена история обнаружения мусора, хранящаяся в базе данных.",
    version="hackaton-beta 0.0.1",
    contact={
        "name": "Дубы подземелья. Связь с капитаном команды",
        "url": "https://t.me/saha_sorokina",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные HTTP методы
    allow_headers=["*"],  # Разрешенные заголовки
)
# Путь к папкам с изображениями
FOLDER_1 = "test1"  # Путь к первой папке с изображениями
FOLDER_2 = "test2"  # Путь ко второй папке с изображениями

# Настройка базы данных
DB_NAME = "detections.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            address TEXT,
            trash_status BOOLEAN
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Загружаем обученную модель YOLO
model = YOLO('best.pt')

# Функция для добавления записи в базу данных
def add_record_to_db(address: str, trash_status: bool, trash_outside_status: bool):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO detections (timestamp, address, trash_status)
        VALUES (?, ?, ?)
    """, (timestamp, address, trash_status))
    conn.commit()
    conn.close()

# Функция выбора случайного изображения из папки
#!!! ДЕМОНСТРАЦИОННЫЙ ФУНКЦИОНАЛ
def get_random_image(folder: str):
    images = os.listdir(folder)
    if not images:
        raise FileNotFoundError(f"No images found in {folder}")
    random_image = random.choice(images)
    image_path = os.path.join(folder, random_image)
    return image_path
#!!!

# Функция для проверки является ли файл изображением
def is_image(file_path: str) -> bool:
    try:
        with Image.open(file_path) as img:
            img.verify()  # Проверяет, что файл является допустимым изображением
        return True
    except Exception:
        return False

# Функция обработки изображения с использованием YOLO
def process_image(image_path: str):
    # Чтение изображения
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Failed to load image.")
    
    # Применение модели YOLO
    results = model(img)

    # Проверяем наличие объектов "trash" и "trash outside"
    trash_status = False
    trash_outside_status = False
    for box in results[0].boxes:
        class_name = model.names[int(box.cls)]
        if class_name == "trash":  # Если обнаружен "trash"
            trash_status = True
        elif class_name == "trash outside":  # Если обнаружен "trash outside"
            trash_outside_status = True

    return img, trash_status, trash_outside_status

# Конвертация изображения для ответа клиенту
def image_to_bytes(image):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    print('5')
    buf = BytesIO()
    print('6')
    print(image.shape)
    pil_image.save(buf, format="JPEG")
    print('7')

    buf.seek(0)
    print('8')

    return buf

@app.post("/process", 
          summary="Обработка изображения",
    description="Этот эндпоинт принимает изображение, выполняет детекцию мусора и возвращает результаты анализа. \nДля демонстрации работы системы так же реализован демонстрационный функционал иммитации обработки кадров с видеопотока, осуществляемый с помощью обработки случайного элемента массива изображений. \nДемонстрационный функционал отмечен в коде комментариями.",
    response_description="Результат детекции в формате JSON, включая статус мусора и его расположение, а так же хранит само изображение в виде двоичных данных."
)
async def process_image_based_on_index(
    index: str = Form(None, description="Параметр для реализации демонстрационного функционала. Используется для определения тестовых маркеров."),  # Опциональный параметр `index`, передается как form-data
    file: UploadFile = File(None, description="Файл, являющийся изображением, которое будет обработанно с помощью нейронной сети и возвращенно пользователю.")  # Файл остается опциональным
):
    try:
        # Проверяем, был ли передан файл
        if file:
            # Сохраняем загруженный файл во временную директорию
            file_bytes = await file.read()
            adress = "Пример"
            image_path = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            with open(image_path, "wb") as f:
                f.write(file_bytes)

            # Проверяем, является ли загруженный файл изображением
            if not is_image(image_path):
                os.remove(image_path)
                raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
        #!!! ДЕМОНСТРАЦИОННЫЙ ФУНКЦИОНАЛ
        elif index == '1':
            # Если индекс 1, выбираем случайное изображение из папки FOLDER_1
            folder = FOLDER_1
            adress = "Вознесенского 9"
            image_path = get_random_image(folder)
        elif index == '2':
            # Если индекс 2, выбираем случайное изображение из папки FOLDER_2
            folder = FOLDER_2
            adress = "Рязанская 4"
            image_path = get_random_image(folder)
        #!!!
        else:
            raise HTTPException(status_code=400, detail="Either index or a valid file must be provided.")

        # Обрабатываем изображение
        img, trash_status, trash_outside_status = process_image(image_path)

        # Если файл был загружен временно, удаляем его после обработки
        if file:
            os.remove(image_path)

        # Если обнаружен мусор, записываем в базу данных
        add_record_to_db(adress, trash_status, trash_outside_status)
        _, buffer = cv2.imencode('.jpg', img)
        byte_stream = BytesIO(buffer)
        img_base64 = base64.b64encode(byte_stream.getvalue()).decode('utf-8')

        # Формируем ответ в формате JSON
        response_data = {
            "image_base64": img_base64,
            "trash_status": trash_status,
            "trash_outside_status": trash_outside_status
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/records", summary="Получение записей",
    description="Возвращает список всех записей детекции из базы данных.",
    response_description="Массив записей с ID, временем, адресом и состоянием мусора."
)
async def get_records():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM detections")
        rows = cursor.fetchall()
        conn.close()
        return {"records": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 #Данный блок кода предназначен для    
def fetch_data():
    try:
        url = "http://127.0.0.1:8000" #Адресс сервера с запущенным FastAPI
        """Данный блок кода можно использовать вместо последующего кода для обработки конкретного изображения (например, последнего кадра с камеры).

        try:
        path_img = "img.jpg"
        with open(path_img, "rb") as img_file:
            files = {"img": img_file}
            response = requests.post(url+"/process", files=files)
            
            if response.status_code == 200:
                json_data = response.json()
                print("Наличие мусора:", json_data["trash_status"])
                print ("Наличие мусора на площадке:", json_data["trash_outside_status"])
            else:
                print(f"Ошибка запроса: {response.status_code}")
        except Exception as e:
            print("Ошибка:", e)

        В коде ниже используется демонстрационный функционал"""
        form_data = {"index": '1'}
        response = requests.post(url + "/process", data=form_data)
        print("Значение первой камеры:")
        if response.status_code == 200:
            json_data = response.json()
            print("Наличие мусора:", json_data["trash_status"])
            print ("Наличие мусора на площадке:", json_data["trash_outside_status"])
        else:
            print(f"Ошибка запроса: {response.status_code}")
        
        form_data = {"index": '2'}
        response = requests.post(url + "/process", data=form_data)
        print("Значение второй камеры:")
        if response.status_code == 200:
            json_data = response.json()
            print("Наличие мусора:", json_data["trash_status"])
            print ("Наличие мусора на площадке:", json_data["trash_outside_status"])
        else:
            print(f"Ошибка запроса: {response.status_code}")
    except Exception as e:
        print("Ошибка:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_data, "interval", seconds=20)  # Запускаем запрос каждые 20 секунд. Чтобы изменить период - измените значение seconds

scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()  # Останавливаем планировщик при завершении приложения