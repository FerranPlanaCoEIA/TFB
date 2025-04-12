import os
import shutil
from markitdown import MarkItDown

# Obtener la lista de archivos que convertir (pdf, docx, md)
def create_convert_and_index_array(data_folder_path,extensions_to_index,extensions_to_convert):

    # Obtener el array de todos los documentos sobre los que hacer el RAG
    all_files=os.listdir(data_folder_path)
    files_to_index=[]
    for file in all_files:
        if file.endswith(tuple(extensions_to_index)):
            files_to_index.append(file)

    # Sustituir los espacios de todos los archivos por _ para evitar posibles errores
    for i,file_name in enumerate(files_to_index):
        if " " in file_name:
            new_file_name=file_name.replace(" ","_")
            os.rename(file_name,new_file_name)
            files_to_index[i]=new_file_name

    # Obtener la lista de documentos que convertir a md
    files_to_convert=[]
    for file in files_to_index:
        if file.endswith(tuple(extensions_to_convert)):
            files_to_convert.append(file)


    return files_to_index,files_to_convert


# Convertir los archivos según su tipo
# TODO: Add a try-except in the md conversion and deal with the error cases
def transform_to_md(script_path,files_to_index,extensions_to_convert):
    md=MarkItDown()

    for file in files_to_index:
        if file.endswith(".md"): # Copiamos en la misma carpeta los que ya sean md
            shutil.copy(f"{script_path}/{file}",f"{script_path}/Markdowns convertidos/{file}")

    for terminacion in extensions_to_convert:
        for file in files_to_index:
            if file.endswith(terminacion):
                resultado=md.convert(file)
                new_name=file.replace(terminacion,".md")
                with open(f"Markdowns convertidos/{new_name}",'w',encoding='utf-8') as f:
                    f.write(resultado.text_content)
                files_to_index[files_to_index.index(file)]=new_name


    return files_to_index

            



extensions_to_index=[".pdf",".docx",".html",".md"]
extensions_to_convert=[".pdf",".docx",".html"]
script_path=os.path.dirname(os.path.abspath(__file__)) # Path de este script
files_to_index,files_to_convert=create_convert_and_index_array(script_path,extensions_to_index,extensions_to_convert)

files_to_index=transform_to_md(script_path,files_to_index,extensions_to_convert)




