# TFB
Chatbot de la Coppermind

> :warning: **Aviso**: Este repositorio debe ser ejecutado en python 3.11.11. Hacerlo en otra versión podría producir fallos o errores de dependencias a la hora de instalar los requirements.

## Pasar la documentación a pdf  

pandoc "Documentación TFB.html" -o "Documentación TFB.pdf" 
pandoc "Documentación TFB.html" -o "Documentación TFB.pdf" --pdf-engine=pdflatex -V geometry:margin=2.5cm
cp "Documentación TFB.pdf" /home/fpc/Downloads