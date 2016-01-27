# Run this script to add wines to the DB

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbinit import Base, Varietal, Wine, User

engine = create_engine('sqlite:///redwines.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

userptr = User(name="Joe Red", email="joered@example.com", picture="https://upload.wikimedia.org/wikipedia/commons/5/5f/Rilley_elf_south_park_avatar.png")
session.add(userptr)
session.commit()

varietalptr = Varietal(name = "Cabernet Sauvignon")
session.add(varietalptr)
session.commit()

wineptr = Wine(user_id=1, name = "Caymus Napa Valley", year = "2013" , label="/static/158729le.png", description = "The 2013 growing season was another great one in Napa Valley. Deep, red and opulent in color, this wine opens with the vibrant scent of dark cherry and blackberry, subtly layered with warm notes of vanilla. The palate is explosive, bright, balanced - cassis at the center, with flourishes of cocoa and sweet tobacco that provide nuance and continually shifting points of interest. Velvety meshed tannins make this wine lush yet structured, with a texture that grabs attention, expands and unfolds. Fruit, oak and acidity are held in balance throughout the long, drawn-out finish.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(user_id=1, name = "Silver Oak Alexander Valley", year = "2011", label="/static/647389le.png", description = "The 2011 Alexander Valley Cabernet Sauvignon is a harmonious and vibrant wine. This full-bodied, classic expression of Alexander Valley Cabernet in a cool vintage has a bright ruby-red color with purple undertones. The nose exudes aromas of black cherry, cedar and black olives. On the palate, its dried herb, cocoa and lavender flavors are framed by dusty tannins and a savory texture. This wine finishes with lively acidity and a lingering persistence. Given proper cellaring, this wine should give drinking pleasure through 2029.", varietal = varietalptr)
session.add(wineptr)
session.commit()

varietalptr = Varietal(name = "Pinot Noir")
session.add(varietalptr)
session.commit()

wineptr = Wine(user_id=1, name = "Goldeneye Anderson Valley", year = "2012", label="/static/143857le.jpg", description = "The exceptional 2012 vintage yielded a rich, robust Anderson Valley Pinot Noir with a delightful blend of sweet and savory elements. On the palate, beautifully delineated layers of freshly tilled earth, leather, lavender and pennyroyal are balanced by flavors of sweet Bing cherry, Japanese plum and black currant notes. The mouth feel is round and plump, gliding to a long, satisfying finish marked by lingering notes of chocolaty French oak.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(user_id=1, name = "Leese-Fitch", year="2013", label="/static/138547le.jpg", description="Light Ruby in color, this Pinot Noir boast aromas of cherry pie, cola, orange blossom, toasty brioche, and freshly crushed raspberries. The wine is bright upon entry with flavors of Bing cherry, tart cranberry, sour plum, cardamom, black tea leaf, and hints of clove, watermelon rind, and vanilla.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(user_id=1, name = "Chapter 24 Last Chapter", year="2012", label="/static/136122le.jpg", description="The Last Chapter Pinot Noir is produced from grapes grown in both volcanic soil (Fire) and sedimentary soil (Flood). Coming from four vineyards (Shea, Hyland, Tresori, DDL) the combination carries both bright and tart 'red' notes from the fire set against deeper more soulful 'blue' notes from the flood.", varietal = varietalptr)
session.add(wineptr)
session.commit()

varietalptr = Varietal(name = "Malbec")
session.add(varietalptr)
session.commit()

wineptr = Wine(user_id=1, name = "Duckhorn Napa Valley", year="2012", label="/static/877453le.png", description="This Napa Valley Merlot is a complex blend of several individual vineyard lots, incorporating fruit from our Estate Vineyards and from top independent growers throughout the Napa Valley. The final wine is a rich and cohesive expression of the entire Napa Valley, reflecting the varied microclimates and soils of this unique appellation.", varietal = varietalptr)
session.add(wineptr)
session.commit()

varietalptr = Varietal(name = "Merlot")
session.add(varietalptr)
session.commit()

wineptr = Wine(user_id=1, name = "Casarena Jamilla's Vineyard", year="2011", label="/static/145292le.jpg", description="Casarena Jamilla's Vineyard Malbec is pure elegance. Rocky limestone and shallow soil terroir's best expression is this wine with mineral notes, floral and red fruit flavors. Fresh.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(user_id=1, name = "Tangley's Oaks", year="2012", label="/static/352689le.png", description="The 2012 Tangley Oaks Merlot is a medium garnet color. This wine offers aromas of rich plums, dark cherries, chocolate and savory herbs. On the palate, lush plums and cherry fruit with undertones of mocha.", varietal = varietalptr)
session.add(wineptr)
session.commit()

varietalptr = Varietal(name = "Syrah")
session.add(varietalptr)
session.commit()

wineptr = Wine(user_id=1, name = "Mollydooker Carnival of Love", year="2011", label="/static/632891le.png", description="This is the wine I tell all my friends about. To see the look on their faces after their first sip is priceless. The 2011 Carnival of Love so clearly shows the essence of Mollydooker. It has elegance; a complete, intense, seamless flavour spectrum; a sumptuous mouth feel and perfect balance. At 92% Fruit Weight it is a wine to go WOW about, an absolute beauty.", varietal = varietalptr)
session.add(wineptr)
session.commit()

wineptr = Wine(user_id=1, name = "Clarendon Hills Astralis Syrah", year="2010", label="http://png.clipart.me/previews/563/vintage-wine-label-collection-03-vector-5372.jpg", description="The pride of our portfolio, Clarendon Hills Astralis Syrah has a deep black-purple crimson color that alludes to its aromas of boysenberry, forest floor and Asian spice and flavors ripe blackberry. An overall full-bodied wine, the Astralis is softened by silky tannins and a mouth-engulfing structure that sails on seamlessly to a long, lingering finish.", varietal = varietalptr)
session.add(wineptr)
session.commit()

print "Added wines!"
