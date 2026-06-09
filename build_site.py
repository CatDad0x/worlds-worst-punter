"""
Builds the WC 2026 First Shot On Target Edge Finder website.
UI matches the design spec exactly.
"""
import json, math, os
from datetime import datetime, timezone, timedelta

AEST = timezone(timedelta(hours=10))  # Brisbane — no daylight saving

CACHE = "cache"

def load(f):
    p = f"{CACHE}/{f}"
    return json.load(open(p)) if os.path.exists(p) else {}

# Complete WC 2026 squads — sourced from Al Jazeera / FIFA official lists
WC_SQUADS = {
    "Algeria": ["Oussama Benbot","Melvin Masstil","Luca Zidane","Achraf Abada","Rayan Ait Nouri","Zinedine Belaid","Rafik Belghali","Ramy Bensebaini","Samir Chergui","Jaouen Hadjam","Aissa Mandi","Mohamed Amine Tougai","Houssem Aouar","Nabil Bentaleb","Hicham Boudaoui","Fares Chaibi","Ibrahim Maza","Yassine Titraoui","Ramiz Zerrouki","Mohamed Amine Amoura","Nadir Benbouali","Adil Boulbina","Fares Ghedjemis","Amine Gouiri","Riyad Mahrez","Anis Hadj Moussa"],
    "Argentina": ["Emiliano Martinez","Geronimo Rulli","Juan Musso","Leonardo Balerdi","Gonzalo Montiel","Nicolas Tagliafico","Lisandro Martinez","Cristian Romero","Nicolas Otamendi","Facundo Medina","Nahuel Molina","Leandro Paredes","Rodrigo De Paul","Valentin Barco","Giovani Lo Celso","Exequiel Palacios","Alexis Mac Allister","Enzo Fernandez","Julian Alvarez","Lionel Messi","Nicolas Gonzalez","Thiago Almada","Giuliano Simeone","Nicolas Paz","Jose Manuel Lopez","Lautaro Martinez"],
    "Australia": ["Patrick Beach","Paul Izzo","Mathew Ryan","Aziz Behich","Jordan Bos","Cameron Burgess","Alessandro Circati","Milos Degenek","Jason Geria","Lucas Herrington","Jacob Italiano","Harry Souttar","Kai Trewin","Cameron Devlin","Ajdin Hrustic","Jackson Irvine","Connor Metcalfe","Aiden O'Neill","Paul Okon-Engstler","Nestory Irankunda","Mathew Leckie","Awer Mabil","Mohamed Toure","Nishan Velupillay","Cristian Volpato","Tete Yengi"],
    "Austria": ["Patrick Pentz","Alexander Schlager","Florian Wiegele","David Affengruber","David Alaba","Kevin Danso","Marco Friedl","Philipp Lienhart","Phillipp Mwene","Stefan Posch","Alexander Prass","Michael Svoboda","Christoph Baumgartner","Carney Chukwuemeka","Florian Grillitsch","Konrad Laimer","Marcel Sabitzer","Xaver Schlager","Romano Schmid","Alessandro Schopf","Nicolas Seiwald","Paul Wanner","Patrick Wimmer","Marko Arnautovic","Michael Gregoritsch","Sasa Kalajdzic"],
    "Belgium": ["Thibaut Courtois","Senne Lammens","Mike Penders","Timothy Castagne","Zeno Debast","Maxim De Cuyper","Koni De Winter","Brandon Mechele","Thomas Meunier","Nathan Ngoy","Joaquin Seys","Arthur Theate","Kevin De Bruyne","Amadou Onana","Nicolas Raskin","Youri Tielemans","Hans Vanaken","Axel Witsel","Charles De Ketelaere","Jeremy Doku","Matias Fernandez-Pardo","Romelu Lukaku","Dodi Lukebakio","Diego Moreira","Alexis Saelemaekers","Leandro Trossard"],
    "Bosnia & Herzegovina": ["Nikola Vasilj","Martin Zlomislic","Osman Hadzikic","Sead Kolasinac","Amar Dedic","Nihad Mujakic","Nikola Katic","Tarik Muharemovic","Stjepan Radeljic","Dennis Hadzikadunic","Nidal Celik","Amir Hadziahmetovic","Ivan Sunjic","Ivan Basic","Dzenis Burnic","Ermin Mahmic","Benjamin Tahirovic","Amar Memic","Armin Gigovic","Kerim Alajbegovic","Esmir Bajraktarevic","Ermedin Demirovic","Jovo Lukic","Samed Bazdar","Haris Tabakovic","Edin Dzeko"],
    "Brazil": ["Alisson","Ederson","Weverton","Alex Sandro","Bremer","Danilo","Douglas Santos","Gabriel Magalhaes","Ibanez","Leo Pereira","Marquinhos","Wesley","Bruno Guimaraes","Casemiro","Danilo Santos","Fabinho","Lucas Paqueta","Endrick","Gabriel Martinelli","Igor Thiago","Luiz Henrique","Matheus Cunha","Neymar Jr","Raphinha","Rayan","Vinicius Jr"],
    "Canada": ["Dayne St Clair","Maxime Crepeau","Owen Goodman","Alistair Johnston","Derek Cornelius","Richie Laryea","Niko Sigur","Joel Waterman","Luc de Fougerolles","Moise Bombito","Alphonso Davies","Alfie Jones","Stephen Eustaquio","Ismael Kone","Tajon Buchanan","Mathieu Choiniere","Ali Ahmed","Nathan Saliba","Liam Millar","Jacob Shaffelburg","Jonathan Osorio","Jonathan David","Cyle Larin","Tani Oluwaseyi","Promise David"],
    "Cape Verde": ["CJ dos Santos","Marcio Rosa","Vozinha","Sidny Cabral","Diney Borges","Logan Costa","Roberto Lopes","Steven Moreira","Wagner Pina","Kelvin Pires","Joao Paulo Fernandes","Ianique Tavares","Telmo Arcanjo","Deroy Duarte","Laros Duarte","Jamiro Monteiro","Kevin Pina","Yannick Semedo","Gilson Benchimol","Jovane Cabral","Dailon Livramento","Ryan Mendes","Nuno da Costa","Garry Rodrigues","Willy Semedo","Helio Varela"],
    "Colombia": ["Camilo Vargas","Alvaro Montero","David Ospina","Davinson Sanchez","Jhon Lucumi","Yerry Mina","Willer Ditta","Daniel Munoz","Santiago Arias","Johan Mojica","Deiver Machado","Richard Rios","Jefferson Lerma","Kevin Castano","Juan Camilo Portilla","Gustavo Puerta","Jhon Arias","Jorge Carrascal","Juan Fernando Quintero","James Rodriguez","Jaminton Campaz","Juan Camilo Hernandez","Luis Diaz","Luis Suarez","Carlos Gomez","Jhon Cordoba"],
    "Croatia": ["Dominik Livakovic","Dominik Kotarski","Ivor Pandur","Josko Gvardiol","Duje Caleta-Car","Josip Sutalo","Josip Stanisic","Marin Pongracic","Martin Erlic","Luka Vuskovic","Luka Modric","Mateo Kovacic","Mario Pasalic","Nikola Vlasic","Luka Sucic","Martin Baturina","Kristijan Jakic","Petar Sucic","Nikola Moro","Toni Fruk","Ivan Perisic","Andrej Kramaric","Ante Budimir","Marco Pasalic","Petar Musa","Igor Matanovic"],
    "Curaçao": ["Tyrick Bodack","Trevor Doornbusch","Eloy Room","Riechedly Bazoer","Joshua Brenet","Roshon van Eijma","Sherel Floranus","Deveron Fonville","Jurien Gaari","Armando Obispo","Shurandy Sambo","Juninho Bacuna","Leandro Bacuna","Livano Comenencia","Kevin Felida","Arjany Martha","Tyrese Noslin","Godfried Roemeratoe","Jeremy Antonisse","Tahith Chong","Kenji Gorre","Sontje Hansen","Gervane Kastaneer","Brandley Kuwas","Jurgen Locadia","Jearl Margaritha"],
    "Czech Republic": ["Lukas Hornicek","Matej Kovar","Jindrich Stanek","Vladimir Coufal","David Doudera","Tomas Holes","Robin Hranac","Stepan Chaloupek","David Jurasek","Ladislav Krejci","Jaroslav Zeleny","David Zima","Lukas Cerv","Vladimir Darida","Lukas Provod","Michal Sadilek","Hugo Sochurek","Alexandr Sojka","Tomas Soucek","Pavel Sulc","Denis Visinsky","Adam Hlozek","Tomas Chory","Mojmir Chytil","Jan Kuchta","Patrik Schick"],
    "DR Congo": ["Matthieu Epolo","Timothy Fayulu","Lionel Mpasi","Dylan Batubinsika","Gedeon Kalulu","Steve Kapuadi","Joris Kayembe","Arthur Masuaku","Chancel Mbemba","Axel Tuanzebe","Aaron Wan-Bissaka","Brian Cipenga","Meshack Elia","Gael Kakuta","Edo Kayembe","Nathanael Mbuku","Samuel Moutoussamy","Ngal'ayel Mukau","Charles Pickel","Noah Sadiki","Aaron Tshibola","Cedric Bakambu","Simon Banza","Fiston Mayele","Yoane Wissa","Theo Bongonda"],
    "Ecuador": ["Hernan Galindez","Moises Ramirez","Gonzalo Valle","Piero Hincapie","Willian Pacho","Pervis Estupinan","Felix Torres","Joel Ordonez","Jackson Porozo","Angelo Preciado","Yaimar Medina","Moises Caicedo","Alan Franco","Kendry Paez","Gonzalo Plata","Pedro Vite","Jordy Alcivar","Denil Castillo","John Yeboah","Nilson Angulo","Alan Minda","Enner Valencia","Kevin Rodriguez","Jordy Caicedo","Anthony Valencia","Jeremy Arevalo"],
    "Egypt": ["Mohamed El Shenawy","Mostafa Shobeir","El Mahdy Soliman","Mohamed Alaa","Mohamed Abdelmonem","Mohamed Hany","Yasser Ibrahim","Hossam Abdelmaguid","Ahmed Fattouh","Tarek Alaa","Rami Rabia","Karim Hafez","Marwan Attia","Ahmed Sayed","Mahmoud Hassan","Emam Ashour","Mostafa Abdel Raouf","Mohannad Lasheen","Haitham Hassan","Mahmoud Saber","Ibrahim Adel","Nabil Emad","Hamdi Fathi","Mohamed Salah","Omar Marmoush","Hamza Abdel Karim"],
    "England": ["Jordan Pickford","Dean Henderson","James Trafford","Reece James","Ezri Konsa","Jarell Quansah","John Stones","Marc Guehi","Dan Burn","Nico O'Reilly","Djed Spence","Tino Livramento","Declan Rice","Elliot Anderson","Kobbie Mainoo","Jordan Henderson","Morgan Rogers","Jude Bellingham","Eberechi Eze","Harry Kane","Ivan Toney","Ollie Watkins","Bukayo Saka","Marcus Rashford","Anthony Gordon","Noni Madueke"],
    "France": ["Mike Maignan","Robin Risser","Brice Samba","Lucas Digne","Malo Gusto","Lucas Hernandez","Theo Hernandez","Ibrahima Konate","Maxence Lacroix","Jules Kounde","William Saliba","Dayot Upamecano","N'Golo Kante","Manu Kone","Adrien Rabiot","Aurelien Tchouameni","Warren Zaire-Emery","Maghnes Akliouche","Bradley Barcola","Rayan Cherki","Ousmane Dembele","Desire Doue","Michael Olise","Kylian Mbappe","Jean-Philippe Mateta","Marcus Thuram"],
    "Germany": ["Manuel Neuer","Oliver Baumann","Alexander Nuebel","Nico Schlotterbeck","David Raum","Nathaniel Brown","Jonathan Tah","Waldemar Anton","Joshua Kimmich","Malick Thiaw","Antonio Rudiger","Pascal Gross","Leon Goretzka","Felix Nmecha","Jamal Musiala","Nadiem Amiri","Jamie Leweling","Lennart Karl","Florian Wirtz","Leroy Sane","Aleksandar Pavlovic","Angelo Stiller","Kai Havertz","Nick Woltemade","Deniz Undav","Maximilian Beier"],
    "Ghana": ["Joseph Anang","Benjamin Asare","Lawrence Ati-Zigi","Jonas Adjetey","Derrick Luckassen","Gideon Mensah","Abdul Mumin","Jerome Opoku","Kojo Oppong Preprah","Baba Abdul Rahman","Alidu Seidu","Marvin Senaya","Augustine Boakye","Abdul Fatawu Issahaku","Elisha Owusu","Thomas Partey","Kwasi Sibo","Kamal Deen Sulemana","Caleb Yirenkyi","Prince Kwabena Adu","Jordan Ayew","Christopher Bonsu Baah","Ernest Nuamah","Antoine Semenyo","Brandon Thomas-Asante","Inaki Williams"],
    "Haiti": ["Josue Duverger","Alexandre Pierre","Johny Placide","Ricardo Ade","Carlens Arcus","Hannes Delcroix","Jean-Kevin Duverne","Martin Experience","Duke Lacroix","Wilguens Paugain","Keeto Thermoncy","Carl Fred Sainte","Jean-Ricner Bellegarde","Leverton Pierre","Danley Jean Jacques","Woodensky Pierre","Dominique Simon","Josue Casimir","Louicius Deedson","Derrick Etienne Jr","Yassin Fortune","Wilson Isidor","Lenny Joseph","Duckens Nazon","Frantzdy Pierrot","Ruben Providence"],
    "Iran": ["Alireza Beiranvand","Seyed Hossein Hosseini","Payam Niazmand","Danial Eiri","Ehsan Hajsafi","Saleh Hardani","Hossein Kanaani","Shoja Khalilzadeh","Milad Mohammadi","Ali Nemati","Ramin Rezaeian","Rouzbeh Cheshmi","Saeid Ezatolahi","Mehdi Ghaedi","Saman Ghoddos","Mohammad Ghorbani","Alireza Jahanbakhsh","Mohammad Mohebi","Amir Mohammad Razzaghinia","Mehdi Torabi","Aria Yousefi","Ali Alipour","Dennis Dargahi","Amirhossein Hosseinzadeh","Mehdi Taremi","Shahriar Moghanlou"],
    "Iraq": ["Fahad Talib","Jalal Hassan","Ahmed Basil","Hussein Ali","Manaf Younis","Zaid Tahseen","Rebin Sulaka","Akam Hashem","Merchas Doski","Ahmed Yahya","Zaid Ismail","Frans Putros","Mustafa Saadoon","Amir Al Ammari","Kevin Yakob","Zidane Iqbal","Aimar Sher","Ibrahim Bayesh","Ahmed Qasim","Youssef Amyn","Marko Farji","Ali Jassim","Ali Al Hamadi","Ali Yousef","Aymen Hussein","Mohanad Ali"],
    "Ivory Coast": ["Yahia Fofana","Mohamed Kone","Alban Lafont","Emmanuel Agbadou","Christopher Operi","Ousmane Diomande","Guela Doue","Ghislain Konan","Odilon Kossounou","Wilfried Singo","Evan Ndicka","Seko Fofana","Parfait Guiagon","Christ Inao Oulai","Franck Kessie","Ibrahim Sangare","Jean Michael Seri","Simon Adingra","Ange-Yoan Bonny","Amad Diallo","Oumar Diakite","Yan Diomande","Evann Guessand","Nicolas Pepe","Bazoumana Toure","Elye Wahi"],
    "Japan": ["Tomoki Hayakawa","Keisuke Osako","Zion Suzuki","Ko Itakura","Hiroki Ito","Yuto Nagatomo","Ayumu Seko","Yukinari Sugawara","Junnosuke Suzuki","Shogo Taniguchi","Takehiro Tomiyasu","Tsuyoshi Watanabe","Ritsu Doan","Wataru Endo","Junya Ito","Daichi Kamada","Takefusa Kubo","Keito Nakamura","Kaishu Sano","Ao Tanaka","Keisuke Goto","Daizen Maeda","Koki Ogawa","Kento Shiogai","Yuito Suzuki","Ayase Ueda"],
    "Jordan": ["Yazid Abulaila","Noor Bani Attiah","Abdallah Al Fakhouri","Mohammad Abu Hashish","Abdullah Nasib","Hussam Abu Dhahab","Yazan Al Arab","Mohammad Abu Alnadi","Salem Obaid","Saed Al Rosan","Ehsan Haddad","Anas Badawi","Amer Jamous","Noor Al Rawabdeh","Rajaei Ayed","Ibrahim Sadeh","Mohannad Abu Taha","Nizar Al Rashdan","Mohammad Al Dawoud","Mahmoud Mardahi","Mohammad Abu Zraiq","Ali Olwan","Mousa Al Tamari","Odeh Fakhoury","Ibrahim Sabra","Ali Azaizeh"],
    "Mexico": ["Raul Rangel","Guillermo Ochoa","Carlos Acevedo","Jorge Sanchez","Israel Reyes","Cesar Montes","Johan Vasquez","Jesus Gallardo","Mateo Chavez","Edson Alvarez","Erik Lira","Orbelin Pineda","Alvaro Fidalgo","Brian Gutierrez","Luis Romo","Obed Vargas","Gilberto Mora","Luis Chavez","Roberto Alvarado","Cesar Huerta","Alexis Vega","Julian Quinones","Guillermo Martinez","Armando Gonzalez","Santiago Gimenez","Raul Jimenez"],
    "Morocco": ["Yassine Bounou","Munir El Kajoui","Ahmed Reda Tagnaouti","Noussair Mazraoui","Anas Salah-Eddine","Youssef Bellammari","Achraf Hakimi","Zakaria El Ouahdi","Nayef Aguerd","Chadi Riad","Redouane Halhal","Issa Diop","Samir El Mourabet","Ayoub Bouaddi","Neil El Aynaoui","Sofyan Amrabat","Azzedine Ounahi","Bilal El Khannouss","Ismael Saibari","Abdesamad Ezzalzouli","Chemsdine Talbi","Soufiane Rahimi","Ayoub El Kaabi","Brahim Diaz","Yassine Gessim","Ayoube Amaimouni-Echghouyab"],
    "Netherlands": ["Mark Flekken","Robin Roefs","Bart Verbruggen","Nathan Ake","Virgil van Dijk","Denzel Dumfries","Jan Paul van Hecke","Jurrien Timber","Jorrel Hato","Micky van de Ven","Ryan Gravenberch","Frenkie de Jong","Teun Koopmeiners","Tijjani Reijnders","Marten de Roon","Guus Til","Quinten Timber","Mats Wieffer","Brian Brobbey","Memphis Depay","Cody Gakpo","Noa Lang","Donyell Malen","Crysencio Summerville","Wout Weghorst","Justin Kluivert"],
    "New Zealand": ["Max Crocombe","Alex Paulsen","Michael Woud","Tyler Bindon","Michael Boxall","Liberato Cacace","Francis de Vries","Callan Elliot","Tim Payne","Nando Pijnaker","Tommy Smith","Finn Surman","Lachlan Bayliss","Joe Bell","Matt Garbett","Eli Just","Callum McCowatt","Ben Old","Alex Rufer","Marko Stamenic","Sarpreet Singh","Ryan Thomas","Kosta Barbarouses","Jesse Randall","Ben Waine","Chris Wood"],
    "Norway": ["Orjan Nyland","Egil Selvik","Sander Tangvik","Kristoffer Ajer","Fredrik Bjorkan","Henrik Falchener","Sondre Langas","Torbjorn Heggem","Marcus Holmgren Pedersen","Julian Ryerson","David Moller Wolfe","Leo Ostigard","Thelonious Aasgaard","Fredrik Aursnes","Patrick Berg","Sander Berge","Oscar Bobb","Jens Petter Hauge","Antonio Nusa","Andreas Schjelderup","Morten Thorsby","Kristian Thorstvedt","Martin Odegaard","Erling Haaland","Alexander Sorloth","Jorgen Strand Larsen"],
    "Panama": ["Orlando Mosquera","Luis Mejia","Cesar Samudio","Cesar Blackman","Jorge Gutierrez","Amir Murillo","Fidel Escobar","Andres Andrade","Edgardo Farina","Jose Cordoba","Eric Davis","Jiovany Ramos","Roderick Miller","Anibal Godoy","Adalberto Carrasquilla","Carlos Harvey","Cristian Martinez","Jose Luis Rodriguez","Cesar Yanis","Yoel Barcenas","Alberto Quintero","Azarias Londono","Ismael Diaz","Cecilio Waterman","Jose Fajardo","Tomas Rodriguez"],
    "Paraguay": ["Orlando Gill","Roberto Fernandez","Gaston Olveira","Juan Caceres","Gustavo Velazquez","Gustavo Gomez","Junior Alonso","Jose Canale","Omar Alderete","Alexandro Maidana","Fabian Balbuena","Diego Gomez","Mauricio Magalhaes","Damian Bobadilla","Braian Ojeda","Andres Cubas","Matias Galarza","Alejandro Gamarra","Gustavo Caballero","Ramon Sosa","Alex Arce","Isidro Pitta","Gabriel Avalos","Miguel Almiron","Julio Enciso","Antonio Sanabria"],
    "Portugal": ["Diogo Costa","Jose Sa","Rui Silva","Tomas Araujo","Joao Cancelo","Diogo Dalot","Ruben Dias","Goncalo Inacio","Nuno Mendes","Matheus Nunes","Nelson Semedo","Renato Veiga","Samuel Costa","Bruno Fernandes","Joao Neves","Ruben Neves","Bernardo Silva","Vitinha","Francisco Conceicao","Joao Felix","Goncalo Guedes","Rafael Leao","Pedro Neto","Goncalo Ramos","Cristiano Ronaldo","Francisco Trincao"],
    "Qatar": ["Salah Zakaria","Meshaal Barsham","Mahmoud Abunada","Boualem Khoukhi","Pedro Miguel","Sultan Al Brake","Al Hashmi Al Hussain","Ayoub Al Alawi","Issa Laye","Lucas Mendes","Homam Al Amin","Ahmed Fathi","Jassim Gaber","Assim Madibo","Abdulaziz Hatem","Karim Boudiaf","Mohammed Mannai","Almoez Ali","Akram Afif","Tahsin Mohammed","Edmilson Junior","Ahmed Al-Janehi","Ahmed Alaa","Hassan Al Haydos","Mohammed Muntari","Yusuf Abdurisag"],
    "Saudi Arabia": ["Nawaf Al Aqidi","Mohamed Al Owais","Ahmed Alkassar","Saud Abdulhamid","Jehad Thakri","Abdulelah Al Amri","Hassan Tambakti","Ali Lajami","Hassan Kadesh","Moteb Al Harbi","Nawaf Boushal","Ali Majrashi","Mohammed Abu Alshamat","Ziyad Al Johani","Nasser Al Dawsari","Mohamed Kanno","Abdullah Al Khaibari","Alaa Al Hejji","Musab Al Juwayr","Sultan Mandash","Ayman Yahya","Khalid Al Ghannam","Salem Al Dawsari","Abdullah Al Hamdan","Feras Al Brikan","Saleh Al Shehri"],
    "Scotland": ["Craig Gordon","Angus Gunn","Liam Kelly","Grant Hanley","Jack Hendry","Aaron Hickey","Dom Hyam","Scott McKenna","Nathan Patterson","Anthony Ralston","Andy Robertson","John Souttar","Kieran Tierney","Ryan Christie","Findlay Curtis","Lewis Ferguson","Tyler Fletcher","Ben Gannon-Doak","John McGinn","Kenny McLean","Scott McTominay","Che Adams","Lyndon Dykes","George Hirst","Lawrence Shankland","Ross Stewart"],
    "Senegal": ["Edouard Mendy","Mory Diaw","Yehvann Diouf","Krepin Diatta","Antoine Mendy","Kalidou Koulibaly","El Hadji Malick Diouf","Mamadou Sarr","Moussa Niakhate","Abdoulaye Seck","Ismail Jakobs","Idrissa Gana Gueye","Pape Gueye","Lamine Camara","Habib Diarra","Pathe Ciss","Pape Matar Sarr","Bara Sapoko Ndiaye","Sadio Mane","Ismaila Sarr","Iliman Ndiaye","Assane Diao","Ibrahim Mbaye","Nicolas Jackson","Bamba Dieng","Cherif Ndiaye"],
    "South Africa": ["Ronwen Williams","Ricardo Goss","Sipho Chaine","Aubrey Modiba","Khuliso Mudau","Khulumani Ndamane","Kamogelo Sebelebele","Nkosinathi Sibisi","Bradley Cross","Samukele Kabini","Olwethu Makhanya","Thabang Matuludi","Mbekezeli Mbokazi","Ime Okon","Oswin Appollis","Thalente Mbatha","Relebohile Mofokeng","Jayden Adams","Teboho Mokoena","Themba Zwane","Sphephelo Sithole","Evidence Makgopa","Tshepang Moremi","Lyle Foster","Thapelo Maseko","Iqraam Rayners"],
    "South Korea": ["Song Bumkeun","Jo Hyeonwoo","Kim Seung-gyu","Jens Castrop","Lee Hanbeom","Park Jinseob","Lee Kihyuk","Kim Minjae","Kim Moonhwan","Kim Taehyeon","Lee Taeseok","Seol Youngwoo","Cho Wije","Lee Donggyeong","Hwang Heechan","Yang Hyunjun","Hwang Inbeom","Lee Jaesung","Kim Jingyu","Eom Jisung","Bae Junho","Lee Kangin","Paik Seungho","Cho Guesung","Son Heungmin","Oh Hyeongyu"],
    "Spain": ["Unai Simon","David Raya","Joan Garcia","Marc Cucurella","Pau Cubarsi","Aymeric Laporte","Alejandro Grimaldo","Pedro Porro","Eric Garcia","Marcos Llorente","Marc Pubill","Gavi","Rodri","Pedri","Martin Zubimendi","Fabian Ruiz","Alex Baena","Mikel Merino","Lamine Yamal","Nico Williams","Dani Olmo","Ferran Torres","Mikel Oyarzabal","Yeremy Pino","Borja Iglesias","Victor Munoz"],
    "Sweden": ["Viktor Johansson","Gustaf Lagerbielke","Kristoffer Nordfeldt","Jacob Zetterstrom","Hjalmar Ekdal","Gabriel Gudmundsson","Isak Hien","Victor Lindelof","Eric Smith","Carl Starfelt","Daniel Svensson","Yasin Ayari","Lucas Bergvall","Jesper Karlstrom","Benjamin Nygren","Ken Sema","Elliot Stroud","Mattias Svanberg","Besfort Zeneli","Taha Ali","Alexander Bernhardsson","Anthony Elanga","Viktor Gyokeres","Alexander Isak","Gustaf Nilsson"],
    "Switzerland": ["Marvin Keller","Gregor Kobel","Yvon Mvogo","Manuel Akanji","Aurele Amenda","Eray Comert","Nico Elvedi","Luca Jaquez","Miro Muheim","Ricardo Rodriguez","Silvan Widmer","Michel Aebischer","Christian Fassnacht","Remo Freuler","Ardon Jashari","Fabian Rieder","Djibril Sow","Cedric Itten","Granit Xhaka","Denis Zakaria","Ruben Vargas","Zeki Amdouni","Breel Embolo","Dan Ndoye","Noah Okafor","Johan Manzambi"],
    "Tunisia": ["Sabri Ben Hessen","Abdelmouhib Chamakh","Aymen Dahman","Ali Abdi","Adem Arous","Mohamed Amine Ben Hamida","Dylan Bronn","Raed Chikhaoui","Moutaz Neffati","Omar Rekik","Montassar Talbi","Yan Valery","Mortadha Ben Ouanes","Anis Ben Slimane","Ismael Gharbi","Rani Khedira","Mohamed Hadj Mahmoud","Hannibal Mejbri","Ellyes Skhiri","Elias Achouri","Khalil Ayari","Firas Chaouat","Rayan Elloumi","Hazem Mastouri","Elias Saad","Sebastian Tounekti"],
    "Turkey": ["Altay Bayindir","Mert Gunok","Ugurcan Cakir","Abdulkerim Bardakci","Caglar Soyuncu","Eren Elmali","Ferdi Kadioglu","Merih Demiral","Mert Muldur","Ozan Kabak","Samet Akaydin","Zeki Celik","Hakan Calhanoglu","Ismail Yuksek","Kaan Ayhan","Orkun Kokcu","Salih Ozcan","Arda Guler","Baris Alper Yilmaz","Can Uzun","Deniz Gul","Irfan Can Kahveci","Kenan Yildiz","Kerem Akturkoglu","Oguz Aydin","Yunus Akgun"],
    "Uruguay": ["Sergio Rochet","Fernando Muslera","Santiago Mele","Guillermo Varela","Ronald Araujo","Jose Maria Gimenez","Santiago Bueno","Sebastian Caceres","Mathias Olivera","Joaquin Piquerez","Matias Vina","Maximiliano Araujo","Giorgian de Arrascaeta","Rodrigo Bentancur","Agustin Canobbio","Nicolas de la Cruz","Emiliano Martinez","Facundo Pellistri","Brian Rodriguez","Juan Manuel Sanabria","Manuel Ugarte","Federico Valverde","Rodrigo Zalazar","Rodrigo Aguirre","Federico Vinas","Darwin Nunez"],
    "USA": ["Chris Brady","Matt Freese","Matt Turner","Max Arfsten","Sergino Dest","Alex Freeman","Mark McKenzie","Tim Ream","Chris Richards","Antonee Robinson","Miles Robinson","Joe Scally","Auston Trusty","Tyler Adams","Sebastian Berhalter","Weston McKennie","Cristian Roldan","Brenden Aaronson","Christian Pulisic","Gio Reyna","Malik Tillman","Tim Weah","Alejandro Zendejas","Folarin Balogun","Ricardo Pepi","Haji Wright"],
    "Uzbekistan": ["Botirali Ergashev","Abduvohid Nematov","Utkir Yusupov","Abdukodir Khusanov","Khojiakbar Alijonov","Rustamjon Ashurmatov","Farrukh Sayfiev","Sherzod Nasrullaev","Umarbek Eshmuradov","Avazbek Ulmasaliev","Jakhongir Urozov","Bekhruz Karimov","Abdulla Abdullaev","Akmal Mozgovoy","Otabek Shukurov","Jamshid Iskanderov","Odiljon Hamrobekov","Jaloliddin Masharipov","Azizbek Ganiev","Sherzod Esanov","Abbosbek Fayzullaev","Azizbek Amonov","Eldor Shomurodov","Igor Sergeev","Oston Urunov","Dostonbek Hamdamov"],
}

