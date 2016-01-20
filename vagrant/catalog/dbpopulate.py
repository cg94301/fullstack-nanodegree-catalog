from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbinit import Base, Varietal, Wine

engine = create_engine('sqlite:///redwines.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

varietalptr = Varietal(name = "Cabernet Sauvignon")
session.add(varietalptr)
session.commit()

wineptr = Wine(name = "Caymus Napa Valley", year = "2013" , description = "The 2013 growing season was another great one in Napa Valley. Deep, red and opulent in color, this wine opens with the vibrant scent of dark cherry and blackberry, subtly layered with warm notes of vanilla. The palate is explosive, bright, balanced - cassis at the center, with flourishes of cocoa and sweet tobacco that provide nuance and continually shifting points of interest. Velvety meshed tannins make this wine lush yet structured, with a texture that grabs attention, expands and unfolds. Fruit, oak and acidity are held in balance throughout the long, drawn-out finish.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(name = "Silver Oak Alexander Valley", year = "2011", description = "The 2011 Alexander Valley Cabernet Sauvignon is a harmonious and vibrant wine. This full-bodied, classic expression of Alexander Valley Cabernet in a cool vintage has a bright ruby-red color with purple undertones. The nose exudes aromas of black cherry, cedar and black olives. On the palate, its dried herb, cocoa and lavender flavors are framed by dusty tannins and a savory texture. This wine finishes with lively acidity and a lingering persistence. Given proper cellaring, this wine should give drinking pleasure through 2029.", varietal = varietalptr)
session.add(wineptr)
session.commit()

varietalptr = Varietal(name = "Pinot Noir")
session.add(varietalptr)
session.commit()

wineptr = Wine(name = "Goldeneye Anderson Valley", year = "2012", description = "The exceptional 2012 vintage yielded a rich, robust Anderson Valley Pinot Noir with a delightful blend of sweet and savory elements. On the palate, beautifully delineated layers of freshly tilled earth, leather, lavender and pennyroyal are balanced by flavors of sweet Bing cherry, Japanese plum and black currant notes. The mouth feel is round and plump, gliding to a long, satisfying finish marked by lingering notes of chocolaty French oak.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(name = "Leese-Fitch", year="2013", description="Light Ruby in color, this Pinot Noir boast aromas of cherry pie, cola, orange blossom, toasty brioche, and freshly crushed raspberries. The wine is bright upon entry with flavors of Bing cherry, tart cranberry, sour plum, cardamom, black tea leaf, and hints of clove, watermelon rind, and vanilla.", varietal = varietalptr)
session.add(wineptr)
session.commit()

print "Added wines!"
