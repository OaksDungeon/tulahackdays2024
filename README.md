# tulahackdays2024
## Цель проекта

Разработка и внедрение механизма анализа фотоматериалов, поступающих в Систему управления потоками отходов региона, для автоматического выявления и контроля нарушений, обеспечения своевременной реакции на проблемы с вывозом ТКО и содержанием контейнерных площадок, а также предоставления аналитической информации для повышения эффективности управления отходами.

## Ключевые функции

- 🔍 **Обнаружение мусора**: Используя YOLO (You Only Look Once), наша модель способна обнаруживать мусор внутри контейнеров и снаружи их и сохранять значение датчиков наличия мусора
  
- 🗒️ **Сохранение истории**: В системе сохраняются все обнаруженные нарушения на контейнерных площадках

- 🫳 **Интерактивная карта**: В пользовательском интерфейсе реализована интерактивная карта города, на котором отмечены кликабельные маркеры соответсвующие местоположению контейнерных площадок, которые перенаправляют на соответсвующую страницу

- 📊 **Тестирование функционала**: Реализована система тестирования функционала программы с помощью загрузки пользовательского изображения

- ⬇️ **Потоковая проверка**: Помимо прочего функционала, программа в фоне автоматически проверяет поток фотографий каждые 20 секунд (период выбран в связи с малой мощностью устройства и может быть уменьшен) и проводит анализ каждого кадра с помощью нейронной сети

## Как начать

1. Убедитесь, что ваша среда соответствует требованиям из `requirements.txt` (так же вам необходим установленный Python3, Uvicorn).
2. Скачайте и распакуйте папки `server` и `client`
3. Запустите API-сервер, перейдя по пути `server` и выполнив команду `uvicorn base:app --host 0.0.0.0 --port 8000`.
4. Откройте все `.html` файлы в папке `client` и найдите переменную `url`. Вставьте в нее адрес сервера на котором запущено API-приложение или `http://127.0.0.1:8000` если запуск сервера происходит на том же устройстве, на котором открывается веб-приложение. Повторите в каждом HTML-файле
5. В каждом файлах `index.html`, `stream1.html` и `stream2.html` найдите строку `<script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU&apikey=ВАШ_КЛЮЧ" type="text/javascript"></script>` и вставьте ваш yandex-api ключ вместо ВАШ_КЛЮЧ
6. Откройте `index.html` в удобном Вам браузере

## Особенности

- **Масштабируемость**: Наш проект легко улучшить, использовав другие варианты моделей YOLO, что позволит изменить условия выделения объектов.

- **Современный дизайн**: Веб-интерфейс создан с учетом последних трендов в дизайне, обеспечивая вас приятным и продуктивным опытом, при этом сохраняя фирменный стиль сайта Tele2.

- **Открытый исходный код**: Мы приветствуем вклады и обратную связь от сообщества. Присоединяйтесь к нашему проекту и делитесь своим опытом!

## Инструкция по созданию нового маркера
1. Найдите на всех страницах (index.html, stream1.html, stream2.html) функцию "function initMap()" и массив points внутри данной функции</a>
2. После запятой последнего элемента внутри массива points вставьте строку "{ coords: [c_1, c_2], name: "adress", url: 'page'  }," без кавычек, где c_1 и c_2 - это координаты, adress - это адресс маркера, page - это путь к новой странице в формате "page.html"</a>
3. Вставьте следующий текст разметки в файл новой страницы:
```
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Главная страница</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU&apikey=ВАШ_КЛЮЧ" type="text/javascript"></script>
</head>
<body>
        <section class="header-back">
            <h1 class="text_h1_h">АДРЕС ТОЧКИ</h1>
    </section>
    <section class="main-back">

        <main>
            <div class="imagePreviewContainer">
                <button class="but" onclick="window.location.href='index.html';" style="display: flex; flex-direction: column; align-items: center; margin-top: 10 px;">Домой</button>

                <div id="response">
                    <h1 class="h1_main" style="display: flex; flex-direction: column; align-items: center; ">Изображение:</h1>
                    <img id="receivedImage" class="imagePreview" alt="Received from server" style="max-height: 500px; width: auto; display: none;">

                </div>
                                <div class="checkbox-container">
                    <label class="checkbox-label">
                        <input type="checkbox" id="containerCleanup">
                        <span class="custom-checkbox"></span>
                        Необходим вывоз мусора из контейнера
                    </label>
                    </div>
                    <div>
                    <label class="checkbox-label">
                        <input type="checkbox" id="territoryCleanup">
                        <span class="custom-checkbox"></span>
                        Необходим вывоз мусора с территории возле контейнера
                    </label>
                </div>
            </div>            
            <h1 class="h1_main">Интерактивная карта:</h1>
            <div id="map" class="map"></div>
        </main>
</section>

    <footer class="footer">
        <p>© 2024 Дубы подземелья</p>
    </footer>

    <script>
        url = 'АДРЕС_API_СЕРВЕРА'; // Адрес сервера с запущенным FastAPI
        window.addEventListener('load', async () => {

const formData = new FormData(); 
formData.append('file', ПУТЬ_К_ИЗОБРАЖЕНИЮ); 
    const response = await fetch(url + '/process', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
    }

    // Получение данных из ответа
    const data = await response.json();

    // Логирование полученных данных
    console.log("Response Data:", data);

    const trashStatus = data.trash_status;
    const trashOutsideStatus = data.trash_outside_status;

    // Логирование статуса
    console.log("trashStatus:", trashStatus);
    console.log("trashOutsideStatus:", trashOutsideStatus);

    // Преобразование base64 изображения в объект URL
    const imageUrl = `data:image/jpeg;base64,${data.image_base64}`;

    // Отображение изображения
    const imgElement = document.getElementById('receivedImage');
    imgElement.src = imageUrl;
    imgElement.style.display = 'block'; // Показываем изображение

    // Устанавливаем состояние чекбоксов в зависимости от полученных данных
    document.getElementById('containerCleanup').checked = trashStatus;
    document.getElementById('territoryCleanup').checked = trashOutsideStatus;

    } catch (error) {
console.log('1');    }
});


        // Инициализация Яндекс.Карты
        function initMap() {
            const map = new ymaps.Map('map', {
                center: [54.1553733711842, 37.5893092549873], // Центр карты
                zoom: 16, // Масштаб
            });

            const points = [ // Координаты маркеров
                { coords: [54.15452451410942, 37.59107416679381], name: "Вознесенского 9", url: 'stream1.html' },
                { coords: [54.15539871134127, 37.58658591280211], name: "Рязанская 4", url: 'stream2.html'  },
                НАСТРОЙКИ_НОВОГО_МАРКЕРА
            ];

            points.forEach(point => {
                const placemark = new ymaps.Placemark(point.coords, { iconCaption: point.name });
                placemark.events.add('click', () => {
                    window.location.href = point.url; // Переход по URL
                });
                map.geoObjects.add(placemark);
            });
        }

        ymaps.ready(initMap);
    </script>
</body>
</html>

```  
4. Настройте систему передачи изображения в скрипте и введите данные вместо заглушек
5. Сохраните изменения

## Демонстрация работы программы

![alt-text](demo.gif)


## О команде Oaks Dungeons
### Участники
- Сорокина Александра Валерьевна (капитан)
- Винтерголлер Тимофей Андреевич
- Овчинников Олег Александрович

### Описание
Команда, состоящая из студентов 3 курса Института Передовых Информационных Технологий.

**Соединим виртуальное и реальное, создадим будущее вместе!** 🚀🌟

*С любовью, команда Дубы Подземелья*



   