# Build reverse lookup: normalised player name -> team
PLAYER_TEAM = {}
for _team, _players in WC_SQUADS.items():
    for _p in _players:
        PLAYER_TEAM[_p.lower()] = _team

import unicodedata, re as _re

def _norm(s):
    """Normalise: lowercase, strip accents, remove hyphens/punctuation"""
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = _re.sub(r"[-'\.]", " ", s)
    s = _re.sub(r"\s+", " ", s).strip()
    return s

# Build normalised reverse lookup
PLAYER_TEAM_NORM = {_norm(p): team for team, players in WC_SQUADS.items() for p in players}
# Also index by individual words (for partial surname matching)
PLAYER_WORDS = {}  # word -> list of (norm_name, team)
for _np, _team in PLAYER_TEAM_NORM.items():
    for _w in _np.split():
        if len(_w) > 2:
            PLAYER_WORDS.setdefault(_w, []).append((_np, _team))

def find_player_team(name):
    """Fuzzy match bookmaker player name to their WC team"""
    nn = _norm(name)

    # 1. Exact normalised match
    if nn in PLAYER_TEAM_NORM:
        return PLAYER_TEAM_NORM[nn]

    # 2. Try reversed word order (handles Asian name formats: "Son Heung-min" ↔ "Heung-Min Son")
    words = nn.split()
    if len(words) >= 2:
        reversed_nn = " ".join(words[::-1])
        if reversed_nn in PLAYER_TEAM_NORM:
            return PLAYER_TEAM_NORM[reversed_nn]
        # Also try joining all words (removes spaces): "heungmin son" etc
        joined = "".join(words)
        for key, team in PLAYER_TEAM_NORM.items():
            if "".join(key.split()) == joined:
                return team

    # 3. Every word in query appears somewhere in one player's full name (substring)
    query_words = [w for w in words if len(w) > 2]
    for norm_key, team in PLAYER_TEAM_NORM.items():
        joined_key = norm_key.replace(" ", "")
        if all(w in joined_key for w in query_words):
            return team

    # 4. Surname (last word) match + first initial
    if query_words:
        for surname_idx in [-1, 0]:  # try last word then first word as surname
            surname = query_words[surname_idx]
            first_init = query_words[0][0]
            candidates = PLAYER_WORDS.get(surname, [])
            for norm_key, team in candidates:
                kw = norm_key.split()
                if any(w[0] == first_init for w in kw):
                    return team
            if len(candidates) == 1:
                return candidates[0][1]

    return ""

