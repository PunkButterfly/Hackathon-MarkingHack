# Система предиктивной аналитики рынка

[Ссылка на веб-сервис](https://ten-numbers-glow-217-197-0-160.loca.lt/) (доступно по тунельному соединению) 

## Концепция 
В рамках хакатона MARKING HACK команда Punk Butterfly разработала сервис, взаимодействующий с системой маркировки "ЧЕСТНЫЙ ЗНАК", с помощью которого государство может выявлять потенциально подозрительные на мошенничество точки продажи, выявлять монополии среди поставщиков, а также регионы, в которых потенциально может возникнуть дефицит на товары.

## Описание алгоритмов 

### Аналитика показателей дистрибьютеров

Государству интересно видеть аномальные показатели продаж для выявления потенциально подозрительных торговых точек.

В качестве бейзлайна для проведения аналитики мы используем показатели цены:  
**Аномально высокую минимальную цену** у ретейлера на товар с конкретным `gtin` относительно окружающих его регионов. Смотрим, какой ретейл продал выбранный `gtin` в регионе по минимальной цене в заданный промежуток времени. Государство видит карту регионов, где регионы имеют соответствующую раскраску, исходя из показателя минимальный цены на данный товар.  
> Дополнительно могут быть рассмотрены объемы продаж и разнообразие товаров, продаваемых ритейлером.  

На сайте - страница Analytics

### Индекс Хиршмана-Херфиндаля
Мы использовали индекс Хиршмана-Херфиндаля для поиска монополий среди поставщиков. Для каждого `TNVED10` суммируется общее количество товаров у каждого `INN`. Далее считается доля `INN`, как доля товаров одного `INN` на сумму товаров 

Пусть у нас есть $I = \overline{1,m}$ разных видов товара (в нашем решении вид товара $\Leftrightarrow$ `TNVED10`). Пусть так же есть $J = \overline{1,n}$ ИНН, производящих продукцуию типов $I$. Тогда 
$HHI_I = s_1^2 + s_2^2 + \ldots + s_n^2$ -- индекс Хиршмана-Херфиндаля, где 
* $s_j$ - доля товаров фирмы $J$ на общее количетсво количество товаров типа $I$: $$s_j = \frac{\text{число товаров типа I у INN = J}}{\sum_j \text{(число товаров типа I)}}$$

С помощью этого подхода мы получаем список `TNVED10`, ранжированный по индексу. После чего можно посмотреть список `INN`, отранжированный по количеству производимой продукции типа `TNVED10`.


На сайте - страница Deviance

### Прогнозирование спроса по регионам в разрезе gtin
Когда возникает локальный дефицит товара, государство заинтересовано в предотвращении этого дефицита, поэтому ему (государству) выгодно привлекать производителей товара в регион, где ожидается резкий скачек роста на спрос по товару (группе товаров). 

Для предотвращения дефицита мы разработали систему прогнозирования спроса на конкретный `gtin` в конкретном регионе. В качестве модели используется нейронная сеть LSTM, обучающаяся на данных о спросе для каждой уникальной пары (`gtin`, `reg_id`), а затем считающая предсказания спроса на 12 недель вперед. В рамках хакатона для увеличения скорости вычислений мы решили взять только 100 уникальных `gtin` самых популярных (по спросу).

В системе можно увидеть карту регионов, на которой при вводе `gtin` подсвечиваются регионы с максимальной введеной нами **метрикой**. Пусть
* $\text{predicted window max}$ -- максимальное значение известного спроса за последние 12 недель
* $\text{previous window max}$ -- максимальное значение предсказанного спроса за следующие 12 недель.

Тогда **метрика** вводится как 

$$\text{metric}:=\frac{\text{predicted window max} - \text{previous window max}}{\text{previous window max}}$$

Чем **больше** это значение, тем более резкий скачок роста спроса на товар может произойти в регионе. 

Данная разработка может помочь государству выделить регионы, в которые стоит привлечь поставщиков конкретных товаров. Для привлечения можно использовать льготы, по типу освобождения от налогов и т.п.

На сайте - страница Predicting Demand 

### Прогнозирование спроса и поставок товаров в стране
Также мы разработали систему одновременного предсказания ввода товара в оборот и вывода товара из оборота относительно всей страны (без деления по регионам).

Для этого так же использовались сети LSTM.

Для каждого gtin строится график с предсказаниями ввода и вывода товара на 60 дней вперед. Для оценки снова была введена метрика. Пусть 
* $\text{last predicted enty cumsum}$ -- последнее предсказанное значение количества введеного товара.
* $\text{last predicted sold cumsum}$ -- последнее предсказанное значение количество выведенного из оборота товара

Тогда мeтрика считается как:

$$\text{metric}:=\frac{\text{(last predicted enty cumsum} - \text{last predicted sold cumsum}}{\text{last predicted enty cumsum}}$$

Метрика показывает насколько процентов предсказанный вывод товара из оборота меньше ввода в оборот. Чем ниже процент, тем больше в стране требуется конкретного товара (отрицательный процент означает, что вывод товара превысит поставки). 

На сайте - страница Predicting General 

## Развернутый прототип 

## Исходный код
Исходный код веб-сервиса, обработки данных и построения предиктов моделями находится в [github-репозитории](https://github.com/PunkButterfly/Hackathon-MarkingHack).

Дерево файлов в репозитории

```
pages
├── Analytics.py <- аналитика по дистрибьютерам, вывод страницы Analytics
├── Deviance.py <- поиск монополий по индексу Хиршмана-Херфиндаля, вывод страницы Deviance
├── Predicting.py <- прогнозирование спроса по регионам, вывод страницы Predicting
└── PredictingEntity.py <- прогнозирование спроса и поставок по стране, вывод страницы PredictingEntity
prediction_models
├── regs
│   └── build_reg_graphs.py <- обучение модели, получение предсказаний по спросу в регионах для страницы Predicting
└── rus
    └── build_rus_graphs.py <- обучение модели, получение предсказаний спроса по стране для страницы PredictingEntity
```
