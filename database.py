import sqlalchemy
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode
from localisation import Localisation

class Database:
    def __init__(self, connection_url: str) -> None:
        self.engine = sqlalchemy.create_engine(connection_url)
        self.indices = dict[str, VectorStoreIndex]()

    def generateIndices(self, locales: list[Localisation]) -> None:
        """
        ``lang`` is required because Index is created for localised string representations of data
        """
        with self.engine.connect() as db:
            cursor = db.execute(sqlalchemy.text('SELECT id, name, is_available, price FROM medicines'))
            result = cursor.fetchall()
            medicines = [MedicineData(*row._data) for row in result]

        # calculate embedding for each row localised string, put the index into vector store
        for loc in locales:
            nodes = [TextNode(text=m.str(loc)) for m in medicines]
            index = VectorStoreIndex(nodes)
            self.indices[loc.lang_code] = index

    def getIndex(self, lang_code: str) -> VectorStoreIndex:
        index = self.indices.get(lang_code, None)
        if index is None:
            raise KeyError(f'no index for language "{lang_code}"')
        return index

class MedicineData:
    def __init__(self, id: int, name: str, is_available: int, price: int) -> None:
        self.id = id
        self.name = name
        self.is_available = is_available != 0
        self.price = price
    
    def str(self, locale: Localisation):
        if(self.is_available):
            return locale.getStr("medicine_data_available_format_str").format(
                name=self.name, price=self.price, id=self.id)
        else:
            return locale.getStr("medicine_data_unavailable_format_str").format(
                name=self.name, price=self.price, id=self.id)