POS_TIMING = {
    "Attacker": 1.18, "Forward": 1.18,
    "Midfielder": 1.0, "Defender": 0.80,
    "Goalkeeper": 0.20, "Unknown": 1.0,
}

# Known set-piece / free kick specialists per national team
# These players get a +12% boost — FK takers get early direct shots
FK_SPECIALISTS = {
    "Trent Alexander-Arnold", "Phil Foden", "James Maddison",
    "Antoine Griezmann", "Kylian Mbappé", "Ousmane Dembélé",
    "Bruno Fernandes", "Cristiano Ronaldo", "Bernardo Silva",
    "Lionel Messi", "Rodrigo De Paul", "Angel Di Maria",
    "Neymar", "Casemiro", "Lucas Paquetá",
    "Florian Wirtz", "Kai Havertz", "Jamal Musiala",
    "Kevin De Bruyne", "Yannick Carrasco",
    "Heung-Min Son", "Lee Kang-in",
    "Takumi Minamino", "Ritsu Doan",
    "Hakim Ziyech", "Sofiane Boufal",
    "Christian Pulisic", "Weston McKennie",
    "Federico Valverde", "Luis Suárez", "Darwin Núñez",
    "James Rodríguez", "Luis Díaz",
    "Enner Valencia", "Moisés Caicedo",
    "Luka Modrić", "Ivan Perišić",
    "Granit Xhaka", "Xherdan Shaqiri",
    "Martin Ødegaard", "Erling Haaland",
    "Emil Forsberg", "Dejan Kulusevski",
    "Hakan Çalhanoğlu", "Arda Güler",
    "Patrik Schick", "Tomáš Souček",
    "Memphis Depay", "Frenkie de Jong",
    "Mehdi Taremi", "Sardar Azmoun",
    "Saleh Al-Shehri", "Firas Al-Buraikan",
    "Jonathan David", "Tajon Buchanan",
    "Hirving Lozano", "Alexis Vega",
}

# Players with confirmed injuries / fitness doubts — penalised -60% (bookies may lag)
# Update this list as tournament news comes in
INJURED_DOUBTFUL = {
    "Neymar Jr", "Neymar",           # ACL recovery, fitness doubt
    "Gavi",                           # Knee injury recovery
    "Trent Alexander-Arnold",        # Thigh injury
}

# High-press / early-game attackers — known to shoot in first 15 mins
# +10% boost on top of position timing (separate from FK)
EARLY_SHOOTERS = {
    "Kylian Mbappe", "Vinicius Jr", "Bukayo Saka", "Leroy Sane",
    "Lamine Yamal", "Nico Williams", "Jamal Musiala", "Florian Wirtz",
    "Son Heungmin", "Heung-Min Son", "Marcus Rashford", "Antoine Griezmann",
    "Sadio Mane", "Ismaila Sarr", "Luis Diaz", "Rafael Leao",
    "Cody Gakpo", "Donyell Malen", "Viktor Gyokeres", "Alexander Isak",
    "Richarlison", "Gabriel Martinelli", "Endrick",
    "Hirving Lozano", "Santiago Gimenez",
}

COUNTRY_FLAGS = {
    "Mexico":"🇲🇽","South Africa":"🇿🇦","South Korea":"🇰🇷","Czech Republic":"🇨🇿",
    "Canada":"🇨🇦","Bosnia & Herzegovina":"🇧🇦","USA":"🇺🇸","Paraguay":"🇵🇾",
    "Qatar":"🇶🇦","Switzerland":"🇨🇭","Brazil":"🇧🇷","Morocco":"🇲🇦",
    "Haiti":"🇭🇹","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Australia":"🇦🇺","Turkey":"🇹🇷",
    "Germany":"🇩🇪","Curaçao":"🇨🇼","Netherlands":"🇳🇱","Japan":"🇯🇵",
    "Ivory Coast":"🇨🇮","Ecuador":"🇪🇨","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Spain":"🇪🇸","Cape Verde":"🇨🇻","Belgium":"🇧🇪","Egypt":"🇪🇬",
    "Saudi Arabia":"🇸🇦","Uruguay":"🇺🇾","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "France":"🇫🇷","Senegal":"🇸🇳","Iraq":"🇮🇶","Norway":"🇳🇴",
    "Argentina":"🇦🇷","Algeria":"🇩🇿","Austria":"🇦🇹","Jordan":"🇯🇴",
    "Portugal":"🇵🇹","DR Congo":"🇨🇩","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Croatia":"🇭🇷",
    "Ghana":"🇬🇭","Uzbekistan":"🇺🇿","Colombia":"🇨🇴","Panama":"🇵🇦",
}

