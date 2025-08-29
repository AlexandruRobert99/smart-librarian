book_summaries_dict = {
    "1984": (
        "Roman distopic despre o societate în care statul controlează totul prin supraveghere, "
        "cenzură și propagandă. Winston Smith simte nevoia de adevăr și libertate, dar orice formă "
        "de gândire independentă este considerată crimă. În încercarea de a se opune, descoperă prețul "
        "rezistenței într-un sistem care rescrie realitatea."
    ),
    "The Hobbit": (
        "Bilbo Baggins, un hobbit comod, pornește pe neașteptate într-o călătorie alături de un grup "
        "de pitici pentru a-și recăpăta comoara furată de dragonul Smaug. Pe drum, Bilbo descoperă curaj, "
        "spirit de echipă și ingeniozitate, trecând prin întâlniri cu troli, orci și creaturi misterioase. "
        "Povestea explorează prietenia, aventura și maturizarea interioară."
    ),
    "The Fellowship of the Ring": (
        "Prima parte din Stăpânul Inelelor urmărește formarea Frăției Ineleului, un grup unit de misiunea "
        "de a distruge Inelul Suprem. Frodo, Sam, Aragorn și ceilalți pornesc într-o călătorie periculoasă, "
        "încercând să reziste tentației și amenințării lui Sauron. Sacrificiul, prietenia și speranța sunt "
        "forțele care îi țin împreună."
    ),
    "Harry Potter and the Philosopher's Stone": (
        "Harry află că este vrăjitor și pășește în lumea magică a Hogwarts-ului, unde își face prieteni "
        "adevărați și descoperă indicii despre trecutul său. Înfruntă primele pericole și învață să aibă "
        "încredere în sine. Cartea vorbește despre prietenie, curaj și alegerea binelui."
    ),
    "To Kill a Mockingbird": (
        "Prin ochii lui Scout Finch, copilăria într-un orășel din Alabama dezvăluie tensiuni rasiale și "
        "nedreptăți profunde. Tatăl ei, avocatul Atticus, apără un bărbat nevinovat acuzat pe nedrept. "
        "Romanul subliniază empatia, formarea morală și curajul de a face ceea ce e drept."
    ),
    "The Little Prince": (
        "O întâlnire poetică între un pilot rătăcit și un prinț venit de pe o planetă minusculă. "
        "Prințul povestește despre călătoriile sale și despre rose, invitându-ne să privim cu inima, "
        "nu doar cu ochii. Tema centrală e sensul prieteniei și al iubirii în fața superficialității adulte."
    ),
    "The Book Thief": (
        "În Germania nazistă, Liesel fură și împarte cărți, găsind în cuvinte sprijin împotriva "
        "pierderii și fricii. Familia ei ascunde un evreu în pivniță, iar războiul le schimbă viețile. "
        "Narațiunea reflectă puterea cuvintelor, umanitatea în vremuri întunecate și curajul."
    ),
    "Dune": (
        "Pe planeta deșertică Arrakis, Paul Atreides devine ținta intrigilor politice pentru controlul "
        "condimentului-spice. Între profeții, ecologie și supraviețuire, el îmbrățișează destinul său "
        "în mijlocul triburilor Fremen. Romanul examinează puterea, religia, mediul și leadership-ul."
    ),
    "Pride and Prejudice": (
        "Elizabeth Bennet și domnul Darcy își depășesc prejudecățile și greșelile de judecată pentru a se "
        "descoperi cu adevărat. Într-o societate ghidată de etichetă, reputație și clasă, povestea "
        "evidențiază auto-reflecția, respectul și iubirea care crește din înțelegere reală."
    ),
    "The Alchemist": (
        "Santiago pornește într-o călătorie spre Egipt călăuzit de un vis repetitiv, întâlnind mentori și "
        "semne care îl ghidează spre propriul său scop. Pe drum învață să-și asculte inima și să recunoască "
        "oportunitățile. O parabolă despre destin, perseverență și sens personal."
    ),
    "The Lion, the Witch and the Wardrobe": (
        "Patru frați descoperă Narnia, o lume înghețată de o vrăjitoare, și îl întâlnesc pe leul Aslan. "
        "Prin încercări și trădări, aleg calea curajului și a iertării. Povestea explorează sacrificiul, "
        "redempțiunea și prietenia."
    ),
    "The Catcher in the Rye": (
        "Holden Caulfield rătăcește prin New York după ce pleacă de la internat, respingând ipocrizia pe "
        "care o percepe în jur. Între durere și cinism, caută autenticitate și protejarea inocenței. "
        "O meditație asupra alienării și trecerii la maturitate."
    )
}

def get_summary_by_title(title: str) -> str:
    """Returnează rezumatul complet pentru un titlu exact sau un mesaj prietenos dacă nu există."""
    return book_summaries_dict.get(title, "Nu am găsit un rezumat complet pentru acest titlu.")
