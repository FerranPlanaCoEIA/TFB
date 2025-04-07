# TFB
Chatbot de la Coppermind

> :warning: **Aviso**: Este repositorio debe ser ejecutado en python 3.11.11. Hacerlo en otra versión podría producir fallos o errores de dependencias a la hora de instalar los requirements.

## Pasar la documentación a pdf  

pandoc "Documentación TFB.md" -o "Documentación TFB.html" 
pandoc "Documentación TFB.html" -o "Documentación TFB.pdf" --pdf-engine=pdflatex -V geometry:margin=2.5cm
cp "Documentación TFB.pdf" /home/fpc/Downloads

## Pasar de pdf a texto plano a md  

Posibilidades:  

* pdftotext nombre.pdf - | pandoc -f markdown -t markdown -o nombre.md  

* pip install markitdown  
    pip install "markitdown[all]"  
    markitdown nombre.pdf -o nombre.md

Buscar alternativas mejores y comparar estas 2