# 🧬 Gezgin Satıcı Problemi (TSP) Çözümü — Genetik Algoritma Uygulaması

## 🚀 Proje Hakkında

Bu proje, **Gezgin Satıcı Problemi (TSP)** olarak bilinen NP-zor bir optimizasyon problemini **Genetik Algoritma (GA)** yaklaşımı ile çözmeyi amaçlamaktadır. Hedef, tüm şehirleri yalnızca bir kez ziyaret ederek başlangıç noktasına dönen **en kısa rotayı** bulmaktır.

Proje; algoritma parametrelerinin sistematik test edilmesini, farklı veri setlerinin işlenmesini ve sonuçların görselleştirilmesini sağlamaktadır.

---

## 🎯 Temel Hedefler

- TSP probleminin doğasını ve çözüm zorluklarını anlamak  
- Genetik Algoritma’nın operatörlerini (seçilim, çaprazlama, mutasyon) TSP’ye uyarlamak  
- Parametre ayarlamalarıyla algoritmanın performansını iyileştirmek  
- Elde edilen rotaları ve algoritma yakınsamasını **görselleştirmek**  

---

## 🔧 Özellikler

### 📂 Girdi Desteği
- **TSPLIB benzeri dosyalar** (.txt veya .tsp) desteği
- Her satır: `Şehir ID – X – Y` şeklinde koordinat bilgisi

### 🧬 Genetik Algoritma Bileşenleri
- **Kromozom Temsili:** Şehir sıralarının permütasyonuyla tur gösterimi  
- **Başlangıç Popülasyonu:** Rastgele oluşturulan bireyler  
- **Uygunluk Fonksiyonu:** Turun toplam **Öklid mesafesi**  
- **Seçilim:** Turnuva Seçimi  
- **Çaprazlama:** Order Crossover (OX1)  
- **Mutasyon:** Inversion Mutation (ters çevirme)  
- **Elitizm:** En iyi bireylerin korunması  

### ⚙️ Parametre Ayarlama (Grid Search)
- Popülasyon büyüklüğü  
- Jenerasyon sayısı  
- Çaprazlama ve mutasyon oranları  
- Turnuva boyutu  
- Elitizm oranı  
Tüm kombinasyonlar test edilerek **en iyi performans** bulunur.

### 📊 Görselleştirme
- En iyi turun grafiksel gösterimi  
- Jenerasyonlara göre **uygunluk yakınsama grafiği**


