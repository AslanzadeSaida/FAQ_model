# FAQ_model

Layihə: Azərbaycan Dillində FAQ Chatbot Modeli (RAG yanaşması ilə)
Bu layihə dövlət qurumlarına aid olan verilmiş üç linkdən FAQ məlumat bazasına əsaslanaraq istifadəçidən gələn sualı cavablandıran bir Telegram chatbot yaratmaq məqsədi daşıyır. Layihənin əsas hissələri aşağıdakı mərhələlərlə təşkil olunub:

1. Veb-Səhifədən Məlumat Toplanması (Scraping)
Tools: BeautifulSoup, requests, pandas

Description: Müxtəlif dövlət saytlarındakı FAQ bölmələrindən sual-cavab məlumatları çıxarılıb.

Result: Hər bir səhifədən çıxarılan məlumatlar .csv faylı şəklində saxlanılıb.

Yekun: merged_faq_data_file.csv

2. Embedding və ChromaDB-ə Yükləmə
Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

Features: Hər bir sual-cavab birləşdirilərək chunk-lara bölünüb (məs: 300 simvol + 15 simvol overlap).

ChromaDB istifadə olunaraq bu chunk-ların embedding-ləri çıxarılıb və lokal chroma_store direc yazılıb.

3. İstifadəçi Sualının Emalı (QA Modeli)
Step 1: Telegram istifadəçisinin sualı OpenAI GPT-4 ilə qrammatik düzəliş olunur.

Step 2: Düzəldilmiş sual ChromaDB-də axtarılır və ən uyğun chunk-lar tapılır (top_k=5).

Step 3: Sual və tapılan chunk-lar RAG formatında OpenAI GPT-4 modelinə göndərilir və cavab yaradılır.

Result: İstifadəçiyə qısa və dəqiq cavab təqdim olunur.

4. Telegram Bot İnteqrasiyası
İnteqrasiya: python-telegram-bot kitabxanası ilə edilmişdir.

Processing: İstifadəçi sual göndərir → arxa planda bütün proseslər işləyir → istifadəçiyə cavab qayıdır.

Əlavə xüsusiyyət: Hər mərhələdə logging əlavə olunub, beləliklə arxa planda baş verənlər tam şəkildə izlənilə bilər.

5. Ətraf Mühit Parametrləri (.env)
Bütün konfiqurasiya dəyişənləri .env faylına köçürülmüşdür:
"""
OPENAI_API_KEY=...
CHROMA_DB_DIR=chroma_store
MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CSV_PATH=merged_faq_data_file.csv
CHUNK_SIZE=300
OVERLAP=15
TOP_K=5"""
