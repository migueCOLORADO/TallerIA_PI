# 🎬 Workshop 3 - Integración de Inteligencia Artificial en el Proyecto de Películas

En este workshop integraremos herramientas de **Inteligencia Artificial** al proyecto de películas. 

### 📌 Objetivos
- Utilizar modelos de lenguaje (GPT vía API de OpenAI) para **crear nuevas películas** en la base de datos.
- Generar **imágenes representativas** de cada película usando una API de creación de imágenes.
- Desarrollar un **sistema de recomendación** basado en embeddings.

---
> ⚠️ **Recomendación Importante**
>
> Antes de realizar cada actividad, lee el documento completo de la etapa correspondiente.  
> Esto te permitirá comprender mejor las instrucciones y evitar errores durante el desarrollo.  
> **Ejemplo:** Lee el documento `1_Fork_and_clone.md` completo antes de realizar las actividades del punto 1.  
> Haz lo mismo con cada etapa del taller.
---
---
>⚠️ Recomendación Importante
>
>Asegúrate de incluir el archivo openAI.env en el archivo .gitignore de tu proyecto.
>Esto evitará que por error subas tu llave privada de OpenAI a GitHub y la expongas públicamente.
>Ejemplo: Agrega la línea openAI.env dentro de tu .gitignore antes de hacer git add.
>Verifica siempre que los archivos sensibles no estén en el área de staging.

---


## 📝 Instrucciones por etapas
1. [Hacer Fork del proyecto base](1_Fork_and_clone.md)
2. [Crear la API key en OpenAI](2a_openAIapikey.md) (No es necesario, las API keys serán entregadas por el docente)
3. [Instalar las librerías necesarias](3_Instalaciones.md)
4. [Generar o actualizar las descripciones de las películas](4_movie_descriptions.md)
5. [Crear ilustraciones de las películas](5_movie_pictures.md)
6. [Crear embeddings de las descripciones de las películas](6_movie_similarities.md)
7. [Implementar el sistema de recomendación](7_movie_recommendations.md)

---

## ✅ Entregable en Clase
Entregar un archivo **PDF** que contenga:

1. ✅ Link del repositorio del proyecto en GitHub.
2. ✅ Captura de pantalla de la **modificación de la descripción de la primera película** usando [update_descriptions.py](update_descriptions.py).
3. ✅ Captura de pantalla de la **actualización de las descripciones** con el comando `update_movies_from_csv`.
4. ✅ Captura de pantalla de la **modificación de la imagen de la primera película** con [update_images.py](update_images.py).
5. ✅ Captura de pantalla de la **modificación de todas las imágenes de las películas** usando `update_images_from_folder`.
6. ✅ Captura de pantalla de la ejecución de la **generación de embeddings** y comparación con **similitud de coseno** usando [movie_similarities.py](movie_similarities.py).
7. ✅ Captura de pantalla del embedding generado para una película al azar.

---

## 🚀 Entregable Final - Semana del **14 de septiembre de 2026**
**Objetivo:** Convertir el sistema de recomendación en una **nueva app** dentro del proyecto.

### 📲 Requisitos de la App
- Incluir un nuevo ítem en la **barra de navegación** (similar a *News*).
- La app debe tener un campo para ingresar el **prompt** de la recomendación (Ejemplo: _Película de la segunda guerra mundial_).
- Mostrar como resultado:
  - ✅ La película recomendada
  - ✅ La imagen
  - ✅ La descripción
- La vista debe ser similar a la búsqueda de película en la app **Movies**.

### 📄 Entrega
Entregar un archivo **PDF** con:
1. ✅ Link al repositorio de GitHub actualizado
2. ✅ Captura de pantalla de la app funcionando con un ejemplo de búsqueda y su resultado

---
