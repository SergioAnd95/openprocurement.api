��          �      l      �     �     �     �  m     2  �  #   �  )   �       !   "     D     b     j  0   x  �   �  &   c  D   �  E   �  a     X   w  �   �  >  {     �	     �	  ;   �	  �    
  I  �
  W   I  N   �  6   �  G   '  A   o     �     �  g   �  )  I  U   s  h   �  m   2  �   �  �   L  R  �                         
                                 	                                        Batching Example request: Getting list of all tenders If next page request returns no data (i.e. empty array) then there is little sense in fetching further pages. It is often necessary to be able to syncronize central database changes to other database (we'll call it "local").  The default sorting "by modification date" altogether by Batching mechanism allows one to implement synchronization effectively.  The synchronization process can go page by page until there is no new data returned.  Then the synchronizer have to pause for a while to let central database register some changes and attempt fetching subsequent page.  The `next_page` guarantees to have all changes from the last request to be included in new batch. Limiting number of Tenders returned Reading the individual tender information Reading the tender document Reading the tender documents list Retrieving Tender Information Sorting Synchronizing Tenders retuned are sorted by modification time. The document can be retrieved by requesting the url returned in structures from document list request in `data[*].url`.  It is safe to provide the download URL to end user for download. The full version of URL for next page. The response contains `next_page` element with following properties: The safe frequency of synchronization requests is once per 5 minutes. This is path section of URL with original parameters and `offset` parameter added/replaced above. This is the parameter you have to add to the original request you made to get next page. You can control the number of `data` entries in the tenders feed (batch size) with `limit` parameter. If not specified, data is being returned in batches of 100 elements. Project-Id-Version: openprocurement.api 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2014-10-29 12:11+0200
PO-Revision-Date: 2014-11-10 12:18+0300
Last-Translator: 
Language-Team: LANGUAGE <LL@li.org>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 1.5.4
 Пакети Приклад запиту: Отримати список всіх закупівель Якщо запит наступної сторінки повертається без даних (наприклад, пустий масив), тоді немає сенсу викликати сторінки далі. Часто необхідно мати можливість синхронізувати зміни центральної бази даних з іншою базою даних (ми будемо називати її "локальною"). Стандартне сортування "за датою модифікації" разом із механізмом пакетування дозволяє ефективно здійснювати синхронізацію. Процес синхронізації може виконуватись посторінково, поки не буде жодних нових даних, що повертаються. Тоді синхронізатор призупиниться на деякий час, щоб дозволити центральній базі даних зареєструвати деякі зміни і спробувати завантажити наступну сторінку. `next_page` гарантує, що усі зміни з останнього запиту будуть включені у новий пакет. Обмежити кількість Закупівель, що повертаються Прочитати інформацію про окремі закупівлі Прочитати документ закупівлі Прочитати список документів закупівлі Отримання інформації про закупівлі Сортування Синхронізація Повернені закупівлі просортовані за датою модифікації.  Документ можна отримати за допомогою запиту url-адреси з відповіді на запит списку документів у `data[*].url`. URL для скачування безпечно надавати кінцевому користувачу. Повна версія URL-адреси для наступної сторінки.  Відповідь містить елемент `next_page` з такими властивостями: Безпечна частота запитів на синхронізацію це раз в 5 хвилин. Це частина шляху URL-адреси з вихідними параметрами та доданим/заміненим `offset` параметром вище. Це параметр, який ви повинні додати до вихідного запиту, щоб отримати наступну сторінку.  Ви можете контролювати кількість `data` записів потоку даних закупівлі (розмір пакета) за допомогою параметра `limit`. Якщо він не вказаний, то дані будуть повернені пакетами по 100 елементів.  