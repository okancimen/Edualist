#!/usr/bin/env python3
import os, json

BASE = '/Users/okancimen/Edualist/httpdocs/blog'

FAQS = {
    'turkiye-egitim-sistemi-neden-yetmiyor': [
        ('Türkiye PISA sıralamalarında nerede yer alıyor?',
         'Türkiye 2022 PISA değerlendirmesinde matematik ve okuma okuryazarlığında OECD ortalamasının belirgin biçimde altında kalmaktadır. Bu durum, Türkiye eğitim sisteminin uluslararası standartlara göre yapısal açıdan zayıf kaldığını göstermektedir.'),
        ('MEB müfredatı son 20 yılda kaç kez değişti?',
         "Milli Eğitim Bakanlığı müfredatı 2000'li yıllardan bu yana 17'den fazla kez köklü değişikliğe uğramıştır. Bu sık değişimler hem öğrencilerde hem öğretmenlerde istikrarsızlık yaratmakta ve uzun vadeli eğitim planlamasını zorlaştırmaktadır."),
        ('Türk eğitim sisteminden uluslararası okula geçiş zor mu?',
         'Türk ulusal müfredatından IB veya İngiliz sistemine geçiş, özellikle akademik İngilizce, eleştirel düşünme ve proje tabanlı öğrenme alışkanlıkları açısından ciddi uyum gerektirmektedir. Profesyonel danışmanlık bu geçişi önemli ölçüde kolaylaştırır.'),
    ],
    'lise-yurt-disi-tasinma-adaptasyon': [
        ('Lise döneminde yurt dışına taşınmak üniversite başvurularını etkiler mi?',
         'Evet, önemli ölçüde etkiler. Özellikle IB Diploma veya A-Level programlarına lise döneminde geçiş, üniversite kabul hesaplamalarında ve burs başvurularında stratejik planlama gerektirir. Doğru zamanlama kariyer fırsatlarını artırabilir.'),
        ('Lise çağındaki bir çocuğun yurt dışına adaptasyon süreci ne kadar sürer?',
         'Akademik adaptasyon genellikle 1-2 sömestr, sosyal ve duygusal uyum ise 6-18 ay arasında değişmektedir. Dil desteği, okul seçiminin doğruluğu ve aile yaklaşımı bu süreci doğrudan belirlemektedir.'),
        ('Hangi müfredat lise dönemindeki geçişler için en uygundur?',
         'IB programı, farklı ülkelerden öğrencileri ortak bir çerçevede buluşturduğundan lise dönemindeki geçişler için en esnek seçenektir. Mevcut derslerin tanınması ve kredi transferi en kolay IB sisteminde gerçekleşmektedir.'),
    ],
    'bae-uluslararasi-okul-rehberi': [
        ("BAE'de kaç uluslararası okul var?",
         "BAE genelinde 1.600'den fazla uluslararası okul faaliyet göstermektedir. Dubai'deki okullar KHDA (Bilgi ve İnsani Kalkınma Kurumu), Abu Dhabi'dekiler ise ADEK tarafından denetlenmektedir."),
        ("Dubai ve Abu Dhabi'deki okul sistemleri arasındaki fark nedir?",
         "Dubai'de okullar KHDA tarafından derecelendirilir ve 200'den fazla uluslararası okul bulunur; müfredat çeşitliliği yüksektir. Abu Dhabi'deki okullar ADEK denetimine tabidir. Her iki şehirde de IB ve İngiliz müfredatı yaygındır."),
        ("BAE'de en yaygın uluslararası müfredat hangisi?",
         "BAE'de British (GCSE/A-Level) müfredatı en yaygın seçenektir. IB programı ise en hızlı büyüyen müfredat olup expatriyat ailelerin tercihi olarak öne çıkmaktadır. Amerikan (AP) ve Fransız (Baccalauréat) müfredatları da belirli okullarda mevcuttur."),
    ],
    'kizim-sinifin-zemininde-yatiyordu': [
        ('Çocuğumun yanlış okula gittiğini nasıl anlarım?',
         'Okul korkusu, sürekli karın/baş ağrısı, sosyal çekilme, akademik motivasyon kaybı ve öğretmenden şikayet gibi belirtiler yanlış okul seçiminin işaretleri olabilir. Bu belirtilerin devam etmesi halinde profesyonel bir değerlendirme alınması önerilir.'),
        ('Uluslararası okul seçiminde en sık yapılan hata nedir?',
         "En yaygın hata, okulun derecelendirmesine veya ücretine göre seçim yapmak ve çocuğun bireysel profilini (dil seviyesi, öğrenme stili, sosyal yapısı) göz ardı etmektir. Doğru okul, en iyi okul değil; çocuk için en uygun okultur."),
        ('Okul değiştirmek çocuk için zararlı mı?',
         'Doğru gerekçeyle ve doğru zamanda yapılan okul değişikliği çocuğa zarar vermez. Yanlış ortamda geçirilen uzun süreden daha az hasar bırakır. Geçiş süreci profesyonel destekle yönetildiğinde çocuklar yeni ortama genellikle 1-2 dönemde uyum sağlar.'),
    ],
    'oglumun-ingilizcesi-iyiydi': [
        ('EAL (İngilizce Ek Dil) nedir?',
         "EAL (English as an Additional Language), anadili İngilizce olmayan öğrencilerin akademik İngilizce becerilerini geliştirmesi için sunulan özel eğitim desteğidir. Uluslararası okulların çoğu EAL programları yürütmektedir; bu destek günlük konuşma değil, akademik dil becerilerini hedefler."),
        ('Akademik İngilizce ile günlük İngilizce arasındaki fark nedir?',
         'Günlük İngilizce (BICS) genellikle 1-2 yılda kazanılır. Akademik İngilizce (CALP) ise 5-7 yıl sürebilir ve ders anlatımını anlama, yazılı ifade ve analitik düşünme becerilerini kapsar.'),
        ("Çocuğumun İngilizce seviyesi uluslararası okul için yeterli mi, nasıl anlarım?",
         "Uluslararası okulların çoğu kendi giriş değerlendirmelerini yapar. Buna ek olarak Cambridge Placement Test veya bir EAL uzmanının yapacağı bireysel değerlendirme, çocuğun mevcut seviyesini netleştirir. Edualist bu değerlendirmeyi taşınma öncesinde gerçekleştirebilir."),
    ],
    'cocugunuz-yurt-disinda-okumaya-hazir-mi': [
        ("Çocuğun yurt dışında okumaya hazır olup olmadığını gösteren işaretler neler?",
         "Hazırlık beş boyutta değerlendirilir: duygusal dayanıklılık, dil yeterliliği (akademik İngilizce), akademik güç (bağımsız çalışma alışkanlığı), sosyal uyum ve aile desteği. Bu boyutlarda eksikler varsa geçiş öncesi hazırlık planlanmalıdır."),
        ("Kaç yaşındaki çocuklar yurt dışında okumaya hazır sayılır?",
         "Yurt dışında okuma için belirlenmiş bir minimum yaş yoktur; hazırlık yaşa değil, bireysel profile bağlıdır. İlkokul dönemindeki çocuklar (6-10 yaş) dil ve sosyal uyumda en hızlı ilerlemeyi gösterirken, lise döneminde akademik gereksinimler ön planlama gerektirir."),
        ("Yurt dışı eğitim kararını vermeden önce hangi adımlar atılmalı?",
         "Öncelikle çocuğun dil düzeyi, duygusal olgunluğu ve akademik geçmişi değerlendirilmeli; ardından hedef ülke/şehir ve müfredat araştırması yapılmalı, bütçe planlanmalı ve okul araştırması taşınmadan en az 12 ay önce başlatılmalıdır."),
    ],
    'turk-egitim-sisteminden-uluslararasi-okula-gecis': [
        ("Türkiye'deki özel okul diplomasının uluslararası geçerliliği var mı?",
         "Türkiye'deki devlet veya özel okul diplomaları yabancı ülkelerde doğrudan kabul görmeyebilir; denklik başvurusu gerekebilir. IB veya Cambridge programını uygulayan Türk özel okullarından alınan diplomalar daha geniş uluslararası tanınırlığa sahiptir."),
        ("Türk müfredatından IB programına geçişte en zor konu nedir?",
         "En yaygın zorluk, ezber odaklı çalışma alışkanlığından araştırma ve eleştirel düşünme temelli IB yaklaşımına geçiştir. Extended Essay, Theory of Knowledge ve CAS programı Türk öğrenciler için ilk dönemde en büyük uyum alanlarıdır."),
        ("Uluslararası okula geçişte hangi dersler en fazla zorlanmaya neden olur?",
         "Akademik İngilizce gerektiren dersler (Edebiyat, Tarih, İnsan Bilimleri) ile matematiksel muhakeme vurgulu Matematik genellikle en yüksek uyum gerektirir. Fen bilimleri deney ve gözlem odaklı yaklaşımıyla Türkiye'deki uygulamalı eğitim zayıflığını ortaya çıkarabilir."),
    ],
    'dubai-en-iyi-uluslararasi-okullar': [
        ("KHDA nedir ve okul derecelendirmesi nasıl çalışır?",
         "KHDA (Knowledge and Human Development Authority), Dubai'deki özel okul ve kreşleri denetleyen resmi kurumdur. Okulları Outstanding, Very Good, Good, Acceptable ve Weak olmak üzere beş kategoride değerlendirir. Raporlar khda.ae adresinde kamuya açıktır."),
        ("Dubai'de kaç tane KHDA Outstanding okul var?",
         "2023-24 KHDA denetim döneminde Dubai'de 23 okul 'Outstanding' (Üstün) derecesini almıştır. Bu okullar arasında IB, British ve Amerikan müfredatı uygulayan kurumlar bulunmaktadır."),
        ("KHDA derecelendirmesi okul seçiminde tek belirleyici olmalı mı?",
         "KHDA derecelendirmesi önemli bir başlangıç göstergesidir, ancak tek belirleyici olmamalıdır. Çocuğun dil seviyesi, ailenin bütçesi, ulaşım mesafesi, müfredat tercihi ve okulun kültürel atmosferi de en az derecelendirme kadar belirleyici faktörlerdir."),
    ],
    'uluslararasi-okul-mulakatı-nasil-gecilir': [
        ("Uluslararası okul mülakatında çocuğa hangi sorular sorulur?",
         "Çocuk mülakatlarında genellikle kendini tanıtma, hobiler ve ilgi alanları, önceki okul deneyimleri, yeni ülkeye ilişkin düşünceler ve İngilizce iletişim becerisi değerlendirilir. Bazı okullar kısa bir matematiksel veya sözel beceri sorusu da ekleyebilir."),
        ("Ebeveyn görüşmesinde okullar ne sorar?",
         "Ebeveyn görüşmelerinde genellikle taşınma gerekçesi, çocuğun eğitim geçmişi, dil seviyesi, güçlü ve zayıf yönleri, beklentiler ve olası uyum endişeleri ele alınır. Bu görüşme aynı zamanda ailenin okul değerleriyle uyumunu ölçmek için de kullanılır."),
        ("Uluslararası okul başvurusunda genellikle hangi belgeler istenir?",
         "Çoğu uluslararası okulda başvuru için pasaport kopyası, son 2 yılın okul transkripti, öğretmen referans mektubu, aşı belgesi ve ülkeye göre değişen oturma izni veya vize belgesi talep edilmektedir."),
    ],
    'kanada-okul-kayit-rehberi': [
        ("Kanada'da yabancı öğrenciler devlet okuluna ücretsiz gidebilir mi?",
         "Kanada'da kalıcı oturum izni (PR) veya belirli vize türlerine sahip aileler devlet okullarına ücretsiz erişebilmektedir. Öğrenci vizesiyle gelen çocuklar genellikle yıllık 10.000-14.000 CAD arasında okul harcı ödemektedir."),
        ("Ontario ve BC okul sistemleri arasındaki en önemli fark nedir?",
         "Ontario 12 yıllık sistemde OSSD (Ontario Secondary School Diploma) verir; BC benzeri bir diploma sistemiyle French Immersion seçeneklerini ön plana çıkarır. Her iki eyalet de güçlü IB programı sunan okullara sahiptir."),
        ("Kanada'da okul kaydı için hangi belgeler gerekli?",
         "Kanada devlet okulu kaydı için genellikle pasaport/doğum belgesi, ikamet kanıtı, aşı kayıtları ve önceki okul transkriptinin noter onaylı İngilizce çevirisi talep edilmektedir."),
    ],
    'ucuncu-kultur-cocugu-tck-rehberi': [
        ("Üçüncü kültür çocuğu (TCK) nedir?",
         "Üçüncü kültür çocuğu (Third Culture Kid – TCK), gelişim yıllarının önemli bir bölümünü ebeveynlerinin kültüründen farklı bir veya birden fazla ülkede geçiren çocuklardır. Birden fazla kültürden beslenen ancak bunların hiçbirine tam anlamıyla ait olmayan kendine özgü bir kimlik geliştirirler."),
        ("TCK çocukların en sık yaşadığı zorluklar neler?",
         "TCK çocukların en sık yaşadığı zorluklar arasında kimlik belirsizliği, sürekli veda ve kayıp duygusu, köksüzlük hissi ve ergenlik döneminde aidiyet arayışı yer almaktadır. Bununla birlikte çok dilli olmak, kültürel esneklik ve küresel bakış açısı TCK'ların en güçlü yanlarıdır."),
        ("Ebeveynler TCK çocuklarını nasıl destekleyebilir?",
         "TCK çocukları desteklemek için güçlü bir aile kültürü oluşturmak, her ülkedeki anıları belgelemek, sık veda süreçleri için duygusal hazırlık yapmak ve TCK topluluklarıyla bağlantı kurmak etkili stratejiler arasında yer almaktadır."),
    ],
    'cocugumu-yurtdisinda-okutmali-miyim': [
        ("Çocuğumu yurt dışında okutmanın en büyük avantajları neler?",
         "Yurt dışında eğitimin başlıca avantajları arasında çok dilli yetkinlik, kültürel zeka ve küresel ağ oluşturma kapasitesi yer almaktadır. IB veya A-Level gibi uluslararası müfredatlar dünya genelindeki üniversitelere başvuruyu kolaylaştırırken, expatriyat deneyimi bağımsızlık ve uyum becerisini güçlendirir."),
        ("Yurt dışında eğitimin dezavantajları neler?",
         "Yurt dışı eğitimin zorlukları arasında yüksek maliyetler, dil bariyeri, Türkiye'deki aile ve sosyal çevreden kopukluk, kimlik karmaşası ve okul geçişlerinde uyum zorlukları sayılabilir. Doğru hazırlık ve profesyonel danışmanlık bu riskleri önemli ölçüde azaltır."),
        ("Çocuğumu yurt dışında okutma kararını nasıl vermeliyim?",
         "Bu kararı verirken çocuğun yaşı, dil seviyesi ve karakteri; ailenin mali durumu ve taşınma planları; hedef ülkedeki yaşam koşulları ve okul kalitesi birlikte değerlendirilmelidir. Bir eğitim danışmanıyla ön görüşme bu kararı daha sağlıklı bir zemine oturtmaya yardımcı olur."),
    ],
    'yurtdisi-egitim-maliyet-karsilastirma': [
        ("Hangi ülkedeki uluslararası eğitim en uygun fiyatlı?",
         "Uluslararası eğitimde en uygun ücretler genellikle Almanya ve Hollanda'daki devlet okullarında görülmektedir. Özel uluslararası okullar arasında Almanya ve İtalya'daki seçenekler Dubai veya Londra'ya kıyasla daha erişilebilir ücretler sunabilmektedir."),
        ("Dubai ve İngiltere uluslararası okul ücretleri nasıl karşılaştırılır?",
         "Dubai'de yıllık öğretim ücreti 25.000-120.000 AED (6.800-32.700 USD) arasında değişirken, Londra'daki bağımsız okullarda yıllık ücretler 15.000-45.000 GBP (19.000-57.000 USD) seviyelerine ulaşabilmektedir. Yaşam maliyeti dahil edildiğinde Londra genel olarak daha pahalıdır."),
        ("Yurt dışı eğitim maliyetini düşürmenin yolları var mı?",
         "Yurt dışı eğitim maliyetini azaltmak için burs ve finansal yardım başvuruları, işveren eğitim katkısı (education allowance), devlet okullarının tercih edilmesi ve erken başvuru indirimleri değerlendirilebilir. IB ve A-Level okullarının çoğu akademik başarı bursu sunmaktadır."),
    ],
    'ib-alevel-amerikan-mufredat-karsilastirma': [
        ("IB programı mı, A-Level mi, Amerikan AP sistemi mi daha prestijli?",
         "Üç sistem de dünya genelinde saygın üniversiteler tarafından kabul görmektedir. IB en geniş küresel tanınırlığa sahipken, A-Level İngiltere ve Commonwealth ülkeleri için tercih edilir; AP ise ABD üniversiteleri için avantaj sağlar. Seçim prestije değil, çocuğun hedeflerine ve öğrenme stiline göre yapılmalıdır."),
        ("IB Diploma Programı kaç yıl sürer ve nasıl değerlendirilir?",
         "IB Diploma Programı (DP) 16-19 yaş arası için iki yıllık bir programdır. Öğrenciler 6 farklı konu grubundan ders alır; ayrıca Extended Essay, Theory of Knowledge ve CAS programını tamamlamalıdır. Toplam 45 puan üzerinden değerlendirme yapılır; 24 puan ve üzeri diploma almak için yeterlidir."),
        ("IB mi, A-Level mi Türkiye'deki üniversiteler için daha avantajlı?",
         "Her iki sistem de YÖK denklik hesaplamasında kullanılmaktadır. IB Diploma'nın 45 puan üzerinden yapılan değerlendirmesi ve A-Level'in konu bazlı sistemi YÖK tabloları aracılığıyla Türkçe üniversite puanlarına dönüştürülmektedir. Hangi sistemin daha avantajlı olduğu, hedef üniversite ve bölüme göre değişir."),
    ],
    'dubai-school-guide': [
        ("Dubai'ye taşınmadan önce okul araştırmasına ne zaman başlamalıyım?",
         "Dubai'deki popüler uluslararası okullarda bekleme listeleri 12-18 ay öncesine uzanabilmektedir. Taşınma kararını verdikten hemen sonra, hatta Türkiye'deyken okul araştırmasına başlamak ve 2-3 okula ön başvuru yapmak kritik öneme sahiptir."),
        ("Dubai'de aileler için en uygun semt hangisi?",
         "Dubai'de Jumeirah ve Al Wasl köklü İngiliz okullarıyla; Arabian Ranches ve Motor City IB ağırlıklı topluluk yapısıyla; Dubai Hills ise yeni gelişen altyapısıyla öne çıkmaktadır. En doğru semt seçimi, çocuğun okul lokasyonuna ve sabah trafiğine göre yapılmalıdır."),
        ("KHDA nedir ve Dubai okul seçiminde nasıl kullanılır?",
         "KHDA (Knowledge and Human Development Authority), Dubai'deki tüm özel okul ve kreşleri denetleyen resmi kurumdur. Okulları yıllık olarak Outstanding, Very Good, Good, Acceptable ve Weak şeklinde değerlendirir. khda.ae adresinden güncel raporlara ücretsiz ulaşılabilir."),
    ],
    'ingiltere-okul-kayit-rehberi': [
        ("İngiltere'de state school ile independent school arasındaki fark nedir?",
         "State school (devlet okulu) İngiltere'de yasal oturum hakkı olan aileler için ücretsizdir ve devlet müfredatını uygular. Independent school (bağımsız okul) ise yıllık 15.000-45.000 GBP arasında değişen ücretlerle; daha küçük sınıf mevcutları ve prestijli üniversitelere yüksek yerleştirme oranlarıyla öne çıkar."),
        ("11+ sınavı nedir ve nasıl hazırlanılır?",
         "11+ sınavı İngiltere'de bazı eyaletlerde grammar school (seçici devlet okulu) kabulü için 10-11 yaşında uygulanan değerlendirmedir. Sözel muhakeme, sayısal muhakeme, İngilizce ve matematik içerir. Yoğun bir hazırlık süreci (genellikle 6-12 ay) ve özel koçluk yaygın olarak kullanılmaktadır."),
        ("Ofsted derecelendirmesi okul seçiminde ne kadar belirleyici?",
         "Ofsted (Eğitim, Çocuk Hizmetleri ve Beceriler Ofisi) İngiliz okullarını Outstanding, Good, Requires Improvement ve Inadequate olarak derecelendirir. Bu derecelendirme önemli bir göstergedir ancak tek kriter olmamalıdır; sınıf kültürü, EAL desteği ve çocuğun bireysel ihtiyaçları da göz önüne alınmalıdır."),
    ],
    'fransa-okul-kayit-rehberi': [
        ("Fransa'da okula kayıt için hangi belgeler gerekli?",
         "Fransa'da devlet okulu kaydı için genellikle pasaport veya kimlik belgesi, ikamet kanıtı, aşı kartı (DTP ve ROR zorunlu) ve önceki okul belgelerinin Fransızca tercümesi talep edilmektedir. Kayıt Mairie (belediye) üzerinden yapılmaktadır."),
        ("Baccalauréat nedir ve uluslararası geçerliliği var mı?",
         "Fransız Baccalauréat (Bac), lise sonunda alınan ve üniversite girişi için kullanılan ulusal sınavdır. Türkiye dahil pek çok ülkede denklik için başvurulabilmektedir. Uluslararası Bac (IB) ile karıştırılmamalıdır; Fransız Bac Fransa dışında daha az tanınırlığa sahiptir."),
        ("Fransa'da uluslararası bölümler (Section Internationale) nedir?",
         "Fransa'daki bazı devlet liseleri, yabancı dilde eğitim veren Uluslararası Bölümler (OIB) sunmaktadır. Bu bölümlerde Fransızca yanı sıra İngilizce, Almanca, İspanyolca gibi dillerde ağırlıklı ders alınabilmektedir; Türk aileler için iyi bir geçiş seçeneğidir."),
    ],
    'hollanda-okul-kayit-rehberi': [
        ("Hollanda'da VWO, HAVO ve VMBO arasındaki fark nedir?",
         "VWO (6 yıl) üniversiteye hazırlayan en akademik izdir; HAVO (5 yıl) mesleki yükseköğretime hazırlarken VMBO (4 yıl) mesleki eğitime yönlendirir. Türk öğrenciler bu izkuruma genellikle 7. sınıfta CITO testi ve öğretmen görüşüyle yönlendirilir."),
        ("Hollanda'da yabancı öğrenciler için ISK programı nedir?",
         "ISK (Internationale Schakelklas – Uluslararası Geçiş Sınıfı), yeni gelen yabancı öğrencilerin Hollandacayı öğrenmesi ve Hollanda okul sistemine hazırlanması için tasarlanmış 1-2 yıllık bir geçiş programıdır."),
        ("Hollanda'da okul kaydı için hangi belgeler gerekli?",
         "Hollanda'da devlet okulu kaydı için pasaport, BSN numarası, ikamet adresi kanıtı ve önceki okul belgelerinin resmi çevirisi talep edilmektedir. BSN numarası almak için Gemeente'ye kayıt yaptırılması gerekmektedir."),
    ],
    'italya-okul-kayit-rehberi': [
        ("İtalya'da Codice Fiscale nedir ve okul kaydı için neden gerekli?",
         "Codice Fiscale, İtalya'daki her türlü resmi işlem için zorunlu olan bireysel vergi kimlik numarasıdır. Okul kaydı, sağlık hizmetleri ve kamu kurumlarıyla tüm işlemler için bu numaraya ihtiyaç duyulur. Agenzia delle Entrate'den ücretsiz alınabilmektedir."),
        ("İtalya'da Liceo Scientifico ve Liceo Classico arasındaki fark nedir?",
         "Liceo Scientifico matematik ve fen bilimlerini ön plana çıkarırken, Liceo Classico Latince ve Eski Yunanca ağırlıklı klasik eğitim sunar. Yabancı öğrenciler için Liceo Scientifico'nun daha evrensel içeriği tercih sebebidir."),
        ("İtalya'da uluslararası okul ücretleri ne kadar?",
         "İtalya'daki uluslararası okullarda yıllık öğretim ücreti genellikle 8.000-25.000 EUR arasındadır. Dubai veya Londra'ya kıyasla İtalya daha uygun maliyetli bir uluslararası eğitim seçeneği sunmaktadır."),
    ],
    'almanya-okul-kayit-rehberi': [
        ("Almanya'da okul için Almanca zorunlu mu?",
         "Alman devlet okullarında öğretim dili büyük ölçüde Almancadır. Yeni gelen öğrenciler için Willkommensklasse (hoş geldin sınıfı) gibi dil destek programları mevcuttur. Uluslararası okullar ise İngilizce veya iki dilli eğitim sunarak Almanca bilmeden kayıt imkânı tanımaktadır."),
        ("Almanya Gymnasium'a nasıl girilir?",
         "Almanya'da Gymnasium'a (üniversiteye hazırlayan lise kolu) geçiş genellikle 4. sınıf sonunda öğretmen tavsiyesiyle belirlenir. Bazı eyaletlerde veli isteği ve öğrenci başarısı birlikte değerlendirilir."),
        ("Almanya'da okul kaydı için hangi belgeler gerekli?",
         "Almanya'da okul kaydı için Anmeldung (oturma kaydı belgesi), pasaport, aşı kartı ve önceki okul belgelerinin Almanca onaylı çevirisi talep edilmektedir. Kayıt yerel Schulamt veya doğrudan okul aracılığıyla yapılmaktadır."),
    ],
    'dubai-okul-kayit-rehberi': [
        ("Dubai'de okul kaydı için hangi belgeler gerekli?",
         "Dubai'de uluslararası okul kaydı için pasaport kopyası (öğrenci ve ebeveyn), Emirates ID, vize veya oturma izni belgesi, önceki okul transkripti (noter onaylı ve İngilizce çevirisiyle), aşı kartı ve pasaport fotoğrafı talep edilmektedir."),
        ("Dubai'de okul başvurusu ne zaman yapılmalı?",
         "Dubai uluslararası okullarında akademik yıl Eylül'de başlamaktadır. Popüler KHDA Outstanding okullarına başvurular için en geç bir önceki yılın Ocak-Mart döneminde harekete geçmek gerekmektedir. Bekleme listeleri olan okullar için 12-18 ay öncesinden planlama yapılması önerilir."),
        ("KHDA online portalı okul seçiminde nasıl kullanılır?",
         "khda.ae adresi üzerinden Dubai'deki tüm özel okulların denetim raporlarına, derecelendirme geçmişine ve okul bilgi sayfalarına ücretsiz ulaşılabilmektedir. Arama filtrelerini kullanarak müfredata, bölgeye ve derecelendirmeye göre okul listesi oluşturulabilmektedir."),
    ],
}

def build_schema(faqs):
    items = []
    for q, a in faqs:
        items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return json.dumps(schema, ensure_ascii=False, indent=2)

ok = 0
skip = 0
missing = 0

for slug, faqs in FAQS.items():
    filepath = os.path.join(BASE, slug, 'index.html')
    if not os.path.exists(filepath):
        print(f"NOT FOUND: {slug}")
        missing += 1
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if '"@type": "FAQPage"' in content or '"@type":"FAQPage"' in content:
        print(f"SKIP: {slug}")
        skip += 1
        continue
    block = '\n  <!-- FAQ Schema -->\n  <script type="application/ld+json">\n' + build_schema(faqs) + '\n  </script>\n'
    new_content = content.replace('</head>', block + '</head>', 1)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"OK: {slug}")
    ok += 1

print(f"\nDone — {ok} updated, {skip} skipped, {missing} not found")