TEAM_ABBR = {
    "Mexico":"MEX","South Africa":"RSA","South Korea":"KOR","Czech Republic":"CZE",
    "Canada":"CAN","Bosnia & Herzegovina":"BIH","USA":"USA","Paraguay":"PAR",
    "Qatar":"QAT","Switzerland":"SUI","Brazil":"BRA","Morocco":"MAR",
    "Haiti":"HAI","Scotland":"SCO","Australia":"AUS","Turkey":"TUR",
    "Germany":"GER","Curaçao":"CUW","Netherlands":"NED","Japan":"JPN",
    "Ivory Coast":"CIV","Ecuador":"ECU","Sweden":"SWE","Tunisia":"TUN",
    "Spain":"ESP","Cape Verde":"CPV","Belgium":"BEL","Egypt":"EGY",
    "Saudi Arabia":"KSA","Uruguay":"URU","Iran":"IRN","New Zealand":"NZL",
    "France":"FRA","Senegal":"SEN","Iraq":"IRQ","Norway":"NOR",
    "Argentina":"ARG","Algeria":"ALG","Austria":"AUT","Jordan":"JOR",
    "Portugal":"POR","DR Congo":"COD","England":"ENG","Croatia":"CRO",
    "Ghana":"GHA","Uzbekistan":"UZB","Colombia":"COL","Panama":"PAN",
}

BM_STYLES = {
    "William Hill": '<span class="bm wh">William <strong>HILL</strong></span>',
    "Unibet":       '<span class="bm un">UNIBET<span class="un-dots">••••</span></span>',
    "1xBet":        '<span class="bm xbet">1xBet</span>',
    "FanDuel":      '<span class="bm fd">FanDuel</span>',
    "BetRivers":    '<span class="bm br">BetRivers</span>',
    "Bet365":       '<span class="bm b365">bet365</span>',
    "Paddy Power":  '<span class="bm pp">PADDY POWER.</span>',
    "LeoVegas":     '<span class="bm lv">LeoVegas</span>',
    "Betfair":      '<span class="bm bf">betfair</span>',
}

def bm_html(name):
    return BM_STYLES.get(name, f'<span class="bm generic">{name}</span>')

def implied_lambda(price):
    p = min(1 / price, 0.9999)
    return -math.log(1 - p)

def avatar_color(name):
    colors = ["#3b82f6","#10b981","#8b5cf6","#f59e0b","#ef4444","#06b6d4","#ec4899","#84cc16"]
    return colors[hash(name) % len(colors)]

def initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return parts[0][0].upper() + parts[-1][0].upper()
    return name[:2].upper()

def get_squad_pos(name, team, squads):
    squad = squads.get(team, [])
    nl = name.lower()
    for p in squad:
        if p["name"].lower() == nl or nl in p["name"].lower() or p["name"].lower() in nl:
            return p.get("position", "Unknown")
    return "Unknown"

def get_statsbomb_timing(player_name, sb_data):
    """
    Look up StatsBomb WC shot timing data for a player.
    Returns early_sot_pct_15, avg_first_sot_min, sot_per_game or None.
    """
    nl = _norm(player_name)
    best = None
    best_matches = 0
    for key, v in sb_data.items():
        kname = _norm(v.get("player", ""))
        if kname == nl:
            if v["matches"] > best_matches:
                best = v
                best_matches = v["matches"]
        elif nl and kname and (nl in kname or kname in nl):
            # partial — only use if longer match
            parts_nl = set(nl.split())
            parts_k  = set(kname.split())
            overlap  = len(parts_nl & parts_k)
            if overlap >= 2 and v["matches"] > best_matches:
                best = v
                best_matches = v["matches"]
    return best

def get_nat_stats(name, team, nat_agg):
    team_data = nat_agg.get(team, {})
    nl = name.lower()
    for pid, s in team_data.items():
        sname = s.get("name", "").lower()
        if sname == nl or nl in sname or sname in nl:
            return s
    return None

def confidence(has_nat, edge, team_prob_known, has_sb):
    """
    Data quality score — how much independent evidence backs this prediction.
    High  = national stats + StatsBomb timing + team win probability all available
    Medium = some independent data (national stats or StatsBomb timing)
    Low   = bookie-only — we're just reweighting their own numbers
    """
    score = 0
    if has_nat:         score += 2   # international SOT/90 data
    if has_sb:          score += 2   # StatsBomb shot timing data
    if team_prob_known: score += 1   # team win probability (h2h)
    if score >= 4: return "High"
    if score >= 2: return "Medium"
    return "Low"

# ── STEP 1: Team first-SOT probability ─────────────────────────────────────
def get_team_first_sot_probs(event_odds, home, away):
    """
    Two-step model step 1:
    P(team gets first SOT) derived from h2h odds.
    The stronger team (higher win probability) is more likely to attack first.
    Adjusted by match total (higher total → faster first SOT overall).
    Returns (p_home, p_away, total_line)
    """
    home_win_prob = away_win_prob = draw_prob = None
    total_line = 2.5  # default

    for bm in event_odds.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] == "h2h" and home_win_prob is None:
                for o in mkt["outcomes"]:
                    p = 1 / o["price"]
                    if o["name"] == home:   home_win_prob = p
                    elif o["name"] == away: away_win_prob = p
                    elif o["name"] == "Draw": draw_prob = p
            if mkt["key"] == "totals":
                for o in mkt["outcomes"]:
                    if o["name"] == "Over":
                        total_line = o.get("point", 2.5)
                        break

    if home_win_prob and away_win_prob and draw_prob:
        # Remove overround
        total_imp = home_win_prob + away_win_prob + draw_prob
        hw = home_win_prob / total_imp
        aw = away_win_prob / total_imp
        dw = draw_prob / total_imp

        # P(team first SOT) ≈ P(win) + 0.45*P(draw)
        # (favourites attack first ~65% when they win, draws roughly split)
        p_home_raw = hw + 0.45 * dw
        p_away_raw = aw + 0.45 * dw
        # Normalise to sum to 1
        total = p_home_raw + p_away_raw
        p_home = p_home_raw / total
        p_away = p_away_raw / total
        return p_home, p_away, total_line, True
    else:
        return 0.5, 0.5, total_line, False

# ── STEP 2: Player first-SOT within their team ─────────────────────────────
def build_predictions(event_odds, home, away, nat_agg, squads, sb_data=None):
    """
    Two-step model:
      P(player first SOT) = P(team first SOT) × P(player | team first SOT)

    Weights (v1):
      35% bookmaker SOT implied rate (Poisson λ)
      25% national team SOT/90
      15% early-game tendency (curated list + position timing)
      10% tactical role/position
       7.5% team/opponent matchup (game total proxy)
       5% set-piece / FK responsibility
       2.5% injury/availability penalty

    bm_pct uses raw bookmaker λ normalised — our benchmark.
    model_pct uses the full weighted model.
    """
    # Extract Over 0.5 SOT odds per player
    bookie_data = {}
    for bm in event_odds.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] != "player_shots_on_target": continue
            for o in mkt["outcomes"]:
                if o.get("point") == 0.5 and o.get("name") == "Over":
                    nm = o["description"]
                    pr = o["price"]
                    if nm not in bookie_data or pr < bookie_data[nm]["price"]:
                        bookie_data[nm] = {"price": pr, "bm": bm["title"]}

    if not bookie_data: return []

    # Step 1: team-level first SOT probabilities
    p_home_team, p_away_team, total_line, team_known = get_team_first_sot_probs(event_odds, home, away)

    # Total line modifier: high-scoring game → first SOT comes sooner → spread wider
    # We use it as a slight boost for the stronger team's players (effect already in h2h)
    # Higher totals also mean more SOT overall, which doesn't change ratios much
    # So we keep this simple and just use it for confidence display

    # Step 2: build player-level model lambdas
    players = []
    for name, bi in bookie_data.items():
        # --- Bookmaker signal (35%) ---
        bm_lam = implied_lambda(bi["price"])

        # --- National team stats (25%) ---
        nat = get_nat_stats(name, home, nat_agg) or get_nat_stats(name, away, nat_agg)
        pos = (nat.get("pos","Unknown") if nat else None) or \
              get_squad_pos(name, home, squads) or \
              get_squad_pos(name, away, squads) or "Unknown"

        if nat and nat.get("sot_per90", 0) > 0:
            nat_lam  = max(nat["sot_per90"], 0.001)
            has_nat  = True
            nat_apps = nat.get("apps", 0)
            nat_sot  = nat.get("sot_per90", 0)
        else:
            nat_lam  = bm_lam  # fallback to bookie when no intl data
            has_nat  = False
            nat_apps = nat_sot = None

        # Weighted base rate: 35% bookie + 25% national (+ 40% bookie if no nat data)
        if has_nat:
            base_lam = 0.35 * bm_lam + 0.25 * nat_lam + 0.40 * bm_lam
            # simplifies to: 0.75 * bm_lam + 0.25 * nat_lam
        else:
            base_lam = bm_lam

        # --- Tactical role / position (10%) ---
        timing = POS_TIMING.get(pos, 1.0)

        # --- Early-game tendency (15%) ---
        # Curated list of high-press early shooters
        # --- Early-game tendency (15%) ---
        # Use StatsBomb WC shot timing data if available, else fall back to curated list
        sb_timing = get_statsbomb_timing(name, sb_data) if sb_data else None
        if sb_timing and sb_timing.get("matches", 0) >= 2:
            # Data-driven: use % SOT in first 15 mins
            # Average early SOT% across all players is ~20%
            # We scale: 0% early = 0.7x, 20% = 1.0x, 40% = 1.3x, 60%+ = 1.5x
            early_pct = sb_timing.get("early_sot_pct_15", 0.2)
            early_mult = 0.7 + (early_pct / 0.4) * 0.6  # linear scale
            early_mult = min(max(early_mult, 0.5), 1.6)  # clamp 0.5-1.6
            has_sb = True
        else:
            early_mult = 1.15 if name in EARLY_SHOOTERS else 1.0
            has_sb = False

        # --- Set piece / FK (5%) ---
        fk_mult = 1.12 if name in FK_SPECIALISTS else 1.0

        # --- Injury / availability (2.5% weight — hard penalty) ---
        injured    = name in INJURED_DOUBTFUL
        inj_mult   = 0.35 if injured else 1.0

        # Final model lambda
        model_lam = base_lam * timing * early_mult * fk_mult * inj_mult

        # Which team
        team = find_player_team(name)
        is_home = (team == home)

        players.append({
            "name": name, "pos": pos, "price": bi["price"], "bm": bi["bm"],
            "bm_lam": bm_lam, "model_lam": model_lam,
            "has_nat": has_nat, "nat_apps": nat_apps, "nat_sot": nat_sot,
            "is_fk": name in FK_SPECIALISTS,
            "is_early": name in EARLY_SHOOTERS or has_sb,
            "has_sb": has_sb,
            "sb_early_pct": sb_timing.get("early_sot_pct_15") if sb_timing else None,
            "sb_avg_first_sot": sb_timing.get("avg_first_sot_min") if sb_timing else None,
            "injured": injured,
            "team": team, "is_home": is_home,
        })

    if not players: return []

    # --- Bookie benchmark: raw λ normalised across all players ---
    tb = sum(p["bm_lam"] for p in players)

    # --- Two-step model ---
    # Group by team
    home_players = [p for p in players if p["team"] == home]
    away_players = [p for p in players if p["team"] == away]
    unknown_players = [p for p in players if not p["team"]]

    def first_sot_within_team(team_players):
        """P(player first SOT | their team gets it) = λ_player / Σλ_team"""
        total = sum(p["model_lam"] for p in team_players)
        for p in team_players:
            p["_within_team"] = p["model_lam"] / total if total > 0 else 0

    all_lam = sum(q["model_lam"] for q in players) or 1
    for p in players: p["_within_team"] = 0  # default
    if home_players: first_sot_within_team(home_players)
    if away_players: first_sot_within_team(away_players)
    for p in unknown_players:
        p["_within_team"] = p["model_lam"] / all_lam

    # Combine: P(player first SOT) = P(team first) × P(player | team first)
    for p in players:
        if p["team"] == home:
            team_prob = p_home_team
        elif p["team"] == away:
            team_prob = p_away_team
        else:
            team_prob = 0.5
        p["model_lam_final"] = team_prob * p["_within_team"]

    tm = sum(p["model_lam_final"] for p in players)
    for p in players:
        p["bm_pct"]    = round(p["bm_lam"] / tb * 100, 1) if tb > 0 else 0
        p["model_pct"] = round(p["model_lam_final"] / tm * 100, 1) if tm > 0 else 0
        p["edge"]      = round(p["model_pct"] - p["bm_pct"], 1)
        p["conf"]      = confidence(p["has_nat"], p["edge"], team_known, p.get("has_sb", False))

    players.sort(key=lambda x: x["model_pct"], reverse=True)
    return players

