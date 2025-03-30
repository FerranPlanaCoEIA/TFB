# TFB
Chatbot de la Coppermind


## Pasar la documentación a pdf  

pandoc "Documentación TFB.html" -o "Documentación TFB.pdf" 
pandoc "Documentación TFB.html" -o "Documentación TFB.pdf" --pdf-engine=pdflatex -V geometry:margin=2.5cm
cp "Documentación TFB.pdf" /home/fpc/Downloads