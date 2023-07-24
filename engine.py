from sqlalchemy import create_engine

connection_string = "mysql+mysqlconnector://root:password:Brezza0585!@127.0.0.1:3306/Lodha_Chemist"

engine = create_engine(connection_string, echo=True)