def edge_pill(edge, short=False):
    if edge >= 1.5:  cls,lbl,slbl = "e-strong-val", f"+{edge}% Strong", f"+{edge}%"
    elif edge >= 0.5:cls,lbl,slbl = "e-slight-val", f"+{edge}% Slight", f"+{edge}%"
    elif edge <= -1.5:cls,lbl,slbl= "e-strong-fad", f"{edge}% Fade",    f"{edge}%"
    elif edge <= -0.5:cls,lbl,slbl= "e-slight-fad", f"{edge}% Slight",  f"{edge}%"
    else:             cls,lbl,slbl = "e-neutral",    "Neutral",          "—"
    if short:
        return f'<span class="epill {cls}">{slbl}</span>'
    return f'<span class="epill {cls}"><span class="pill-long">{lbl}</span><span class="pill-short">{slbl}</span></span>'

def conf_badge(c):
    cls  = {"High":"conf-hi","Medium":"conf-med","Low":"conf-lo"}.get(c,"conf-lo")
    icon = {"High":"✦","Medium":"◉","Low":"○"}.get(c,"○")
    lbl  = {"High":"✦ Rich data","Medium":"◉ Some data","Low":"○ Bookie only"}.get(c,"○ Bookie only")
    tip  = {
        "High":   "National stats + shot timing data + team win probability all available",
        "Medium": "Some independent data (national stats or shot timing)",
        "Low":    "Bookmaker data only — we're reweighting their own numbers. Less reliable.",
    }.get(c, "")
    return f'<span class="cbadge {cls}" title="{tip}">{lbl}</span>'

def fmt_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.strftime("%a %d %b · %H:%M UTC")
    except: return iso[:10]

def fmt_date_short(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.strftime("%a %d %b")
    except: return iso[:10]

def fmt_time(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        return dt.strftime("%H:%M")
    except: return ""

def best_edges_rows(all_games):
    candidates = []
    for g in all_games:
        if not g["has_data"]: continue
        for p in g["players"][:5]:
            if p["edge"] > 0:
                candidates.append({**p, "home": g["home"], "away": g["away"], "date_short": g["date_short"], "time": g["time"]})
    candidates.sort(key=lambda x: x["edge"], reverse=True)
    rows = []
    for i, p in enumerate(candidates[:5]):
        ha = TEAM_ABBR.get(p["home"], p["home"][:3].upper())
        aa = TEAM_ABBR.get(p["away"], p["away"][:3].upper())
        flag = COUNTRY_FLAGS.get(p["home"], "") # rough guess
        col = avatar_color(p["name"])
        ini = initials(p["name"])
        rows.append(f"""            <tr class="be-row">
              <td><span class="rank-circle">{i+1}</span></td>
              <td>
                <div class="be-player">
                  <div class="avatar" style="background:{col}">{ini}</div>
                  <div>
                    <div class="be-name">{p["name"]} {"<span class='fk-tag'>FK</span>" if p.get("is_fk") else ""} {"<span class='early-tag'>⚡EARLY</span>" if p.get("is_early") else ""} {"<span class='inj-tag'>⚠ DOUBT</span>" if p.get("injured") else ""}</div>
                    <div class="be-country">{COUNTRY_FLAGS.get(p.get("team", p["home"]),"")} {p.get("team", p["home"])}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="be-match">{ha} vs {aa}</div>
                <div class="be-date">{p["date_short"]} · {p["time"]}</div>
              </td>
              <td class="td-model">{p["model_pct"]}% <span class="mob-edge">{edge_pill(p["edge"])}</span></td>
              <td class="td-bm">{p["bm_pct"]}%</td>
              <td>{edge_pill(p["edge"])}</td>
              <td><span class="odds-val">{p["price"]:.2f}</span> {bm_html(p["bm"])}</td>
              <td>{conf_badge(p["conf"])}</td>
            </tr>""")
    return "\n".join(rows)

def match_player_rows(players):
    if not players:
        return '<tr><td colspan="7" class="no-data">Odds not yet available — check back closer to kick-off</td></tr>'
    medals = ["🥇","🥈","🥉","",""]
    rows = []
    for i, p in enumerate(players[:5]):
        med = f'<span class="medal">{medals[i]}</span>' if medals[i] else f'<span class="rank-sm">{i+1}</span>'
        rows.append(f"""              <tr>
                <td>{med}</td>
                <td class="td-pname"><span class="p-flag">{COUNTRY_FLAGS.get(p.get("team",""),"")}</span> {p["name"]} {"<span class='fk-tag'>FK</span>" if p.get("is_fk") else ""} {"<span class='early-tag'>⚡</span>" if p.get("is_early") else ""} {"<span class='inj-tag'>⚠ DOUBT</span>" if p.get("injured") else ""}</td>
                <td class="td-model">{p["model_pct"]}% <span class="mob-edge">{edge_pill(p["edge"])}</span></td>
                <td class="td-bm">{p["bm_pct"]}%</td>
                <td>{edge_pill(p["edge"])}</td>
                <td><span class="odds-val">{p["price"]:.2f}</span> {bm_html(p["bm"])}</td>
                <td>{conf_badge(p["conf"])}</td>
              </tr>""")
    return "\n".join(rows)

def match_cards(games):
    cards = []
    for g in games:
        uid = g["id"][:8]
        hf = COUNTRY_FLAGS.get(g["home"],"🏳")
        af = COUNTRY_FLAGS.get(g["away"],"🏳")
        has = g["has_data"]
        nat_c = g["nat_count"]
        badge = '<span class="mbadge nat-badge">★ Intl data</span>' if nat_c > 0 else ('<span class="mbadge bk-badge">Bookie-only</span>' if has else '<span class="mbadge tbc-badge">Odds TBC</span>')
        dim = "" if has else " card-dim"

        cards.append(f"""    <div class="mcard{dim}" id="mc-{uid}">
      <div class="mcard-header" onclick="tog('{uid}')">
        <div class="mcard-left">
          <span class="mflag">{hf}</span>
          <span class="mteam">{g["home"]}</span>
          <span class="mvs">vs</span>
          <span class="mteam">{g["away"]}</span>
          <span class="mflag">{af}</span>
          {badge}
        </div>
        <div class="mcard-right">
          <span class="mdate">{g["date_fmt"]}</span>
          <span class="mchev" id="chev-{uid}">▾</span>
        </div>
      </div>
      <div class="mcard-body" id="mb-{uid}">
        <table class="mtable">
          <thead>
            <tr>
              <th>RANK</th><th>PLAYER</th>
              <th class="th-m">CAT DAD MODEL</th>
              <th class="th-b">BOOKIE</th>
              <th>EDGE <span class="th-info">ⓘ</span></th>
              <th>ODDS</th>
              <th title="Data Quality: how much independent evidence backs this prediction. High = national stats + shot timing data. Low = bookmaker data only.">DATA ⓘ</th>
            </tr>
          </thead>
          <tbody>
{match_player_rows(g["players"])}
          </tbody>
        </table>
        <p class="mfootnote">First SOT prob = λ<sub>player</sub>/Σλ. Model: intl SOT rate + bookie λ · timing · FK +12%. <span class="fk-tag">FK</span> = FK taker. Odds shown = best available across William Hill, Unibet, 1xBet.</p>
      </div>
    </div>""")
    return "\n".join(cards)

def build_html(games, updated, nat_cov, total, with_odds, sb_players=0):
    be_rows = best_edges_rows(games)
    mcards  = match_cards(games)
    nat_pct = round(nat_cov / 48 * 100)
    odds_pct = round(with_odds / total * 100)

    # Donut SVG helper
    def donut(pct, color):
        r = 16; c = 20; circ = 2 * 3.14159 * r
        # At 100%, use slightly less than full circ to avoid gap at join
        dash = min(pct / 100 * circ, circ - 0.1)
        gap  = max(circ - dash, 0.1)
        return (f'<svg width="44" height="44" viewBox="0 0 44 44">'
                f'<circle cx="22" cy="22" r="{r}" fill="none" stroke="#1e2d3d" stroke-width="4"/>'
                f'<circle cx="22" cy="22" r="{r}" fill="none" stroke="{color}" stroke-width="4" '
                f'stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-dashoffset="{circ/4:.2f}" stroke-linecap="round"/>'
                f'<text x="22" y="22" text-anchor="middle" dy=".35em" fill="{color}" font-size="9" font-weight="800">{pct}%</text>'
                f'</svg>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>World's Worst Punter · First Shot On Target Edge Finder</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#080d18;color:#e2e8f0;min-height:100vh;font-size:12px}}

/* ── TOPBAR ── */
.topbar{{display:flex;justify-content:space-between;align-items:center;padding:10px 20px;background:#0d1424;border-bottom:1px solid #1a2540}}
.topbar-left{{display:flex;align-items:center;gap:10px}}
.trophy{{font-size:1.35rem}}
.site-title{{font-size:1.08rem;font-weight:800;letter-spacing:-.3px}}
.site-title .wc{{color:#22c55e}}
.site-title .rest{{color:#f1f5f9}}
.site-title .accent{{color:#4ade80}}
.site-subtitle{{color:#64748b;font-size:.68rem;margin-top:2px}}
.topbar-right{{display:flex;align-items:center;gap:10px;text-align:right}}
.last-upd-label{{color:#64748b;font-size:.6rem;text-transform:uppercase;letter-spacing:.4px}}
.last-upd-val{{color:#94a3b8;font-size:.68rem;font-weight:600}}
.refresh-btn{{width:26px;height:26px;background:#1a2540;border:1px solid #2a3a5c;border-radius:5px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:#64748b;font-size:.75rem}}
.refresh-btn:hover{{background:#1e2d4a;color:#e2e8f0}}

/* ── KPI BAR ── */
.kpi-bar{{display:flex;gap:0;background:#0d1424;border-bottom:1px solid #1a2540}}
.kpi{{flex:1;display:flex;align-items:center;gap:10px;padding:12px 16px;border-right:1px solid #1a2540}}
.kpi:last-child{{border-right:none}}
.kpi-icon{{width:34px;height:34px;border-radius:8px;background:#22c55e18;display:flex;align-items:center;justify-content:center;font-size:.95rem;flex-shrink:0}}
.kpi-icon.blue{{background:#3b82f618}}
.kpi-icon.purple{{background:#8b5cf618}}
.kpi-icon.amber{{background:#f59e0b18}}
.kpi-n{{font-size:1.3rem;font-weight:800;color:#f1f5f9;line-height:1}}
.kpi-sub{{font-size:.6rem;color:#64748b;margin-top:3px}}
.kpi-sub .dim{{color:#4b5563;font-size:.57rem}}

/* ── MAIN LAYOUT ── */
.main{{display:flex;gap:0;min-height:calc(100vh - 100px)}}
.content{{flex:1;padding:16px 16px 32px;min-width:0;border-right:1px solid #1a2540}}
.sidebar{{width:248px;flex-shrink:0;padding:16px 13px;background:#0b1020}}

/* ── SECTION HEADERS ── */
.sec-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}
.sec-title{{display:flex;align-items:center;gap:7px;font-weight:700;font-size:.83rem;color:#f1f5f9}}
.sec-title .ico{{color:#22c55e}}
.sec-subtitle{{color:#64748b;font-size:.63rem;font-weight:400;margin-left:4px}}
.view-all{{background:#1a2540;border:1px solid #2a3a5c;color:#94a3b8;font-size:.67rem;padding:5px 10px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:4px;text-decoration:none}}
.view-all:hover{{background:#1e2d4a;color:#e2e8f0}}

/* ── BEST EDGES TABLE ── */
.be-card{{background:#0f1929;border:1px solid #1a2540;border-radius:9px;overflow:hidden;margin-bottom:16px}}
.be-table{{width:100%;border-collapse:collapse}}
.be-table th{{padding:8px 10px;font-size:.58rem;color:#4b5563;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #1a2540;text-align:left;white-space:nowrap}}
.be-table th.th-m{{color:#3b82f6}}
.be-table th.th-b{{color:#f59e0b}}
.be-row td{{padding:9px 10px;border-bottom:1px solid #111d30;vertical-align:middle}}
.be-row:last-child td{{border-bottom:none}}
.be-row:hover td{{background:#111e33}}

.rank-circle{{display:inline-flex;width:19px;height:19px;background:#22c55e;border-radius:50%;align-items:center;justify-content:center;font-size:.63rem;font-weight:800;color:#000}}
.avatar{{width:29px;height:29px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.63rem;font-weight:700;color:#fff;flex-shrink:0}}
.be-player{{display:flex;align-items:center;gap:7px}}
.be-name{{font-weight:600;color:#f1f5f9;font-size:.77rem}}
.be-country{{font-size:.6rem;color:#64748b;margin-top:1px}}
.be-match{{font-weight:700;font-size:.72rem;color:#f1f5f9}}
.be-date{{font-size:.6rem;color:#64748b;margin-top:1px}}
.td-model{{color:#3b82f6;font-weight:800;font-size:.82rem}}
.td-bm{{color:#f59e0b;font-weight:700;font-size:.77rem}}
.odds-val{{font-weight:800;color:#f1f5f9;margin-right:3px}}
.mob-edge{{display:none}}
.pill-short{{display:none}}

/* ── FK TAG ── */
.fk-tag{{font-size:.55rem;font-weight:800;background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44;padding:1px 4px;border-radius:3px;letter-spacing:.3px;vertical-align:middle}}
.early-tag{{font-size:.55rem;font-weight:800;background:#3b82f622;color:#60a5fa;border:1px solid #3b82f644;padding:1px 4px;border-radius:3px;letter-spacing:.3px;vertical-align:middle}}
.inj-tag{{font-size:.55rem;font-weight:800;background:#ef444422;color:#ef4444;border:1px solid #ef444444;padding:1px 5px;border-radius:3px;letter-spacing:.3px;vertical-align:middle}}

/* ── FILTER BAR ── */
.filter-bar{{display:flex;align-items:center;gap:7px;margin-bottom:12px;flex-wrap:wrap}}
.ftab{{background:#0f1929;border:1px solid #1a2540;color:#94a3b8;font-size:.67rem;padding:6px 12px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:4px;white-space:nowrap}}
.ftab:hover{{background:#162038;color:#e2e8f0}}
.ftab.active{{background:#22c55e18;border-color:#22c55e55;color:#22c55e}}
.ftab .fi{{font-size:.72rem}}
.search-wrap{{flex:1;min-width:160px;position:relative}}
.search-wrap input{{width:100%;padding:6px 10px 6px 28px;background:#0f1929;border:1px solid #1a2540;border-radius:5px;color:#e2e8f0;font-size:.7rem;outline:none}}
.search-wrap input:focus{{border-color:#22c55e55}}
.search-wrap input::placeholder{{color:#4b5563}}
.search-icon{{position:absolute;left:9px;top:50%;transform:translateY(-50%);color:#4b5563;font-size:.72rem}}
.filter-btn{{background:#0f1929;border:1px solid #1a2540;color:#94a3b8;font-size:.67rem;padding:6px 10px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:4px}}

/* ── MATCH CARDS ── */
.mcard{{background:#0f1929;border:1px solid #1a2540;border-radius:9px;margin-bottom:7px;overflow:hidden}}
.mcard:hover{{border-color:#2a3a5c}}
.card-dim{{opacity:.45}}
.mcard-header{{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;cursor:pointer;flex-wrap:wrap;gap:5px}}
.mcard-header:hover{{background:#111d30}}
.mcard-left{{display:flex;align-items:center;gap:7px;flex-wrap:wrap}}
.mflag{{font-size:1rem}}
.mteam{{font-weight:700;font-size:.82rem;color:#f1f5f9}}
.mvs{{color:#4b5563;font-size:.63rem;font-weight:700;background:#1a2540;padding:2px 5px;border-radius:3px}}
.mbadge{{font-size:.58rem;font-weight:600;padding:2px 7px;border-radius:3px}}
.nat-badge{{background:#22c55e18;color:#22c55e;border:1px solid #22c55e33}}
.bk-badge{{background:#1a2540;color:#64748b}}
.tbc-badge{{background:#f59e0b18;color:#f59e0b}}
.mcard-right{{display:flex;align-items:center;gap:9px}}
.mdate{{color:#64748b;font-size:.65rem}}
.mchev{{color:#4b5563;font-size:.72rem;transition:transform .2s}}
.mchev.open{{transform:rotate(180deg)}}

.mcard-body{{display:none;padding:0 14px 12px}}
.mcard.open .mcard-body{{display:block}}
.mcard.open .mcard-header{{border-bottom:1px solid #1a2540}}

.mtable{{width:100%;border-collapse:collapse;margin-top:5px}}
.mtable th{{padding:7px 9px;font-size:.57rem;color:#4b5563;text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid #1a2540;text-align:left;white-space:nowrap}}
.mtable th.th-m{{color:#3b82f6}}
.mtable th.th-b{{color:#f59e0b}}
.th-info{{color:#2a3a5c;cursor:help}}
.mtable td{{padding:8px 9px;border-bottom:1px solid #111d30;vertical-align:middle;font-size:.77rem}}
.mtable tr:last-child td{{border-bottom:none}}
.mtable tr:hover td{{background:#111e33}}
.medal{{font-size:.85rem}}
.rank-sm{{display:inline-flex;width:16px;height:16px;background:#1a2540;border-radius:50%;align-items:center;justify-content:center;font-size:.58rem;color:#64748b;font-weight:700}}
.td-pname{{font-weight:600;color:#f1f5f9}}
.p-flag{{font-size:.9rem;margin-right:2px}}
.no-data{{text-align:center;color:#4b5563;padding:16px!important;font-style:italic;font-size:.72rem}}
.mfootnote{{color:#2a3a5c;font-size:.58rem;margin-top:9px;padding-top:7px;border-top:1px solid #111d30;line-height:1.6}}
.mfootnote sub{{font-size:.54rem;vertical-align:sub}}

/* ── EDGE PILLS ── */
.epill{{font-size:.72rem;font-weight:700;padding:3px 8px;border-radius:4px;white-space:nowrap;display:inline-flex;align-items:center;gap:3px}}
.e-strong-val{{background:#22c55e22;color:#22c55e;border:1px solid #22c55e44}}
.e-slight-val{{background:#22c55e11;color:#4ade80}}
.e-neutral{{background:#1a2540;color:#64748b}}
.e-slight-fad{{background:#ef444411;color:#fca5a5}}
.e-strong-fad{{background:#ef444422;color:#ef4444;border:1px solid #ef444444}}

/* ── CONFIDENCE ── */
.cbadge{{font-size:.7rem;font-weight:600;padding:3px 8px;border-radius:4px;white-space:nowrap}}
.conf-hi{{background:#22c55e18;color:#22c55e}}
.conf-med{{background:#f59e0b18;color:#f59e0b}}
.conf-lo{{background:#ef444418;color:#ef4444}}

/* ── BOOKMAKER LOGOS ── */
.bm{{font-size:.68rem;font-weight:700;white-space:nowrap}}
.wh{{color:#f1f5f9;background:#111;padding:2px 5px;border-radius:3px;font-size:.63rem}}
.wh strong{{font-size:.7rem}}
.un{{color:#f59e0b;font-size:.65rem;letter-spacing:.5px}}
.un-dots{{color:#f59e0b44;font-size:.5rem;margin-left:1px}}
.pp{{color:#22c55e;font-size:.65rem}}
.lv{{color:#c084fc;font-size:.65rem}}
.bf{{color:#f97316;font-size:.65rem}}
.xbet{{color:#1d9bf0;font-size:.65rem;font-weight:700}}
.fd{{color:#1db954;font-size:.65rem;font-weight:700}}
.br{{color:#7c3aed;font-size:.65rem;font-weight:700}}
.b365{{color:#f97316;font-size:.65rem;font-weight:700}}
.generic{{color:#94a3b8;font-size:.65rem;background:#1a2540;padding:2px 5px;border-radius:3px}}

/* ── SIDEBAR ── */
.sb-section{{background:#0f1929;border:1px solid #1a2540;border-radius:9px;padding:11px 13px;margin-bottom:10px}}
.sb-title{{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:.73rem;color:#f1f5f9;margin-bottom:10px}}
.sb-title .sb-ico{{color:#22c55e;margin-right:5px}}
.sb-toggle{{color:#64748b;cursor:pointer;font-size:.67rem}}

.model-item{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.model-item:last-child{{margin-bottom:0}}
.mi-circle{{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:middle;justify-content:center;font-size:.62rem;font-weight:800;flex-shrink:0}}
.mi-green{{background:#22c55e22;color:#22c55e;border:2px solid #22c55e44}}
.mi-blue{{background:#3b82f622;color:#3b82f6;border:2px solid #3b82f644}}
.mi-purple{{background:#8b5cf622;color:#8b5cf6;border:2px solid #8b5cf644}}
.mi-amber{{background:#f59e0b22;color:#f59e0b;border:2px solid #f59e0b44}}
.mi-label{{font-weight:700;font-size:.7rem;color:#f1f5f9;line-height:1.2}}
.mi-sub{{font-size:.6rem;color:#64748b;margin-top:1px}}
.show-details{{color:#22c55e;font-size:.65rem;cursor:pointer;display:flex;align-items:center;gap:4px;margin-top:7px}}

.sb-stat{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #111d30}}
.sb-stat:last-child{{border-bottom:none}}
.sb-stat-label{{color:#64748b;font-size:.67rem}}
.sb-stat-val{{font-weight:700;color:#f1f5f9;font-size:.73rem}}
.sb-upd{{color:#4b5563;font-size:.6rem;margin-top:7px}}
.sb-upd span{{color:#22c55e}}

.cov-item{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.cov-item:last-child{{margin-bottom:0}}
.cov-label{{font-size:.66rem;color:#94a3b8;font-weight:600;line-height:1.3}}
.cov-sub{{font-size:.59rem;color:#4b5563;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}

.leg-item{{display:flex;align-items:center;gap:7px;padding:4px 0;font-size:.65rem;color:#94a3b8}}
.leg-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.leg-range{{color:#4b5563;font-size:.6rem;margin-left:auto}}

.disclaimer{{background:#1a2540;border:1px solid #2a3a5c;border-left:3px solid #3b82f6;border-radius:5px;padding:8px 10px;margin-top:7px;color:#64748b;font-size:.62rem;line-height:1.6}}

/* ── MODAL ── */
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:1000;align-items:center;justify-content:center;padding:20px}}
.modal-overlay.open{{display:flex}}
.modal{{background:#0f1929;border:1px solid #2a3a5c;border-radius:14px;width:100%;max-width:580px;max-height:88vh;overflow-y:auto;box-shadow:0 25px 60px rgba(0,0,0,.6)}}
.modal-head{{display:flex;justify-content:space-between;align-items:center;padding:18px 20px 14px;border-bottom:1px solid #1a2540;position:sticky;top:0;background:#0f1929;z-index:1}}
.modal-head h2{{font-size:.95rem;font-weight:800;color:#f1f5f9;display:flex;align-items:center;gap:8px}}
.modal-close{{width:28px;height:28px;background:#1a2540;border:1px solid #2a3a5c;border-radius:6px;color:#64748b;cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;line-height:1}}
.modal-close:hover{{background:#2a3a5c;color:#f1f5f9}}
.modal-body{{padding:18px 20px}}
.modal-section{{margin-bottom:20px}}
.modal-section:last-child{{margin-bottom:0}}
.modal-section h3{{font-size:.72rem;text-transform:uppercase;letter-spacing:.6px;color:#22c55e;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px}}
.modal-section p,.modal-section li{{font-size:.78rem;color:#94a3b8;line-height:1.75}}
.modal-section ul{{padding-left:16px;margin-top:6px}}
.modal-section li{{margin-bottom:4px}}
.modal-section strong{{color:#f1f5f9}}
.modal-formula{{background:#080d18;border:1px solid #1a2540;border-radius:7px;padding:12px 14px;font-family:monospace;font-size:.75rem;color:#22c55e;margin:10px 0;line-height:1.8}}
.modal-factor{{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid #1a2540}}
.modal-factor:last-child{{border-bottom:none}}
.mf-circle{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:800;flex-shrink:0;margin-top:1px}}
.mf-title{{font-weight:700;font-size:.8rem;color:#f1f5f9;margin-bottom:3px}}
.mf-desc{{font-size:.72rem;color:#64748b;line-height:1.6}}
.modal-divider{{border:none;border-top:1px solid #1a2540;margin:16px 0}}

/* ── BEST EDGES COLLAPSE ── */
.be-toggle{{display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none}}
.be-chev{{color:#64748b;font-size:.75rem;transition:transform .2s}}
.be-chev.closed{{transform:rotate(-90deg)}}
.be-body{{overflow:hidden;transition:max-height .25s ease}}
.be-body.collapsed{{display:none}}

/* ── TABLET ── */
@media(max-width:900px){{
  .sidebar{{display:none}}
  .kpi{{padding:10px 12px}}
}}

/* ── HELPERS ── */
.mob-only{{display:none}}
.desk-only{{display:inline}}

/* ── TABLET ── */
@media(max-width:900px){{
  .sidebar{{display:none}}
  .kpi{{padding:10px 12px}}
}}

/* ── MOBILE ── */
@media(max-width:600px){{

  /* Show/hide helpers */
  .mob-only{{display:inline}}
  .desk-only{{display:none!important}}
  .mob-edge{{display:inline-flex!important;margin-left:4px}}

  /* Topbar — single compact line */
  .topbar{{padding:8px 12px;gap:8px}}
  .topbar-left{{gap:8px}}
  .trophy{{font-size:1rem;flex-shrink:0}}
  .site-title{{font-size:.78rem;font-weight:800;line-height:1.2}}

  /* KPI bar — 3 items, hide date */
  .kpi-bar{{flex-wrap:wrap}}
  .kpi{{flex:1;min-width:33%;padding:8px 10px;gap:6px;border-right:none;border-bottom:1px solid #1a2540}}
  .kpi:last-child{{display:none}}
  .kpi-icon{{width:26px;height:26px;font-size:.75rem;flex-shrink:0}}
  .kpi-n{{font-size:1rem}}
  .kpi-sub{{font-size:.55rem}}
  .kpi-sub .dim{{display:none}}

  /* Content */
  .content{{padding:10px 10px 32px}}

  /* Best Edges — clean header */
  .be-card > div:first-child{{padding:10px 12px 8px;flex-direction:row;gap:6px;align-items:center;flex-wrap:wrap}}
  .sec-title{{font-size:.8rem;flex:1}}
  .sec-subtitle{{display:none}}
  .be-toggle{{gap:6px}}
  .view-all{{font-size:.62rem;padding:4px 8px}}

  /* BE table — fix rank/player spacing */
  .be-table th:nth-child(1),.be-row td:nth-child(1){{width:28px;padding:8px 6px 8px 8px}}
  .be-table th:nth-child(2),.be-row td:nth-child(2){{width:auto;padding-left:0}}
  .be-table th:nth-child(4),.be-row td:nth-child(4){{width:86px;text-align:right;padding-right:8px;overflow:hidden}}
  .be-table th:nth-child(4){{font-size:.58rem}}
  .be-row td:nth-child(4) .mob-edge .epill{{max-width:82px;overflow:hidden;font-size:.58rem}}

  /* Best Edges table — rank | player | model+edge only */
  .be-table th:nth-child(3),.be-row td:nth-child(3),
  .be-table th:nth-child(5),.be-row td:nth-child(5),
  .be-table th:nth-child(6),.be-row td:nth-child(6),
  .be-table th:nth-child(7),.be-row td:nth-child(7),
  .be-table th:nth-child(8),.be-row td:nth-child(8){{display:none}}
  .be-table{{font-size:.75rem;table-layout:fixed;width:100%}}
  .be-table th:nth-child(1){{width:30px}}
  .be-table th:nth-child(2){{width:auto}}
  .be-table th:nth-child(4){{width:90px;white-space:nowrap}}
  .be-row td{{padding:8px 10px;vertical-align:middle}}
  .rank-circle{{width:18px;height:18px;font-size:.6rem}}
  .avatar{{width:26px;height:26px;font-size:.6rem;flex-shrink:0}}
  .be-player{{gap:6px}}
  .be-name{{font-size:.75rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:110px;display:block}}
  .be-country{{font-size:.6rem}}
  .td-model{{font-size:.82rem;white-space:nowrap}}
  .epill{{font-size:.62rem;padding:2px 5px}}
  .pill-long{{display:none}}
  .pill-short{{display:inline}}

  /* Match card headers */
  .mcard-header{{padding:10px 12px;gap:4px}}
  .mteam{{font-size:.78rem}}
  .mflag{{font-size:.9rem}}
  .mdate{{font-size:.6rem}}
  .mbadge{{font-size:.55rem;padding:1px 5px}}
  .mvs{{font-size:.6rem;padding:2px 4px}}

  /* Match card table — show only: rank | player | model+edge */
  .mtable th:nth-child(4),.mtable td:nth-child(4),
  .mtable th:nth-child(5),.mtable td:nth-child(5),
  .mtable th:nth-child(6),.mtable td:nth-child(6),
  .mtable th:nth-child(7),.mtable td:nth-child(7){{display:none}}
  .mtable{{table-layout:fixed;width:100%}}
  .mtable th:nth-child(1),.mtable td:nth-child(1){{width:32px;padding-right:4px}}
  .mtable th:nth-child(2),.mtable td:nth-child(2){{width:auto}}
  .mtable th:nth-child(3),.mtable td:nth-child(3){{width:110px;text-align:right}}
  .mtable td{{padding:8px 6px;font-size:.78rem}}
  .td-pname{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px;display:block}}
  .td-model{{text-align:right;white-space:nowrap}}
  .mcard-body{{padding:0 10px 12px}}
  .medal{{font-size:.85rem}}
  .rank-sm{{width:16px;height:16px;font-size:.6rem}}

  /* Filter bar */
  .filter-bar{{gap:5px;flex-wrap:wrap}}
  .ftab{{font-size:.62rem;padding:5px 9px;flex-shrink:0}}
  .filter-btn{{display:none}}
  .search-wrap{{order:10;min-width:100%;margin-top:2px}}
  .search-wrap input{{font-size:.7rem;padding:7px 12px 7px 28px}}

}}
</style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <div class="topbar-left">
    <span class="trophy">🏆</span>
    <div>
      <div class="site-title">
        <span class="wc">WC 2026</span>&nbsp;
        <span class="rest desk-only">World's Worst Punter's <span class="accent">First Shot On Target Edge Finder</span></span>
        <span class="mob-only" style="color:#f1f5f9;font-weight:800">First Shot <span class="accent">Edge Finder</span></span>
      </div>
      <div class="site-subtitle desk-only">Cat Dad Model probabilities vs bookmaker-implied odds for every group-stage match.</div>
      <div class="mob-only" style="color:#64748b;font-size:.6rem;margin-top:2px">Updated {updated}</div>
    </div>
  </div>
  <div class="topbar-right desk-only">
    <div>
      <div class="last-upd-label">Last updated</div>
      <div class="last-upd-val">{updated}</div>
    </div>
    <div class="refresh-btn" onclick="location.reload()">↻</div>
  </div>
</div>

<!-- KPI BAR -->
<div class="kpi-bar">
  <div class="kpi">
    <div class="kpi-icon">📅</div>
    <div><div class="kpi-n">{total}</div><div class="kpi-sub">Matches<br><span class="dim">Group Stage</span></div></div>
  </div>
  <div class="kpi">
    <div class="kpi-icon blue">📈</div>
    <div><div class="kpi-n">{with_odds}</div><div class="kpi-sub">With Live Odds<br><span class="dim">{odds_pct}% of matches</span></div></div>
  </div>
  <div class="kpi">
    <div class="kpi-icon purple">👥</div>
    <div><div class="kpi-n">48</div><div class="kpi-sub">Teams<br><span class="dim">Qualified</span></div></div>
  </div>
  <div class="kpi">
    <div class="kpi-icon amber">🕐</div>
    <div><div class="kpi-n">{updated.split()[0]} {updated.split()[1]} {updated.split()[2]}</div><div class="kpi-sub">Last Updated<br><span class="dim">{updated.split("·")[1].strip() if "·" in updated else ""}</span></div></div>
  </div>
</div>

<!-- MAIN -->
<div class="main">

  <!-- CONTENT -->
  <div class="content">

    <!-- BEST EDGES -->
    <div class="be-card">
      <div style="padding:14px 16px 0;display:flex;justify-content:space-between;align-items:center">
        <div class="sec-title">
          <span class="ico">📊</span> Best Edges
          <span class="sec-subtitle">Top value opportunities across all matches</span>
        </div>
        <div class="be-toggle" onclick="toggleBE()">
          <a class="view-all" href="#all-matches" onclick="event.stopPropagation()">View all matches →</a>
          <span style="margin-left:6px;color:#64748b;font-size:.67rem" id="be-label">▲ Collapse</span>
        </div>
      </div>
      <div class="be-body" id="be-body">
      <table class="be-table" style="margin-top:10px">
        <thead>
          <tr>
            <th>RANK</th><th>PLAYER</th><th>MATCH</th>
            <th class="th-m">CAT DAD MODEL</th>
            <th class="th-b">BOOKIE</th>
            <th>EDGE ⓘ</th>
            <th>ODDS</th>
            <th title="Data Quality: how much independent evidence backs this prediction. High = national stats + shot timing data. Low = bookmaker data only.">DATA ⓘ</th>
          </tr>
        </thead>
        <tbody>
{be_rows}
        </tbody>
      </table>
      </div>
    </div>

    <!-- FILTER BAR -->
    <div class="filter-bar" id="all-matches">
      <button class="ftab active" onclick="filterMatches('all',this)"><span class="fi">📅</span> All Matches</button>
      <button class="ftab" onclick="filterMatches('value',this)"><span class="fi">⭐</span> Value Only</button>
      <button class="ftab" onclick="filterMatches('live',this)"><span class="fi">📡</span> With Live Odds</button>
      <button class="ftab" onclick="filterMatches('high',this)"><span class="fi">✦</span> Rich Data</button>
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input type="text" placeholder="Search player or team..." oninput="searchMatches(this.value)">
      </div>
      <button class="filter-btn">⚙ Filters</button>
    </div>

    <!-- MATCH CARDS -->
    <div id="match-list">
{mcards}
    </div>

  </div><!-- /content -->

  <!-- SIDEBAR -->
  <div class="sidebar">

    <!-- How it works -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">🐱</span> How the Cat Dad Model Works</span><span class="sb-toggle">▾</span></div>
      <p style="color:#64748b;font-size:.62rem;margin-bottom:9px">Two-step model: which team shoots first, then which player.</p>
      <div class="model-item">
        <div class="mi-circle mi-blue" style="font-size:.55rem">H2H</div>
        <div><div class="mi-label">Step 1 · Team First SOT</div><div class="mi-sub">Win odds → P(team attacks first)</div></div>
      </div>
      <div class="model-item">
        <div class="mi-circle mi-green" style="font-size:.55rem">SOT</div>
        <div><div class="mi-label">Step 2 · Player Shot Rate</div><div class="mi-sub">35% bookie λ + 25% intl SOT/90</div></div>
      </div>
      <div class="model-item">
        <div class="mi-circle mi-purple">⚡</div>
        <div><div class="mi-label">Early-Game Tendency</div><div class="mi-sub">High-press forwards shoot in first 15 mins</div></div>
      </div>
      <div class="model-item">
        <div class="mi-circle mi-amber">FK</div>
        <div><div class="mi-label">Set Piece Specialist</div><div class="mi-sub">FK takers +12% · Injury doubts −65%</div></div>
      </div>
      <div class="show-details" onclick="openModal()">Show full details ▾</div>
    </div>

    <!-- Model Status -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">📈</span> Model Status</span></div>
      <div class="sb-stat"><span class="sb-stat-label">Total Matches</span><span class="sb-stat-val">{total}</span></div>
      <div class="sb-stat"><span class="sb-stat-label">With Live Odds</span><span class="sb-stat-val">{with_odds}</span></div>
      <div class="sb-stat"><span class="sb-stat-label">Teams with National Data</span><span class="sb-stat-val">{nat_cov}</span></div>
      <p class="sb-upd">Last Updated <span>{updated}</span></p>
    </div>

    <!-- Data Coverage -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">📊</span> Data Coverage</span></div>
      <div class="cov-item">
        {donut(nat_pct, "#22c55e")}
        <div>
          <div class="cov-label">National Team Stats</div>
          <div class="cov-sub">{nat_cov} / 48 teams · 2022–2025</div>
        </div>
      </div>
      <div class="cov-item">
        {donut(odds_pct, "#3b82f6")}
        <div>
          <div class="cov-label">Bookmaker Odds</div>
          <div class="cov-sub">{with_odds} / {total} matches · updates daily</div>
        </div>
      </div>
      <div class="cov-item">
        {donut(min(100, round(sb_players / 7)), "#8b5cf6")}
        <div>
          <div class="cov-label">Shot Timing Data</div>
          <div class="cov-sub">{sb_players} players · WC 2018 & 2022</div>
        </div>
      </div>
    </div>

    <!-- Edge Legend -->
    <div class="sb-section">
      <div class="sb-title"><span><span class="sb-ico">📋</span> Edge Legend</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#22c55e;border:2px solid #22c55e66"></span> Strong Value <span class="leg-range">(≥ +1.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#4ade80"></span> Slight Value <span class="leg-range">(+0.5% to +1.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#2a3a5c"></span> Neutral <span class="leg-range">(−0.5% to +0.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#fca5a5"></span> Slight Fade <span class="leg-range">(−0.5% to −1.5%)</span></div>
      <div class="leg-item"><span class="leg-dot" style="background:#ef4444;border:2px solid #ef444466"></span> Strong Fade <span class="leg-range">(≤ −1.5%)</span></div>
    </div>

    <div class="disclaimer">
      ⓘ This is a modelling tool, not betting advice. Bookmaker odds move quickly. Always check live prices before placing a bet.
    </div>

  </div><!-- /sidebar -->

</div><!-- /main -->

<script>
// Toggle match cards
// ── MODAL ──
function openModal() {{
  document.getElementById('model-modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeModal() {{
  document.getElementById('model-modal').classList.remove('open');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', function(e) {{ if(e.key==='Escape') closeModal(); }});

// ── BEST EDGES COLLAPSE ──
var beOpen = true;
function toggleBE() {{
  beOpen = !beOpen;
  var body = document.getElementById('be-body');
  var lbl  = document.getElementById('be-label');
  body.classList.toggle('collapsed', !beOpen);
  lbl.textContent = beOpen ? '▲ Collapse' : '▼ Expand';
}}

// ── MATCH CARDS ──
function tog(id) {{
  var c = document.getElementById('mc-'+id);
  var ch = document.getElementById('chev-'+id);
  var open = c.classList.contains('open');
  c.classList.toggle('open', !open);
  if(ch) ch.classList.toggle('open', !open);
}}

// Filter tabs
var activeFilter = 'all';
function filterMatches(type, btn) {{
  activeFilter = type;
  document.querySelectorAll('.ftab').forEach(function(b){{ b.classList.remove('active'); }});
  if(btn) btn.classList.add('active');
  applyFilters();
}}

function searchMatches(q) {{
  document.getElementById('search-query', q);
  applyFilters(q);
}}

function applyFilters(searchQ) {{
  var q = (searchQ || document.querySelector('.search-wrap input').value || '').toLowerCase();
  document.querySelectorAll('.mcard').forEach(function(card) {{
    var txt = card.textContent.toLowerCase();
    var matchSearch = !q || txt.includes(q);
    var matchFilter = true;
    if(activeFilter === 'value') matchFilter = card.querySelector('.e-strong-val, .e-slight-val') !== null;
    if(activeFilter === 'live')  matchFilter = !card.classList.contains('card-dim');
    if(activeFilter === 'high')  matchFilter = card.querySelector('.conf-hi') !== null;
    card.style.display = (matchSearch && matchFilter) ? '' : 'none';
  }});
}}

// Auto-open first 3 matches with data
var n=0;
document.querySelectorAll('.mcard:not(.card-dim)').forEach(function(c){{
  if(n<3){{ var id=c.id.replace('mc-',''); tog(id); n++; }}
}});
</script>

<!-- ── MODEL DETAIL MODAL ── -->
<div class="modal-overlay" id="model-modal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-head">
      <h2>🐱 The Cat Dad Model — How It Works</h2>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">

      <div class="modal-section">
        <h3>🎯 The Bet</h3>
        <p><strong>First Shot on Target</strong> — you pick one player to have the first shot on target in a match. It doesn't need to be a goal, just any attempt that forces the goalkeeper to save. This is a prop bet offered by William Hill, Unibet, and others. It's a niche market, which means bookmakers sometimes misprice it — that's our edge.</p>
      </div>

      <div class="modal-section">
        <h3>🧠 The Core Idea — Two Steps</h3>
        <p>We don't just ask <em>"who shoots the most?"</em> — we ask <em>"who generates the first shot before everyone else?"</em> That's a different problem. We solve it in two steps:</p>
        <div class="modal-formula">
          Step 1 · Which team gets the first SOT?<br>
          Step 2 · Which player on that team pulls the trigger?<br><br>
          P(player first SOT) = P(team first SOT) × P(player | team shoots first)
        </div>
        <p><strong>Why this matters:</strong> If Mexico are 80% likely to get the first SOT (they're big favourites), Mexican strikers should dominate the rankings — even if a South African player has great individual stats.</p>
      </div>

      <hr class="modal-divider">

      <div class="modal-section">
        <h3>⚙️ Step 1 — Which Team Shoots First?</h3>
        <div class="modal-factor">
          <div class="mf-circle mi-blue" style="font-size:.55rem">H2H</div>
          <div>
            <div class="mf-title">Match Win Odds → Team Attack Probability</div>
            <div class="mf-desc">We convert the bookmaker's match winner odds into a probability that each team generates the first SOT. The stronger team (shorter price to win) attacks first in roughly 65% of matches they win, and 50/50 in draws. We weight these to get <strong>P(team gets first SOT)</strong>. Example: Mexico 1.36 to win → ~79% chance they get first SOT.</div>
          </div>
        </div>
      </div>

      <div class="modal-section">
        <h3>⚙️ Step 2 — Which Player on That Team?</h3>
        <p style="margin-bottom:10px">Once we know which team is likely to shoot first, we rank players within that team using five factors:</p>

        <div class="modal-factor">
          <div class="mf-circle mi-green" style="font-size:.6rem">SOT</div>
          <div>
            <div class="mf-title">International Shooting Stats <span style="color:#64748b;font-weight:400;font-size:.7rem">(35% bookie + 25% nat stats)</span></div>
            <div class="mf-desc">We use each player's <strong>shots on target per 90 minutes for their national team</strong> (2022–2025: World Cup, Nations League, qualifiers). This beats club stats because players have different roles for their country — a striker who shoots 3× a game at club level may play deeper internationally. The bookmaker's "Over 0.5 SOT" odds fill the gaps where we lack data.</div>
          </div>
        </div>

        <div class="modal-factor">
          <div class="mf-circle mi-purple">⚡</div>
          <div>
            <div class="mf-title">Early-Game Tendency <span style="color:#64748b;font-weight:400;font-size:.7rem">(15%)</span></div>
            <div class="mf-desc">This market isn't about who shoots most over 90 minutes — it's about who shoots <em>first</em>. High-press forwards (Mbappe, Son, Saka, Vinicius Jr) attempt shots in the opening 10–15 minutes far more often than ball-retention midfielders. We apply a <strong>+15% boost</strong> to known early-game attackers. ⚡ badge = confirmed early shooter.</div>
          </div>
        </div>

        <div class="modal-factor">
          <div class="mf-circle mi-amber">FK</div>
          <div>
            <div class="mf-title">Free Kick Specialist <span style="color:#64748b;font-weight:400;font-size:.7rem">(5%)</span></div>
            <div class="mf-desc">Free kicks inside the final third are one of the most common sources of early shots on target. If a foul is won in the first 5 minutes, the designated FK taker walks up and shoots. We track known specialists (Son, Griezmann, Bruno Fernandes, De Bruyne, Messi) with a <strong>+12% boost</strong>. FK badge = verified taker.</div>
          </div>
        </div>

        <div class="modal-factor">
          <div class="mf-circle" style="background:#ef444422;color:#ef4444;border:2px solid #ef444444;font-size:.55rem">⚠</div>
          <div>
            <div class="mf-title">Injury / Availability <span style="color:#64748b;font-weight:400;font-size:.7rem">(hard penalty)</span></div>
            <div class="mf-desc">A player with a 10% model probability becomes near-zero if he's doubtful to start. We apply a <strong>−65% penalty</strong> to confirmed injury doubts. The bookmaker odds often lag on fitness news — this is where we can find real edge. ⚠ DOUBT badge = flagged as uncertain starter.</div>
          </div>
        </div>
      </div>

      <hr class="modal-divider">

      <div class="modal-section">
        <h3>📐 Reading the Edge</h3>
        <p><strong>Edge = Cat Dad Model % − Bookmaker Implied %</strong></p>
        <p style="margin-top:6px">The bookmaker implied % is calculated by normalising their "Over 0.5 SOT" odds across all players in the match — it tells you what the market thinks. Our model % is our independent estimate. The gap between them is the edge.</p>
        <div style="margin-top:10px;display:flex;flex-direction:column;gap:6px">
          <div style="display:flex;align-items:center;gap:8px"><span class="epill e-strong-val">+2.1% Strong</span><span style="font-size:.75rem;color:#94a3b8">Our model rates this player significantly higher than the market. Potential value bet.</span></div>
          <div style="display:flex;align-items:center;gap:8px"><span class="epill e-slight-val">+0.8% Slight</span><span style="font-size:.75rem;color:#94a3b8">Small disagreement. Worth noting but not a strong signal.</span></div>
          <div style="display:flex;align-items:center;gap:8px"><span class="epill e-neutral">Neutral</span><span style="font-size:.75rem;color:#94a3b8">Model and market agree. No edge either way.</span></div>
          <div style="display:flex;align-items:center;gap:8px"><span class="epill e-strong-fad">−2.0% Fade</span><span style="font-size:.75rem;color:#94a3b8">Market is overrating this player vs our model. Consider avoiding.</span></div>
        </div>
      </div>

      <hr class="modal-divider">

      <div class="modal-section">
        <h3>⚠️ What This Model Doesn't Do (Yet)</h3>
        <ul>
          <li><strong>Confirmed lineups</strong> — we don't yet factor in whether a player is starting. A high-probability player who's on the bench is worthless. Always check team news before betting.</li>
          <li><strong>Shot timing data</strong> — ✅ Now integrated from StatsBomb WC 2018 + 2022 event data. Players with real early-shot % data get a data-driven timing multiplier.</li>
          <li><strong>Opponent defensive profile</strong> — we don't yet adjust for how many early SOTs each opponent concedes. Coming in v2.</li>
          <li>Positive edge does not guarantee profit. This is a tool, not a guarantee.</li>
        </ul>
      </div>

    </div>
  </div>
</div>

</body>
</html>"""

if __name__ == "__main__":
    print("Loading data...")
    events   = load("wc_events.json") or []
    all_odds = load("all_odds.json") or {}
    squads   = load("wc_squads.json") or {}
    nat_agg  = load("national_stats_agg.json") or {}
    sb_data  = load("statsbomb_shot_timing.json") or {}

    updated = datetime.now(AEST).strftime("%d %b %Y · %H:%M AEST")
    nat_cov = len(nat_agg)
    sb_players = len(sb_data)
    print(f"  Events: {len(events)}, Nat stat teams: {nat_cov}, StatsBomb players: {sb_players}")

    games = []
    for event in sorted(events, key=lambda e: e["commence_time"]):
        eid = event["id"]
        home, away = event["home_team"], event["away_team"]
        players = build_predictions(all_odds.get(eid,{}), home, away, nat_agg, squads, sb_data)
        nat_c = sum(1 for p in players[:5] if p.get("has_nat"))
        games.append({
            "id": eid, "home": home, "away": away,
            "date_fmt": fmt_date(event["commence_time"]),
            "date_short": fmt_date_short(event["commence_time"]),
            "time": fmt_time(event["commence_time"]),
            "players": players,
            "has_data": bool(players),
            "nat_count": nat_c,
        })

    total = len(games)
    with_odds = sum(1 for g in games if g["has_data"])
    odds_pct = round(with_odds / total * 100) if total else 0
    print(f"  {total} games, {with_odds} with odds")

    html = build_html(games, updated, nat_cov, total, with_odds, sb_players)
    with open("index.html","w") as f: f.write(html)
    print("Built → index.html")
